#!/usr/bin/env python3
"""Sum up 18 November 2026's world news in one image.

Entry for make.fun competition news-image-20261118.
Draws a newspaper front page (1024x1024 PNG) with six real stories
reported on Wednesday 18 November 2026, using only the Python 3.13
standard library. No network access, no randomness, no timestamps:
running it twice writes byte-identical output.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
PAPER = (247, 243, 234)
INK = (17, 24, 39)
NAVY = (14, 42, 71)
NAVY_DARK = (9, 28, 50)
RED = (185, 28, 28)
GOLD = (201, 162, 39)
GOLD_LIGHT = (232, 197, 92)
TEAL = (14, 116, 144)
SEA = (23, 64, 94)
SEA_DARK = (15, 46, 70)
ORANGE = (234, 88, 12)
YELLOW = (250, 204, 21)
GREY = (107, 114, 128)
GREY_DARK = (75, 85, 99)
LINE = (203, 213, 225)
WHITE = (255, 255, 255)
SKY = (186, 214, 235)
SAND = (214, 186, 140)
GREEN = (21, 128, 61)

# ---------------------------------------------------------------------------
# 5x7 bitmap font (all glyphs are 7 rows of 5 bits, '1' = filled pixel).
# Text is drawn in ALL CAPS so only uppercase glyphs are needed.
# ---------------------------------------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "\u00b7": ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
    "\u2022": ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "\\": ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
}


def text_width(text, scale):
    """Pixel width of text drawn at the given scale."""
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = (current + " " + word).strip()
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """An RGB raster with simple vector drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        row = bytes((r, g, b)) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with square brush of size thick."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled:
                    if d2 <= r * r:
                        self.set(xx, yy, color)
                else:
                    if abs(d2 - r * r) <= r:
                        self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=2):
        for t in range(thick):
            self.circle(cx, cy, r - t, color, filled=False)

    def polygon(self, points, color):
        """Scanline fill of a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, color)

    def star(self, cx, cy, r_outer, r_inner, color, rot=-90):
        pts = []
        for i in range(10):
            r = r_outer if i % 2 == 0 else r_inner
            a = math.radians(rot + i * 36)
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.polygon(pts, color)

    def burst(self, cx, cy, r, color, spikes=12):
        """Explosion starburst: filled circle plus radiating spikes."""
        for i in range(spikes):
            a = math.radians(i * (360.0 / spikes))
            x1 = int(cx + r * math.cos(a))
            y1 = int(cy + r * math.sin(a))
            self.line(cx, cy, x1, y1, color, thick=3)
        self.circle(cx, cy, r // 2, color)

    def text(self, x, y, s, scale, color, align="left"):
        """Draw text at top-left (x, y); returns the pixel width drawn."""
        if align == "center":
            x = x - text_width(s, scale) // 2
        elif align == "right":
            x = x - text_width(s, scale)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for r, row in enumerate(glyph):
                for c, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + c * scale, y + r * scale, scale, scale, color)
            cx += 6 * scale
        return cx - x - scale if s else 0


def _png_chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path, canvas):
    """Encode the canvas as a deterministic PNG (filter 0, zlib level 9)."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _png_chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# Story illustrations (simple vector scenes, one per story)
# ---------------------------------------------------------------------------

def draw_gulf(cv, x, y, w, h):
    """Qeshm Island / Gulf: sea, island, missile trails, explosion, radar."""
    cv.rect(x, y, w, h, SEA)
    # waves
    for i in range(4):
        wy = y + h - 18 - i * 14
        cv.hline(x + 8 + (i % 2) * 20, wy, w - 40, (120, 180, 210), thick=2)
    # island
    cv.polygon(
        [(x + 18, y + h - 8), (x + 60, y + h - 70), (x + 130, y + h - 78),
         (x + 190, y + h - 40), (x + 210, y + h - 8)],
        SAND,
    )
    cv.rect(x + 96, y + h - 96, 10, 22, INK)  # small tower
    cv.rect(x + 88, y + h - 104, 26, 8, INK)
    # missile trails from the island
    cv.line(x + 120, y + h - 80, x + 250, y + 46, ORANGE, thick=4)
    cv.line(x + 150, y + h - 70, x + 300, y + 90, GOLD_LIGHT, thick=4)
    cv.circle(x + 250, y + 46, 6, WHITE)
    cv.circle(x + 300, y + 90, 6, WHITE)
    # explosion over the island
    cv.burst(x + 120, y + h - 84, 26, ORANGE)
    cv.burst(x + 120, y + h - 84, 13, YELLOW)
    # radar arcs top right (kept inside the sea rect)
    cv.ring(x + w - 44, y + 30, 26, WHITE, thick=2)
    cv.ring(x + w - 44, y + 30, 16, WHITE, thick=2)
    cv.circle(x + w - 44, y + 30, 4, WHITE)


def draw_bridge(cv, x, y, w, h):
    """Kerch Bridge: deck across the strait, one span collapsed, smoke."""
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 60, y + 34, 22, GOLD_LIGHT)  # pale sun
    # water
    cv.rect(x, y + h - 46, w, 46, SEA)
    cv.hline(x + 10, y + h - 30, w - 30, (120, 180, 210), thick=2)
    cv.hline(x + 30, y + h - 16, w - 50, (120, 180, 210), thick=2)
    # bridge deck with a broken gap in the middle (deck sits low so the
    # explosion and smoke above it stay inside the strip)
    deck_y = y + h - 66
    cv.rect(x + 6, deck_y, w // 2 - 40, 8, INK)
    cv.rect(x + w // 2 + 46, deck_y, w // 2 - 52, 8, INK)
    # collapsed span falling into the strait
    cv.line(x + w // 2 - 34, deck_y + 4, x + w // 2 + 6, deck_y + 34, INK, thick=6)
    cv.line(x + w // 2 + 40, deck_y + 4, x + w // 2 + 10, deck_y + 30, INK, thick=6)
    # supports
    for sx in (x + 40, x + w - 60):
        cv.rect(sx, deck_y + 8, 8, h - 46 - (deck_y - y) - 8, INK)
    # standing arch on the left half
    cv.ring(x + w // 4, deck_y + 6, 24, NAVY, thick=4)
    # explosion + smoke at the break (kept inside the strip)
    cv.burst(x + w // 2 + 4, deck_y - 2, 14, ORANGE)
    cv.burst(x + w // 2 + 4, deck_y - 2, 7, YELLOW)
    cv.circle(x + w // 2 - 24, deck_y - 12, 8, GREY)
    cv.circle(x + w // 2 - 6, deck_y - 16, 10, GREY)
    cv.circle(x + w // 2 + 14, deck_y - 12, 7, GREY)


def draw_skyline(cv, x, y, w, h):
    """Shenzhen skyline at the APEC summit: towers, sun, flags."""
    cv.rect(x, y, w, h, SKY)
    towers = [(0, 92, 46), (52, 128, 40), (98, 76, 52), (156, 140, 36),
              (198, 104, 48), (252, 132, 38), (296, 88, 50), (352, 120, 42),
              (400, 96, 44)]
    for tx, th, tw in towers:
        cv.rect(x + tx, y + h - th, tw, th, NAVY)
        for wy in range(y + h - th + 10, y + h - 8, 18):
            for wx in range(x + tx + 8, x + tx + tw - 6, 14):
                cv.rect(wx, wy, 5, 6, GOLD_LIGHT)
    # sun drawn last so it sits on top of the towers
    cv.circle(x + 46, y + 30, 20, GOLD)
    # flags on the tallest tower
    fx = x + 98 + 26
    cv.vline(fx, y + h - 76 - 26, 26, INK, thick=3)
    cv.polygon([(fx, y + h - 102), (fx + 22, y + h - 96), (fx, y + h - 90)], RED)
    # red summit banner across the bottom
    cv.rect(x, y + h - 22, w, 22, RED)
    cv.text(x + 12, y + h - 19, "APEC", 2, WHITE)


def draw_ballot(cv, x, y, w, h):
    """Alaska Senate flip: ballot box, paper slip, big check, gold star.

    Fits inside the (w x h) illustration area: box sits at the bottom,
    the slip rises only to the top of the area.
    """
    cv.rect(x, y, w, h, PAPER)
    bw, bh = 92, 44
    bx = x + w // 2 - bw // 2
    by = y + h - bh - 2
    cv.rect(bx, by, bw, bh, NAVY)
    cv.rect(bx - 8, by - 8, bw + 16, 10, NAVY_DARK)
    cv.rect(bx + 18, by - 3, 56, 4, INK)
    # paper slip going in (top stays inside the area)
    cv.polygon([(bx + 26, y + 2), (bx + 68, y + 2), (bx + 66, by - 3),
                (bx + 28, by - 3)], WHITE)
    cv.line(bx + 34, y + 10, bx + 60, y + 10, GREY_DARK, thick=2)
    cv.line(bx + 34, y + 18, bx + 60, y + 18, GREY_DARK, thick=2)
    # big red check over the box
    cv.line(bx + 6, by + 22, bx + 30, by + 38, RED, thick=7)
    cv.line(bx + 30, by + 38, bx + 86, by + 2, RED, thick=7)
    # Alaska star (the state flag's Big Dipper star)
    cv.star(x + 26, y + 22, 13, 6, GOLD)


def draw_virus(cv, x, y, w, h, body_color, spike_color):
    """Spiky virus ball (measles): circle with radiating spikes."""
    cv.rect(x, y, w, h, PAPER)
    cx, cy = x + w // 2, y + h // 2 + 6
    for i in range(14):
        a = math.radians(i * (360.0 / 14))
        x1 = int(cx + 44 * math.cos(a))
        y1 = int(cy + 44 * math.sin(a))
        cv.line(cx, cy, x1, y1, spike_color, thick=4)
        cv.circle(x1, y1, 6, spike_color)
    cv.circle(cx, cy, 34, body_color)
    cv.circle(cx - 12, cy - 10, 8, (255, 255, 255))
    cv.circle(cx + 10, cy + 12, 5, (255, 255, 255))


def draw_filament(cv, x, y, w, h):
    """Ebola filament: a long curved worm-like strand with rounded ends."""
    cv.rect(x, y, w, h, PAPER)
    pts = []
    for t in range(0, 101):
        px = x + 18 + t * (w - 36) / 100.0
        py = y + h // 2 + 26 * math.sin(t * math.pi * 1.6 / 50.0)
        pts.append((int(px), int(py)))
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], GREEN, thick=14)
    cv.circle(pts[0][0], pts[0][1], 9, GREEN)
    cv.circle(pts[-1][0], pts[-1][1], 9, GREEN)
    # small branch filaments
    cv.line(pts[30][0], pts[30][1], pts[30][0] - 16, pts[30][1] - 30, GREEN, thick=6)
    cv.line(pts[65][0], pts[65][1], pts[65][0] + 14, pts[65][1] + 28, GREEN, thick=6)


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------

def panel(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 3, NAVY)
    # 2px outline
    cv.hline(x, y, w, INK, thick=2)
    cv.hline(x, y + h - 2, w, INK, thick=2)
    cv.vline(x, y, h, INK, thick=2)
    cv.vline(x + w - 2, y, h, INK, thick=2)


def kicker(cv, x, y, s, scale=2):
    cv.text(x, y, s, scale, RED)


def headline(cv, x, y, lines, scale, max_w, color=INK, gap=6):
    yy = y
    for line in lines:
        cv.text(x, yy, line, scale, color)
        yy += 7 * scale + gap
    return yy


def summary(cv, x, y, text, scale, max_w, color=GREY_DARK, gap=4):
    yy = y
    for line in wrap_text(text, scale, max_w):
        cv.text(x, yy, line, scale, color)
        yy += 7 * scale + gap
    return yy


def draw_page():
    cv = Canvas(W, H, PAPER)

    # --- masthead ---------------------------------------------------------
    cv.rect(0, 0, W, 116, NAVY)
    cv.rect(0, 116, W, 4, GOLD)
    cv.text(W // 2, 18, "THE WORLD IN ONE DAY", 5, WHITE, align="center")
    cv.text(W // 2, 74, "WEDNESDAY, 18 NOVEMBER 2026", 3, GOLD_LIGHT, align="center")

    # --- lead story: Gulf -------------------------------------------------
    lx, ly, lw, lh = 24, 132, 976, 276
    panel(cv, lx, ly, lw, lh)
    draw_gulf(cv, lx + 14, ly + 14, 360, lh - 28)
    tx = lx + 396
    tw = lw - 396 - 24
    kicker(cv, tx, ly + 22, "MIDDLE EAST  \u00b7  GULF CRISIS")
    headline(cv, tx, ly + 52,
             ["US STRIKES IRAN'S", "QESHM ISLAND BASE"], 4, tw)
    summary(cv, tx, ly + 172,
            "US JETS HIT A GUARD MISSILE SITE. IRAN FIRED DRONES AT "
            "US BASES IN BAHRAIN AND KUWAIT.", 3, tw)

    # --- second row: Crimea bridge / APEC ---------------------------------
    y2, h2 = 424, 252
    # Crimea
    ax, aw = 24, 476
    panel(cv, ax, y2, aw, h2)
    draw_bridge(cv, ax + 12, y2 + 12, aw - 24, 96)
    kicker(cv, ax + 16, y2 + 122, "EUROPE  \u00b7  UKRAINE WAR")
    headline(cv, ax + 16, y2 + 148, ["KERCH BRIDGE HIT", "FOR SECOND DAY"], 3, aw - 32)
    summary(cv, ax + 16, y2 + 202,
            "UKRAINE HIT THE BRIDGE AGAIN; PART OF THE ROAD SPAN FELL.",
            2, aw - 32)
    # APEC
    bx, bw = 524, 476
    panel(cv, bx, y2, bw, h2)
    draw_skyline(cv, bx + 12, y2 + 12, bw - 24, 96)
    kicker(cv, bx + 16, y2 + 122, "ASIA  \u00b7  TRADE")
    headline(cv, bx + 16, y2 + 148, ["APEC OPENS IN", "SHENZHEN"], 3, bw - 32)
    summary(cv, bx + 16, y2 + 202,
            "XI HOSTS LEADERS AS TRUMP, XI AND PUTIN PREPARE THURSDAY "
            "SUMMIT TALKS.", 2, bw - 32)

    # --- third row: Alaska / measles / Ebola -------------------------------
    y3, h3 = 692, 252
    pw, gap = 312, 20
    # Alaska
    cx0 = 24
    panel(cv, cx0, y3, pw, h3)
    draw_ballot(cv, cx0 + 12, y3 + 12, pw - 24, 84)
    kicker(cv, cx0 + 14, y3 + 108, "USA  \u00b7  POLITICS")
    headline(cv, cx0 + 14, y3 + 132, ["DEMOCRATS FLIP", "ALASKA SENATE"], 3, pw - 28)
    summary(cv, cx0 + 14, y3 + 194,
            "PELTOLA BEATS SULLIVAN; SENATE MAJORITY NOW 56.", 2, pw - 28)
    # Measles
    cx1 = cx0 + pw + gap
    panel(cv, cx1, y3, pw, h3)
    draw_virus(cv, cx1 + 12, y3 + 12, pw - 24, 84, RED, (120, 20, 20))
    kicker(cv, cx1 + 14, y3 + 108, "USA  \u00b7  HEALTH")
    headline(cv, cx1 + 14, y3 + 132, ["US LOSES MEASLES-", "FREE STATUS"], 3, pw - 28)
    summary(cv, cx1 + 14, y3 + 194,
            "5,400 CASES, 10 DEATHS END 26 YEARS OF ELIMINATION.", 2, pw - 28)
    # Ebola
    cx2 = cx1 + pw + gap
    panel(cv, cx2, y3, pw, h3)
    draw_filament(cv, cx2 + 12, y3 + 12, pw - 24, 84)
    kicker(cv, cx2 + 14, y3 + 108, "AFRICA  \u00b7  HEALTH")
    headline(cv, cx2 + 14, y3 + 132, ["EBOLA SURGE IN", "DR CONGO"], 3, pw - 28)
    summary(cv, cx2 + 14, y3 + 194,
            "OUTBREAK DOUBLES: 11,000 CASES, 5,400 DEATHS.", 2, pw - 28)

    # --- footer ------------------------------------------------------------
    cv.rect(0, 960, W, 64, NAVY)
    cv.rect(0, 960, W, 3, GOLD)
    cv.text(24, 976, "IN BRIEF: RUSSIAN MILITARY PLANE CRASHES IN SIBERIA, "
             "KILLING ALL 19 ABOARD.", 2, WHITE)
    cv.text(24, 998, "ALL EVENTS REPORTED ON 18 NOVEMBER 2026", 2, GOLD_LIGHT)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = draw_page()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, canvas)
    print(f"wrote {path} ({size} bytes, {canvas.w}x{canvas.h})")


if __name__ == "__main__":
    main()
