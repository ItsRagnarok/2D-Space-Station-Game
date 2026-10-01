"""S3 masters: the station seen from space (top-down hull modules, solar arrays, engines), star tile and a barren planet."""
import os
from core import *
from hydroponics import add_outline, RAMPS

HZ = lambda w, h: __import__('station_rooms').hazard_strip_img(w, h)

def plating(w, h, base=2):
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[base]); outline(im, 0, 0, w, h, STEEL[6])
    hline(im, 1, 1, w - 2, STEEL[7]); vline(im, 1, 1, h - 2, STEEL[5])
    hline(im, 1, h - 2, w - 2, STEEL[1]); vline(im, w - 2, 1, h - 2, STEEL[1])
    r = random.Random(w * 7 + h)
    for x in range(16, w - 8, 16): vline(im, x, 3, h - 6, STEEL[1]); vline(im, x + 1, 3, h - 6, STEEL[4])
    for y in range(16, h - 8, 16): hline(im, 3, y, w - 6, STEEL[1]); hline(im, 3, y + 1, w - 6, STEEL[4])
    for _ in range(w * h // 90): px(im, r.randint(3, w - 4), r.randint(3, h - 4), STEEL[1] if r.random() < .5 else STEEL[4])
    for (x, y) in ((3, 3), (w - 5, 3), (3, h - 5), (w - 5, h - 5)): rect(im, x, y, 2, 2, STEEL[8])
    return im

def window_strip(im, x, y, w, color, h=3):
    rect(im, x, y, w, h, color[1]); hline(im, x, y, w, color[3]); hline(im, x, y + h - 1, w, color[0])

def hull_command():
    w, h = 96, 84
    im = plating(w, h); d = ImageDraw.Draw(im)
    cut = 14
    for (x, y, dx, dy) in ((0, 0, 1, 1), (w - 1, 0, -1, 1), (0, h - 1, 1, -1), (w - 1, h - 1, -1, -1)):        # chamfer the corners (transparent)
        for i in range(cut):
            for j in range(cut - i):
                px(im, x + dx * i, y + dy * j, CLEAR)
    d.ellipse([22, 14, 73, 69], fill=STEEL[0], outline=STEEL[7]); d.ellipse([26, 18, 69, 65], fill=TEAL[0], outline=TEAL[3])
    for k in range(3):
        d.ellipse([30 + k * 4, 22 + k * 4, 65 - k * 4, 61 - k * 4], outline=TEAL[1 + k % 2])
    d.ellipse([40, 33, 55, 50], fill=TEAL[3]); d.ellipse([43, 36, 52, 46], fill=TEAL[4]); px(im, 46, 38, rgb('#ffffff'))
    for (x, y, ww, hh) in ((0, 34, 6, 16), (w - 6, 34, 6, 16), (34, 0, 28, 6), (34, h - 6, 28, 6)):                # docking collars
        rect(im, x, y, ww, hh, STEEL[4]); outline(im, x, y, ww, hh, STEEL[8]); rect(im, x + 1, y + 1, ww - 2, hh - 2, STEEL[1])
    window_strip(im, 14, h - 11, 20, TEAL); window_strip(im, 62, h - 11, 20, TEAL)
    return add_outline(im)

def hull_hydro():
    w, h = 128, 92
    im = plating(w, h)
    G = RAMPS['green']
    for r_ in range(2):
        for c in range(4):
            x, y = 8 + c * 29, 10 + r_ * 38
            rect(im, x, y, 24, 32, G[0]); outline(im, x, y, 24, 32, STEEL[7])
            for yy in range(y + 2, y + 30):
                for xx in range(x + 2, x + 22):
                    t = (yy - y) / 30
                    px(im, xx, yy, G[1] if t < .35 else G[0] if t < .7 else rgb('#07241a'))
            for (dx, dy, cc) in ((6, 22, 3), (12, 18, 2), (17, 24, 3), (9, 12, 3)):                                 # plant silhouettes
                rect(im, x + dx, y + dy, 3, 6, G[cc]); px(im, x + dx + 1, y + dy - 1, G[3])
            vline(im, x + 3, y + 3, 14, G[3])
    rect(im, 4, 4, w - 8, 4, STEEL[1]); [px(im, x, 5, G[3]) for x in range(8, w - 8, 12)]
    hline(im, 4, h - 8, w - 8, STEEL[1]); [px(im, x, h - 7, ORANGE[3]) for x in range(8, w - 8, 12)]
    return add_outline(im)

def hull_reactor():
    w, h = 104, 92
    im = plating(w, h); d = ImageDraw.Draw(im)
    cx, cy = 44, 46
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=STEEL[0], outline=STEEL[7])
    for i, (r, c) in enumerate(((27, ORANGE[0]), (22, ORANGE[1]), (17, ORANGE[2]), (12, ORANGE[3]), (7, ORANGE[4]), (3, ORANGE[5]))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    for a in range(0, 360, 30):
        x1, y1 = cx + 28 * math.cos(math.radians(a)), cy + 28 * math.sin(math.radians(a))
        px(im, int(x1), int(y1), ORANGE[4])
    for i in range(5):                                                                    # cooling fins on the right
        rect(im, 80, 8 + i * 16, 20, 10, STEEL[4]); hline(im, 80, 8 + i * 16, 20, STEEL[8]); [vline(im, 84 + k * 4, 9 + i * 16, 8, STEEL[1]) for k in range(4)]
    im.alpha_composite(HZ(w - 8, 3), (4, h - 7)); im.alpha_composite(HZ(w - 8, 3), (4, 4))
    return add_outline(im)

def mini_ship():
    w, h = 34, 30
    im = new(w, h); d = ImageDraw.Draw(im); cx = w // 2
    d.polygon([(cx, 1), (cx + 5, 10), (cx + 6, 24), (cx - 6, 24), (cx - 5, 10)], fill=STEEL[7])
    d.polygon([(cx - 2, 12), (2, 24), (cx - 6, 22)], fill=STEEL[6]); d.polygon([(cx + 2, 12), (w - 3, 24), (cx + 6, 22)], fill=STEEL[5])
    d.polygon([(cx, 4), (cx + 2, 9), (cx - 2, 9)], fill=BLUE[3]); rect(im, cx - 1, 25, 2, 3, BLUE[4])
    return im

def hull_hangar():
    w, h = 140, 84
    im = plating(w, h)
    bx, by, bw, bh = 28, 22, 84, 56
    rect(im, bx, by, bw, bh, STEEL[0]); outline(im, bx, by, bw, bh, STEEL[8]); outline(im, bx + 1, by + 1, bw - 2, bh - 2, STEEL[1])
    for x in range(bx + 4, bx + bw - 3, 8): vline(im, x, by + 3, bh - 6, STEEL[1])
    for y in range(by + 4, by + bh - 3, 8): hline(im, bx + 3, y, bw - 6, STEEL[1])
    d = ImageDraw.Draw(im); d.ellipse([bx + 22, by + 12, bx + bw - 22, by + bh - 6], outline=ORANGE[3])
    im.alpha_composite(mini_ship(), (bx + bw // 2 - 17, by + 14))
    for x in range(bx + 6, bx + bw - 4, 14): rect(im, x, by + bh - 4, 3, 2, ORANGE[4])
    im.alpha_composite(HZ(w - 8, 3), (4, 4))
    rect(im, 6, 8, 18, 10, STEEL[1]); outline(im, 6, 8, 18, 10, STEEL[6]); rect(im, 8, 10, 14, 6, BLUE[1]); hline(im, 8, 10, 14, BLUE[3])
    return add_outline(im)

def hull_lab():
    w, h = 96, 70
    im = plating(w, h, base=1)
    r = random.Random(5)
    for _ in range(5):                                           # missing plates (still under construction)
        x, y = r.randint(6, w - 30), r.randint(6, h - 24); rect(im, x, y, r.randint(14, 24), r.randint(10, 18), STEEL[0])
    for x in range(8, w - 8, 14):                                # scaffolding
        vline(im, x, 4, h - 8, ORANGE[2]); vline(im, x + 1, 4, h - 8, ORANGE[3])
    for y in (14, 30, 48): hline(im, 6, y, w - 12, ORANGE[2])
    [rect(im, x, 6, 3, 3, ORANGE[5]) for x in (10, 38, 66, 84)]
    return add_outline(im)

def solar_array(w=140, h=34):
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[1]); outline(im, 0, 0, w, h, STEEL[6])
    B = RAMPS['blue']
    for s in range(4):
        x0 = 3 + s * (w - 6) // 4
        rect(im, x0, 3, (w - 6) // 4 - 2, h - 6, B[1])
        for yy in range(3, h - 3, 6): hline(im, x0, yy, (w - 6) // 4 - 2, B[0])
        for xx in range(x0, x0 + (w - 6) // 4 - 2, 7): vline(im, xx, 3, h - 6, B[0])
        for yy in range(4, h - 4, 6): hline(im, x0 + 1, yy, 4, B[3]) if s % 2 == 0 else hline(im, x0 + 3, yy, 4, B[2])
    return add_outline(im)

def antenna():
    im = new(22, 22); d = ImageDraw.Draw(im)
    d.ellipse([2, 2, 19, 19], fill=STEEL[3], outline=STEEL[8]); d.ellipse([6, 6, 15, 15], fill=STEEL[1], outline=STEEL[6]); rect(im, 10, 10, 2, 2, ORANGE[4])
    return add_outline(im)

def engine(frame=0):
    w, h = 72, 44
    im = new(w, h); d = ImageDraw.Draw(im)
    fl = (26, 32, 38)[frame % 3]
    for i in range(fl):                                           # flame to the left
        t = i / fl; half = int(9 * (1 - t) + 1)
        c = BLUE[5] if t < .15 else BLUE[4] if t < .4 else BLUE[3] if t < .7 else BLUE[2]
        for y in range(h // 2 - half, h // 2 + half + 1): px(im, 42 - i, y, c)
    rect(im, 42, 8, 26, 28, STEEL[4]); hline(im, 42, 8, 26, STEEL[8]); hline(im, 42, 35, 26, STEEL[0])
    rect(im, 42, 12, 6, 20, STEEL[2]); rect(im, 46, 16, 3, 12, STEEL[0]); [vline(im, x, 9, 26, STEEL[1]) for x in (54, 60)]
    px(im, 64, 12, ORANGE[4]); px(im, 64, 30, ORANGE[4])
    return add_outline(im)

def conn(horizontal=True):
    w, h = (22, 18) if horizontal else (18, 22)
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[3]); outline(im, 0, 0, w, h, STEEL[7])
    for i in range(3, (w if horizontal else h) - 3, 5):
        (vline(im, i, 1, h - 2, STEEL[1]) if horizontal else hline(im, 1, i, w - 2, STEEL[1]))
    (rect(im, 8, 7, 6, 4, TEAL[2]) if horizontal else rect(im, 7, 8, 4, 6, TEAL[2]))
    return im

def stars_tile(S=256):
    im = new(S, S, rgb('#02040a')); r = random.Random(42)
    for i in range(70):
        x, y = r.randint(0, S - 1), r.randint(0, S - 1)
        c = [rgb('#2a3050'), rgb('#4a5278'), rgb('#8a92b8'), rgb('#e8ecff')][min(3, int(r.random() ** 2.2 * 4))]
        px(im, x, y, c)
        if r.random() < .12: [px(im, x + dx, y + dy, rgb('#4a5278')) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    return im

def planet(S=220):
    im = new(S, S); c = S / 2; R = S / 2 - 3
    cols = [rgb(x) for x in ('#0a0806', '#1c1612', '#2e251c', '#44382a', '#5e4f3a', '#7a6a50')]
    r = random.Random(9); craters = [(r.uniform(-.7, .7), r.uniform(-.7, .7), r.uniform(.05, .16)) for _ in range(14)]
    for y in range(S):
        for x in range(S):
            nx, ny = (x - c) / R, (y - c) / R; d2 = nx * nx + ny * ny
            if d2 > 1: continue
            nz = math.sqrt(1 - d2); light = max(0, -.62 * nx - .5 * ny + .6 * nz)
            lvl = light * 1.1 + (bay(x, y) - .5) * .35
            for (cx_, cy_, cr) in craters:
                dd = math.hypot(nx - cx_, ny - cy_)
                if dd < cr: lvl -= .22 if dd > cr * .55 else -.05
                elif dd < cr * 1.25: lvl += .1
            im.putpixel((x, y), cols[max(0, min(5, int(lvl * 6)))])
    for y in range(S):                                           # thin blue rim: the only hint of an atmosphere
        for x in range(S):
            d = math.hypot(x - c, y - c)
            if R - .5 < d < R + 1.5 and x < c + R * .3: im.putpixel((x, y), BLUE[1] if (x + y) % 2 else BLUE[2])
    return im

def all_sprites():
    out = {'hull_command': hull_command(), 'hull_hydro': hull_hydro(), 'hull_reactor': hull_reactor(), 'hull_hangar': hull_hangar(), 'hull_lab': hull_lab(),
           'solar_array': solar_array(), 'antenna': antenna(), 'conn_h': conn(True), 'conn_v': conn(False)}
    for f in range(3): out[f'engine_{f}'] = engine(f)
    return out

if __name__ == '__main__':
    sp = all_sprites(); k = 3; pad = 8; maxw = 1500
    pick = [sp[n] for n in ('hull_command', 'hull_hydro', 'hull_reactor', 'hull_hangar', 'hull_lab', 'solar_array', 'antenna', 'engine_1', 'conn_h', 'conn_v')]
    sheet = new(maxw, 900, (30, 34, 46, 255)); x = y = pad; rowh = 0
    for im in pick:
        w, h = im.width * k, im.height * k
        if x + w > maxw - pad: x = pad; y += rowh + pad; rowh = 0
        sheet.alpha_composite(upscale(im, k), (x, y)); x += w + pad; rowh = max(rowh, h)
    sheet.crop((0, 0, maxw, y + rowh + pad)).convert('RGB').save('../out/exterior_sheet.png'); print(len(sp), 'sprites')
