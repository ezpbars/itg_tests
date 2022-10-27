import os
from typing import Iterator, Callable, Optional
import multiprocessing
from itgs import Itgs
import asyncio
import importlib
import inspect
import updater
import traceback
import argparse
import re

REPOS_UNDER_TEST = ["backend", "websocket", "jobs"]


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-once", action="store_true")
    parser.add_argument("-k", "--test-regex", type=str, required=False)
    parser.add_argument("--test-dot-all", action="store_true")
    args = parser.parse_args()

    test_regex: Optional[re.Pattern] = None
    if args.test_regex is not None:
        test_regex = re.compile(args.test_regex, re.DOTALL if args.test_dot_all else 0)

    asyncio.run(main(args.run_once, test_regex))


async def main(run_once: bool, test_regex: Optional[re.Pattern] = None):
    if not run_once:
        multiprocessing.Process(target=updater.listen_forever_sync, daemon=True).start()
    async with Itgs() as itgs:
        redis = await itgs.redis()
        pubsub = redis.pubsub()
        while True:
            await run_tests(test_regex)
            if run_once:
                break
            await pubsub.subscribe(*[f"updates:{repo}" for repo in REPOS_UNDER_TEST])
            while (
                await pubsub.get_message(ignore_subscribe_messages=True, timeout=5)
            ) is None:
                pass
            await pubsub.unsubscribe(*[f"updates:{repo}" for repo in REPOS_UNDER_TEST])
            await pubsub.reset()
            await asyncio.sleep(30)


def discover_tests() -> Iterator[Callable[[], None]]:
    for folder, _, files in os.walk("."):
        if "venv" in folder or "__pycache__" in folder:
            continue
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                module = importlib.import_module(
                    f"{folder.replace(os.path.sep,'/').lstrip('./').replace('/', '.')}.{file[:-3]}"
                )
                # all the functiosn starting with test_ in the module
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith("test_"):
                        yield func


async def run_tests(test_regex: Optional[re.Pattern] = None):
    try:
        await _run_tests(test_regex)
        async with Itgs() as itgs:
            slack = await itgs.slack()
            await slack.send_ops_message("Integration tests passed")
    except Exception as e:
        traceback.print_exc()
        async with Itgs() as itgs:
            slack = await itgs.slack()
            await slack.send_web_error_message(
                f"Error running integration tests:\n\n```\n{traceback.format_exc()}\n```",
                f"Error running integration tests: {e}",
            )


async def _run_tests(test_regex: Optional[re.Pattern] = None):
    for test in discover_tests():
        if test_regex is not None and not test_regex.search(
            test.__module__ + "." + test.__name__
        ):
            continue

        print(f"running {test.__name__}")
        try:
            await test()
        except Exception:
            print(f"failed {test.__name__}")
            raise
        print(f"passed {test.__name__}")


if __name__ == "__main__":
    cli_main()
