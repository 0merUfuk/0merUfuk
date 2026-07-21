#!/usr/bin/env python3
"""Fetch GitHub contribution calendar from public HTML — no API token needed.

GitHub serves your contribution calendar as public HTML at:
  https://github.com/users/<username>/contributions

This script fetches that page, parses the day cells with BeautifulSoup,
and writes data/contributions.json with raw days plus derived stats.

The current GitHub HTML structure uses <td> elements with data-date and
data-level attributes. The data-count attribute is no longer present;
contribution counts are inferred from levels (0=no contributions, 1-4=levels).
The total is parsed from the <h2> summary text.
"""

import json
import os
import re
import sys
from collections import defaultdict
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


def parse_total(html: str) -> int:
    """Parse the 'N contributions in the last year' text from the h2."""
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.find_all(["h2", "p"]):
        text = el.get_text(strip=True)
        # "359 contributions in the last year"
        match = re.search(r"([\d,]+)\s+contributions", text)
        if match:
            return int(match.group(1).replace(",", ""))
    return 0


def parse_days(html: str) -> list[dict]:
    """Parse the contribution calendar HTML into a list of day dicts."""
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # Current GitHub structure: td.ContributionCalendar-day with data-date and data-level
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        # Fallback: older rect-based SVG structure
        cells = soup.select("rect.ContributionCalendar-day")

    for cell in cells:
        date = cell.get("data-date")
        level_str = cell.get("data-level", "0")
        count_str = cell.get("data-count")

        if not date:
            continue

        try:
            level = int(level_str)
        except (ValueError, TypeError):
            level = 0

        try:
            count = int(count_str) if count_str else 0
        except (ValueError, TypeError):
            count = 0

        days.append({
            "date": date,
            "count": count,
            "level": level,
        })

    # Sort by date to ensure chronological order
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict], total_from_page: int) -> dict:
    """Compute derived stats from the day list."""
    if not days:
        return {}

    # If data-count wasn't available, use the total from the page
    has_counts = any(d["count"] > 0 for d in days)
    total = total_from_page if not has_counts else sum(d["count"] for d in days)

    # Current streak (counting back from the last day with contributions)
    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0 or d["count"] > 0:
            current_streak += 1
        else:
            break

    # Longest streak
    longest_streak = 0
    streak = 0
    for d in days:
        if d["level"] > 0 or d["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    # Best day (by count if available, else by level)
    if has_counts:
        best_day = max(days, key=lambda d: d["count"])
        if best_day["count"] == 0:
            best_day = None
    else:
        best_day = max(days, key=lambda d: d["level"])
        if best_day["level"] == 0:
            best_day = None

    # Monthly totals (only meaningful if we have counts)
    monthly = defaultdict(int)
    if has_counts:
        for d in days:
            month = d["date"][:7]  # YYYY-MM
            monthly[month] += d["count"]

    active_days = sum(1 for d in days if d["level"] > 0 or d["count"] > 0)

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {
            "date": best_day["date"],
            "count": best_day["count"],
            "level": best_day["level"],
        } if best_day else None,
        "monthly_totals": dict(sorted(monthly.items())) if has_counts else {},
        "days_with_contributions": active_days,
    }


def main():
    print(f"Fetching contributions for {USERNAME}...")
    html = fetch_calendar_html(USERNAME)
    days = parse_days(html)

    if not days:
        print("ERROR: No contribution days found. The HTML structure may have changed.")
        sys.exit(1)

    total_from_page = parse_total(html)
    stats = compute_stats(days, total_from_page)
    output = {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(days)} days to {OUTPUT}")
    print(f"  Total: {stats.get('total_contributions', 0)}")
    print(f"  Active days: {stats.get('days_with_contributions', 0)}")
    print(f"  Current streak: {stats.get('current_streak', 0)}")
    print(f"  Longest streak: {stats.get('longest_streak', 0)}")


if __name__ == "__main__":
    main()