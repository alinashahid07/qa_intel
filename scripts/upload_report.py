import argparse
import sys

import httpx

from app.config import settings


def main() -> int:
    parser = argparse.ArgumentParser(description="upload a junit xml report to the platform")
    parser.add_argument("report", help="path to the junit xml file")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--token", default=settings.ingest_token)
    parser.add_argument("--repo", default="demo/qa-intel-sample-app")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--commit", default="local")
    parser.add_argument("--pr", default=None)
    args = parser.parse_args()

    data = {"repo": args.repo, "branch": args.branch, "commit_sha": args.commit}
    if args.pr:
        data["pr_number"] = args.pr
    with open(args.report, "rb") as handle:
        response = httpx.post(
            f"{args.url}/api/runs",
            headers={"X-API-Token": args.token},
            files={"report": (args.report, handle, "application/xml")},
            data=data,
            timeout=30,
        )
    print(response.status_code)
    print(response.text)
    return 0 if response.is_success else 1


if __name__ == "__main__":
    sys.exit(main())