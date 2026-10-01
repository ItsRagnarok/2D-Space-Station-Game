"""Separate sprite builders for the research module. Every function returns an RGBA image."""
from core import *

# ---------------- generator (octagonal holo-table machine) ----------------
def octagon(cx, cy, rx, ry, cxm, cym):
    return [(cx - rx + cxm, cy - ry), (cx + rx - cxm, cy - ry), (cx + rx, cy - ry + cym), (cx + rx, cy + ry - cym),
            (cx + rx - cxm, cy + ry), (cx - rx + cxm, cy + ry), (cx - rx, cy + ry - cym), (cx - rx, cy - ry + cym)]

def generator(phase=0.0):
    W, H = 66, 54
    im = new(W, H)
    d = ImageDraw.Draw(im)
    cx, cy = 33, 24
    # front thickness (3/4 view: we see the machine's side below the top face)
    d.polygon(octagon(cx, cy + 9, 31, 20, 10, 8), fill=STEEL[0])
    d.polygon(octagon(cx, cy + 7, 31, 20, 10, 8), fill=STEEL[2])
    d.polygon(octagon(cx, cy + 7, 30, 19, 10, 8), outline=STEEL[3])
    # side plates + warm vent on the front
    for x0 in (10, 26, 42):
        rect(im, x0, 45, 12, 5, STEEL[1]); hline(im, x0, 45, 12, STEEL[4])
        hline(im, x0 + 2, 47, 8, ORANGE[2] if x0 == 26 else STEEL[0])
        if x0 == 26: hline(im, x0 + 2, 48, 8, ORANGE[3])
    # top face
    d.polygon(octagon(cx, cy, 31, 20, 10, 8), fill=STEEL[0])
    d.polygon(octagon(cx, cy, 30, 19, 10, 8), fill=STEEL[4])
    d.polygon(octagon(cx, cy, 28, 17, 9, 7), fill=STEEL[3])
    # rim segments
    for (x, y, w, h) in ((14, 5, 12, 3), (40, 5, 12, 3), (3, 19, 4, 10), (59, 19, 4, 10), (14, 40, 12, 3), (40, 40, 12, 3)):
        rect(im, x, y, w, h, STEEL[7]); hline(im, x, y, w, STEEL[8]); hline(im, x, y + h - 1, w, STEEL[5])
    # glowing teal ring (pulses)
    k = 0.5 + 0.5 * math.sin(phase * 2 * math.pi)
    ring_c = TEAL[3] if k > .45 else TEAL[2]
    d.polygon(octagon(cx, cy, 24, 14, 8, 5), fill=ring_c)
    d.polygon(octagon(cx, cy, 22, 12, 7, 4), fill=TEAL[1])
    d.polygon(octagon(cx, cy, 20, 10, 6, 3), fill=TEAL[0])
    for x in range(14, 53, 4):
        px(im, x, 11 + (0 if x < 33 else 0), TEAL[4]); px(im, x, 36, TEAL[4])
    # centre: dark well with a small floating green hologram
    d.ellipse([22, 16, 44, 32], fill=STEEL[0])
    d.ellipse([24, 17, 42, 30], fill=TEAL[0])
    gk = GREEN[3] if k > .5 else GREEN[2]
    for (x, y) in ((33, 19), (31, 21), (35, 21), (30, 23), (36, 23), (32, 25), (34, 25), (33, 27)):
        px(im, x, y, gk)
    px(im, 33, 23, GREEN[3]); px(im, 33, 22, GREEN[3]); px(im, 33, 24, GREEN[3])
    # orange status lights
    for (x, y) in ((8, 14), (57, 14), (8, 35), (57, 35)):
        px(im, x, y, ORANGE[4]); px(im, x + 1, y, ORANGE[3])
    return im

# ---------------- hologram globe + pedestal ----------------
def land(lon, lat):
    # fragmented, earth-like continents: low-frequency masses + coastline detail
    v = (math.sin(1.7 * lon + .4) * math.cos(1.3 * lat + .2) * 1.6
         + math.sin(3.1 * lon - 1.2 * lat + 2.0) * .8
         + math.sin(5.3 * lon + 2.1 * lat) * .35
         + math.cos(4.2 * lat - 1.1 * lon) * .45)
    return v > 0.75 and abs(lat) < 1.25

def globe(angle=0.0, R=17):
    S = R * 2 + 3
    im = new(S, S)
    c = S // 2
    def is_land(x, y):
        nx, ny = (x - c) / R, (y - c) / R
        d2 = nx * nx + ny * ny
        if d2 > 1: return False
        return land(math.atan2(nx, math.sqrt(1 - d2)) + angle, math.asin(-ny))
    for y in range(S):
        for x in range(S):
            nx, ny = (x - c) / R, (y - c) / R
            d2 = nx * nx + ny * ny
            if d2 > 1:
                continue
            nz = math.sqrt(1 - d2)
            light = max(0.0, -0.55 * nx - 0.5 * ny + 0.65 * nz)
            lvl = light + (bay(x, y) - .5) * .30
            ld = is_land(x, y)
            if ld:
                coast = not (is_land(x - 1, y) and is_land(x + 1, y) and is_land(x, y - 1) and is_land(x, y + 1))
                col = BLUE[5] if coast else (BLUE[4] if lvl > .38 else BLUE[3])
            else:
                col = BLUE[3] if lvl > .72 else BLUE[2] if lvl > .38 else BLUE[1]
            if d2 > .80: col = BLUE[4] if not ld else BLUE[5]       # bright limb
            if y % 3 == 0 and d2 < .80: col = lerp(col, BLUE[0], .30)  # hologram scanlines
            im.putpixel((x, y), col)
    return im

def pedestal(phase=0.0):
    im = new(18, 20)
    rect(im, 3, 12, 12, 7, STEEL[3]); hline(im, 3, 12, 12, STEEL[6]); hline(im, 3, 18, 12, STEEL[0])
    rect(im, 5, 8, 8, 5, STEEL[4]); hline(im, 5, 8, 8, STEEL[7])
    rect(im, 4, 14, 10, 1, STEEL[1]); rect(im, 4, 16, 10, 1, STEEL[1])
    k = 0.5 + 0.5 * math.sin(phase * 2 * math.pi)
    rect(im, 6, 5, 6, 3, BLUE[3] if k > .4 else BLUE[2]); hline(im, 7, 5, 4, BLUE[5])
    px(im, 4, 13, ORANGE[4]); px(im, 13, 13, ORANGE[4])
    return im

# ---------------- astronauts ----------------
SCHEMES = {
    'white': dict(W='#e8edf3', L='#ffffff', S='#97a3b8', A='#e8902a', P='#bcc6d6', p='#8794ac', B='#4e5562', G='#c8d0de'),
    'yellow': dict(W='#f0c030', L='#ffe27a', S='#b88a14', A='#6a3a0a', P='#2f5f8f', p='#1f3f66', B='#2e333d', G='#e8b890'),
    'green': dict(W='#38c068', L='#86f0a8', S='#1f7a42', A='#e8f6ff', P='#3a5a8a', p='#223a5e', B='#2e333d', G='#e8b890'),
}
BASE = [
"....OOOO....",
"..OOLLLWOO..",
".OLLWWWWWSO.",
".OLWVVVVVSO.",
"OLWVvvVVVVSO",
"OLWVVVVVVVSO",
".OWVVVVVVSO.",
".OWWSSSSSSO.",
"..OOWWWWOO..",
".OAAWWWWAAO.",
"OWOWWAAWWOSO",
"OWOWWAAWWOSO",
"OWOSWWWWSOSO",
"OGOSWWWWSOGO",
".OOPPPPPPOO.",
"..OPPOOPPO..",
"..OPPOOPPO..",
"..OPPOOPPO..",
"..OPpOOpPO..",
"..OBBOOBBO..",
"..OBBOOBBO..",
"..OOO..OOO..",
]

def astronaut(scheme='white', pose='idle', frame=0):
    pal = {k: rgb(v) for k, v in SCHEMES[scheme].items()}
    pal.update(O=STEEL[0], V=rgb('#10243a'), v=BLUE[3], )
    rows = [list(r.ljust(12, '.')) for r in BASE]
    W = 16
    canvas = [['.'] * W for _ in range(len(rows))]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            canvas[y][x + 2] = ch
    if pose == 'point':          # right arm out to the side
        for y in (9, 10, 11): canvas[y][13] = '.'; canvas[y][14] = '.'
        for x, ch in zip(range(13, 16), 'OWG'): canvas[9][x] = ch
        canvas[10][12] = 'W'; canvas[10][13] = 'W'; canvas[10][14] = 'G'
        canvas[11][13] = 'O'
        for y in (11, 12, 13): canvas[y][12] = 'O'
    if pose == 'work':           # arms bent forward toward a console, hands alternate (typing)
        for y in (10, 11, 12, 13):
            for x in (2, 3, 12, 13): canvas[y][x] = '.'
        canvas[10][3] = 'O'; canvas[10][12] = 'O'
        for y, x in ((11, 4), (12, 4), (11, 11), (12, 11)): canvas[y][x] = 'O'
        for y, x in ((11, 5), (11, 10)): canvas[y][x] = 'W'
        canvas[13][5] = 'G'; canvas[13][6] = 'G'
        canvas[13 if frame % 2 == 0 else 12][9] = 'G'; canvas[13 if frame % 2 == 0 else 12][10] = 'G'
    im = ascii_sprite(["".join(r) for r in canvas], pal)
    if frame % 2 == 1 and pose == 'idle':     # breathing: the head dips a pixel
        top = im.crop((0, 0, im.width, 9)); body = im.crop((0, 9, im.width, im.height))
        out = new(im.width, im.height)
        out.alpha_composite(top, (0, 1)); out.alpha_composite(body, (0, 9))
        return out
    return im

# ---------------- furniture ----------------
def console(frame=0, w=44):
    h = 28
    im = new(w, h)
    # raised back monitor
    rect(im, 3, 0, w - 6, 11, STEEL[1]); frame_c = STEEL[6]
    outline(im, 3, 0, w - 6, 11, frame_c)
    rect(im, 5, 2, w - 10, 7, TEAL[0])
    for i, x in enumerate(range(6, w - 6, 3)):
        hh = 1 + int(3 + 3 * math.sin(i * .9 + frame * .8)) % 5
        rect(im, x, 8 - hh, 2, hh, TEAL[3] if i % 4 else TEAL[4])
    # desk top (lighter, seen from above)
    rect(im, 0, 11, w, 6, STEEL[5]); hline(im, 0, 11, w, STEEL[8]); hline(im, 0, 16, w, STEEL[2])
    for x in range(3, w - 3, 4):
        px(im, x, 13, STEEL[2]); px(im, x + 1, 13, STEEL[7]); px(im, x, 14, STEEL[2]); px(im, x + 1, 14, STEEL[3])
    # front face
    rect(im, 0, 17, w, 11, STEEL[3]); hline(im, 0, 17, w, STEEL[6]); hline(im, 0, 27, w, STEEL[0])
    vline(im, 0, 17, 11, STEEL[1]); vline(im, w - 1, 17, 11, STEEL[1])
    rect(im, 3, 19, w // 2 - 5, 6, TEAL[0]); outline(im, 3, 19, w // 2 - 5, 6, STEEL[7])
    rect(im, w // 2 + 2, 19, w // 2 - 5, 6, GREEN[0]); outline(im, w // 2 + 2, 19, w // 2 - 5, 6, STEEL[7])
    for i in range(4):
        hline(im, 5, 20 + i + (frame + i) % 2, 6 + (i * 3 + frame) % 6, TEAL[3])
    for i in range(3):
        hline(im, w // 2 + 4, 20 + i * 2, 5 + (frame + i * 2) % 7, GREEN[3])
    px(im, w - 5, 21, ORANGE[4]); px(im, w - 5, 23, GREEN[3] if frame % 2 else RED[2])
    return im

def bench(frame=0):
    w, h = 40, 26
    im = new(w, h)
    rect(im, 0, 10, w, 6, STEEL[6]); hline(im, 0, 10, w, STEEL[8]); hline(im, 0, 15, w, STEEL[3])
    rect(im, 0, 16, w, 10, STEEL[3]); hline(im, 0, 16, w, STEEL[5]); hline(im, 0, 25, w, STEEL[0])
    rect(im, 2, 18, 12, 6, STEEL[1]); frame_c = STEEL[5]; outline(im, 2, 18, 12, 6, frame_c)
    rect(im, 17, 18, 12, 6, STEEL[1]); outline(im, 17, 18, 12, 6, STEEL[5])
    px(im, 30, 20, ORANGE[4]); px(im, 30, 22, GREEN[3])
    # microscope
    rect(im, 4, 5, 4, 6, STEEL[7]); rect(im, 3, 9, 8, 2, STEEL[4]); rect(im, 6, 2, 3, 4, STEEL[5]); px(im, 7, 1, TEAL[4])
    # flasks
    for (x, col) in ((16, GREEN[3]), (22, BLUE[4]), (28, ORANGE[4])):
        rect(im, x, 4, 5, 7, lerp(col, (0, 0, 0, 255), .45)); rect(im, x + 1, 6, 3, 4, col)
        rect(im, x + 1, 2, 3, 3, STEEL[6]); px(im, x + 1, 7, BLUE[5])
    if frame % 2: px(im, 19, 3, GREEN[3])
    return im

def rack(frame=0):
    w, h = 18, 34
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[2]); outline(im, 0, 0, w, h, STEEL[6]); hline(im, 0, h - 1, w, STEEL[0])
    for i, y in enumerate(range(3, h - 4, 5)):
        rect(im, 2, y, w - 4, 4, STEEL[0]); hline(im, 2, y, w - 4, STEEL[4])
        for j in range(4):
            on = (frame + i + j) % 3
            px(im, 4 + j * 3, y + 2, [GREEN[3], TEAL[4], ORANGE[4]][on] if (i + j) % 2 == 0 else STEEL[3])
    return im

def locker(frame=0):
    w, h = 14, 40
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[2]); outline(im, 0, 0, w, h, STEEL[6]); hline(im, 0, h - 1, w, STEEL[0])
    rect(im, 2, 3, w - 4, h - 7, ORANGE[0]); outline(im, 2, 3, w - 4, h - 7, ORANGE[2])
    for y in range(6, h - 6, 3):
        hline(im, 4, y, w - 8, ORANGE[3] if (y // 3 + frame) % 5 else ORANGE[4])
    rect(im, w - 5, 18, 2, 6, STEEL[7])
    return im

def pipes_v(h=100):
    w = 12
    im = new(w, h)
    for x0 in (1, 7):
        rect(im, x0, 0, 4, h, ORANGE[2]); vline(im, x0, 0, h, ORANGE[4]); vline(im, x0 + 3, 0, h, ORANGE[0])
    for y in range(8, h, 22):
        rect(im, 0, y, w, 4, STEEL[4]); hline(im, 0, y, w, STEEL[7]); hline(im, 0, y + 3, w, STEEL[0])
        px(im, 5, y + 1, TEAL[4])
    return im

def crate(kind='steel'):
    w, h = 16, 14
    im = new(w, h)
    top = STEEL[6] if kind == 'steel' else ORANGE[3]; side = STEEL[3] if kind == 'steel' else ORANGE[1]
    rect(im, 0, 0, w, 5, top); hline(im, 0, 0, w, STEEL[8] if kind == 'steel' else ORANGE[5])
    rect(im, 0, 5, w, 9, side); hline(im, 0, 13, w, STEEL[0]); vline(im, 0, 5, 9, STEEL[1]); vline(im, w - 1, 5, 9, STEEL[1])
    hline(im, 1, 8, w - 2, ORANGE[3]); hline(im, 1, 9, w - 2, ORANGE[2])
    px(im, 2, 11, STEEL[7]); px(im, w - 3, 11, STEEL[7])
    return im

def plant_jar(frame=0):
    w, h = 14, 22
    im = new(w, h)
    rect(im, 1, 4, 12, 17, TEAL[0]); outline(im, 1, 4, 12, 17, TEAL[3])
    rect(im, 0, 2, 14, 3, STEEL[6]); rect(im, 0, 19, 14, 3, STEEL[3]); hline(im, 0, 21, 14, STEEL[0])
    sway = 1 if frame % 2 else 0
    for (x, y, c) in ((7, 17, GREEN[2]), (7, 15, GREEN[2]), (7, 13, GREEN[3]), (6 + sway, 11, GREEN[3]), (5 + sway, 9, GREEN[3]), (8 - sway, 10, GREEN[3]), (9 - sway, 8, GREEN[3])):
        px(im, x, y, c)
    px(im, 7, 7, ORANGE[4]); px(im, 7, 6, ORANGE[5])
    return im

def drone(frame=0):
    w, h = 14, 10
    im = new(w, h)
    rect(im, 3, 3, 8, 5, STEEL[6]); hline(im, 3, 3, 8, STEEL[8]); hline(im, 3, 7, 8, STEEL[3])
    rect(im, 5, 4, 4, 2, TEAL[0]); px(im, 6 if frame % 2 else 7, 4, TEAL[4]); px(im, 7, 5, TEAL[3])
    hline(im, 0 if frame % 2 else 1, 2, 5, STEEL[7]); hline(im, 9 if frame % 2 else 8, 2, 5, STEEL[7])
    px(im, 3, 2, STEEL[3]); px(im, 10, 2, STEEL[3])
    return im
