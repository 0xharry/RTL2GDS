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
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field
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

EDA_SERVICE_HOST = os.getenv("EDA_SERVICE_HOST", "localhost")
EDA_SERVICE_PORT = int(os.getenv("EDA_SERVICE_PORT", "9444"))

# for iEDA runtime notification
IEDA_ECOS_NOTIFICATION_URL = os.getenv(
    "IEDA_ECOS_NOTIFICATION_URL",
    f"http://{EDA_SERVICE_HOST}:{EDA_SERVICE_PORT}/apis/v1/ieda/running_notify",
)
IEDA_ECOS_NOTIFICATION_SECRET = os.getenv("IEDA_ECOS_NOTIFICATION_SECRET", "1234567890")


# Notification classes and functions
@dataclass
class NotifyTaskBody:
    files: dict[str, str | list[str]]
    serverTimestamp: int
    status: str
    taskId: int
    taskType: str
    projectId: int


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
    task_id: int,
    status: TaskStatus,
    project_id: int,
):
    """Asynchronously send notification to front-end service about task completion."""
    notify_host = os.getenv("FRONT_SERVICE_HOST", "localhost")
    notify_port = int(os.getenv("FRONT_SERVICE_PORT", "9443"))
    notify_url = f"http://{notify_host}:{notify_port}/console-srv/v1/notify/task"
    if not notify_url:
        logging.exception("FRONT_SERVICE_HOST env variable not set. Cannot notify.")
        return

    logging.info("Sending notification to: %s", notify_url)

    json_body = NotifyTaskBody(
        files=result_files,
        serverTimestamp=int(datetime.now().timestamp()),
        status=status.value,
        taskId=task_id,
        taskType=task_type,
        projectId=project_id,
    )
    logging.info("Notification body: %s", json_body)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logging.info("Sending notification for task %s to %s...", task_id, notify_url)
            response = await client.post(
                url=notify_url,
                headers={
                    "Content-Type": "application/json",
                    "ecos-app-secret": os.getenv("ECOS_APP_SECRET"),
                },
                json=asdict(json_body),
            )
            response.raise_for_status()
            logging.info("Notification for task %s sent successfully: %s", task_id, response.text)
    except httpx.RequestError as e:
        # catches non-retryable httpx errors or the final error after retries are exhausted.
        logging.error(
            "Failed to send notification for task %s after all attempts. Final error: %s",
            task_id,
            e,
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
    # implicit project workspace rule:
    project_folder_name = f"project_{project_id}"
    proj_workspace = MOUNT_POINT / project_folder_name
    config_yaml = proj_workspace / "config.yaml"
    # Prepare configuration dictionary
    config = await _upper_dict_key(task_params)

    # implicit task workspace rule:
    task_folder_name = f"task_{task_id}"
    task_workspace = proj_workspace / task_folder_name
    task_workspace.mkdir(parents=True, exist_ok=True)
    task_workspace_abs_path = str(task_workspace.resolve())

    config.update(
        {
            "RESULT_DIR": task_workspace_abs_path,
            "IEDA_ECOS_NOTIFICATION_URL": IEDA_ECOS_NOTIFICATION_URL,
            "IEDA_ECOS_NOTIFICATION_SECRET": IEDA_ECOS_NOTIFICATION_SECRET,
            "ECOS_TASK_ID": task_id,
            "ECOS_PROJECT_ID": project_id,
            "ECOS_TASK_TYPE": step_name,
        }
    )

    # create config.yaml at init step (synthesis for now)
    if step_name == StepName.SYNTHESIS:
        if not config_yaml.is_file():
            # @TODO: support rtl from parameter, sv and multiple rtl files
            tmp_rtl_file = proj_workspace / "top.v"
            config["RTL_FILE"] = str(tmp_rtl_file.resolve())
            logging.info("Creating config.yaml at %s", config_yaml)
            with open(config_yaml, "w", encoding="utf-8") as f:
                yaml.dump(config, f)
        # else:
        #     assert False, f"Config file {config_yaml} already exists before synthesis."
    else:
        if not config_yaml.is_file():
            raise FileNotFoundError(
                f"Config file {config_yaml} does not initialized at synthesis step."
            )

    # update RESULT_DIR back to config yaml
    with open(config_yaml, "r", encoding="utf-8") as f:
        previous_config = yaml.safe_load(f)
    previous_config.update(config)
    with open(config_yaml, "w", encoding="utf-8") as f:
        yaml.dump(previous_config, f)
    logging.debug("update RESULT_DIR in config.yaml to %s", task_workspace_abs_path)

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
        "Task %s of project %s is waiting for an available execution slot...", task_id, project_id
    )

    try:
        async with semaphore:
            logging.info(
                "Semaphore acquired. Executing RTL2GDS task %s for project %s", task_id, project_id
            )
            async with task_lock:
                ACTIVE_TASKS[task_id]["status"] = TaskStatus.RUNNING.value

            # lock for generate config
            async with task_lock:
                config, config_yaml, result_dir = await prepare_rtl2gds_task(
                    project_id, task_id, step_name, stdin.parameter
                )

            logging.info("Generated config: %s, result_dir: %s", config, result_dir)
            logging.info("Calling cloud_main for task %s, step: %s", task_id, step_name)

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
            # logging.debug("STDOUT: %s", stdout.decode())
            # logging.debug("STDERR: %s", stderr.decode())

            if proc.returncode == 0:
                logging.info("Task %s completed successfully.", task_id)
                result_files = {}
                task_res_files_json = os.path.join(
                    MOUNT_POINT, f"project_{project_id}", "result_files.json"
                )
                with open(task_res_files_json, "r", encoding="utf-8") as f:
                    result_files = json.load(f)

                await notify_task_async(
                    result_files=result_files,
                    status=TaskStatus.SUCCESS,
                    task_id=int(task_id),
                    task_type=step_name,
                    project_id=int(project_id),
                )
            else:
                error_output = stderr.decode().strip()
                raise RuntimeError(f"RTL2GDS execution failed: {error_output}")

    except Exception:
        logging.exception("Unexpected error in RTL2GDS task %s", task_id)
        try:
            await notify_task_async(
                result_files={},
                status=TaskStatus.FAILED,
                task_id=int(task_id),
                task_type=step_name,
                project_id=int(project_id),
            )
        except Exception as notify_exc:
            logging.error(
                "Additionally, failed to send FAILED notification for task %s: %s",
                task_id,
                notify_exc,
            )
    finally:
        async with task_lock:
            if task_id in ACTIVE_TASKS:
                del ACTIVE_TASKS[task_id]
            else:
                assert False, f"Task {task_id} not found in ACTIVE_TASKS"
        logging.info("Semaphore released for task %s", task_id)


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


@app.post("/apis/v1/ieda/stdin", response_model=ResponseModel)
async def call_rtl2gds(stdin: StdinEDA, background_tasks: BackgroundTasks) -> ResponseModel:
    """
    Handles requests to trigger RTL2GDS cloud flow steps with task queue management.
    """
    logging.info("Received request: %s", stdin)

    # Check if the Request stdin is valid
    try:
        await check_stdin(stdin)
    except Exception as e:
        logging.error("Invalid request: %s", e)
        try:
            await notify_task_async(
                result_files={},
                status=TaskStatus.FAILED,
                task_id=int(stdin.taskId),
                task_type=stdin.taskType,
                project_id=int(stdin.projectId),
            )
        except Exception as notify_exc:
            logging.error(
                "Failed to send FAILED notification for task %s: %s", stdin.taskId, notify_exc
            )
        return ResponseModel(
            code=400,
            message=f"Invalid request: {e}",
            data=ResponseData(code="INVALID_REQUEST"),
        )

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
        message="Task queued successfully.",
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


class EdaNotificationResponse(BaseModel):
    success: bool
    response_code: int
    error_message: str = "No error message"


class NotificationPayload(BaseModel):
    tool_name: str = Field(..., description="Name of the iEDA tool")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    metadata: dict[str, str] = Field(default_factory=dict, description="Metadata")


class TaskContext(BaseModel):
    """
    Task context information extracted from notification or query parameters.
    """

    task_id: str = Field(..., description="Unique task identifier")
    project_id: str = Field(..., description="Project identifier")
    task_type: str | None = Field(None, description="Type of task")


def extract_task_context(
    request: Request,
    task_id: str | None = Query(None, description="Task ID"),
    project_id: str | None = Query(None, description="Project ID"),
    task_type: str | None = Query(None, description="Task type"),
) -> TaskContext:
    """
    Extract task context from query parameters or request payload metadata.

    Args:
        request: FastAPI request object
        task_id: Task ID from query parameters
        project_id: Project ID from query parameters
        task_type: Task type from query parameters

    Returns:
        TaskContext: Extracted task context

    Raises:
        HTTPException: If required context is missing
    """
    # Try to get from query parameters first
    context_task_id = task_id
    context_project_id = project_id
    context_task_type = task_type

    # If not in query params, we'll try to extract from payload metadata later
    # For now, require at least task_id and project_id from query params
    if not context_task_id or not context_project_id:
        raise HTTPException(
            status_code=400, detail="task_id and project_id are required as query parameters"
        )

    return TaskContext(
        task_id=context_task_id,
        project_id=context_project_id,
        task_type=context_task_type,
    )


@app.post("/apis/v1/ieda/running_notify", response_model=EdaNotificationResponse)
async def receive_ieda_runtime_notification(
    payload: NotificationPayload, context: TaskContext = Depends(extract_task_context)
) -> EdaNotificationResponse:
    """
    Receive HTTP notifications from iEDA NotificationUtility during algorithm iterations.

    This endpoint:
    1. Accepts JSON payload from NotificationUtility
    2. Extracts task_id and project_id from query parameters
    3. Parses notification data including algorithm metrics and iteration progress
    4. Calls notify_task_async with TaskStatus.RUNNING

    Args:
        payload: Notification payload from iEDA NotificationUtility
        context: Task context extracted from query parameters

    Returns:
        NotificationResponse: Response indicating success/failure

    Raises:
        HTTPException: For malformed requests or processing errors
    """
    try:
        logging.info(
            "Received notification for task %s in project %s", context.task_id, context.project_id
        )

        task_status = TaskStatus.RUNNING

        # Prepare result files metadata from notification payload
        result_files = {
            "stage": payload.metadata["stage"],
            "json_path": payload.metadata["json_path"],
        }

        # Call the existing notify_task_async function
        await notify_task_async(
            result_files=result_files,
            status=task_status,
            task_id=int(context.task_id),
            task_type=context.task_type,
            project_id=int(context.project_id),
        )

        return EdaNotificationResponse(
            success=True,
            response_code=200,
            error_message="",
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error("Error processing notification: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@app.get("/hello")
def get_hello():
    return {"Hello": "RTL2GDS Cloud YES!"}


if __name__ == "__main__":
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    uvicorn.run(
        app="cloud:app",
        host=EDA_SERVICE_HOST,
        port=EDA_SERVICE_PORT,
        log_level=log_level,
        reload=True,
        reload_includes=["cloud.py"],
    )
