#!/usr/bin/env python3
"""Generate the neofetch-style info card SVG using SMIL animations.

Clean, senior-facing profile card: no company, school, focus, or stack list.
Rows fade in via SMIL <animate> because GitHub strips <style> tags.
"""

import os

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

WIDTH = 560
HEIGHT = 132
PADDING = 16
LINE_HEIGHT = 24
TITLE_BAR_HEIGHT = 28

ROWS = [
    ("Current Position", "Forward Deployed AI/ML Engineering"),
    ("Location", "Istanbul, Türkiye"),
]

COLORS = {
    "key": "#39d353",
    "value": "#c9d1d9",
    "title_bar_bg": "#21262d",
    "title_bar_fg": "#f0f6fc",
    "dots": ["#ff5f56", "#ffbd2e", "#27c93f"],
    "bg": "#0d1117",
    "border": "#30363d",
}

FONT = "-apple-system, BlinkMacSystemFont, monospace"


def render_svg() -> str:
    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{COLORS["bg"]}" rx="8"/>')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="none" stroke="{COLORS["border"]}" rx="8" stroke-width="1"/>')

    parts.append(f'<rect width="{WIDTH}" height="{TITLE_BAR_HEIGHT}" fill="{COLORS["title_bar_bg"]}" rx="8"/>')
    parts.append(f'<rect y="{TITLE_BAR_HEIGHT - 8}" width="{WIDTH}" height="8" fill="{COLORS["title_bar_bg"]}"/>')

    for i, color in enumerate(COLORS["dots"]):
        cx = 16 + i * 20
        cy = TITLE_BAR_HEIGHT // 2
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{color}"/>')

    title_text = "ufuk@github ~ whoami"
    parts.append(
        f'<text x="{WIDTH/2}" y="{TITLE_BAR_HEIGHT//2 + 4}" '
        f'fill="{COLORS["title_bar_fg"]}" font-size="12" '
        f'font-family="{FONT}" text-anchor="middle">{title_text}</text>'
    )

    y_start = TITLE_BAR_HEIGHT + PADDING + 14
    key_col_width = 148
    for i, (key, value) in enumerate(ROWS):
        y = y_start + i * LINE_HEIGHT
        x = PADDING + 10
        delay = 0.3 + i * 0.15
        key_text = f"{key}:"

        parts.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>'
            f'<text x="{x}" y="{y}" fill="{COLORS["key"]}" font-size="13" '
            f'font-family="{FONT}" font-weight="bold">{key_text}</text>'
            f'<text x="{x + key_col_width}" y="{y}" fill="{COLORS["value"]}" font-size="13" '
            f'font-family="{FONT}">{value}</text>'
            f'</g>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = render_svg()
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}")