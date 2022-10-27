import secrets
import time
from itgs import Itgs
from login import create_and_login_user
from retryer import retry


async def test_bootstrap():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            uid = secrets.token_urlsafe(8)
            backend = await itgs.backend()
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

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 1, data
                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"sort": [{"key": "name", "dir": "desc"}]},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 2, data
                assert data["items"][0]["name"] == "step1", data
                response = await backend.post(
                    "/api/1/progress_bars/traces/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 1, data

            await retry(check)


async def test_bootstrap_iterated_step():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            uid = secrets.token_urlsafe(8)
            backend = await itgs.backend()
            await backend.post(
                "/api/1/progress_bars/traces/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "pbar_name": "test",
                    "uid": uid,
                    "step_name": "step1",
                    "iterations": 10,
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
                    "iteration": 10,
                    "iterations": 10,
                    "done": True,
                    "now": time.time(),
                },
            )
            assert response.ok, response

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 1, data

                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"sort": [{"key": "name", "dir": "desc"}]},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 2, data
                assert data["items"][0]["name"] == "step1", data
                assert data["items"][0]["iterated"] is True, data

                response = await backend.post(
                    "/api/1/progress_bars/traces/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 1, data

            await retry(check)


async def test_bootstrap_replacement():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            uid = secrets.token_urlsafe(8)
            backend = await itgs.backend()
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

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/traces/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 1, data

                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={
                        "filters": {
                            "progress_bar_name": {"operator": "eq", "value": "test"}
                        },
                        "sort": [{"key": "name", "dir": "desc"}],
                    },
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 2, data
                assert data["items"][0]["iterated"] is False, data

            await retry(check)

            await backend.post(
                "/api/1/progress_bars/traces/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "pbar_name": "test",
                    "uid": uid,
                    "step_name": "step1",
                    "iterations": 10,
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
                    "iteration": 10,
                    "iterations": 10,
                    "done": True,
                    "now": time.time(),
                },
            )
            assert response.ok, response

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={
                        "filters": {
                            "progress_bar_name": {"operator": "eq", "value": "test"}
                        },
                        "sort": [{"key": "name", "dir": "desc"}],
                    },
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 2, data
                assert data["items"][0]["iterated"] is True, data

                response = await backend.post(
                    "/api/1/progress_bars/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"filters": {"name": {"operator": "eq", "value": "test"}}},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 1, data
                assert data["items"][0]["version"] == 1, data

            await retry(check)


async def test_bootstrap_no_steps():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "name": "test",
                    "sampling_max_count": 10000,
                    "sampling_max_age_seconds": 100,
                },
            )
            assert response.ok, response

            uid = secrets.token_urlsafe(8)
            await backend.post(
                "/api/1/progress_bars/traces/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "pbar_name": "test",
                    "uid": uid,
                    "step_name": "step1",
                    "iterations": 10,
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
                    "iteration": 10,
                    "iterations": 10,
                    "done": True,
                    "now": time.time(),
                },
            )
            assert response.ok, response

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={
                        "filters": {
                            "progress_bar_name": {"operator": "eq", "value": "test"}
                        },
                        "sort": [{"key": "name", "dir": "desc"}],
                    },
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 2, data

                response = await backend.post(
                    "/api/1/progress_bars/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"filters": {"name": {"operator": "eq", "value": "test"}}},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 1, data
                assert data["items"][0]["version"] == 1, data

                response = await backend.post(
                    "/api/1/progress_bars/traces/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={},
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 1, data

            await retry(check)


async def test_bootstrap_uses_default_step_config():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "name": "test",
                    "default_step_config": {"one_off_technique": "harmonic_mean"},
                },
            )
            assert response.ok, response

            uid = secrets.token_urlsafe(8)
            response = await backend.post(
                "/api/1/progress_bars/traces/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "pbar_name": "test",
                    "uid": uid,
                    "step_name": "step1",
                    "now": time.time(),
                },
            )
            assert response.ok, response

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

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={
                        "filters": {
                            "progress_bar_name": {"operator": "eq", "value": "test"}
                        },
                        "sort": [{"key": "name", "dir": "desc"}],
                    },
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 2, data
                assert data["items"][0]["one_off_technique"] == "harmonic_mean", data


async def test_bootstrap_replace_uses_default_step_config():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "name": "test",
                    "default_step_config": {"one_off_technique": "harmonic_mean"},
                },
            )
            assert response.ok, response
            response = await backend.post(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
                json={"one_off_technique": "percentile"},
            )
            assert response.ok, response

            uid = secrets.token_urlsafe(8)
            response = await backend.post(
                "/api/1/progress_bars/traces/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "pbar_name": "test",
                    "uid": uid,
                    "step_name": "step2",
                    "now": time.time(),
                },
            )
            assert response.ok, response

            response = await backend.post(
                "/api/1/progress_bars/traces/steps/",
                headers={"Authorization": f"bearer {user.token}"},
                json={
                    "pbar_name": "test",
                    "trace_uid": uid,
                    "step_name": "step2",
                    "done": True,
                    "now": time.time(),
                },
            )
            assert response.ok, response

            async def check():
                response = await backend.post(
                    "/api/1/progress_bars/steps/search",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={
                        "filters": {
                            "progress_bar_name": {"operator": "eq", "value": "test"}
                        },
                        "sort": [{"key": "name", "dir": "desc"}],
                    },
                )
                data = await response.json()
                assert response.ok, data
                assert len(data["items"]) == 2, data
                assert data["items"][0]["one_off_technique"] == "harmonic_mean", data

            await retry(check)
