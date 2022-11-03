"""Configures a specific user so that they appear to have some traces in their recent history"""
import argparse
import asyncio
import secrets
import time
from itgs import Itgs
import tqdm


def main():
    parser = argparse.ArgumentParser(
        description="Configures a specific user so that they appear to have some traces in their recent history"
    )
    parser.add_argument(
        "-s", "--sub", help="The sub of the user to configure", required=True
    )
    parser.add_argument(
        "-n",
        "--num-traces",
        help="The number of traces to create",
        type=int,
        default=10,
    )
    args = parser.parse_args()
    asyncio.run(add_traces(args.sub, args.num_traces))


async def add_traces(sub: str, num: int) -> None:
    async with Itgs() as itgs:
        conn = await itgs.conn()
        cursor = conn.cursor()
        response = await cursor.execute(
            "SELECT 1 FROM users WHERE sub = ?",
            (sub,),
        )
        if not response.results:
            print(f"User with sub {sub} not found")
            return
        now = time.time()
        user_uid = "ep_ut_uid_" + secrets.token_urlsafe(16)
        new_token = "ep_ut_" + secrets.token_urlsafe(48)
        name = "test"
        reponse = await cursor.execute(
            """
                INSERT INTO user_tokens (
                    user_id,
                    uid,
                    token,
                    name,
                    created_at,
                    expires_at
                ) SELECT
                    users.id,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                FROM users
                WHERE users.sub = ?
                """,
            (user_uid, new_token, name, now, now + 3600, sub),
        )
        try:
            backend = await itgs.backend()
            for _ in tqdm.trange(num):
                uid = secrets.token_urlsafe(8)
                response = await backend.post(
                    "/api/1/progress_bars/traces/",
                    headers={"Authorization": f"bearer {new_token}"},
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
                    headers={"Authorization": f"bearer {new_token}"},
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
        finally:
            await cursor.execute(
                """
                DELETE FROM user_tokens
                WHERE user_tokens.uid = ?
                """,
                (user_uid,),
            )


if __name__ == "__main__":
    main()
