#!/usr/bin/env python3
"""Render the public GitHub contribution calendar as an animated SVG.

Reads data/contributions.json and writes contrib-heatmap.svg — a 53-week × 7-day
grid of rounded, colored boxes with a diagonal reveal animation using SMIL
<animate> elements. No derived stats are rendered: GitHub's public HTML exposes
contribution levels, not exact per-day counts, so custom streak/metric text would
be unreliable.
"""

import json
import os
from datetime import datetime, timedelta

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
STEP = CELL + GAP
MARGIN_LEFT = 36
MARGIN_TOP = 24
WIDTH = MARGIN_LEFT + 53 * STEP + 20
LEGEND_HEIGHT = 25
HEIGHT = MARGIN_TOP + 7 * STEP + LEGEND_HEIGHT + 20
FONT = "-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif"


def load_data():
    with open(DATA) as f:
        return json.load(f)


def build_grid(days: list[dict]) -> list[list[dict | None]]:
    """Build a 53-week × 7-day grid. Returns grid[week][day] = day dict or None."""
    if not days:
        return [[None] * 7 for _ in range(53)]

    first = datetime.fromisoformat(days[0]["date"])
    start_sunday = first - timedelta(days=(first.weekday() + 1) % 7)

    grid: list[list[dict | None]] = [[None] * 7 for _ in range(53)]
    for d in days:
        dt = datetime.fromisoformat(d["date"])
        delta = dt - start_sunday
        week = delta.days // 7
        day = delta.days % 7
        if 0 <= week < 53 and 0 <= day < 7:
            grid[week][day] = d
    return grid


def month_labels(grid: list[list[dict | None]]) -> list[tuple[int, str]]:
    labels: list[tuple[int, str]] = []
    current_month = None
    for week_idx in range(53):
        month_name = None
        for day_idx in range(7):
            cell = grid[week_idx][day_idx]
            if cell:
                month_name = datetime.fromisoformat(cell["date"]).strftime("%b")
                break
        if month_name and month_name != current_month:
            labels.append((week_idx, month_name))
            current_month = month_name
    return labels


def render_svg(data: dict) -> str:
    grid = build_grid(data["days"])

    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#0d1117" rx="6"/>')

    for week_idx, name in month_labels(grid):
        x = MARGIN_LEFT + week_idx * STEP
        parts.append(f'<text x="{x}" y="{MARGIN_TOP - 8}" fill="#8b949e" font-size="10" font-family="{FONT}">{name}</text>')

    for day_idx, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = MARGIN_TOP + day_idx * STEP + 10
        parts.append(f'<text x="5" y="{y}" fill="#8b949e" font-size="9" font-family="{FONT}">{label}</text>')

    for week_idx in range(53):
        for day_idx in range(7):
            cell = grid[week_idx][day_idx]
            x = MARGIN_LEFT + week_idx * STEP
            y = MARGIN_TOP + day_idx * STEP
            level = min(int(cell.get("level", 0)), 5) if cell else 0
            color = PALETTE[level]
            delay = (week_idx * 0.02) + (day_idx * 0.015)

            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" ry="2" fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'dur="0.5s" begin="{delay:.3f}s" fill="freeze"/>'
                f'</rect>'
            )

    legend_y = MARGIN_TOP + 7 * STEP + 12
    legend_x = WIDTH - 200
    parts.append(f'<text x="{legend_x - 50}" y="{legend_y + 10}" fill="#8b949e" font-size="10" font-family="{FONT}">Less</text>')
    for i in range(6):
        lx = legend_x + i * (CELL + GAP)
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{PALETTE[i]}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{1.5 + i * 0.05:.2f}s" fill="freeze"/>'
            f'</rect>'
        )
    parts.append(f'<text x="{legend_x + 6 * (CELL + GAP) + 5}" y="{legend_y + 10}" fill="#8b949e" font-size="10" font-family="{FONT}">More</text>')

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    data = load_data()
    svg = render_svg(data)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}")