#!/usr/bin/env python3
"""Render the contribution heatmap as an animated SVG.

Reads data/contributions.json and writes contrib-heatmap.svg — a 53-week × 7-day
grid of rounded, colored boxes with a diagonal reveal animation (CSS keyframes,
plays once and freezes). Includes a Less→More legend and stats footer.
"""

import json
import os
from datetime import datetime, timedelta

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

# Layout
CELL = 13
GAP = 3
STEP = CELL + GAP
MARGIN_LEFT = 30
MARGIN_TOP = 20
LABEL_MONTHS = True
WIDTH = MARGIN_LEFT + 53 * STEP + 20
STATS_HEIGHT = 30
LEGEND_HEIGHT = 25
HEIGHT = MARGIN_TOP + 7 * STEP + LEGEND_HEIGHT + STATS_HEIGHT + 20


def load_data():
    with open(DATA) as f:
        return json.load(f)


def build_grid(days: list[dict]) -> list[list[dict | None]]:
    """Build a 53-week × 7-day grid. Returns grid[week][day] = day dict or None."""
    if not days:
        return [[None] * 7 for _ in range(53)]

    # Find the Sunday of the first day's week
    first = datetime.fromisoformat(days[0]["date"])
    start_sunday = first - timedelta(days=(first.weekday() + 1) % 7)

    grid = [[None] * 7 for _ in range(53)]
    for d in days:
        dt = datetime.fromisoformat(d["date"])
        delta = dt - start_sunday
        week = delta.days // 7
        day = delta.days % 7
        if 0 <= week < 53 and 0 <= day < 7:
            grid[week][day] = d
    return grid


def render_svg(data: dict) -> str:
    days = data["days"]
    stats = data.get("stats", {})
    grid = build_grid(days)

    # Month labels
    month_labels = []
    current_month = None
    for week_idx in range(53):
        for day_idx in range(7):
            cell = grid[week_idx][day_idx]
            if cell:
                dt = datetime.fromisoformat(cell["date"])
                month_name = dt.strftime("%b")
                if month_name != current_month and day_idx == 0:
                    month_labels.append((week_idx, month_name))
                    current_month = month_name
                    break
                elif month_name != current_month:
                    month_labels.append((week_idx, month_name))
                    current_month = month_name
                    break

    # Build SVG
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#0d1117" rx="6"/>')

    # CSS keyframes for diagonal reveal
    parts.append("""<style>
    rect.cell { opacity: 0; animation: reveal 0.6s ease-out forwards; }
    @keyframes reveal {
      0%   { opacity: 0; transform: translateY(-8px); }
      100% { opacity: 1; transform: translateY(0); }
    }
    text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }
    """)
    # Per-cell animation delay based on column (diagonal effect)
    parts.append("</style>")

    # Month labels
    for week_idx, name in month_labels:
        x = MARGIN_LEFT + week_idx * STEP
        parts.append(f'<text x="{x}" y="{MARGIN_TOP - 8}" fill="#8b949e" font-size="10">{name}</text>')

    # Day labels (Mon, Wed, Fri)
    for day_idx, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = MARGIN_TOP + day_idx * STEP + 10
        parts.append(f'<text x="5" y="{y}" fill="#8b949e" font-size="9">{label}</text>')

    # Cells
    for week_idx in range(53):
        for day_idx in range(7):
            cell = grid[week_idx][day_idx]
            x = MARGIN_LEFT + week_idx * STEP
            y = MARGIN_TOP + day_idx * STEP

            if cell:
                level = min(cell["level"], 5)
                color = PALETTE[level]
                delay = (week_idx * 0.02) + (day_idx * 0.015)
            else:
                color = PALETTE[0]
                delay = (week_idx * 0.02) + (day_idx * 0.015)

            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" ry="2" fill="{color}" '
                f'style="animation-delay: {delay:.3f}s" '
                f'transform-origin="{x + CELL/2} {y + CELL/2}"/>'
            )

    # Legend
    legend_y = MARGIN_TOP + 7 * STEP + 12
    legend_x = WIDTH - 200
    parts.append(f'<text x="{legend_x - 50}" y="{legend_y + 10}" fill="#8b949e" font-size="10">Less</text>')
    for i in range(6):
        lx = legend_x + i * (CELL + GAP)
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{PALETTE[i]}"/>'
        )
    parts.append(f'<text x="{legend_x + 6 * (CELL + GAP) + 5}" y="{legend_y + 10}" fill="#8b949e" font-size="10">More</text>')

    # Stats footer
    total = stats.get("total_contributions", 0)
    current_streak = stats.get("current_streak", 0)
    longest_streak = stats.get("longest_streak", 0)

    footer_y = legend_y + CELL + 15
    footer_text = f"{total:,} contributions in the last year · Current streak: {current_streak} days · Longest streak: {longest_streak} days"
    parts.append(f'<text x="{WIDTH/2}" y="{footer_y}" fill="#8b949e" font-size="11" text-anchor="middle">{footer_text}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    data = load_data()
    svg = render_svg(data)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}")