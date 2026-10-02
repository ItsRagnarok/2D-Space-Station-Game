"""Hero freighter: 3D render -> pixel sprite + hand-drawn pixel flames (blue jets with particle tails)."""
import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy import ndimage
from PIL import Image
from pixelize import pixelize, RAW, LIB
H = int(sys.argv[1]) if len(sys.argv) > 1 else 124
raw = Image.open(os.path.join(RAW, 'ship_hero.png')).convert('RGBA')
bbox = raw.getbbox(); a = np.asarray(raw).astype(int)
# engine glow centres (cyan/white discs) in raw coords
m = (a[..., 3] > 200) & (a[..., 2] > 215) & (a[..., 1] > 190) & (a[..., 0] < 215); lab, n = ndimage.label(m)
blobs = sorted([(ndimage.sum(m, lab, i), ndimage.center_of_mass(lab == i)) for i in range(1, n + 1)], reverse=True)[:2]
name, ship = pixelize(os.path.join(RAW, 'ship_hero.png'), H, 44, True, 1.22)
sx = ship.width / (bbox[2] - bbox[0]); sy = ship.height / (bbox[3] - bbox[1])
cen = [((c[1] - bbox[0]) * sx + 1, (c[0] - bbox[1]) * sy + 1, np.sqrt(sz) * (sx + sy) / 2) for sz, c in blobs]
PADL = 70; canvas = Image.new('RGBA', (ship.width + PADL, ship.height), (0, 0, 0, 0)); px = canvas.load(); rng = random.Random(4)
cols = [(210, 240, 255), (130, 200, 255), (50, 120, 255), (24, 70, 220), (14, 40, 160)]
for cx, cy, r in cen:
    cx += PADL; r = max(7, r * 0.8); L = 78
    for x in range(int(cx) - L, int(cx)):
        t = min(1.0, max(0.0, (cx - x) / L))
        hw = r * (1 - t) ** 0.9 + 0.8
        for y in range(int(cy - hw) - 1, int(cy + hw) + 2):
            d = abs(y - cy) / (hw + 1e-6)
            if d > 1: continue
            lev = d * 0.7 + t * 0.55 + rng.uniform(-0.12, 0.12)
            c = cols[min(4, max(0, int(lev * 5)))]
            if 0 <= x < canvas.width and 0 <= y < canvas.height: px[x, y] = c + (255,)
    for _ in range(90):      # particle tail
        t = rng.uniform(0.35, 1.25); x = int(cx - t * L); y = int(cy + rng.gauss(0, r * 0.55 * (1 - min(t, 1) * 0.4)))
        if 0 <= x < canvas.width and 0 <= y < canvas.height and px[x, y][3] == 0: px[x, y] = rng.choice(cols[2:]) + (255,)
# scuffs / rivets on light plates (pixel-level texture like the reference)
sp = ship.load(); rr = random.Random(9)
for yy in range(ship.height):
    for xx in range(ship.width):
        r_, g_, b_, a_ = sp[xx, yy]
        if a_ and r_ > 150 and g_ > 150 and b_ > 150:
            v = rr.random()
            if v < 0.010: sp[xx, yy] = (70, 72, 86, 255)
            elif v < 0.015: sp[xx, yy] = (255, 150, 30, 255)
            elif v < 0.04: sp[xx, yy] = (r_ - 22, g_ - 22, b_ - 18, 255)
canvas.alpha_composite(ship, (PADL, 0))
# soft additive halo around the jets
arr = np.asarray(canvas).astype(float)
for cx, cy, r in cen:
    yy, xx = np.mgrid[:canvas.height, :canvas.width]; d = np.sqrt((xx - cx - PADL + 18) ** 2 + ((yy - cy) * 1.3) ** 2) / (r * 4.2); k = np.clip(1 - d, 0, 1) ** 2
    bay = np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0, (canvas.height // 4 + 1, canvas.width // 4 + 1))[:canvas.height, :canvas.width]
    k = np.floor(k * 3 + bay) / 3; k = np.clip(k, 0, 1); empty = arr[..., 3] == 0
    arr[..., 0][empty] = np.maximum(arr[..., 0][empty], 20 * k[empty]); arr[..., 1][empty] = np.maximum(arr[..., 1][empty], 80 * k[empty]); arr[..., 2][empty] = np.maximum(arr[..., 2][empty], 255 * k[empty]); arr[..., 3][empty & (k > 0.34)] = 255
canvas = Image.fromarray(arr.astype(np.uint8), 'RGBA')
# ship covers flame origin
canvas.save(os.path.join(LIB, 'ship_hero.png')); print(canvas.size)
bg = Image.new('RGBA', (canvas.width + 40, canvas.height + 40), (16, 16, 20, 255)); bg.alpha_composite(canvas, (20, 20)); bg = bg.resize((bg.width * 5, bg.height * 5), Image.NEAREST)
bg.convert('RGB').save(os.path.join(os.path.dirname(__file__), '..', 'scenes', 'ship_hero_preview.png'))
