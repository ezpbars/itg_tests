import asyncio
import json
import time
from typing import Dict, Optional
from itgs import Itgs


async def test_get_result():
    async with Itgs() as itgs:
        backend = await itgs.backend()
        now = time.time()

        response = await backend.post(
            "/api/1/examples/job",
            json={"duration": 5, "stdev": 1},
        )
        data = await response.json()
        assert response.ok, (response, data)
        uid = data["uid"]
        sub = data["sub"]
        pbar_name = data["pbar_name"]

        async def get_result() -> Optional[Dict]:
            response = await backend.get(f"/api/1/examples/job?uid={uid}")
            result = await response.json()
            assert response.ok, (result, response)
            if result["status"] == "complete":
                return result["data"]
            return None

        async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
            await ws.send(
                json.dumps(
                    {
                        "sub": sub,
                        "progress_bar_name": pbar_name,
                        "progress_bar_trace_uid": uid,
                    }
                )
            )
            wsresponse_raw = await ws.recv()
            wsresponse = json.loads(wsresponse_raw)
            assert wsresponse["success"], wsresponse

            wsresponse_raw = await ws.recv()
            wsresponse = json.loads(wsresponse_raw)

            while wsresponse["done"] is False:
                wsresponse_raw = await ws.recv()
                wsresponse = json.loads(wsresponse_raw)

            assert wsresponse["done"] is True, wsresponse

            data = await get_result()
            assert data is not None
            assert isinstance(data["number"], int), data

            end = time.time()
            print(f"took {end - now} seconds")

            assert end - now > 0.05, "Job took too little time to complete"
            assert end - now < 10, "Job took too much time to complete"


async def test_get_result_2():
    await asyncio.gather(test_get_result(), test_get_result())
