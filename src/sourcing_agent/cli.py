import argparse
from pathlib import Path

from sourcing_agent.review.api import list_review_queue
from sourcing_agent.workflow import build_digest_from_db, run_daily


DEFAULT_DB = Path("data/sourcing_agent.db")


def _add_db_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="sourcing-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run-daily", help="Run one daily sourcing workflow")
    run_parser.add_argument("--dry-run", action="store_true", help="Use deterministic sample items")
    _add_db_arg(run_parser)

    digest_parser = subparsers.add_parser("show-digest", help="Render digest from stored signals")
    _add_db_arg(digest_parser)

    review_parser = subparsers.add_parser("review-queue", help="List outreach drafts waiting for approval")
    _add_db_arg(review_parser)

    args = parser.parse_args(argv)
    db_path = Path(args.db)

    if args.command == "run-daily":
        result = run_daily(db_path=db_path, dry_run=args.dry_run)
        print("采集条数: {count}".format(count=result.source_count))
        print("处理信号: {count}".format(count=result.signal_count))
        print("生成草稿: {count}".format(count=result.draft_count))
        print(result.digest_markdown)
        return 0

    if args.command == "show-digest":
        print(build_digest_from_db(db_path))
        return 0

    if args.command == "review-queue":
        queue = list_review_queue(db_path)
        if not queue:
            print("暂无待审核建联草稿")
            return 0
        for index, draft in enumerate(queue, start=1):
            print("{idx}. {title} [{language}]".format(idx=index, title=draft["title"], language=draft["language"]))
            print("   URL: " + draft["url"])
            print("   Subject: " + draft["subject"])
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

