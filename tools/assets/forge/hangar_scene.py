"""Hangar scene remake (reference: freighter docking). Ship = Blender render pixelated; rest = forge."""
import json, random, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from core import *

HERE = os.path.dirname(__file__); OUT = os.path.join(HERE, '..', 'out', 'hangar')
ATLAS = os.path.join(HERE, '..', '..', '..', 'public', 'assets')
W, H = 295, 218
random.seed(11)
im = new(W, H, tuple(STEEL[0]))

# ---------- floor: dark brownish-steel tiles ----------
FL = [rgb(c) for c in ('#0d0b09', '#15120e', '#1d1913', '#27221a', '#342d22')]
for y in range(H):
    for x in range(W):
        n = random.random()
        t = 1 if n < .7 else (2 if n < .93 else 3)
        if x % 16 == 0 or y % 16 == 0: t = 0
        elif x % 16 == 1 or y % 16 == 1: t = min(4, t + 1)
        px(im, x, y, FL[t])

def block(x, y, w, h, top=10, ramp=STEEL, accent=ORANGE):
    """Industrial machine: top face + front face + lights."""
    rect(im, x, y, w, h, ramp[2]); rect(im, x, y, w, top, ramp[5]); hline(im, x, y, w, ramp[7]); hline(im, x, y + top, w, ramp[1])
    vline(im, x, y, h, ramp[4]); vline(im, x + w - 1, y, h, ramp[0]); hline(im, x, y + h - 1, w, ramp[0])
    for i in range(2, w - 2, 5):
        rect(im, x + i, y + top + 2, 3, max(1, h - top - 5), ramp[3] if (i // 5) % 2 else ramp[1])
    for _ in range(max(1, w // 9)):
        lx = x + 2 + random.randrange(max(1, w - 4)); ly = y + top + 1 + random.randrange(max(1, h - top - 3))
        px(im, lx, ly, random.choice([accent[4], accent[3], TEAL[3], GREEN[2]]))
    outline(im, x, y, w, h, STEEL[0])

# ---------- walls (north + west + east) ----------
rect(im, 0, 0, W, 40, STEEL[1]); rect(im, 0, 0, 34, H, STEEL[1]); rect(im, W - 34, 0, 34, H, STEEL[1])
x = 0
while x < W - 10:
    w = random.choice([20, 26, 32, 18]); h = random.choice([26, 30, 34]); block(x, 40 - h, w, h, top=9); x += w + random.choice([0, 2, 4])
y = 40
while y < H - 36:
    h = random.choice([20, 26, 30]); block(0, y, 30, h, top=6); block(W - 30, y, 30, h, top=6, accent=TEAL); y += h + 2
# pipes along top
for i, yy in enumerate((6, 12)):
    hline(im, 0, yy, W, ORANGE[2]); hline(im, 0, yy + 1, W, ORANGE[1])
    for xx in range(8, W, 28): rect(im, xx, yy - 1, 3, 4, STEEL[5])
# floor border: orange conduit + dark rail
def rail(x0, y0, x1, y1):
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            px(im, xx, yy, ORANGE[2] if (xx + yy) % 8 < 4 else ORANGE[1])
rail(34, 40, W - 34, 43); rail(34, 40, 37, H - 20); rail(W - 37, 40, W - 34, H - 20)
rect(im, 34, H - 22, W - 68, 22, STEEL[1]); hline(im, 34, H - 22, W - 68, ORANGE[3])
for xx in range(40, W - 40, 18): rect(im, xx, H - 14, 12, 6, STEEL[3]); px(im, xx + 2, H - 12, ORANGE[4])

# ---------- landing pad ----------
PX, PY, PW, PH = 62, 62, 172, 112
shadow(im, PX + PW // 2, PY + PH // 2 + 2, PW // 2 + 6, PH // 2 + 4, 0.6)
for yy in range(PH):
    for xx in range(PW):
        t = 3 if (xx // 12 + yy // 12) % 2 and random.random() < .5 else 2
        if random.random() < .06: t += 1
        px(im, PX + xx, PY + yy, STEEL[t])
outline(im, PX, PY, PW, PH, STEEL[0]); outline(im, PX + 1, PY + 1, PW - 2, PH - 2, STEEL[6])
# hazard border
for i in range(PW):
    for dy in (4, 5, 6, 7):
        c = ORANGE[4] if ((i + dy) // 5) % 2 == 0 else STEEL[0]
        px(im, PX + i, PY + dy - 1, c); px(im, PX + i, PY + PH - dy, c)
for j in range(PH):
    for dx in (4, 5, 6, 7):
        c = ORANGE[4] if ((j + dx) // 5) % 2 == 0 else STEEL[0]
        px(im, PX + dx - 1, PY + j, c); px(im, PX + PW - dx, PY + j, c)
# inner dock frame + corner brackets
outline(im, PX + 14, PY + 14, PW - 28, PH - 28, ORANGE[3])
for cx, cy in ((PX + 14, PY + 14), (PX + PW - 28, PY + 14), (PX + 14, PY + PH - 28), (PX + PW - 28, PY + PH - 28)):
    rect(im, cx, cy, 14, 2, ORANGE[5]); rect(im, cx, cy, 2, 14, ORANGE[5])
    rect(im, cx, cy + 12, 14, 2, ORANGE[5]) if cy > PY + 30 else None
# bay number
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 13); f.getmask('03')
d = ImageDraw.Draw(im); d.fontmode = '1'; d.text((PX + PW - 44, PY + PH - 34), '03', font=f, fill=tuple(ORANGE[4]))
# glow from engines onto pad (blue)
glow(im, 120, 118, 40, BLUE[3], 0.35)

# ---------- ship (blender render -> pixel art) ----------
raw = Image.open(os.path.join(OUT, 'freighter_raw.png')).convert('RGBA'); raw = raw.crop(raw.getbbox())
sw = 150; ship = raw.resize((sw, round(raw.height * sw / raw.width)), Image.LANCZOS)
a = ship.split()[3].point(lambda v: 255 if v > 110 else 0)
ship = ship.convert('RGB').quantize(colors=20, dither=Image.NONE).convert('RGB'); ship.putalpha(a)
# 1px dark outline
sh = ship.copy(); mask = a.filter(ImageFilter.MaxFilter(3))
ol = Image.new('RGBA', ship.size, tuple(STEEL[0])); ol.putalpha(mask)
full = Image.new('RGBA', (ship.width + 2, ship.height + 2)); full.alpha_composite(ol, (1, 1)); full.alpha_composite(ship, (1, 1))
sx = PX + (PW - full.width) // 2 + 4; sy = PY + (PH - full.height) // 2 - 2
shadow(im, sx + full.width // 2, sy + full.height - 4, full.width // 2 - 6, 10, 0.5)
paste(im, full, sx, sy)
# engine glow (additive, dithered)
glow(im, sx + 10, sy + full.height - 26, 30, BLUE[3], 1.0); glow(im, sx + 26, sy + full.height - 12, 28, BLUE[3], 1.0)

# ---------- crates, lights, astronauts ----------
def crate(x, y, c=ORANGE):
    rect(im, x, y, 14, 11, c[2]); rect(im, x, y, 14, 4, c[4]); outline(im, x, y, 14, 11, STEEL[0]); hline(im, x + 1, y + 7, 12, c[1]); vline(im, x + 7, y + 4, 7, c[1])
for x0, y0 in ((42, 150), (42, 163), (58, 163), (236, 52), (252, 52), (240, 66)): crate(x0, y0, ORANGE if (x0 + y0) % 3 else STEEL)
for lx, ly in ((60, 58), (232, 58), (60, 178), (232, 178), (148, 48)):
    glow(im, lx, ly, 22, ORANGE[3], 0.28); rect(im, lx - 1, ly - 1, 3, 3, ORANGE[5])

atlas = Image.open(os.path.join(ATLAS, 'orbital.png')).convert('RGBA'); meta = json.load(open(os.path.join(ATLAS, 'orbital.json')))['frames']
def spr(name):
    fr = meta[name]['frame']; return atlas.crop((fr['x'], fr['y'], fr['x'] + fr['w'], fr['y'] + fr['h']))
for name, (ax, ay) in (('odysseus_eva_down_idle_0', (40, 112)), ('odysseus_eva_up_idle_0', (206, 150))):
    s = spr(name); shadow(im, ax + s.width // 2, ay + s.height - 1, 7, 3, .5); paste(im, s, ax, ay)

# global vignette (dark edges) + scanline-free tone
for y in range(H):
    for x in range(W):
        dx = abs(x - W / 2) / (W / 2); dy = abs(y - H / 2) / (H / 2); v = max(0, (max(dx, dy) - .72) / .28)
        if v > 0:
            p = im.getpixel((x, y)); k = 1 - .45 * v * v
            im.putpixel((x, y), (int(p[0] * k), int(p[1] * k), int(p[2] * k), 255))
im.save(os.path.join(OUT, 'hangar_native.png'))

# ---------- 2x + UI overlay (card + caption) ----------
big = upscale(im, 2).convert('RGB'); d = ImageDraw.Draw(big, 'RGBA')
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf', 15)
fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf', 13)
cx0, cy0, cx1, cy1 = 452, 62, 584, 262
d.rounded_rectangle((cx0, cy0, cx1, cy1), 8, fill=(4, 22, 24, 235), outline=(47, 229, 190, 255), width=2)
d.text((cx0 + 10, cy0 + 8), 'ARRIVAL', font=fb, fill=(120, 255, 235)); d.text((cx0 + 44, cy0 + 30), 'Freighter-7', font=fb, fill=(230, 255, 250))
d.line((cx0 + 8, cy0 + 56, cx1 - 8, cy0 + 56), fill=(31, 138, 120)); d.text((cx0 + 10, cy0 + 62), 'Cargo:', font=fs, fill=(150, 200, 195))
for i, (n, v, c) in enumerate((('Iron', '120', (150, 160, 175)), ('Silicon', '60', (240, 190, 60)), ('Food', '40', (240, 190, 60)))):
    yy = cy0 + 86 + i * 26; d.rectangle((cx0 + 10, yy + 2, cx0 + 22, yy + 14), fill=c); d.text((cx0 + 30, yy), n, font=fs, fill=(230, 255, 250)); d.text((cx1 - 34, yy), v, font=fs, fill=(230, 255, 250))
d.line((cx0 + 8, cy1 - 30, cx1 - 8, cy1 - 30), fill=(31, 138, 120)); d.text((cx0 + 10, cy1 - 24), 'Docking...', font=fs, fill=(120, 255, 235))
d.rectangle((0, 366, 590, 436), fill=(3, 14, 16, 235)); d.line((0, 366, 590, 366), fill=(47, 229, 190, 255), width=2)
ft = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf', 14)
d.text((14, 374), '4.  NAVE CARE VIN ȘI PLEACĂ', font=ft, fill=(255, 255, 255))
d.text((14, 398), 'Primești nave comerciale, cu resurse, misiuni sau cereri speciale.', font=fs, fill=(210, 235, 232))
d.text((14, 414), 'Fii pregătit și gestionează spațiul de andocare.', font=fs, fill=(210, 235, 232))
big.save(os.path.join(OUT, 'hangar_remake.png'))
print('ok')
