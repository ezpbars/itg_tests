from itgs import Itgs
from user_usages.test_read_backend import create_user_usage
import argparse
import asyncio


def main():
    parser = argparse.ArgumentParser(
        description="Configures a specific user so that they appear to have some traces in their recent history"
    )
    parser.add_argument(
        "-s", "--sub", help="The sub of the user to configure", required=True
    )
    parser.add_argument(
        "-b",
        "--months-ago-start",
        help="The smaller number in the range of months_ago to call the function with",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-e",
        "--months-ago-end",
        help="The larger number in the range of months_ago to call the function with",
        type=int,
        default=2,
    )
    args = parser.parse_args()
    asyncio.run(
        create_billing_history(args.sub, args.months_ago_start, args.months_ago_end)
    )


async def create_billing_history(sub: str, months_ago_start: int, months_ago_end: int):
    async with Itgs() as itgs:
        for month in range(months_ago_start, months_ago_end + 1):
            await create_user_usage(
                itgs=itgs,
                user_sub=sub,
                months_ago=month,
            )


if __name__ == "__main__":
    main()
