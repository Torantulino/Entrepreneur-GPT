import json
import os
import requests
import sys
import time
from typing import Dict, List, Tuple


def get_environment_variables() -> Tuple[str, str, str, str, str]:
    """Retrieve and return necessary environment variables."""
    try:
        with open(os.environ["GITHUB_EVENT_PATH"]) as f:
            event = json.load(f)

        sha = event["pull_request"]["head"]["sha"]

        return (
            os.environ["GITHUB_API_URL"],
            os.environ["GITHUB_REPOSITORY"],
            sha,
            os.environ["GITHUB_TOKEN"],
            os.environ["GITHUB_RUN_ID"],
        )
    except KeyError as e:
        print(f"Error: Missing required environment variable or event data: {e}")
        sys.exit(1)


def make_api_request(url: str, headers: Dict[str, str]) -> Dict:
    """Make an API request and return the JSON response."""
    try:
        print("Making API request to:", url)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error: API request failed. {e}")
        sys.exit(1)


def process_check_runs(
    check_runs: List[Dict], current_run_id: str
) -> Tuple[bool, bool]:
    """Process check runs and return their status."""
    runs_in_progress = False
    all_others_passed = True

    for run in check_runs:
        if str(run["id"]) != current_run_id:
            status = run["status"]
            conclusion = run["conclusion"]

            if status == "completed":
                if conclusion not in ["success", "skipped", "neutral"]:
                    all_others_passed = False
                    print(
                        f"Check run {run['name']} (ID: {run['id']}) has conclusion: {conclusion}"
                    )
            else:
                runs_in_progress = True
                print(f"Check run {run['name']} (ID: {run['id']}) is still {status}.")
                all_others_passed = False

    return runs_in_progress, all_others_passed


def main():
    api_url, repo, sha, github_token, current_run_id = get_environment_variables()

    endpoint = f"{api_url}/repos/{repo}/commits/{sha}/check-runs"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    while True:
        data = make_api_request(endpoint, headers)

        print(f"Data received from API: {data}")

        check_runs = data["check_runs"]

        print("Processing check runs...")

        print(check_runs)

        runs_in_progress, all_others_passed = process_check_runs(
            check_runs, current_run_id
        )

        if not runs_in_progress:
            break

        print(
            "Some check runs are still in progress. Waiting 5 seconds before checking again..."
        )
        time.sleep(5)

    if all_others_passed:
        print("All other completed check runs have passed. This check passes.")
        sys.exit(0)
    else:
        print("Some check runs have failed or have not completed. This check fails.")
        sys.exit(1)


if __name__ == "__main__":
    main()
