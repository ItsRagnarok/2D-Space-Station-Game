"""Hydroponics masters: faceted crystals, alien plants/mushrooms, growth stages, glass incubators, bio-generator.
One master per kind; colour variants come from RAMPS (palette swap), animation from per-frame offsets."""
from core import *

RAMPS = {k: [rgb(c) for c in v] for k, v in {
    'blue':   ['#0b1a5a', '#1c46c8', '#3a86ff', '#8fd0ff', '#eaf8ff'],
    'purple': ['#2a0b5a', '#6a2cc8', '#a45cff', '#d6a8ff', '#f6eaff'],
    'amber':  ['#5a2a05', '#c8650f', '#ff9a2a', '#ffd070', '#fff4d0'],
    'green':  ['#0e3a22', '#1f8a4a', '#3ed06a', '#9af5b4', '#eafff0'],
    'pink':   ['#4a0c3a', '#a02070', '#e04aa0', '#ff9ad0', '#ffeaf6'],
    'lime':   ['#1a3a05', '#3a8a0f', '#7ad020', '#c8f55a', '#f4ffc8'],
}.items()}
OUT = STEEL[0]

def add_outline(im, color=OUT):
    out = im.copy(); w, h = im.size
    for y in range(h):
        for x in range(w):
            if im.getpixel((x, y))[3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and im.getpixel((nx, ny))[3] > 0:
                        out.putpixel((x, y), color); break
    return out

# ---------------- crystals ----------------
def shaft(im, cx, base, w, h, lean, R):
    """One faceted hexagonal prism with a pointed tip: light left facet, mid centre, dark right facet."""
    tip = max(3, int(w * 1.1))
    for y in range(h):
        yy = base - y
        t = y / max(1, h - 1)
        shift = int(round(lean * t))
        width = w if y < h - tip else max(1, int(w * (h - y) / tip + .5))
        x0 = cx - width // 2 + shift
        for i in range(width):
            third = i * 3 // max(1, width)
            col = R[3] if third == 0 else R[2] if third == 1 else R[1]
            if i == 0: col = R[4] if y > 2 else R[3]
            if i == width - 1: col = R[0]
            px(im, x0 + i, yy, col)
        if width >= 3 and 3 < y < h - tip - 1 and y % 5 in (0, 1):   # facet edge glints
            px(im, x0 + width // 3, yy, R[4])
    px(im, cx + int(round(lean)), base - h + 1, R[4])

def crystal(stage, ramp='blue', frame=0):
    R = RAMPS[ramp]
    im = new(28, 34)
    base = 30
    spec = {1: [(14, 4, 7, 0)],
            2: [(10, 4, 11, -1), (17, 4, 14, 1), (14, 5, 9, 0)],
            3: [(7, 5, 14, -2), (21, 5, 15, 2), (11, 6, 20, -1), (17, 6, 18, 1), (14, 7, 25, 0)]}[stage]
    for (cx, w, h, lean) in sorted(spec, key=lambda s: s[2]):
        shaft(im, cx, base, w, h, lean, R)
    # base rocks
    for x in range(5, 24):
        px(im, x, base + 1, STEEL[2]); px(im, x, base + 2, STEEL[1]) if 7 < x < 21 else None
    im = add_outline(im)
    if stage == 3:                       # glow pulse + sparkle
        sx, sy = [(15, 6), (10, 12), (19, 10), (14, 3)][frame % 4]
        for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            px(im, sx + dx, sy + dy, R[4])
    return im

# ---------------- alien plants ----------------
def flora(stage, ramp='green', frame=0):
    R = RAMPS[ramp]; bloom = RAMPS['pink']
    im = new(28, 34); d = ImageDraw.Draw(im)
    sway = 1 if frame % 2 else 0
    base = 30
    h = {1: 7, 2: 14, 3: 20}[stage]
    for y in range(h):
        px(im, 14 + (sway if y > h // 2 else 0), base - y, R[1]); px(im, 15 + (sway if y > h // 2 else 0), base - y, R[2])
    n = {1: 2, 2: 4, 3: 6}[stage]
    for i in range(n):
        y = base - 4 - i * (h // max(2, n))
        side = -1 if i % 2 == 0 else 1
        L = 2 + stage
        d.ellipse([14 + side * L - 3 + sway, y - 2, 14 + side * L + 3 + sway, y + 2], fill=R[2])
        px(im, 14 + side * L + sway, y - 1, R[4]); px(im, 14 + side * (L - 2) + sway, y, R[1])
    if stage == 3:
        cx, cy = 14 + sway, base - h - 1
        for (dx, dy) in ((0, -4), (4, -1), (-4, -1), (2, 3), (-2, 3)):
            d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2], fill=bloom[2])
            px(im, cx + dx, cy + dy - 1, bloom[4])
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RAMPS['amber'][3]); px(im, cx, cy - 1, RAMPS['amber'][4])
        if frame % 2: px(im, cx + 6, cy - 7, bloom[4]); px(im, cx - 7, cy - 5, bloom[3])
    return add_outline(im)

def mushroom(stage, ramp='purple', frame=0):
    R = RAMPS[ramp]; G = RAMPS['green']
    im = new(28, 34); d = ImageDraw.Draw(im)
    caps = {1: [(14, 26, 4)], 2: [(14, 24, 7), (7, 28, 4)], 3: [(14, 20, 10), (6, 26, 6), (22, 27, 5)]}[stage]
    for (cx, cy, r) in caps:
        d.rectangle([cx - 1, cy, cx + 1, 30], fill=rgb('#d8d0e8')); px(im, cx - 1, cy + 1, STEEL[8])
        d.pieslice([cx - r, cy - r + 1, cx + r, cy + r + 1], 180, 360, fill=R[2])
        d.pieslice([cx - r + 1, cy - r + 2, cx + r - 3, cy + r - 1], 180, 360, fill=R[3])
        d.line([cx - r, cy + 1, cx + r, cy + 1], fill=R[0])
        for (sx, sy) in ((-r // 2, -r // 2), (r // 3, -r // 3), (r // 2 + 1, -1)):
            if r >= 5: px(im, cx + sx, cy + sy, G[4] if (frame + sx) % 2 else G[3])
    if stage == 3:
        for (x, y) in [(10, 8), (18, 6), (14, 3)]:
            px(im, x + (frame % 2), y - (frame % 2), G[4])
    return add_outline(im)

TYPES = {'crystal': lambda s, f: crystal(s, 'blue', f), 'rare': lambda s, f: crystal(s, 'amber', f),
         'flora': lambda s, f: flora(s, 'green', f), 'mush': lambda s, f: mushroom(s, 'purple', f)}

# ---------------- planting bed ----------------
def bed(frame=0):
    w, h = 56, 32
    im = new(w, h)
    rect(im, 0, 0, w, 26, STEEL[5]); hline(im, 0, 0, w, STEEL[8])
    rect(im, 3, 4, w - 6, 18, rgb('#1c1226'))
    r = random.Random(3)
    for _ in range(46): px(im, r.randint(4, w - 5), r.randint(5, 21), rgb('#2e1c3e') if r.random() < .6 else rgb('#3e2a52'))
    outline(im, 3, 4, w - 6, 18, STEEL[1])
    rect(im, 0, 26, w, 6, STEEL[3]); hline(im, 0, 26, w, STEEL[6]); hline(im, 0, 31, w, STEEL[0])
    for x in (4, 20, 36, 50): rect(im, x, 28, 3, 2, ORANGE[3] if (x // 4 + frame) % 3 else ORANGE[4])
    for x in range(8, 48, 6): px(im, x, 2, TEAL[3])        # irrigation nozzles
    return add_outline(im)

# ---------------- glass incubators ----------------
def incubator(kind='plant', frame=0):
    w, h = 24, 48
    im = new(w, h)
    liq = {'plant': RAMPS['green'], 'crystal': RAMPS['blue'], 'jelly': RAMPS['purple']}[kind]
    # caps
    rect(im, 2, 0, w - 4, 6, STEEL[4]); hline(im, 2, 0, w - 4, STEEL[8]); hline(im, 2, 5, w - 4, STEEL[1])
    rect(im, 2, 42, w - 4, 6, STEEL[3]); hline(im, 2, 42, w - 4, STEEL[6]); hline(im, 2, 47, w - 4, STEEL[0])
    px(im, 5, 44, ORANGE[4]); px(im, w - 6, 44, liq[3]); rect(im, 9, 44, 6, 2, STEEL[1])
    # glass + liquid in 3 bands
    for y in range(6, 42):
        band = liq[2] if y < 18 else liq[1] if y < 32 else liq[0]
        for x in range(3, w - 3):
            px(im, x, y, band)
        px(im, 2, y, TEAL[3]); px(im, w - 3, y, TEAL[1])
    for y in range(8, 30): px(im, 4, y, rgb('#ffffff') if y % 7 else TEAL[4])          # reflection
    for y in range(8, 14): px(im, 6, y, TEAL[4])
    # bubbles rise with the frame
    for i, bx in enumerate((8, 14, 18)):
        by = 38 - ((frame * 3 + i * 9) % 32)
        px(im, bx, by, liq[4]); px(im, bx, by - 1, liq[3]) if i == 1 else None
    # content
    cx = w // 2
    if kind == 'plant':
        for y in range(26, 40): px(im, cx, y, RAMPS['green'][3])
        for (dx, dy) in ((-3, 30), (3, 27), (-4, 34), (4, 33)):
            ImageDraw.Draw(im).ellipse([cx + dx - 2, dy - 1, cx + dx + 2, dy + 1], fill=RAMPS['green'][4])
    elif kind == 'crystal':
        bob = (0, -1, 0, 1)[frame % 4]
        c = crystal(2, 'blue', 0).crop((6, 12, 24, 33)); im.alpha_composite(c, (3, 16 + bob))
    else:
        bob = (0, 1, 0, -1)[frame % 4]
        d = ImageDraw.Draw(im); y0 = 18 + bob
        d.pieslice([cx - 5, y0, cx + 5, y0 + 10], 180, 360, fill=liq[4]); d.pieslice([cx - 4, y0 + 1, cx + 3, y0 + 8], 180, 360, fill=liq[3])
        px(im, cx - 2, y0 + 3, OUT); px(im, cx + 2, y0 + 3, OUT)
        for k, tx in enumerate((cx - 3, cx, cx + 3)):
            for j in range(4 + (k + frame) % 3): px(im, tx + (1 if (j + frame + k) % 4 == 0 else 0), y0 + 5 + j, liq[3])
    return im

# ---------------- bio-generator ----------------
def bio_generator(frame=0, charge=1.0):
    w, h = 56, 64
    im = new(w, h); L = RAMPS['lime']
    # glass cylinder with swirling lime liquid
    cx0, cx1, y0, y1 = 14, 42, 6, 40
    for y in range(y0, y1):
        band = L[3] if y < y0 + 8 else L[2] if y < y0 + 20 else L[1]
        for x in range(cx0, cx1): px(im, x, y, band)
        px(im, cx0 - 1, y, TEAL[3]); px(im, cx1, y, TEAL[1])
    d = ImageDraw.Draw(im)
    d.ellipse([cx0 - 1, y0 - 3, cx1, y0 + 3], fill=L[4], outline=TEAL[3])
    for y in range(y0 + 2, y1 - 2, 6): px(im, cx0 + 2, y, rgb('#ffffff'))
    for i in range(7):                   # swirling particles
        ang = (frame * math.pi / 2) + i * 0.9
        px(im, int(28 + 9 * math.cos(ang) * (0.5 + i / 14)), int(y0 + 10 + i * 3.4 + 2 * math.sin(ang)), L[4])
    core = L[4] if frame % 2 == 0 else L[3]
    d.ellipse([24, 20, 32, 28], fill=core); px(im, 27, 22, rgb('#ffffff'))
    # caps + chimney lamp
    rect(im, 11, 2, 34, 5, STEEL[5]); hline(im, 11, 2, 34, STEEL[8]); hline(im, 11, 6, 34, STEEL[1])
    rect(im, 24, 0, 8, 3, STEEL[4]); px(im, 27, 0, ORANGE[4] if frame % 2 else ORANGE[3]); px(im, 28, 0, ORANGE[4] if frame % 2 else ORANGE[3])
    rect(im, 11, 40, 34, 4, STEEL[5]); hline(im, 11, 40, 34, STEEL[8])
    # machine base
    rect(im, 2, 44, w - 4, 20, STEEL[3]); hline(im, 2, 44, w - 4, STEEL[7]); hline(im, 2, 63, w - 4, STEEL[0])
    vline(im, 2, 44, 20, STEEL[1]); vline(im, w - 3, 44, 20, STEEL[1])
    for (gx, ph) in ((12, 0), (44, 2)):    # gauges with needles
        d.ellipse([gx - 5, 48, gx + 5, 58], fill=STEEL[0], outline=STEEL[7])
        a = -2.4 + (charge * 1.6) + 0.1 * math.sin(frame + ph)
        d.line([gx, 53, gx + int(4 * math.cos(a)), 53 + int(4 * math.sin(a))], fill=ORANGE[4])
    for i in range(4): rect(im, 20 + i * 4, 50, 3, 8, STEEL[0]); px(im, 21 + i * 4, 51 + (i + frame) % 5, ORANGE[3])
    px(im, 4, 46, GREEN[3] if charge > .3 else RED[2]); px(im, 51, 46, ORANGE[4])
    # side pipes
    for x0 in (0, 52):
        rect(im, x0, 24, 4, 24, STEEL[4]); vline(im, x0, 24, 24, STEEL[7]); rect(im, x0, 36, 4, 3, ORANGE[3])
    return im

def sparkle(frame=0):
    im = new(7, 7)
    c = [rgb('#ffffff'), rgb('#bfe8ff')][frame % 2]
    for (x, y) in ((3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3)):
        if frame % 2 == 0 or (x, y) in ((3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (1, 3), (2, 3), (4, 3), (5, 3)):
            px(im, x, y, c)
    return im

def all_sprites():
    out = {}
    for t, f in TYPES.items():
        for s in (1, 2, 3):
            for fr in (0, 1):
                out[f'plant_{t}_{s}_{fr}'] = f(s, fr)
    for fr in range(4):
        for kind in ('plant', 'crystal', 'jelly'):
            out[f'incubator_{kind}_{fr}'] = incubator(kind, fr)
        out[f'biogen_{fr}'] = bio_generator(fr)
    for fr in range(2):
        out[f'bed_{fr}'] = bed(fr); out[f'sparkle_{fr}'] = sparkle(fr)
    return out

if __name__ == '__main__':
    sp = all_sprites()
    names = [n for n in sp if n.endswith(('_0',)) or 'plant_' in n and n.endswith('_0')]
    pick = [sp[f'plant_{t}_{s}_0'] for t in TYPES for s in (1, 2, 3)] + [sp[f'plant_{t}_3_1'] for t in TYPES]
    pick += [sp['bed_0'], sp['incubator_plant_0'], sp['incubator_crystal_1'], sp['incubator_jelly_2'], sp['biogen_0'], sp['biogen_2']]
    k = 5; pad = 8; maxw = 1480
    sheet = new(maxw, 900, (30, 34, 46, 255)); x = y = pad; rowh = 0
    for im in pick:
        w, h = im.width * k, im.height * k
        if x + w > maxw - pad: x = pad; y += rowh + pad; rowh = 0
        sheet.alpha_composite(upscale(im, k), (x, y)); x += w + pad; rowh = max(rowh, h)
    sheet.crop((0, 0, maxw, y + rowh + pad)).convert('RGB').save('../out/hydro_sheet.png'); print(len(sp), 'sprites')
