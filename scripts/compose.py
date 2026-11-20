#!/usr/bin/env python3
"""Build the 20 November 2026 world-news front page for make.fun.

The backdrop is an AI-made dotted world map with no writing on it at
all. Every letter the judge sees is painted here with PIL, so the text
stays sharp when the image is shrunk to a thumbnail. The page is a
newspaper front: a masthead with the day, then the five stories that
led Friday 20 November 2026, each in its own card with a headline, a
single factual line and the place it happened.

Stories were checked on 20 Nov 2026 against the OneTurn world brief,
WSJ, Reuters, Barron's, Morningstar and the NY Post: Anthropic's
Nasdaq debut and its Friday slide, the spreading AI sell-off, the
Houthi missile that hit Riyadh's PIF Tower, the COP31 draft dropping
the fossil-fuel phase-out, and the Russian strike on Kyiv's bridges.
Nothing here is invented; second-tier items (IMF debt warning, Kenya's
last Ebola patient, Bukele's third-term bid) were left out.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parents[1]
BACKDROP = BASE_DIR / "news-bg.png"
TARGET = BASE_DIR / "entry.png"

EDGE = 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PLAIN = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

INK = (9, 25, 38)
PANEL = (17, 41, 60)
AMBER = (224, 169, 78)
PAPER = (243, 244, 246)
GREY = (188, 198, 210)
STRIPES = [(224, 169, 78), (196, 82, 74), (86, 158, 143), (214, 126, 58), (106, 144, 204)]

CARDS = [
    (
        "ANTHROPIC DEBUTS, THEN SLIDES",
        "Shares open at $111.50, close at $97.17 — then slide in Friday pre-market",
        "NEW\u00a0YORK",
    ),
    (
        "AI SELLOFF SPREADS",
        "S&P falls 2% for a fifth straight day; Nikkei drops 4.8%",
        "NEW YORK",
    ),
    (
        "HOUTHI MISSILE HITS RIYADH",
        "PIF Tower windows blown out across seven floors; no injuries",
        "RIYADH",
    ),
    (
        "COP31 DROPS FOSSIL PHASE-OUT",
        "Antalya draft deal drops any call to end fossil fuels",
        "ANTALYA",
    ),
    (
        "KYIV BRIDGES HIT",
        "Russian missile attack hits three bridges; at least six killed",
        "KYIV",
    ),
]


def load(size):
    return ImageFont.truetype(BOLD if size[1] else PLAIN, size[0])


def fit_lines(canvas, text, typeface, width):
    """Split text into as few lines as fit inside width.

    Splits on plain spaces only, so a non-breaking space inside a
    dateline keeps the two words on the same line.
    """
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if canvas.textlength(trial, font=typeface) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build():
    photo = Image.open(BACKDROP).convert("RGB")
    photo = photo.resize((EDGE, EDGE), Image.LANCZOS)
    veil = Image.new("RGB", photo.size, (7, 17, 30))
    page = Image.blend(photo, veil, 0.5)
    pen = ImageDraw.Draw(page, "RGBA")

    # Masthead: title, gold rule, day line, pale rule.
    pen.text((EDGE // 2, 34), "WORLD NEWS", font=load((92, True)),
             fill=PAPER, anchor="ma")
    pen.rectangle([52, 138, EDGE - 52, 141], fill=AMBER)
    pen.text((EDGE // 2, 152), "FRIDAY  •  20 NOVEMBER 2026",
             font=load((40, True)), fill=AMBER, anchor="ma")
    pen.rectangle([52, 212, EDGE - 52, 215], fill=(118, 133, 156))

    # One card per story.
    top = 234
    height, space = 138, 12
    number_face = load((54, True))
    head_face = load((35, True))
    body_face = load((22, False))
    for index, (headline, detail, place) in enumerate(CARDS):
        stripe = STRIPES[index]
        pen.rounded_rectangle([52, top, EDGE - 52, top + height], radius=10,
                              fill=PANEL + (230,))
        pen.rectangle([52, top + 10, 62, top + height - 10], fill=stripe)
        pen.text((96, top + height // 2), f"{index + 1:02d}",
                 font=number_face, fill=stripe, anchor="lm")
        text_x = 196
        text_w = EDGE - 52 - text_x - 26
        head_lines = fit_lines(pen, headline, head_face, text_w)
        cursor = top + 18
        for line in head_lines[:2]:
            pen.text((text_x, cursor), line, font=head_face,
                     fill=PAPER, anchor="la")
            cursor += 42
        body = f"{detail}  —  {place}"
        body_lines = fit_lines(pen, body, body_face, text_w)
        cursor = max(top + 66, cursor + 6)
        for line in body_lines[:2]:
            pen.text((text_x, cursor), line, font=body_face,
                     fill=GREY, anchor="la")
            cursor += 28
        top += height + space

    # Footer.
    pen.text((EDGE // 2, 984), "THE DAY IN FIVE STORIES  •  20 NOVEMBER 2026",
             font=load((23, False)), fill=GREY, anchor="ma")

    page.save(TARGET, "PNG", optimize=True)
    print(f"saved {TARGET} {page.size} {TARGET.stat().st_size} bytes")


if __name__ == "__main__":
    build()
