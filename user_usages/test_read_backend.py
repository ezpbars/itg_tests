import random
import secrets
from typing import Optional
from itgs import Itgs
from login import create_and_login_user
from retryer import retry
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class UserUsage:
    user_sub: str
    uid: str
    hosted_invoice_url: Optional[str]
    period_start: float
    period_end: float
    traces: int
    cost: Optional[float]


async def create_user_usage(
    itgs: Itgs, user_sub: str, months_ago: int, has_invoice: bool = True
) -> UserUsage:
    """creates a user usage for the specified user with the start date set to
    the first day of the month the specified number of months ago and the end
    date set to the end of that month

    Example: if the current date is Nov 13, 2022 and months_ago is 1, then the
    start date will be Oct 1st 2022 00:00 and the end date will be Nov 1st 2022 00:00


    Args:
        itgs (Itgs): the itgs instance
        user_sub (str): the user sub
        months_ago (int): the number of months ago the billing period should start
        has_invoice (bool): whether or not the user usage has an invoice

    Returns:
        UserUsage: the description of the user usage that was created
    """
    usage_uid = secrets.token_urlsafe(8)
    now = datetime.now(timezone.utc)
    new_month = ((now.month - months_ago - 1) % 12) + 1
    new_year = now.year + (now.month - months_ago - 1) // 12
    start = now.replace(month=new_month, year=new_year)
    start_date = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if new_month == 12:
        end_date = start_date.replace(year=new_year + 1, month=1)
    else:
        end_date = start_date.replace(month=new_month + 1)
    traces = random.randint(1, 10000)
    hosted_invoice_url = f"https://example.com/{usage_uid}"
    cost = random.randint(100, 10000)

    stripe_uid = secrets.token_urlsafe(8)
    stripe_id = secrets.token_urlsafe(8)

    async with Itgs() as itgs:
        conn = await itgs.conn()
        cursor = conn.cursor()
        if has_invoice:
            await cursor.executemany3(
                (
                    (
                        """
                        INSERT INTO stripe_invoices (
                            uid,
                            stripe_id,
                            hosted_invoice_url,
                            total,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            stripe_uid,
                            stripe_id,
                            hosted_invoice_url,
                            cost,
                            now.timestamp(),
                        ),
                    ),
                    (
                        """
                        INSERT INTO user_usages (
                            uid,
                            user_id,
                            traces,
                            period_started_at,
                            period_ended_at,
                            stripe_invoice_id
                        ) SELECT
                            ?,
                            users.id,
                            ?,
                            ?,
                            ?,
                            stripe_invoices.id
                        FROM users
                        JOIN stripe_invoices ON stripe_invoices.uid = ?
                        WHERE users.sub = ?

                        """,
                        (
                            usage_uid,
                            traces,
                            start_date.timestamp(),
                            end_date.timestamp(),
                            stripe_uid,
                            user_sub,
                        ),
                    ),
                )
            )
        else:
            await cursor.execute(
                """
                INSERT INTO user_usages (
                    uid,
                    user_id,
                    traces,
                    period_started_at,
                    period_ended_at
                ) SELECT
                    ?,
                    users.id,
                    ?,
                    ?,
                    ?
                FROM users
                WHERE users.sub = ?
                """,
                (
                    usage_uid,
                    traces,
                    start_date.timestamp(),
                    end_date.timestamp(),
                    user_sub,
                ),
            )

    return UserUsage(
        user_sub=user_sub,
        uid=usage_uid,
        hosted_invoice_url=hosted_invoice_url if has_invoice else None,
        period_start=start_date.timestamp(),
        period_end=end_date.timestamp(),
        traces=traces,
        cost=cost if has_invoice else None,
    )


async def test_read_empty():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/user_usages/search",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            data = await response.json()
            assert data["items"] == []


async def test_read_one():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            await create_user_usage(itgs, user.sub, 13)
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/user_usages/search",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            data = await response.json()
            assert len(data["items"]) == 1


async def test_read_one_no_invoice():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            await create_user_usage(itgs, user.sub, 13, has_invoice=False)
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/user_usages/search",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            data = await response.json()
            assert len(data["items"]) == 1


async def test_read_many():
    async with Itgs() as itgs:
        async with create_and_login_user(itgs) as user:
            for i in range(1, 25):
                await create_user_usage(itgs, user.sub, i)
            backend = await itgs.backend()
            response = await backend.post(
                "/api/1/user_usages/search",
                headers={"Authorization": f"bearer {user.token}"},
                json={},
            )
            assert response.ok, response
            data = await response.json()
            assert len(data["items"]) == 24
