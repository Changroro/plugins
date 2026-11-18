"""Pixel grids -> one CSS-animated SVG scene. Writes ../hooks/parts.ts (static sprites; the mod lays them out live).

Run: python3 scene/scene.py  (from the mod folder)"""
import sys

PAL = {
    "K": "#000000",  # ink
    "H": "#1a1a1a",  # hair
    "h": "#4a4a4a",  # hair highlight
    "S": "#f6e7da",  # skin
    "B": "#f0c2b4",  # blush
    "W": "#ffffff",  # card
    "D": "#2b2b2b",  # suit
    "L": "#e8e8e8",  # recessed
    "G": "#999999",  # rule-dashed
    "C": "#d97757",  # claude coral
}

CHANGRORO = """
........KKKKKK........
.....KKKHHHHHHKKK.....
....KHHHHHHHHHHHHK....
...KHHHhHHHHHHHHHHK...
..KHHHhHHHHHHHhHHHHK..
..KHHhHHHHHHHHHhHHHK..
.KHHHHHHHKHHHHHHHHHHK.
.KHHHHHHKSSKHHHHHHHHK.
.KHHHHHKSSSSKKHHHHHHK.
.KHHHKKSSSSSSSKKHHHHK.
.KHHKSSSSSSSSSSSKHHHK.
KSKHKSSSSSSSSSSSSKHKSK
KSSKSSSKSSSSSSKSSSKSSK
KSSKSSSKSSSSSSKSSSKSSK
.KKSSSSKSSSSSSKSSSSKK.
..KSBBSSSSSSSSSSBBSK..
..KSSSSSSSSSSSSSSSSK..
...KSSSSSSSSSSSSSSK...
....KKSSSSSSSSSSKK....
......KKKKKKKKKK......
.....KDDDKWWKDDDK.....
...KKDDDDKWKKDDDDKK...
..KDDDDDDDKKKDDDDDDK..
..KDDDDDDDDKDDDDDDDK..
.KDDDDDDDDDKDDDDDDDDK.
.KDDDDDDDDDDDDDDDDDDK.
.KDDDDDDDDDDDDDDDDDDK.
.KDDDDDDDDDDDDDDDDDDK.
.KDDDDDDDDDDDDDDDDDDK.
.KDDDDDDDDDDDDDDDDDDK.
.KDDDDDDDDDDDDDDDDDDK.
.KDDDDDDDDDDDDDDDDDDK.
"""

HAND = """
KKKK
KSSK
KKKK
"""

LAPTOP = """
KKKKKKKKKKKKKKKKKKKKKKKK
KWWWWWWWWWWWWWWWWWWWWWWK
KWWWWWWWWWKWWWWWWWWWWWWK
KWWWWWWWWWWKWWWWWWWWWWWK
KWWWWWWWWWKWWWKKKKWWWWWK
KWWWWWWWWWWWWWWWWWWWWWWK
KWWWWWWWWWWWWWWWWWWWWWWK
KKKKKKKKKKKKKKKKKKKKKKKK
KLLLLLLLLLLLLLLLLLLLLLLK
KKKKKKKKKKKKKKKKKKKKKKKK
"""

MUG = """
.KKKKKK..
.KWWWWKKK
.KWKKWK.K
.KWWWWK.K
.KWWWWKKK
.KWWWWK..
..KKKK...
"""

CLAUDE_BODY = """
..CCCCCCCCCC..
..CCCCCCCCCC..
..CCKCCCCKCC..
CCCCKCCCCKCCCC
CCCCCCCCCCCCCC
..CCCCCCCCCC..
..CCCCCCCCCC..
"""
CLAUDE_LEGS_A = "..C.C....C.C..\n..C.C....C.C.."
CLAUDE_LEGS_B = "...C.C..C.C...\n...C.C..C.C..."

CODEX_BODY = """
.......K......
......KKK.....
..KKKKKKKKKK..
..KWWWWWWWWK..
..KWKKKKKKWK..
..KWKWKKKKWK..
..KWKKWKKKWK..
..KWKWKWWKWK..
..KWKKKKKKWK..
..KWWWWWWWWK..
..KKKKKKKKKK..
...KWWWWWWK...
...KWWWWWWK...
...KKKKKKKK...
"""
CODEX_LEGS_A = "....K....K....\n....K....K...."
CODEX_LEGS_B = ".....K..K.....\n.....K..K....."


def grid(src):
    rows = [r for r in src.strip("\n").split("\n")]
    w = max(len(r) for r in rows)
    bad = [i for i, r in enumerate(rows) if len(r) != w]
    if bad:
        sys.exit(f"ragged rows {bad} (width {w})")
    return rows


def rects(src, x0=0, y0=0):
    """Run-length merge each row into rects."""
    out = []
    for y, row in enumerate(grid(src)):
        x = 0
        while x < len(row):
            c = row[x]
            if c == ".":
                x += 1
                continue
            n = 1
            while x + n < len(row) and row[x + n] == c:
                n += 1
            out.append(f'<rect x="{x0 + x}" y="{y0 + y}" width="{n}" height="1" fill="{PAL[c]}"/>')
            x += n
    return "".join(out)




DIGITS = {
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", "###", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", ".#.", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
    ":": [".", "#", ".", "#", "."],
}

CSS = """
.fa{animation:fa .5s steps(1) infinite}
.fb{opacity:0;animation:fb .5s steps(1) infinite}
@keyframes fa{0%{opacity:1}50%{opacity:0}}
@keyframes fb{0%{opacity:0}50%{opacity:1}}
.hands .fa,.hands .fb{animation-duration:.6s}
.bob{animation:bob 2s ease-in-out infinite}
@keyframes bob{50%{transform:translate(0,1px)}}
.run{animation:run 16s linear infinite}
.run2{animation-delay:-1.6s}
@keyframes run{from{transform:translate(-40px,0)}to{transform:translate(360px,0)}}
.hop{animation:hop .5s ease-in-out infinite}
@keyframes hop{50%{transform:translate(0,-2px)}}
.cheer .hop{animation:jump .45s ease-out 6}
@keyframes jump{50%{transform:translate(0,-9px)}}
.st{opacity:0;animation:st 2.4s ease-out infinite}
@keyframes st{0%{opacity:0;transform:translate(0,0)}40%{opacity:1}100%{opacity:0;transform:translate(0,-6px)}}
.blink{animation:blink 2s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
"""


def to_rects(rows, fill="#000000"):
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if row[x] != "#":
                x += 1
                continue
            n = 1
            while x + n < len(row) and row[x + n] == "#":
                n += 1
            out.append(f'<rect x="{x}" y="{y}" width="{n}" height="1" fill="{fill}"/>')
            x += n
    return "".join(out)


def frames(a, b, cls=""):
    return f'<g class="{cls}"><g class="fa">{a}</g><g class="fb" opacity="0">{b}</g></g>'


def runner(body, legs_a, legs_b):
    h = len(grid(body))
    return rects(body) + frames(rects(legs_a, 0, h), rects(legs_b, 0, h))


# Changroro at his desk, origin = desk top-left; 96 wide, desk top at y=32.
DESK_Y = 32
chx = 30
desk = (
    f'<rect x="0" y="{DESK_Y}" width="96" height="3" fill="#000"/>'
    f'<rect x="1" y="{DESK_Y + 1}" width="94" height="1" fill="#fff"/>'
    f'<rect x="6" y="{DESK_Y + 3}" width="2" height="15" fill="#000"/>'
    f'<rect x="88" y="{DESK_Y + 3}" width="2" height="15" fill="#000"/>'
)
DESK = (
    f'<g class="bob">{rects(CHANGRORO, chx, 0)}</g>'
    + desk
    + rects(LAPTOP, chx - 1, DESK_Y - 10)
    + frames(
        rects(HAND, chx - 4, DESK_Y - 4) + rects(HAND, chx + 22, DESK_Y - 3),
        rects(HAND, chx - 4, DESK_Y - 3) + rects(HAND, chx + 22, DESK_Y - 4),
        "hands",
    )
)

parts = {
    "CSS": CSS.strip(),
    "DESK": DESK,
    "MUG": rects(MUG),
    "CLAUDE": runner(CLAUDE_BODY, CLAUDE_LEGS_A, CLAUDE_LEGS_B),
    "CODEX": runner(CODEX_BODY, CODEX_LEGS_A, CODEX_LEGS_B),
}
digits = {k: to_rects(v) for k, v in DIGITS.items()}

import json, os
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, "..", "hooks", "parts.ts")
with open(out, "w") as f:
    f.write("// Generated by scene/scene.py; edit that and rerun.\n")
    for k, v in parts.items():
        f.write(f"export const {k} = {json.dumps(v, ensure_ascii=False)}\n")
    f.write(f"export const DIGITS: Record<string, string> = {json.dumps(digits)}\n")
total = sum(len(v) for v in parts.values()) + len(json.dumps(digits))
print(f"{total} chars of parts -> {os.path.normpath(out)}")
