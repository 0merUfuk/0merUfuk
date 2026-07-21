#!/usr/bin/env python3
"""Fetch GitHub's public contribution calendar levels — no API token needed.

GitHub's public contribution-calendar HTML currently exposes each day as a
`td.ContributionCalendar-day` with `data-date` and `data-level` attributes.
It does NOT expose exact per-day counts, so this script intentionally stores
only dates and visual levels. No custom streaks, totals, or inferred metrics.
"""

import json
import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "0merUfuk")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_calendar_html(username: str) -> str:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    """Parse public contribution calendar cells into date+level rows."""
    soup = BeautifulSoup(html, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        cells = soup.select("rect.ContributionCalendar-day")

    days = []
    for cell in cells:
        date = cell.get("data-date")
        level_str = cell.get("data-level", "0")
        if not date:
            continue

        try:
            level = int(level_str)
        except (ValueError, TypeError):
            level = 0

        days.append({"date": date, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def main():
    print(f"Fetching public contribution levels for {USERNAME}...")
    html = fetch_calendar_html(USERNAME)
    days = parse_days(html)

    if not days:
        print("ERROR: No contribution days found. The GitHub HTML structure may have changed.")
        sys.exit(1)

    output = {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "source": f"https://github.com/users/{USERNAME}/contributions public HTML",
        "note": "Stores visual contribution levels only. Exact per-day counts/streaks are not exposed by this public endpoint.",
        "days": days,
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(days)} public contribution-level days to {OUTPUT}")


if __name__ == "__main__":
    main()