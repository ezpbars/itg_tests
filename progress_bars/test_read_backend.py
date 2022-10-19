from itgs import Itgs
from login import create_and_login_user
from retryer import retry


async def test_read_empty():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/progress_bars/search",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            assert await response.json() == {"items": [], "next_page_sort": None}


async def test_read_one():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={},
                )
                assert response.ok, response
                data = await response.json()
                assert len(data["items"]) == 1, data

            await retry(check)


async def test_name_filter():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"filters": {"name": {"operator": "eq", "value": "test2"}}},
                )
                assert response.ok, response
                data = await response.json()
                assert len(data["items"]) == 0, data

            await retry(check)


async def test_name_sort():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test2"},
            )

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"sort": [{"key": "name", "dir": "desc"}]},
                )
                assert response.ok, response
                data = await response.json()
                assert len(data["items"]) == 2, data
                assert data["items"][0]["name"] == "test2", data
                assert data["items"][1]["name"] == "test", data

            await retry(check)
