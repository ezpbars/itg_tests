from itgs import Itgs
from login import create_and_login_user


async def test_update_exists():
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
                json={"one_off_technique": "percentile"},
            )
            response = await backend.put(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
                json={"one_off_technique": "arithmetic_mean"},
            )
            assert response.ok, response


async def test_update_nonexistant_pbar():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.put(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
                json={"one_off_technique": "arithmetic_mean"},
            )
            data = await response.json()
            assert response.status == 404, data
            assert data["type"] == "pbar_not_found", data


async def test_update_nonexistant_step():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )
            response = await backend.put(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
                json={"one_off_technique": "arithmetic_mean"},
            )
            data = await response.json()
            assert response.status == 404, data
            assert data["type"] == "step_not_found", data


async def test_update_default_step():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )
            response = await backend.put(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=default",
                headers={"Authorization": f"bearer {user.token}"},
                json={"one_off_technique": "arithmetic_mean"},
            )
            data = await response.json()
            assert response.status == 409, data
            assert isinstance(data, dict), (data, type(data))
            assert data["type"] == "cannot_edit_default_step", data
