from itgs import Itgs
from login import create_and_login_user


async def test_update_exists():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test", "sampling_max_count": 100},
            )
            response = await backend.put(
                "/api/1/progress_bars/?name=test",
                headers={"Authorization": f"bearer {user.token}"},
                json={"sampling_max_count": "75"},
            )
            assert response.ok, response


async def test_update_nonexistant():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.put(
                "/api/1/progress_bars/?name=test",
                headers={"Authorization": f"bearer {user.token}"},
                json={"sampling_max_count": "75"},
            )
            assert response.status == 404, response
