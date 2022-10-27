import asyncio
import random
from login import create_and_login_user
from retryer import retry
from itgs import Itgs
import secrets
import json
import time


async def test_watch_no_trace():
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

            async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
                await ws.send(
                    json.dumps(
                        {
                            "sub": user.sub,
                            "progress_bar_name": "test",
                            "progress_bar_trace_uid": uid,
                        }
                    )
                )
                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["success"] is True, data

                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["type"] == "update", data
                assert data["done"] is False, data
                assert data["data"]["step_name"] == "step1", data

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

                while True:
                    wsresponse: str = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(wsresponse)
                    assert data["data"]["step_name"] == "step1", data
                    assert data["type"] == "update", data
                    if data["done"]:
                        break


async def test_watch_before_create():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/progress_bars/",
                headers={"Authorization": f"bearer {user.token}"},
                json={"name": "test"},
            )
            assert response.ok, response

            response = await backend.post(
                "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            uid = secrets.token_urlsafe(8)
            async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
                await ws.send(
                    json.dumps(
                        {
                            "sub": user.sub,
                            "progress_bar_name": "test",
                            "progress_bar_trace_uid": uid,
                        }
                    )
                )
                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["success"] is True, data

                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["type"] == "update", data
                assert data["done"] is False, data
                assert data["data"]["step_name"] == "step1", data

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

                while True:
                    wsresponse: str = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(wsresponse)
                    assert data["data"]["step_name"] == "step1", data
                    assert data["type"] == "update", data
                    if data["done"]:
                        break


async def test_bootstrap_create_before_watch():
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

            async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
                await ws.send(
                    json.dumps(
                        {
                            "sub": user.sub,
                            "progress_bar_name": "test",
                            "progress_bar_trace_uid": uid,
                        }
                    )
                )
                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["success"] is True, data

                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["type"] == "update", data
                assert data["done"] is False, data
                assert data["data"]["step_name"] == "step1", data

                await backend.post(
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

                while True:
                    wsresponse: str = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(wsresponse)
                    assert data["data"]["step_name"] == "step1", data
                    assert data["type"] == "update", data
                    if data["done"]:
                        break


async def test_bootstrap_watch_before_create():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            uid = secrets.token_urlsafe(8)
            async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
                await ws.send(
                    json.dumps(
                        {
                            "sub": user.sub,
                            "progress_bar_name": "test",
                            "progress_bar_trace_uid": uid,
                        }
                    )
                )
                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["success"] is True, data

                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["type"] == "update", data
                assert data["done"] is False, data

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

                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["type"] == "update", data
                assert data["done"] is False, data
                assert data["data"]["step_name"] == "step1", data

                await backend.post(
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

                while True:
                    wsresponse: str = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(wsresponse)
                    assert data["data"]["step_name"] == "step1", data
                    assert data["type"] == "update", data
                    if data["done"]:
                        break


async def test_repeated_create_before_watch():
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

            for _ in range(100):
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

                await asyncio.sleep(0.01)

            async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
                uid = secrets.token_urlsafe(8)
                await ws.send(
                    json.dumps(
                        {
                            "sub": user.sub,
                            "progress_bar_name": "test",
                            "progress_bar_trace_uid": uid,
                        }
                    )
                )
                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["success"] is True, data

                wsresponse: str = await ws.recv()
                data = json.loads(wsresponse)
                assert data["data"]["overall_eta_seconds"] > 0, data
                assert data["data"]["step_overall_eta_seconds"] > 0, data


async def test_matrix_repeated_create_before_watch_one_off():
    async def inner(default_technique: str, step_technique: str):
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
                        "default_step_config": {"one_off_technique": default_technique},
                    },
                )
                assert response.ok, response
                response = await backend.post(
                    "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"one_off_technique": step_technique},
                )
                assert response.ok, response

                for _ in range(100):
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

                    await asyncio.sleep(0.01)

                async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
                    uid = secrets.token_urlsafe(8)
                    await ws.send(
                        json.dumps(
                            {
                                "sub": user.sub,
                                "progress_bar_name": "test",
                                "progress_bar_trace_uid": uid,
                            }
                        )
                    )
                    wsresponse: str = await ws.recv()
                    data = json.loads(wsresponse)
                    assert data["success"] is True, data

                    wsresponse: str = await ws.recv()
                    data = json.loads(wsresponse)
                    assert data["data"]["overall_eta_seconds"] > 0, data
                    assert data["data"]["step_overall_eta_seconds"] > 0, data

    async def do_inner(default_technique: str, step_technique: str):
        print(f"  {default_technique=} {step_technique=}...")
        await inner(default_technique, step_technique)

    techniques = ["percentile", "arithmetic_mean", "geometric_mean", "harmonic_mean"]

    for technique in techniques:
        await do_inner(technique, "percentile")
    for technique in techniques:
        await do_inner("percentile", technique)


async def test_matrix_repeated_create_before_watch_iterated():
    async def inner(default_technique: str, step_technique: str):
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
                        "default_step_config": {
                            "iterated": True,
                            "iterated_technique": default_technique,
                        },
                    },
                )
                assert response.ok, response
                response = await backend.post(
                    "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"iterated": True, "iterated_technique": step_technique},
                )
                assert response.ok, response

                for _ in range(100):
                    uid = secrets.token_urlsafe(8)
                    response = await backend.post(
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
                    assert response.ok, response

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

                    await asyncio.sleep(0.01)

                async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
                    uid = secrets.token_urlsafe(8)
                    await ws.send(
                        json.dumps(
                            {
                                "sub": user.sub,
                                "progress_bar_name": "test",
                                "progress_bar_trace_uid": uid,
                            }
                        )
                    )
                    wsresponse: str = await ws.recv()
                    data = json.loads(wsresponse)
                    assert data["success"] is True, data

                    wsresponse: str = await ws.recv()
                    data = json.loads(wsresponse)
                    assert data["data"]["overall_eta_seconds"] > 0, data
                    assert data["data"]["step_overall_eta_seconds"] > 0, data

    async def do_inner(default_technique: str, step_technique: str):
        print(f"  {default_technique=} {step_technique=}...")
        await inner(default_technique, step_technique)

    techniques = [
        "best_fit.linear",
        "percentile",
        "arithmetic_mean",
        "geometric_mean",
        "harmonic_mean",
    ]

    for technique in techniques:
        await do_inner("percentile", technique)


async def test_matrix_repeated_create_before_watch_iterated2():
    async def inner(default_technique: str, step_technique: str):
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
                        "default_step_config": {
                            "iterated": True,
                            "iterated_technique": default_technique,
                        },
                    },
                )
                assert response.ok, response
                response = await backend.post(
                    "/api/1/progress_bars/steps/?pbar_name=test&step_name=step1",
                    headers={"Authorization": f"bearer {user.token}"},
                    json={"iterated": True, "iterated_technique": step_technique},
                )
                assert response.ok, response

                for _ in range(100):
                    uid = secrets.token_urlsafe(8)
                    iters = random.randint(1, 100)
                    response = await backend.post(
                        "/api/1/progress_bars/traces/",
                        headers={"Authorization": f"bearer {user.token}"},
                        json={
                            "pbar_name": "test",
                            "uid": uid,
                            "step_name": "step1",
                            "iterations": iters,
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
                            "iteration": iters,
                            "iterations": iters,
                            "done": True,
                            "now": time.time(),
                        },
                    )
                    assert response.ok, response

                    await asyncio.sleep(0.01)

                async with itgs.websocket("/api/2/progress_bars/traces/") as ws:
                    uid = secrets.token_urlsafe(8)
                    await ws.send(
                        json.dumps(
                            {
                                "sub": user.sub,
                                "progress_bar_name": "test",
                                "progress_bar_trace_uid": uid,
                            }
                        )
                    )
                    wsresponse: str = await ws.recv()
                    data = json.loads(wsresponse)
                    assert data["success"] is True, data

                    wsresponse: str = await ws.recv()
                    data = json.loads(wsresponse)
                    assert data["data"]["overall_eta_seconds"] > 0, data
                    assert data["data"]["step_overall_eta_seconds"] > 0, data

    async def do_inner(default_technique: str, step_technique: str):
        print(f"  {default_technique=} {step_technique=}...")
        await inner(default_technique, step_technique)

    techniques = [
        "best_fit.linear",
        "percentile",
        "arithmetic_mean",
        "geometric_mean",
        "harmonic_mean",
    ]

    for technique in techniques:
        await do_inner("percentile", technique)
