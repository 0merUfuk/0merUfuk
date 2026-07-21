#!/usr/bin/env python3
"""Generate the neofetch-style info card SVG using SMIL animations.

Hand-authors a small SVG that looks like neofetch output: a title bar,
then colored key/value rows. Each line fades in via SMIL <animate> (no <style>
tag — GitHub strips it).
"""

import os

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

WIDTH = 490
HEIGHT = 170
PADDING = 16
LINE_HEIGHT = 22
TITLE_BAR_HEIGHT = 28

# Content — clean and lean
ROWS = [
    ("Now", "Forward Deployed Engineer"),
    ("Stack", "Go · Python · TypeScript"),
    ("Loc", "İstanbul, Türkiye"),
]

# Colors (neofetch-like)
COLORS = {
    "key": "#39d353",       # green
    "value": "#c9d1d9",      # light gray
    "title_bar_bg": "#21262d",
    "title_bar_fg": "#f0f6fc",
    "dots": ["#ff5f56", "#ffbd2e", "#27c93f"],  # traffic light dots
    "bg": "#0d1117",
    "border": "#30363d",
}


def render_svg() -> str:
    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{COLORS["bg"]}" rx="8"/>')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="none" stroke="{COLORS["border"]}" rx="8" stroke-width="1"/>')

    # Title bar
    parts.append(f'<rect width="{WIDTH}" height="{TITLE_BAR_HEIGHT}" fill="{COLORS["title_bar_bg"]}" rx="8"/>')
    parts.append(f'<rect y="{TITLE_BAR_HEIGHT - 8}" width="{WIDTH}" height="8" fill="{COLORS["title_bar_bg"]}"/>')

    # Traffic light dots
    for i, color in enumerate(COLORS["dots"]):
        cx = 16 + i * 20
        cy = TITLE_BAR_HEIGHT // 2
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{color}"/>')

    # Title text
    title_text = "ufuk@github ~ whoami"
    parts.append(
        f'<text x="{WIDTH/2}" y="{TITLE_BAR_HEIGHT//2 + 4}" '
        f'fill="{COLORS["title_bar_fg"]}" font-size="12" '
        f'font-family="-apple-system, BlinkMacSystemFont, monospace" '
        f'text-anchor="middle">{title_text}</text>'
    )

    # Rows with SMIL fade-in (no <style> tag — GitHub strips it)
    y_start = TITLE_BAR_HEIGHT + PADDING + 10
    for i, (key, value) in enumerate(ROWS):
        y = y_start + i * LINE_HEIGHT
        x = PADDING + 10
        delay = 0.3 + i * 0.15
        key_text = f"{key}:"
        key_width = len(key_text) * 7.2 + 10

        # Wrap row in a <g> with SMIL opacity animation
        parts.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>'
            f'<text x="{x}" y="{y}" fill="{COLORS["key"]}" font-size="13" '
            f'font-family="-apple-system, BlinkMacSystemFont, monospace" '
            f'font-weight="bold">{key_text}</text>'
            f'<text x="{x + key_width}" y="{y}" fill="{COLORS["value"]}" font-size="13" '
            f'font-family="-apple-system, BlinkMacSystemFont, monospace">{value}</text>'
            f'</g>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = render_svg()
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}")