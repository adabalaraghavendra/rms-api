"""Command line:
    python -m migrations status          show applied / pending versions
    python -m migrations upgrade         apply all pending migrations
    python -m migrations downgrade [-n 1]   undo the last N migrations
"""
import argparse

from app.core.database import get_database
from migrations.runner import MigrationRunner


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m migrations")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("upgrade")
    down = sub.add_parser("downgrade")
    down.add_argument("-n", "--steps", type=int, default=1)
    args = parser.parse_args()

    runner = MigrationRunner(get_database())
    if args.command == "status":
        applied = runner.applied_versions()
        print("applied:", ", ".join(applied) or "(none)")
        print("pending:", ", ".join(f"{m.version} ({m.description})" for m in runner.pending()) or "(none)")
    elif args.command == "upgrade":
        done = runner.upgrade()
        print("applied:", ", ".join(done) if done else "nothing to do - already up to date")
    else:
        print("reverted:", ", ".join(runner.downgrade(args.steps)) or "nothing")


if __name__ == "__main__":
    main()
