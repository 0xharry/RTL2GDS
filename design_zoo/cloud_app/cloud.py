import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import httpx
import uvicorn
import yaml
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from rtl2gds.global_configs import CLOUD_FLOW_STEPS, StepName

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,
)

MOUNT_POINT = Path(os.getenv("PROJ_MOUNT_POINT", "/home/user/RTL2GDS/tmp/projectData"))
assert MOUNT_POINT.exists(), f"Mount point {MOUNT_POINT} does not exist."

MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "1"))
ACTIVE_TASKS = {}

task_lock = asyncio.Lock()
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
app = FastAPI()


# Notification classes and functions
@dataclass
class NotifyTaskBody:
    # files: list[str]
    files: dict[str, str | list[str] | dict[str, str]]
    serverTimestamp: int
    status: str
    taskId: str
    taskType: str
    projectId: str


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    SYNTHESIS = StepName.SYNTHESIS
    FLOORPLAN = StepName.FLOORPLAN
    PLACEMENT = StepName.PLACEMENT
    CTS = StepName.CTS
    ROUTING = StepName.ROUTING
    SIGNOFF = StepName.SIGNOFF


@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    reraise=True,
)
async def notify_task_async(
    result_files: dict[str, object],
    task_type: str,
    task_id: str,
    status: TaskStatus,
    project_id: str,
):
    """Asynchronously send notification to front-end service about task completion."""
    notify_host = os.getenv("FRONT_SERVICE_HOST", "localhost")
    notify_port = int(os.getenv("FRONT_SERVICE_PORT", 8083))
    notify_url = f"http://{notify_host}:{notify_port}/apis/v1/notify/task"
    if not notify_url:
        logging.exception("FRONT_SERVICE_HOST env variable not set. Cannot notify.")
        return

    logging.info(f"Sending notification to: {notify_url}")

    json_body = NotifyTaskBody(
        files=result_files,
        serverTimestamp=int(datetime.now().timestamp()),
        status=status.value,
        taskId=task_id,
        taskType=task_type,
        projectId=project_id,
    )
    logging.info(f"Notification body: {json_body}")

    # headers = (
    #     {
    #         "Content-Type": "application/json",
    #         "ecos-app-secret": os.getenv("ECOS_APP_SECRET"),
    #     },
    # )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logging.info(f"Sending notification for task {task_id} to {notify_url}...")
            response = await client.post(url=notify_url, json=asdict(json_body))
            response.raise_for_status()
            logging.info(f"Notification for task {task_id} sent successfully: {response.text}")
    except httpx.RequestError as e:
        # catches non-retryable httpx errors or the final error after retries are exhausted.
        logging.error(
            f"Failed to send notification for task {task_id} after all attempts. Final error: {e}"
        )
        raise


# API Models
class StdinEDA(BaseModel):
    projectId: str
    taskId: str
    taskType: str
    parameter: dict


class ResponseData(BaseModel):
    code: str


class ResponseModel(BaseModel):
    code: int
    message: str
    data: ResponseData


class TaskOverview(BaseModel):
    task_id: str
    project_id: str
    status: str
    submitted_at: datetime


async def _upper_dict_key(dict_str: dict[str, object]) -> dict[str, object]:
    res = {}
    for k, v in dict_str.items():
        if isinstance(v, dict):
            res[k] = _upper_dict_key(v)
            continue
        res[k.upper()] = v
    return res


async def prepare_rtl2gds_task(
    project_id: str, task_id: str, step_name: StepName, task_params: dict
):
    proj_workspace = MOUNT_POINT / f"project_{project_id}"
    config_yaml = proj_workspace / "config.yaml"
    # Prepare configuration dictionary
    config = await _upper_dict_key(task_params)

    task_workspace = proj_workspace / f"task_{task_id}"
    task_workspace.mkdir(parents=True, exist_ok=True)
    task_workspace_abs_path = str(task_workspace.resolve())
    config["RESULT_DIR"] = task_workspace_abs_path

    # create config.yaml at init step (synthesis for now)
    if step_name == StepName.SYNTHESIS:
        if not config_yaml.is_file():
            # @TODO: support rtl from parameter, sv and multiple rtl files
            tmp_rtl_file = proj_workspace / "top.v"
            config["RTL_FILE"] = str(tmp_rtl_file.resolve())
            logging.info(f"Creating config.yaml at {config_yaml}")
            with open(config_yaml, "w") as f:
                yaml.dump(config, f)
        # else:
        #     assert False, f"Config file {config_yaml} already exists before synthesis."
    else:
        if not config_yaml.is_file():
            raise FileNotFoundError(
                f"Config file {config_yaml} does not initialized at synthesis step."
            )

    # update RESULT_DIR back to config yaml
    with open(config_yaml, "r") as f:
        previous_config = yaml.safe_load(f)
    previous_config.update(config)
    with open(config_yaml, "w") as f:
        yaml.dump(previous_config, f)
    logging.debug(f"update RESULT_DIR in config.yaml to {task_workspace_abs_path}")

    return config, config_yaml, task_workspace_abs_path


async def run_rtl2gds_task(stdin: StdinEDA) -> None:
    """
    Background task to run RTL2GDS cloud flow.

    Note: It acquires a semaphore to control concurrency and
    runs the RTL2GDS tool as a separate, non-blocking subprocess.
    """
    task_id = stdin.taskId
    project_id = stdin.projectId
    step_name = stdin.taskType
    logging.info(
        f"Task {task_id} of project {project_id} is waiting for an available execution slot..."
    )

    try:
        async with semaphore:
            logging.info(
                f"Semaphore acquired. Executing RTL2GDS task {task_id} for project {project_id}"
            )
            async with task_lock:
                ACTIVE_TASKS[task_id]["status"] = TaskStatus.RUNNING.value

            config, config_yaml, result_dir = await prepare_rtl2gds_task(
                project_id, task_id, step_name, stdin.parameter
            )

            logging.info(f"Calling cloud_main for task {task_id}, step: {step_name}")

            r2g_args = [
                "python3",
                "-m",
                "rtl2gds.cloud_main",
                step_name,
                str(config_yaml),
            ]
            proc = await asyncio.create_subprocess_exec(
                *r2g_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await proc.communicate()
            logging.debug(f"STDOUT: {stdout.decode()}")
            logging.debug(f"STDERR: {stderr.decode()}")

            if proc.returncode == 0:
                logging.info(f"Task {task_id} completed successfully.")
                result_files = {}
                task_res_files_json = os.path.join(
                    MOUNT_POINT, f"project_{project_id}", "current_task_result_files.json"
                )
                with open(task_res_files_json, "r") as f:
                    result_files = json.load(f)

                await notify_task_async(
                    result_files=result_files,
                    status=TaskStatus.SUCCESS,
                    task_id=task_id,
                    task_type=step_name,
                    project_id=project_id,
                )
            else:
                error_output = stderr.decode().strip()
                raise RuntimeError(f"RTL2GDS execution failed: {error_output}")

    except Exception as e:
        error_msg = f"Unexpected error in RTL2GDS task {task_id}: {e}"
        logging.exception(error_msg)
        try:
            await notify_task_async(
                result_files={},
                status=TaskStatus.FAILED,
                task_id=task_id,
                task_type=step_name,
                project_id=project_id,
            )
        except Exception as notify_exc:
            logging.error(
                f"Additionally, failed to send FAILED notification for task {task_id}: {notify_exc}"
            )
    finally:
        async with task_lock:
            if task_id in ACTIVE_TASKS:
                del ACTIVE_TASKS[task_id]
            else:
                assert False, f"Task {task_id} not found in ACTIVE_TASKS"
        logging.info(f"Semaphore released for task {task_id}")


async def check_stdin(stdin: StdinEDA) -> None:
    """Check if the stdin is valid."""
    if stdin.taskType not in CLOUD_FLOW_STEPS:
        raise ValueError(f"Invalid step name: {stdin.taskType}")
    if stdin.taskId in ACTIVE_TASKS:
        raise ValueError(f"Task {stdin.taskId} is already active.")
    # @TODO: same as line 163 prepare_rtl2gds_task()
    proj_workspace = MOUNT_POINT / f"project_{stdin.projectId}"
    tmp_rtl_file = proj_workspace / "top.v"
    if not tmp_rtl_file.is_file():
        raise FileNotFoundError(f"RTL file {tmp_rtl_file} not found")


def get_expected_step(finished_step: str) -> str | None:
    try:
        index = CLOUD_FLOW_STEPS.index(finished_step)
        if index == len(CLOUD_FLOW_STEPS) - 1:
            return None
        return CLOUD_FLOW_STEPS[index + 1]
    except ValueError:
        return None

    return


@app.post("/apis/v1/ieda/stdin", response_model=ResponseModel)
async def call_rtl2gds(stdin: StdinEDA, background_tasks: BackgroundTasks) -> ResponseModel:
    """
    Handles requests to trigger RTL2GDS cloud flow steps with task queue management.
    """
    logging.info(f"Received request: {stdin}")

    # Check if the Request stdin is valid
    try:
        await check_stdin(stdin)
    except Exception as e:
        logging.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}")

    # Add task to queue
    async with task_lock:
        ACTIVE_TASKS[stdin.taskId] = {
            "task_id": stdin.taskId,
            "project_id": stdin.projectId,
            "status": TaskStatus.PENDING.value,
            "submitted_at": datetime.now(),
        }

    # Submit task for execution
    background_tasks.add_task(run_rtl2gds_task, stdin)

    return ResponseModel(
        code=0,
        message=f"Task queued successfully.",
        data=ResponseData(code="TASK_QUEUED"),
    )


@app.get("/apis/v1/ieda/tasks_overview")
async def get_tasks_overview():
    """Provides an overview of the current task queue."""
    async with task_lock:
        # Create a copy to avoid race conditions while iterating
        tasks_list = list(ACTIVE_TASKS.values())

    running_tasks = [t for t in tasks_list if t["status"] == TaskStatus.RUNNING.value]
    pending_tasks = [t for t in tasks_list if t["status"] == TaskStatus.PENDING.value]

    running_count = len(running_tasks)

    return {
        "max_concurrent_tasks": MAX_CONCURRENT_TASKS,
        "running_count": running_count,
        "pending_count": len(pending_tasks),
        "running_tasks": [TaskOverview(**t) for t in running_tasks],
        "pending_tasks": [TaskOverview(**t) for t in pending_tasks],
    }


@app.get("/hello")
def get_hello():
    return {"Hello": "RTL2GDS Cloud YES!"}


from fastapi import Request


@app.post("/apis/v1/test/echo")
async def test_echo(request: Request):
    body = await request.body()
    logging.info(f"--- /test/echo endpoint was called successfully with {len(body)} bytes. ---")
    return {
        "status": "ok",
        "message": "If you see this, the server is not globally frozen.",
        "received_body": body.decode(),
    }


if __name__ == "__main__":
    eda_service_host = os.getenv("EDA_SERVICE_HOST", "localhost")
    eda_service_port = int(os.getenv("EDA_SERVICE_PORT", 9444))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    logging.info(f"Starting RTL2GDS API server on {eda_service_host}:{eda_service_port}")
    uvicorn.run(
        app="cloud:app",
        host=eda_service_host,
        port=eda_service_port,
        log_level=log_level,
        reload=True,
        reload_includes=["cloud.py"],
    )
