"""
©AngelaMos | 2026
__main__.py
"""

import argparse
import asyncio
from getpass import getpass
import sys

from config import UserRole, settings
from core.database import sessionmanager
from user.schemas import AdminUserCreate
from user.service import UserService


async def create_administrator(email: str, password: str) -> None:
    data = AdminUserCreate(email = email, password = password, role = UserRole.ADMIN)
    sessionmanager.init(str(settings.DATABASE_URL))
    try:
        async with sessionmanager.session() as session:
            await UserService(session).admin_create_user(data)
    finally:
        await sessionmanager.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description = "Create an administrator from the trusted server console"
    )
    parser.add_argument("--email", required = True)
    parser.add_argument("--password-stdin", action = "store_true")
    args = parser.parse_args()
    if args.password_stdin:
        password = sys.stdin.readline().rstrip("\r\n")
    else:
        if not sys.stdin.isatty():
            parser.error("Use an interactive terminal or --password-stdin")
        password = getpass("New administrator password: ")
        if password != getpass("Repeat password: "):
            parser.error("Passwords do not match")
    try:
        asyncio.run(create_administrator(args.email, password))
    except Exception as exc:
        parser.exit(
            1,
            f"Administrator creation failed ({type(exc).__name__}). Check account existence, input requirements, and database availability.\n"
        )
    print("Administrator created. Existing accounts were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
