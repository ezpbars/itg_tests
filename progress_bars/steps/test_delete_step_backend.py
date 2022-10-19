from itgs import Itgs
from login import create_and_login_user


async def test_delete_exists():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )
            await backend.post(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            response = await backend.delete(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
            )
            assert response.ok, response


async def test_delete_nonexistant_pbar():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.delete(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
            )
            data = await response.json()
            assert response.status == 404, data
            assert data["type"] == "pbar_not_found", data


async def test_delete_nonexistant_step():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )
            response = await backend.delete(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
            )
            data = await response.json()
            assert response.status == 404, data
            assert data["type"] == "step_not_found", data


async def test_delete_default_step():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )
            response = await backend.delete(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=default",
                headers={"Authorization": f"bearer {user.token}"},
            )
            data = await response.json()
            assert response.status == 409, data
            assert data["type"] == "cannot_delete_default_step", data
