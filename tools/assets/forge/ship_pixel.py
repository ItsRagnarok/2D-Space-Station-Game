"""Module renders (cabin / mid / engines / all) -> aligned pixel sprites + jets. Usage: ship_pixel.py [height]"""
import sys, os, random
import numpy as np
from scipy import ndimage
from PIL import Image, ImageEnhance, ImageFilter
H = int(sys.argv[1]) if len(sys.argv) > 1 else 200
HERE = os.path.dirname(__file__); SRC = os.path.join(HERE, '..', 'out', 'ship'); LIB = os.path.join(HERE, '..', 'library'); SC = os.path.join(HERE, '..', 'scenes')
raw = {n: Image.open(os.path.join(SRC, f'ship_{n}.png')).convert('RGBA') for n in ('all', 'cabin', 'mid', 'eng')}
bbox = raw['all'].getbbox(); w0 = bbox[2] - bbox[0]; h0 = bbox[3] - bbox[1]; sc = H / h0; W = round(w0 * sc)
def px(im, colors=48, pal=None):
    im = im.crop(bbox).resize((W, H), Image.BOX); a = im.split()[3].point(lambda v: 255 if v > 110 else 0)
    rgb = ImageEnhance.Contrast(ImageEnhance.Color(im.convert('RGB')).enhance(1.25)).enhance(1.1)
    rgb = rgb.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE) if pal is None else rgb.quantize(palette=pal, dither=Image.NONE)
    return rgb, a
rgb_all, a_all = px(raw['all']); pal = rgb_all
def outline(rgb, a):
    out = Image.new('RGBA', (W + 2, H + 2), (0, 0, 0, 0)); m = Image.new('L', (W + 2, H + 2), 0); m.paste(a, (1, 1)); m = m.filter(ImageFilter.MaxFilter(3))
    ol = Image.new('RGBA', out.size, (10, 10, 16, 255)); ol.putalpha(m); out.alpha_composite(ol); im = rgb.convert('RGB').convert('RGBA'); im.putalpha(a); out.alpha_composite(im, (1, 1)); return out
rng = random.Random(7)
def scuff(im):
    p = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = p[x, y]
            if a and r > 165 and g > 165 and b > 165:
                v = rng.random()
                if v < 0.010: p[x, y] = (84, 86, 104, 255)
                elif v < 0.040: p[x, y] = (r - 22, g - 22, b - 18, 255)
            elif a and r > 190 and 120 < g < 215 and b < 90:      # yellow plates: orange speckle
                if rng.random() < 0.03: p[x, y] = (214, 130, 20, 255)
    return im
def seams(im):
    """dark pixel seam on the darker side of strong colour steps -> crisp panel lines like the reference"""
    p = im.load(); w, h = im.size; lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]; mark = []
    for y in range(h - 1):
        for x in range(w - 1):
            c = p[x, y]
            if not c[3]: continue
            for dx, dy in ((1, 0), (0, 1)):
                d = p[x + dx, y + dy]
                if d[3] and abs(lum(c) - lum(d)) > 52: mark.append((x, y) if lum(c) < lum(d) else (x + dx, y + dy))
    for x, y in mark: r, g, b, a = p[x, y]; p[x, y] = (int(r * 0.35), int(g * 0.35), int(b * 0.4), 255)
    return im
sprites = {}
for n in ('all', 'cabin', 'mid', 'eng'):
    rgb, a = px(raw[n], pal=pal) if n != 'all' else (rgb_all, a_all)
    sprites[n] = seams(scuff(outline(rgb, a)))
# engine centres: bright core blobs in the engine-only render
e = np.asarray(raw['eng']).astype(int); m = (e[..., 3] > 200) & (e[..., 2] > 225) & (e[..., 1] > 200) & (e[..., 0] > 150); lab, n = ndimage.label(m)
blobs = sorted([(ndimage.sum(m, lab, i), ndimage.center_of_mass(lab == i)) for i in range(1, n + 1)], reverse=True)[:2]
cen = [((c[1] - bbox[0]) * sc + 1, (c[0] - bbox[1]) * sc + 1, H * 0.085) for s_, c in blobs]
PADL = 120
def flames(base):
    cv = Image.new('RGBA', (base.width + PADL, base.height), (0, 0, 0, 0)); q = cv.load(); r2 = random.Random(5)
    cols = [(225, 245, 255), (140, 205, 255), (50, 125, 255), (26, 74, 224), (14, 40, 160)]
    for cx, cy, r in cen:
        cx += PADL; L = 110
        for x in range(max(0, int(cx) - L), int(cx)):
            t = min(1.0, max(0.0, (cx - x) / L)); hw = r * (1 - t) ** 0.7 + 1.0
            for y in range(int(cy - hw) - 1, int(cy + hw) + 2):
                d = abs(y - cy) / (hw + 1e-6)
                if d > 1 or not (0 <= y < cv.height): continue
                lev = d * 0.75 + t * 0.55 + r2.uniform(-0.12, 0.12); q[x, y] = cols[min(4, max(0, int(lev * 5)))] + (255,)
        for _ in range(130):
            t = r2.uniform(0.3, 1.3); x = int(cx - t * L); y = int(cy + r2.gauss(0, r * 0.5 * (1 - min(t, 1) * 0.45)))
            if 0 <= x < cv.width and 0 <= y < cv.height and q[x, y][3] == 0: q[x, y] = r2.choice(cols[2:]) + (255,)
    arr = np.asarray(cv).astype(float); yy, xx = np.mgrid[:cv.height, :cv.width]
    bay = np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0, (cv.height // 4 + 1, cv.width // 4 + 1))[:cv.height, :cv.width]
    for cx, cy, r in cen:
        d = np.sqrt((xx - cx - PADL + 26) ** 2 + ((yy - cy) * 1.25) ** 2) / (r * 3.4); k = np.clip(1 - d, 0, 1) ** 2; k = np.clip(np.floor(k * 3 + bay) / 3, 0, 1); em = (arr[..., 3] == 0) & (k > 0.34)
        arr[..., 0][em] = 22; arr[..., 1][em] = 78; arr[..., 2][em] = 255; arr[..., 3][em] = 255
    cv = Image.fromarray(arr.astype(np.uint8), 'RGBA'); cv.alpha_composite(base, (PADL, 0)); return cv
full = flames(sprites['all']); full.save(os.path.join(LIB, 'ship_hero.png'))
def show(im, k=4, bgc=(16, 16, 20)):
    b = Image.new('RGBA', (im.width + 30, im.height + 30), bgc + (255,)); b.alpha_composite(im, (15, 15)); return b.resize((b.width * k, b.height * k), Image.NEAREST).convert('RGB')
show(full).save(os.path.join(SC, 'ship_hero_preview.png'))
for n in ('cabin', 'mid', 'eng'):
    sp_ = sprites[n]; bb = sp_.getbbox(); show(sp_.crop(bb), 6).save(os.path.join(SC, f'ship_mod_{n}.png'))
print(full.size, sprites['all'].size)
