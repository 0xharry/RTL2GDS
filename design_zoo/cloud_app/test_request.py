import asyncio
import json
import logging
import os
import uuid

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d]: %(message)s",
)
logger = logging.getLogger(__name__)


EDA_SERVICE_HOST = os.getenv("EDA_SERVICE_HOST", "localhost")
EDA_SERVICE_PORT = int(os.getenv("EDA_SERVICE_PORT", 9444))
EDA_BASE_URL = f"http://{EDA_SERVICE_HOST}:{EDA_SERVICE_PORT}"

FRONT_SERVICE_HOST = os.getenv("FRONT_SERVICE_HOST", "localhost")
FRONT_SERVICE_PORT = int(os.getenv("FRONT_SERVICE_PORT", 8083))
FRONT_BASE_URL = f"http://{FRONT_SERVICE_HOST}:{FRONT_SERVICE_PORT}"

PROJ_ID = "demov1"


async def submit_task(task_payload: dict[str:object]) -> bool:
    """Submit a task to the server."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Submitting {task_payload['taskType']} task {task_payload['taskId']}")
            logger.info(f"Task payload: {json.dumps(task_payload, indent=2)}")

            response = await client.post(f"{EDA_BASE_URL}/apis/v1/ieda/stdin", json=task_payload)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Task submitted successfully: {result}")
                return True
            else:
                logger.error(f"Task submission failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        return False


async def run_synthesis() -> bool:
    """Run synthesis task test."""
    logger.info("=== Running Synthesis Task Test ===")

    task_payload = {
        "projectId": PROJ_ID,
        "taskId": f"synthesis-{uuid.uuid4().hex[:8]}",
        "taskType": "synthesis",
        "parameter": {
            "TOP_NAME": "NPC",
            "CLK_PORT_NAME": "clock",
            "CLK_FREQ_MHZ": 200,
        },
    }
    if not await submit_task(task_payload):
        return False

    return True


async def run_floorplan() -> bool:
    """Run floorplan task test."""
    logger.info("=== Running Floorplan Task Test ===")

    task_payload = {
        "projectId": PROJ_ID,
        "taskId": f"floorplan-{uuid.uuid4().hex[:8]}",
        "taskType": "floorplan",
        "parameter": {
            "CORE_UTIL": 0.6,
        },
    }
    if not await submit_task(task_payload):
        return False

    return True


async def run_pnr(step_name: str) -> bool:
    """Run pnr task test."""
    logger.info("=== Running pnr Task Test ===")

    task_payload = {
        "projectId": PROJ_ID,
        "taskId": f"{step_name}-{uuid.uuid4().hex[:8]}",
        "taskType": step_name,
        "parameter": {
            "WHATEVER": 1,
        },
    }
    if not await submit_task(task_payload):
        return False

    return True


async def monitor_task_overview():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{EDA_BASE_URL}/apis/v1/ieda/tasks_overview")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Task overview: {data}")
            else:
                logger.error(f"Task overview failed: {response.status_code}")
    except Exception as e:
        logger.error(f"Error monitoring task overview: {e}")
        return {}


async def check_server_health() -> bool:
    """Check if server is running and healthy."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response_eda = await client.get(f"{EDA_BASE_URL}/hello")
            response_front = await client.get(f"{FRONT_BASE_URL}/hello")
            if response_eda.status_code == 200 and response_front.status_code == 200:
                logger.info("✓ Server is healthy")
                return True
            else:
                logger.error(
                    f"Server health check failed: {response_eda.status_code}, {response_front.status_code}"
                )
                return False
    except Exception as e:
        logger.error(f"Cannot connect to server: {e}")
        return False


async def main():
    try:
        if not await check_server_health():
            logger.error("Server is not healthy, aborting tests")
            return

        await monitor_task_overview()

        # await run_synthesis()
        # await run_floorplan()
        # await run_pnr("placement")
        # await run_pnr("cts")
        # await run_pnr("routing")
        await run_pnr("signoff")

        await monitor_task_overview()

    except Exception as e:
        logger.error(f"Error running tests: {e}")


if __name__ == "__main__":
    asyncio.run(main())
