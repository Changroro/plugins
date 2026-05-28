#!/usr/bin/env python3
"""
Build a polished project banner from a JSON config.

Usage:
    python build_banner.py <config.json>

The banner is a 1240x440 (default) PNG with three zones:

  ┌──────────────────────────────────────────────────────────────┐
  │ [brand mark]   wordmark (two-tone)             [mockup right]│
  │                TRACKED · UPPERCASE TAGLINE                   │
  │                description line 1                            │
  │                description line 2                            │
  │                [pill] [pill] [pill] [pill]                   │
  └──────────────────────────────────────────────────────────────┘

The script is intentionally a single file with no dependencies beyond
Pillow so a skill can drop it next to a generated JSON config and run
`python build_banner.py config.json`.

Config schema (all fields optional unless marked required):

    {
      "output":          "docs/banner.png",                 (required)
      "canvas":          [1240, 440],
      "theme":           "light",                            "light" | "dark"
      "accent":          [232, 124, 42],                     RGB brand accent
      "wordmark":        ["health", "gochi"],                1st in text color, 2nd in accent
      "tagline":         "LIFT · LOG · LEVEL UP",
      "description":     ["line 1", "line 2"],
      "pills":           ["Routines", "Apple Health"],

      "brand_mark":      {
          "path": "/tmp/icon.png",                           required if you want a brand mark
          "kind": "icon"                                     "icon" (square ~110) | "card" (tall ~190x380)
      },

      "mockup":          {
          "path": "docs/screenshots/home.png",               required if you want a mockup
          "kind": "phone"                                    "phone" | "browser"
      },
      "phone_height":    408,
      "browser_height":  320
    }

Theme presets cover the common cases. Override accent + brand mark to suit.
"""
from __future__ import annotations  # tolerate Python 3.9 with PEP 604 unions

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import functools
import json
import os
import subprocess
import sys


def load_config(path: str) -> dict:
    with open(path) as fh:
        return json.load(fh)


# --- OS-agnostic font resolution -------------------------------------------
# 폰트는 "역할"(round/sans)과 SF named-instance weight 이름으로 요청한다.
# macOS에서는 SF 폰트 + named variation을 그대로 쓰고, 그 외(Linux 등)에서는
# fontconfig로 weight에 맞는 실제 폰트 파일을 찾는다. 호출부는 OS를 몰라도 된다.

_IS_MAC = sys.platform == "darwin"

# SF named-instance weight  →  fontconfig weight 키워드
_FC_WEIGHT = {
    "Heavy": "heavy", "Black": "black", "Bold": "bold",
    "Semibold": "demibold", "Medium": "medium",
    "Regular": "regular", "Light": "light", "Thin": "thin",
}

_MAC_FONTS = {
    "round": ["/System/Library/Fonts/SFNSRounded.ttf", "/System/Library/Fonts/SFNS.ttf"],
    "sans":  ["/System/Library/Fonts/SFNS.ttf"],
}


def _first_existing(paths) -> str | None:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


@functools.lru_cache(maxsize=None)
def _fc_match(pattern: str) -> str | None:
    """fontconfig로 패턴에 맞는 폰트 파일 경로를 찾는다 (없으면 None)."""
    try:
        out = subprocess.run(
            ["fc-match", "-f", "%{file}", pattern],
            capture_output=True, text=True, timeout=5,
        )
        p = out.stdout.strip()
        return p if p and os.path.exists(p) else None
    except Exception:
        return None


@functools.lru_cache(maxsize=None)
def _resolve_font(role: str, variation: str | None) -> tuple[str, str | None]:
    """(role, SF weight 이름) → (폰트 파일 경로, 적용할 named variation 또는 None)."""
    # 1) macOS: SF 폰트 + named variation 그대로 사용
    if _IS_MAC:
        p = _first_existing(_MAC_FONTS.get(role, _MAC_FONTS["sans"]))
        if p:
            return p, variation
    # 2) 그 외(Linux 등): fontconfig로 weight에 맞는 실제 파일을 찾는다
    w = _FC_WEIGHT.get(variation or "Regular", "regular")
    p = _fc_match(f"sans-serif:weight={w}") or _fc_match("sans-serif")
    # 3) fontconfig가 없을 때의 마지막 폴백 후보
    if not p:
        heavy = w in ("bold", "heavy", "black", "demibold", "medium")
        p = _first_existing([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if heavy
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ])
    if not p:
        raise RuntimeError(
            "배너용 폰트를 찾지 못했습니다. fontconfig(fc-match)를 설치하거나 "
            "DejaVu/Noto/Liberation Sans 폰트를 설치하세요."
        )
    # 파일 자체가 weight를 담당하므로 named variation은 적용하지 않는다
    return p, None


def font(role: str, size: int, variation: str | None = None) -> ImageFont.FreeTypeFont:
    path, var = _resolve_font(role, variation)
    f = ImageFont.truetype(path, size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


def theme_palette(name: str) -> dict:
    if name == "dark":
        return dict(
            bg_top=(9, 11, 18), bg_bot=(9, 11, 18),
            glow_color=(40, 66, 150, 170),
            glow_box=lambda W, H: (W * 0.52, -280, W * 1.50, H + 280),
            text=(243, 245, 249), grey=(150, 159, 178),
            pill_bg=(26, 31, 46), pill_bd=(60, 69, 93), pill_tx=(193, 201, 217),
            frame=(28, 26, 30), shadow=(0, 0, 0, 190),
            browser_chrome=(38, 40, 46), browser_chrome_bd=(60, 64, 72),
        )
    return dict(
        bg_top=(252, 249, 245), bg_bot=(246, 232, 229),
        glow_color=(245, 205, 196, 150),
        glow_box=lambda W, H: (-160, 30, 440, H + 140),
        text=(46, 43, 50), grey=(126, 121, 128),
        pill_bg=(255, 255, 255), pill_bd=(231, 224, 224), pill_tx=(92, 87, 95),
        frame=(28, 26, 30), shadow=(70, 52, 52, 110),
        browser_chrome=(236, 236, 240), browser_chrome_bd=(216, 216, 222),
    )


def paint_background(W: int, H: int, p: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), p["bg_top"])
    px = img.load()
    for y in range(H):
        t = y / H
        row = tuple(int(p["bg_top"][i] * (1 - t) + p["bg_bot"][i] * t) for i in range(3))
        for x in range(W):
            px[x, y] = row
    img = img.convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(p["glow_box"](W, H), fill=p["glow_color"])
    return Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(150)))


def paste_phone(img: Image.Image, shot: Image.Image, h: int, p: dict, W: int, H: int) -> tuple[Image.Image, int]:
    """iPhone-style mockup: dark rounded frame, drop shadow."""
    ph_w = round(shot.width * h / shot.height)
    shot = shot.resize((ph_w, h), Image.LANCZOS)
    rad, bw = 30, 6
    fw, fh = ph_w + bw * 2, h + bw * 2
    px = W - fw - 60
    py = (H - fh) // 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [px - 6, py + 20, px + fw + 6, py + fh + 20], radius=rad + bw, fill=p["shadow"])
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(28)))
    fr = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle([0, 0, fw, fh], radius=rad + bw, fill=p["frame"])
    img.alpha_composite(fr, (px, py))
    m = Image.new("L", (ph_w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, ph_w, h], radius=rad, fill=255)
    img.paste(shot, (px + bw, py + bw), m)
    return img, px


def paste_browser(img: Image.Image, shot: Image.Image, h: int, p: dict, W: int, H: int) -> tuple[Image.Image, int]:
    """Desktop browser-window mockup: chrome bar with traffic-light dots, rounded window."""
    chrome_h = 32
    inner_h = h - chrome_h
    inner_w = min(round(shot.width * inner_h / shot.height), 480)
    shot = shot.resize((inner_w, inner_h), Image.LANCZOS)
    fw, fh = inner_w, h
    px = W - fw - 60
    py = (H - fh) // 2
    rad = 14
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [px - 8, py + 18, px + fw + 8, py + fh + 18], radius=rad + 2, fill=p["shadow"])
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(26)))
    win = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    wd = ImageDraw.Draw(win)
    wd.rounded_rectangle([0, 0, fw, fh], radius=rad, fill=p["browser_chrome"],
                          outline=p["browser_chrome_bd"], width=1)
    cy = chrome_h // 2
    cx = 16
    for color in [(255, 95, 86), (255, 189, 46), (39, 201, 63)]:
        wd.ellipse([cx, cy - 5, cx + 10, cy + 5], fill=color)
        cx += 18
    img.alpha_composite(win, (px, py))
    # mask the screenshot with bottom-only rounded corners (top is flat against chrome)
    m = Image.new("L", (inner_w, inner_h), 0)
    md = ImageDraw.Draw(m)
    md.rectangle([0, 0, inner_w, inner_h - rad], fill=255)
    md.rounded_rectangle([0, inner_h - rad * 2, inner_w, inner_h], radius=rad, fill=255)
    img.paste(shot, (px, py + chrome_h), m)
    return img, px


def paste_brand_icon(img: Image.Image, mark: Image.Image) -> int:
    ic = 112
    mark = mark.resize((ic, ic), Image.LANCZOS)
    mm = Image.new("L", (ic, ic), 0)
    ImageDraw.Draw(mm).rounded_rectangle([0, 0, ic, ic], radius=26, fill=255)
    mx, my = 74, 78
    img.paste(mark, (mx, my), mm)
    return mx + ic + 36


def paste_brand_card(img: Image.Image, mark: Image.Image, W: int, H: int) -> tuple[Image.Image, int]:
    """Rounded card with the mascot inside — works when extraction is messy."""
    card_h = 388
    card_w = round(mark.width * card_h / mark.height)
    mark = mark.resize((card_w, card_h), Image.LANCZOS).convert("RGB")
    cr = 30
    cmask = Image.new("L", (card_w, card_h), 0)
    ImageDraw.Draw(cmask).rounded_rectangle([0, 0, card_w, card_h], radius=cr, fill=255)
    cx, cy = 58, (H - card_h) // 2
    csh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(csh).rounded_rectangle(
        [cx - 4, cy + 14, cx + card_w + 4, cy + card_h + 14], radius=cr, fill=(120, 85, 75, 95))
    img = Image.alpha_composite(img, csh.filter(ImageFilter.GaussianBlur(22)))
    img.paste(mark, (cx, cy), cmask)
    ImageDraw.Draw(img).rounded_rectangle(
        [cx, cy, cx + card_w, cy + card_h], radius=cr, outline=(255, 255, 255, 235), width=2)
    return img, cx + card_w + 48


def render(cfg: dict) -> None:
    W, H = cfg.get("canvas", [1240, 440])
    p = theme_palette(cfg.get("theme", "light"))
    accent = tuple(cfg.get("accent", [97, 148, 255]))

    img = paint_background(W, H, p)

    # mockup (right side) — establishes the right boundary for text/pills
    mockup = cfg.get("mockup", {})
    mock_left = W
    if mockup.get("path"):
        shot = Image.open(mockup["path"]).convert("RGB")
        kind = mockup.get("kind", "phone")
        h = cfg.get("phone_height", 408) if kind == "phone" else cfg.get("browser_height", 320)
        if kind == "browser":
            img, mock_left = paste_browser(img, shot, h, p, W, H)
        else:
            img, mock_left = paste_phone(img, shot, h, p, W, H)

    # brand mark (left side) — establishes the left boundary for text
    brand = cfg.get("brand_mark", {})
    bx_start = 74
    if brand.get("path"):
        mark = Image.open(brand["path"]).convert("RGBA")
        if brand.get("kind", "icon") == "card":
            img, bx_start = paste_brand_card(img, mark, W, H)
        else:
            bx_start = paste_brand_icon(img, mark)

    draw = ImageDraw.Draw(img)
    # 폰트는 파일 경로가 아니라 "역할"로 지정한다. font()가 OS에 맞는 실제
    # 폰트 파일을 해석한다 (macOS=SF, 그 외=fontconfig).
    ROUND = "round"
    SANS = "sans"

    # wordmark (auto-fit to space, two-tone)
    wm = cfg.get("wordmark", ["", ""])
    wm_max = max(280, mock_left - bx_start - 24)
    size = 110
    while size > 48:
        f = font(ROUND, size, "Heavy")
        if draw.textlength("".join(wm), font=f) <= wm_max:
            break
        size -= 2
    f = font(ROUND, size, "Heavy")
    asc, _ = f.getmetrics()
    wy = 96
    w1 = draw.textlength(wm[0], font=f)
    draw.text((bx_start, wy), wm[0], font=f, fill=p["text"])
    draw.text((bx_start + w1, wy), wm[1], font=f, fill=accent)

    # tagline (tracked uppercase, in accent)
    tagline = cfg.get("tagline", "")
    if tagline:
        tg = font(SANS, 22, "Bold")
        ty = wy + asc + 2
        tlx = bx_start + 3
        for ch in tagline:
            draw.text((tlx, ty), ch, font=tg, fill=accent)
            tlx += draw.textlength(ch, font=tg) + (7 if ch != " " else 4)
    else:
        ty = wy + asc

    # description (1-2 short lines, grey)
    desc = cfg.get("description", [])
    df = font(SANS, 25, "Regular")
    dy = ty + 52
    for i, line in enumerate(desc):
        draw.text((bx_start, dy + i * 35), line, font=df, fill=p["grey"])

    # pills — stop before they collide with the mockup
    pills = cfg.get("pills", [])
    pf = font(SANS, 21, "Semibold")
    ppx = bx_start
    ppy = dy + 35 * max(len(desc), 1) + 22
    phh = 44
    for label in pills:
        tw = draw.textlength(label, font=pf)
        pw = tw + 36
        if ppx + pw > mock_left - 16:
            break
        draw.rounded_rectangle([ppx, ppy, ppx + pw, ppy + phh], radius=phh // 2,
                                fill=p["pill_bg"], outline=p["pill_bd"], width=1)
        bb = pf.getbbox(label)
        draw.text((ppx + 18, ppy + (phh - (bb[3] - bb[1])) // 2 - bb[1]),
                   label, font=pf, fill=p["pill_tx"])
        ppx += pw + 12

    out = cfg["output"]
    img.convert("RGB").save(out)
    print(f"saved {out} ({W}x{H})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    render(load_config(sys.argv[1]))
