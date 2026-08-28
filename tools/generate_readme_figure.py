"""Generate the vault map shown in the README."""

from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BG, PANEL, INK, MUTED = "#07111b", "#0c1d2a", "#e8f0f7", "#8fa7ba"
CYAN, VIOLET, AMBER, RED, GREEN = "#38d6e8", "#9b8cff", "#ffb454", "#ff6b6b", "#61d6a3"


ENTRIES = [
    ("PII-8", "FREE-FLYER", "route back: standards + gas ceiling", GREEN),
    ("PII-9", "LUNAR MASS DRIVER", "different programme; no host", VIOLET),
    ("PII-11", "DEPLOYABLE TRACK", "architecture change; straightness flips", AMBER),
    ("PII-14", "CABLE GONDOLA", "inertia erased the headline gain", RED),
    ("PII-19", "INDUCTION DRIVE", "optimised the 11% term", AMBER),
    ("PII-21", "WATER / STEAM", "tube heat costs more than fluid saves", RED),
]


def txt(x: float, y: float, value: str, size: int, colour: str = INK, weight: int = 400,
        anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{colour}" font-family="Inter,Segoe UI,sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def box(x: float, y: float, w: float, h: float, stroke: str = "#17384b", fill: str = PANEL,
        radius: int = 18) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def render() -> str:
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">',
        f'<rect width="1600" height="900" fill="{BG}"/>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#3f718c"/></marker></defs>',
        txt(72, 78, "VOLLEY-LAB · THE VAULT", 24, CYAN, 700),
        txt(72, 124, "Rejected against a stated mission, kept with the number that stopped it.", 34, INK, 600),
        txt(72, 162, "Nothing here was stopped by a test. Nothing here should be cited.", 19, MUTED),
        box(72, 220, 420, 520, stroke=CYAN),
        txt(104, 268, "MISSION HELD CONSTANT", 15, CYAN, 700),
        txt(104, 314, "Last-mile orbital delivery", 25, INK, 650),
        txt(104, 352, "from a controlled final stage", 20, MUTED),
        txt(104, 424, "ARCHITECTURE MOVED", 15, AMBER, 700),
        txt(104, 470, "Gen5", 21, INK, 700),
        txt(184, 470, "self-contained motor", 18, MUTED),
        txt(104, 516, "Gen6", 21, INK, 700),
        txt(184, 516, "stage-integrated gas", 18, MUTED),
        txt(104, 590, "THE RULE", 15, RED, 700),
        txt(104, 634, "Every entry states why", 23, INK, 650),
        txt(104, 670, "it stopped, with a number.", 23, INK, 650),
    ]
    out.append('<line x1="492" y1="480" x2="548" y2="480" stroke="#3f718c" stroke-width="3" marker-end="url(#arrow)"/>')
    for i, (identifier, title, reason, colour) in enumerate(ENTRIES):
        col, row = i % 2, i // 2
        x, y = 566 + col * 500, 220 + row * 176
        out += [
            box(x, y, 458, 142, stroke=colour),
            txt(x + 26, y + 40, identifier, 16, colour, 700),
            txt(x + 112, y + 40, title, 17, INK, 700),
            txt(x + 26, y + 82, reason, 16, MUTED),
            txt(x + 26, y + 112, "COMPUTED / ARGUED · NOT TESTED", 12, colour, 650),
        ]
    out += [
        box(566, 762, 958, 70, stroke="#21465b", fill="#091720"),
        txt(594, 804, "A stop can be reopened when its constraint moves. It is not scripture either.", 20, INK, 550),
        txt(1494, 870, "6 LONG-FORM ENTRIES · 0 PHYSICAL OBSERVATIONS", 15, MUTED, 650, "end"),
        "</svg>",
    ]
    return "\n".join(out) + "\n"


def main() -> None:
    output = ROOT / "figures" / "vault-map.svg"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(), encoding="utf-8")
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
