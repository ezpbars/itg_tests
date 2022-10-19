from itgs import Itgs
from login import create_and_login_user


async def test_valid_defaults():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )
            assert response.ok, response
