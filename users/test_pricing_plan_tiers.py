from itgs import Itgs
from login import create_and_login_user


async def test_new_user_has_tier():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/users/pricing_plans/tiers/search",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            data = await response.json()
            assert len(data["items"]) >= 1, data
