import asyncio
import json
import logging
import os
import random

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d]: %(message)s",
)
logger = logging.getLogger(__name__)


EDA_SERVICE_HOST = os.getenv("EDA_SERVICE_HOST", "localhost")
EDA_SERVICE_PORT = int(os.getenv("EDA_SERVICE_PORT", "9444"))
EDA_BASE_URL = f"http://{EDA_SERVICE_HOST}:{EDA_SERVICE_PORT}"

FRONT_SERVICE_HOST = os.getenv("FRONT_SERVICE_HOST", "localhost")
FRONT_SERVICE_PORT = int(os.getenv("FRONT_SERVICE_PORT", "9443"))
FRONT_BASE_URL = f"http://{FRONT_SERVICE_HOST}:{FRONT_SERVICE_PORT}"

PROJ_ID = "1"


async def submit_task(task_payload: dict[str:object]) -> bool:
    """Submit a task to the server."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info("Submitting %s task %s", task_payload["taskType"], task_payload["taskId"])
            logger.info("Task payload: %s", json.dumps(task_payload, indent=2))

            response = await client.post(f"{EDA_BASE_URL}/apis/v1/ieda/stdin", json=task_payload)

            if response.status_code == 200:
                result = response.json()
                logger.info("✓ Task submitted successfully: %s", result)
                return True
            else:
                logger.error("Task submission failed: %s", response.status_code)
                logger.error("Response: %s", response.text)
                return False

    except Exception as e:
        logger.error("Error submitting task: %s", e)
        return False


async def run_synthesis(top_name: str, clk_port_name: str) -> bool:
    """Run synthesis task test."""
    logger.info("=== Running Synthesis Task Test ===")

    task_payload = {
        "projectId": PROJ_ID,
        "taskId": str(random.randint(1, 10000)),
        "taskType": "synthesis",
        "parameter": {
            "TOP_NAME": top_name,
            "CLK_PORT_NAME": clk_port_name,
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
        "taskId": str(random.randint(1, 10000)),
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
        "taskId": str(random.randint(1, 10000)),
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
                logger.info("✓ Task overview: %s", data)
            else:
                logger.error("Task overview failed: %s", response.status_code)
    except Exception as e:
        logger.error("Error monitoring task overview: %s", e)
        return {}


async def check_server_health() -> bool:
    """Check if server is running and healthy."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response_front = await client.get(f"{FRONT_BASE_URL}/hello")
            logger.info("Front response: %s", response_front.status_code)
            response_eda = await client.get(f"{EDA_BASE_URL}/hello")
            logger.info("EDA response: %s", response_eda.status_code)
            if response_eda.status_code == 200 and response_front.status_code == 200:
                logger.info("✓ Server is healthy")
                return True
            else:
                logger.error(
                    "Server health check failed: %s, %s",
                    response_eda.status_code,
                    response_front.status_code,
                )
                return False
    except Exception as e:
        logger.error("check_server_health: Cannot connect to server: %s", e)
        return False


async def main():
    try:
        if not await check_server_health():
            logger.error("Server is not healthy, aborting tests")
            return

        await monitor_task_overview()

        await run_synthesis("gcd", "clk")
        await asyncio.sleep(1)
        await run_floorplan()
        await asyncio.sleep(1)
        await run_pnr("placement")
        await asyncio.sleep(1)
        await run_pnr("cts")
        await asyncio.sleep(1)
        await run_pnr("routing")
        await asyncio.sleep(1)
        await run_pnr("signoff")

        await monitor_task_overview()

    except Exception as e:
        logger.error("Error running tests: %s", e)


if __name__ == "__main__":
    asyncio.run(main())
