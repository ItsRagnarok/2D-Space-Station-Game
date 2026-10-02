"""Shared helpers for composing scenes: raw sprite loading, noise, planets, glow, HUD panels."""
import os, random, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pixelize import pixelize, RAW
HERE = os.path.dirname(__file__); OUT = os.path.join(HERE, '..', 'out', 'scenes'); os.makedirs(OUT, exist_ok=True)
FD = '/usr/share/fonts/truetype/dejavu/'
def font(sz, bold=True): return ImageFont.truetype(FD + ('DejaVuSansCondensed-Bold.ttf' if bold else 'DejaVuSansCondensed.ttf'), sz)

_cache = {}
def spr(name, h=None, flip=False, colors=22, sat=1.25, outline=True):
    key = (name, h, flip, colors, sat, outline)
    if key not in _cache:
        n, im = pixelize(os.path.join(RAW, name + '.png'), h, colors, outline, sat)
        _cache[key] = im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
    return _cache[key].copy()

def noise(w, h, scale=24, octaves=4, seed=0):
    rng = np.random.RandomState(seed); out = np.zeros((h, w)); amp = 1.0; tot = 0
    for o in range(octaves):
        gw, gh = max(2, w // max(1, scale >> o)) + 2, max(2, h // max(1, scale >> o)) + 2
        g = rng.rand(gh, gw); im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += np.asarray(im) / 255 * amp; tot += amp; amp *= 0.5
    return out / tot

def add_glow(im, cx, cy, r, col, k=1.0):
    """Additive soft glow with ordered-dither quantisation (stays pixel-art)."""
    w, h = im.size; y, x = np.ogrid[:h, :w]; d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    a = np.clip(1 - d, 0, 1) ** 2 * k
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
    bm = np.tile(bayer, (h // 4 + 1, w // 4 + 1))[:h, :w]; a = np.floor(a * 4 + bm) / 4; a = np.clip(a, 0, 1)
    arr = np.asarray(im.convert('RGB')).astype(float)
    for i in range(3): arr[..., i] = np.clip(arr[..., i] + a * col[i], 0, 255)
    im.paste(Image.fromarray(arr.astype(np.uint8)), (0, 0))

def shadow(im, cx, cy, rx, ry, k=0.5):
    a = np.asarray(im.convert('RGB')).astype(float); h, w = a.shape[:2]; y, x = np.ogrid[:h, :w]
    m = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1; a[m] *= k; im.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))

def paste(im, s, x, y): im.alpha_composite(s, (int(x), int(y))) if im.mode == 'RGBA' else im.paste(s, (int(x), int(y)), s)

def planet(r, base, mid, hi, seed=3, ring=None, craters=14, bands=0.0):
    """Shaded pixel planet; returns RGBA sprite. ring=(col,tilt) optional."""
    S = 2 * r + 2; yy, xx = np.mgrid[:S, :S]; dx = (xx - r) / r; dy = (yy - r) / r; d2 = dx ** 2 + dy ** 2; inside = d2 <= 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1)); L = np.array([-0.55, -0.6, 0.58]); L /= np.linalg.norm(L)
    light = np.clip(dx * L[0] + dy * L[1] + nz * L[2], 0, 1)
    n = noise(S, S, 16, 4, seed); tex = n + bands * np.sin(dy * 9 + n * 4) * 0.15
    rng = random.Random(seed)
    for _ in range(craters):
        cx, cy, cr = rng.uniform(-.7, .7), rng.uniform(-.7, .7), rng.uniform(.07, .2)
        dd = np.sqrt((dx - cx) ** 2 + (dy - cy) ** 2); tex -= np.clip(1 - dd / cr, 0, 1) * 0.18; tex += np.clip(1 - abs(dd - cr) / 0.03, 0, 1) * 0.1
    v = np.clip(light * 0.85 + (tex - 0.5) * 0.5 + 0.08, 0, 1)
    pal = np.array([base, mid, hi], float); idx = np.clip(v * 2.999, 0, 2.999); lo = idx.astype(int); fr = idx - lo
    rgb = pal[lo] * (1 - fr[..., None]) + pal[np.minimum(lo + 1, 2)] * fr[..., None]
    q = np.floor(rgb / 28) * 28; q += 8; im = np.dstack([q, inside * 255]).astype(np.uint8); out = Image.fromarray(im, 'RGBA')
    rim = np.clip((d2 - 0.78) / 0.22, 0, 1) * (light < 0.5)  # dark limb
    a = np.asarray(out).copy().astype(float); a[..., :3] *= (1 - 0.5 * rim[..., None]); out = Image.fromarray(a.astype(np.uint8), 'RGBA')
    if ring:
        col, tilt = ring; W = int(S * 1.9); big = Image.new('RGBA', (W, S + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
        cx, cy = W // 2, (S + 30) // 2
        for rr, c in ((int(S * .92), col), (int(S * .8), tuple(int(v * .7) for v in col))):
            d.ellipse((cx - rr, cy - int(rr * tilt), cx + rr, cy + int(rr * tilt)), outline=c + (255,), width=3)
        back = big.copy(); front = big.copy()
        m = Image.new('L', big.size, 0); ImageDraw.Draw(m).rectangle((0, cy, W, S + 30), fill=255)
        back.putalpha(Image.eval(back.split()[3], lambda v: v)); bk = Image.composite(Image.new('RGBA', big.size, (0, 0, 0, 0)), big, m)
        ft = Image.composite(big, Image.new('RGBA', big.size, (0, 0, 0, 0)), m)
        res = Image.new('RGBA', big.size, (0, 0, 0, 0)); res.alpha_composite(bk); res.alpha_composite(out, (cx - r - 1, cy - r - 1)); res.alpha_composite(ft); return res
    return out

def hud_panel(d, box, title=None, accent=(47, 229, 190), fill=(4, 22, 24, 232), width=2, r=8):
    d.rounded_rectangle(box, r, fill=fill, outline=accent + (255,), width=width)
    if title: d.text((box[0] + 12, box[1] + 8), title, font=font(15), fill=tuple(min(255, c + 40) for c in accent))

def caption_bar(big, num_title, line1, line2, h=70, accent=(47, 229, 190)):
    W, H = big.size; d = ImageDraw.Draw(big, 'RGBA'); d.rectangle((0, H - h, W, H), fill=(3, 14, 16, 236)); d.line((0, H - h, W, H - h), fill=accent + (255,), width=2)
    d.text((16, H - h + 8), num_title, font=font(15), fill=(255, 255, 255)); d.text((16, H - h + 32), line1, font=font(12, False), fill=(205, 232, 228)); d.text((16, H - h + 48), line2, font=font(12, False), fill=(205, 232, 228))

def stars(im, n, seed=1, tint=((255, 255, 255), (170, 200, 255), (255, 220, 180))):
    rng = random.Random(seed); w, h = im.size
    for _ in range(n):
        x, y = rng.randrange(w), rng.randrange(h); c = rng.choice(tint); b = rng.choice((0.35, 0.5, 0.7, 1.0))
        im.putpixel((x, y), tuple(int(v * b) for v in c) + (255,))
        if b == 1.0 and rng.random() < .25:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < w and 0 <= y + dy < h: im.putpixel((x + dx, y + dy), tuple(int(v * .4) for v in c) + (255,))

import json as _json
_ATL = None
def atlas(name, scale=1):
    global _ATL
    if _ATL is None:
        base = os.path.join(HERE, '..', '..', '..', 'public', 'assets')
        _ATL = (Image.open(os.path.join(base, 'orbital.png')).convert('RGBA'), _json.load(open(os.path.join(base, 'orbital.json')))['frames'])
    im, meta = _ATL; f = meta[name]['frame']; s = im.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))
    return s.resize((s.width * scale, s.height * scale), Image.NEAREST) if scale != 1 else s

def ramp_map(v, stops):
    """v in 0..1 -> RGB through colour stops [(pos,(r,g,b)),...], posterised."""
    out = np.zeros(v.shape + (3,))
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (v >= p0) & (v <= p1); t = ((v - p0) / (p1 - p0 + 1e-9))[..., None]; out[m] = (np.array(c0) * (1 - t) + np.array(c1) * t)[m]
    out[v < stops[0][0]] = stops[0][1]; out[v > stops[-1][0]] = stops[-1][1]; return out

def dither_post(arr, levels=24):
    h, w = arr.shape[:2]; bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5
    bm = np.tile(bayer, (h // 4 + 1, w // 4 + 1))[:h, :w, None]; step = 255 / levels
    return np.clip(np.round(arr / step + bm * 0.9) * step, 0, 255)
