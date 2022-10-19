from itgs import Itgs
from login import create_and_login_user
from retryer import retry


async def read_empty():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/progress_bars/steps/search",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            assert await response.json() == {"items": [], "next_page_sort": None}


async def read_one():
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

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={},
                )
                assert response.ok, response
                data = await response.json()
                assert len(data["items"]) == 1, data

            await retry(check)


async def test_pbar_filter():
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

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={
                        "filters": {
                            "progress_bar_name": {"operator": "eq", "value": "test2"}
                        }
                    },
                )
                assert response.ok, response
                data = await response.json()
                assert len(data["items"]) == 0, data

            await retry(check)


async def test_pbar_sort():
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
            await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test2"},
            )
            await backend.post(
                "/api/1/progress_bars/steps/?pbar_name=test2&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"sort": [{"key": "progress_bar_name", "dir": "desc"}]},
                )
                data = await response.json()
                assert response.ok, (response, data)
                assert len(data["items"]) == 4, data
                assert data["items"][0]["progress_bar_name"] == "test2", data
                assert data["items"][3]["progress_bar_name"] == "test", data

            await retry(check)
