from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator
from itgs import Itgs
import secrets
import time


@dataclass
class TestUser:
    """A user created for testing purposes"""

    sub: str
    """the sub of the genrated user, acts as it's universal id"""
    token: str
    """the token of the generated user, used for authentication"""


@asynccontextmanager
async def create_and_login_user(itgs: Itgs) -> AsyncIterator[TestUser]:
    """creates a new user with a random sub and returns the required information to authenticate as them
    the user is deleted when the context manager exits

    Example:
    ```py
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            # do stuff with user
    ```
    """
    sub = "test_" + secrets.token_urlsafe(8)
    new_token = "ep_ut_" + secrets.token_urlsafe(48)
    uid = "ep_ut_uid_" + secrets.token_urlsafe(16)
    name = "test"
    now = time.time()
    conn = await itgs.conn()
    cursor = conn.cursor()
    await cursor.executemany3(
        (
            (
                """
                INSERT INTO users (
                    sub,
                    created_at
                ) VALUES (
                    ?,
                    ?
                )
                """,
                (sub, now),
            ),
            (
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
                (uid, new_token, name, now, now + 3600, sub),
            ),
            (
                """
                INSERT INTO user_pricing_plans (
                    uid,
                    user_id,
                    pricing_plan_id
                )
                SELECT
                    ?,
                    users.id,
                    pricing_plans.id
                FROM users
                JOIN pricing_plans ON pricing_plans.slug = ?
                WHERE
                    users.sub = ?
                    AND NOT EXISTS (
                        SELECT 1 FROM user_pricing_plans
                        WHERE user_pricing_plans.user_id = users.id
                    )
                """,
                (
                    "ep_upp_" + secrets.token_urlsafe(16),
                    "public",
                    sub,
                ),
            ),
        )
    )
    try:
        yield TestUser(sub, new_token)
    finally:
        await cursor.execute(
            """
            DELETE FROM users
            WHERE sub = ?
            """,
            (sub,),
        )
