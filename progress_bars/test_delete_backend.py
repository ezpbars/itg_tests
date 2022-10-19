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
            response = await backend.delete(
                "/api/1/progress_bars/?name=test",
                headers={"Authorization": f"bearer {user.token}"},
            )
            assert response.ok, response


async def test_delete_nonexistant():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.delete(
                "/api/1/progress_bars/?name=test",
                headers={"Authorization": f"bearer {user.token}"},
            )
            assert response.status == 404, response
