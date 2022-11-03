import secrets
import time
from itgs import Itgs
from login import create_and_login_user


async def test_read_empty():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.get(
                "/api/1/user_usages/get_current",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            data = await response.json()
            assert data["traces"] == 0, data


async def test_read_one():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            uid = secrets.token_urlsafe(8)
            await backend.post(
                "/api/1/progress_bars/traces/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "pbar_name": "test",
                    "uid": uid,
                    "step_name": "step1",
                    "now": time.time(),
                },
            )
            response = await backend.post(
                "/api/1/progress_bars/traces/steps/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "pbar_name": "test",
                    "trace_uid": uid,
                    "step_name": "step1",
                    "done": True,
                    "now": time.time(),
                },
            )
            assert response.ok, response

            response = await backend.get(
                "/api/1/user_usages/get_current",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            data = await response.json()
            assert data["traces"] == 1, data
