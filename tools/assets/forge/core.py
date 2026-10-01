"""Tiny pixel-art toolkit: palettes, drawing helpers, dithered glow, ASCII sprites."""
from PIL import Image, ImageDraw
import math, random

def rgb(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)

# ---- palette (sampled from the reference mood, then simplified) ----
STEEL = [rgb(c) for c in ('#101216', '#181b21', '#22262e', '#2e333d', '#3c424e', '#4e5562', '#6a7383', '#939cad', '#c0c8d6')]
ORANGE = [rgb(c) for c in ('#2e1604', '#6a340a', '#b0580f', '#e8902a', '#ffc455', '#ffe8a0')]
TEAL = [rgb(c) for c in ('#031c20', '#08454e', '#0f808c', '#22c4c4', '#8cf2e6')]
BLUE = [rgb(c) for c in ('#07124a', '#12309a', '#2a66e0', '#58a4ff', '#a6d8ff', '#e8f6ff')]
GREEN = [rgb(c) for c in ('#0e3a22', '#1f7a42', '#38c068', '#86f0a8')]
RED = [rgb(c) for c in ('#4a0c14', '#a01c2a', '#e04458')]
CLEAR = (0, 0, 0, 0)

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def bay(x, y):
    return (BAYER[y % 4][x % 4] + 0.5) / 16.0

def new(w, h, fill=CLEAR):
    return Image.new('RGBA', (w, h), fill)

def px(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((int(x), int(y)), c)

def rect(im, x, y, w, h, c):
    ImageDraw.Draw(im).rectangle([x, y, x + w - 1, y + h - 1], fill=c)

def hline(im, x, y, w, c):
    rect(im, x, y, w, 1, c)

def vline(im, x, y, h, c):
    rect(im, x, y, 1, h, c)

def outline(im, x, y, w, h, c):
    ImageDraw.Draw(im).rectangle([x, y, x + w - 1, y + h - 1], outline=c)

def paste(dst, src, x, y):
    dst.alpha_composite(src, (int(x), int(y)))

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)

def glow(im, cx, cy, r, color, strength=1.0, mask=None):
    """Dithered additive-ish light: pixels near (cx,cy) are pulled toward color in hard steps."""
    for y in range(max(0, int(cy - r)), min(im.height, int(cy + r) + 1)):
        for x in range(max(0, int(cx - r)), min(im.width, int(cx + r) + 1)):
            d = math.hypot(x - cx, y - cy) / r
            if d >= 1:
                continue
            i = (1 - d) ** 1.6 * strength
            lvl = i + (bay(x, y) - 0.5) * 0.22
            if lvl < 0.12:
                continue
            t = 0.55 if lvl > 0.62 else 0.34 if lvl > 0.38 else 0.17
            p = im.getpixel((x, y))
            if p[3] == 0:
                continue
            im.putpixel((x, y), lerp(p, color, t))

def shadow(im, cx, cy, rx, ry, k=0.5):
    """Hard-edged dark ellipse (multiplies what is under it)."""
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and 0 <= x < im.width and 0 <= y < im.height:
                p = im.getpixel((x, y))
                im.putpixel((x, y), (int(p[0] * k), int(p[1] * k), int(p[2] * k), p[3]))

def ascii_sprite(rows, pal):
    h = len(rows); w = max(len(r) for r in rows)
    im = new(w, h)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal and pal[ch] is not None:
                im.putpixel((x, y), pal[ch])
    return im

def upscale(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)
