"""Command-line entry points."""

import argparse
import json
import sys
from dataclasses import replace

from .collector import collect, import_files
from .config import load_settings
from .server import serve
from .store import Store


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="pcbparts-dashboard")
    commands = parser.add_subparsers(dest="command", required=True)
    serving = commands.add_parser("serve", help="Serve the dashboard and start polling")
    serving.add_argument("--host")
    serving.add_argument("--port", type=int)
    serving.add_argument("--no-poll", action="store_true")
    collecting = commands.add_parser("collect", help="Collect one stats and health reply")
    collecting.add_argument("--days", type=int, choices=range(1, 366), metavar="N")
    importing = commands.add_parser("import", help="Import saved stats JSON replies")
    importing.add_argument("files", nargs="+", metavar="FILE")
    args = parser.parse_args(argv)
    try:
        settings = load_settings()
        if args.command == "serve":
            settings = replace(
                settings,
                host=args.host if args.host is not None else settings.host,
                port=args.port if args.port is not None else settings.port,
            )
        with Store(settings.db_path) as store:
            if args.command == "serve":
                serve(settings, store, no_poll=args.no_poll)
                return 0
            if args.command == "collect":
                result = collect(settings, store, days=args.days)
            else:
                result = import_files(store, args.files, settings=settings)
            print(json.dumps(result))
            return 0 if result["ok"] else 1
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"pcbparts-dashboard: {exc}", file=sys.stderr)
        return 1
