"""S2 masters: doors, reactor (off + 4 on-frames), player ship, hangar pad, space gate, fuel tank, command-room screens/terminals."""
from core import *
from hydroponics import shaft, add_outline, RAMPS

GRAY = [rgb(c) for c in ('#101216', '#1e2128', '#2e333d', '#3c424e', '#4e5562')]

def door(state=0):
    w, h = 32, 44
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[1]); outline(im, 0, 0, w, h, STEEL[6])
    rect(im, 3, 7, w - 6, h - 7, STEEL[0])                              # opening
    if state == 2:                                                       # open: light from the next room
        for y in range(8, h):
            for x in range(4, w - 4): px(im, x, y, TEAL[0] if (x + y) % 4 else TEAL[1])
        rect(im, 12, 10, 8, h - 12, TEAL[1])
    gap = (0, 6, 12)[state]
    pw = (w - 6) // 2
    for side in (0, 1):
        pw_vis = pw - gap
        if pw_vis <= 0: continue
        x = 3 if side == 0 else w - 3 - pw_vis
        rect(im, x, 7, pw_vis, h - 7, STEEL[3]); vline(im, x if side == 1 else x + pw_vis - 1, 7, h - 7, STEEL[1])
        if pw_vis >= 4:
            for y in range(12, h - 6, 8): hline(im, x + 1, y, pw_vis - 2, STEEL[5]); hline(im, x + 1, y + 1, pw_vis - 2, STEEL[2])
        hline(im, x, h - 5, pw_vis, ORANGE[3]); hline(im, x, h - 4, pw_vis, ORANGE[1])
    rect(im, 0, 0, w, 7, STEEL[2]); hline(im, 0, 0, w, STEEL[7]); hline(im, 0, 6, w, STEEL[0])
    lamp = GREEN[3] if state == 2 else ORANGE[4]
    rect(im, 13, 2, 6, 3, lamp)
    for x in (2, w - 4): rect(im, x, 1, 2, 4, ORANGE[3])
    return im

def reactor(on=True, frame=0):
    w, h = 60, 84
    im = new(w, h); d = ImageDraw.Draw(im)
    # base platform
    d.ellipse([1, 64, 58, 83], fill=STEEL[0]); d.ellipse([2, 63, 57, 79], fill=STEEL[3]); d.ellipse([6, 65, 53, 76], fill=STEEL[1])
    for i in range(14):                     # rim lights (rotate when on)
        a = i * math.tau / 14 + (frame * .45 if on else 0)
        x, y = 29.5 + 26 * math.cos(a), 71 + 6.5 * math.sin(a)
        px(im, int(x), int(y), (ORANGE[4] if (i + frame) % 3 == 0 else ORANGE[2]) if on else STEEL[2])
    # pillars + coolant pipes
    for x in (8, 48):
        rect(im, x, 28, 5, 42, STEEL[4]); vline(im, x, 28, 42, STEEL[7]); vline(im, x + 4, 28, 42, STEEL[1])
        for y in (34, 50, 62): rect(im, x - 1, y, 7, 3, STEEL[6])
        px(im, x + 2, 40, ORANGE[4] if on else STEEL[2])
    # glass tube
    rect(im, 15, 12, 30, 54, TEAL[0] if on else GRAY[0]); outline(im, 15, 12, 30, 54, TEAL[3] if on else STEEL[4])
    vline(im, 17, 16, 40, TEAL[4] if on else STEEL[5])
    # core crystals (amber when running, dead gray when off)
    R = RAMPS['amber'] if on else GRAY
    k = (frame % 4)
    shaft(im, 22, 60, 7, 24 + (k % 2), -1, R); shaft(im, 38, 60, 7, 22 - (k % 2), 1, R); shaft(im, 30, 60, 10, 36 + (1 if k in (1, 2) else 0), 0, R)
    if on:                                  # glow haze + arcs
        for y in range(14, 62):
            for x in range(18, 43):
                if (x + y + k) % 7 == 0 and im.getpixel((x, y))[3] == 0: px(im, x, y, ORANGE[1])
        for (x0, y0, x1, y1) in ((30, 24, 18, 20 + k), (30, 30, 42, 26 + (k % 2) * 3), (30, 38, 19, 44), (30, 36, 41, 40 - k)):
            n = max(abs(x1 - x0), abs(y1 - y0))
            for i in range(n + 1):
                px(im, x0 + (x1 - x0) * i // n + (i % 2) * (1 if k % 2 else -1), y0 + (y1 - y0) * i // n, ORANGE[5] if i % 3 else ORANGE[4])
    # top cap + exhaust + lamps
    rect(im, 12, 6, 36, 7, STEEL[5]); hline(im, 12, 6, 36, STEEL[8]); hline(im, 12, 12, 36, STEEL[0])
    rect(im, 24, 0, 12, 7, STEEL[4]); hline(im, 24, 0, 12, STEEL[7])
    for x in (15, 29, 43): rect(im, x, 8, 3, 2, ORANGE[4] if on and (frame + x) % 2 else (ORANGE[2] if on else STEEL[2]))
    # fuel hopper (front)
    rect(im, 22, 66, 16, 8, STEEL[2]); outline(im, 22, 66, 16, 8, STEEL[6]); rect(im, 26, 68, 8, 3, ORANGE[3] if on else STEEL[1])
    return add_outline(im)

def ship(frame=0):
    """Player ship, nose up, seen from above-front (3/4). Engines glow at the back."""
    w, h = 76, 64
    im = new(w, h); d = ImageDraw.Draw(im)
    cx = w // 2
    # engine glow first (behind)
    for ex in (cx - 14, cx + 14):
        r = 4 + (frame % 3)
        d.ellipse([ex - r, 54 - 1, ex + r, 54 + 6 + r], fill=BLUE[3]); d.ellipse([ex - 2, 54, ex + 2, 60 + frame % 3], fill=BLUE[5])
    # wings (swept)
    d.polygon([(cx - 4, 26), (6, 50), (6, 56), (cx - 10, 50)], fill=STEEL[6]); d.polygon([(cx + 4, 26), (w - 6, 50), (w - 6, 56), (cx + 10, 50)], fill=STEEL[4])
    d.polygon([(cx - 4, 30), (10, 50), (cx - 10, 48)], fill=STEEL[7]); d.polygon([(cx + 4, 30), (w - 10, 50), (cx + 10, 48)], fill=STEEL[5])
    hline(im, 9, 52, 12, ORANGE[3]); hline(im, w - 21, 52, 12, ORANGE[3])
    # fuselage
    d.polygon([(cx, 2), (cx + 11, 22), (cx + 13, 50), (cx + 8, 58), (cx - 8, 58), (cx - 13, 50), (cx - 11, 22)], fill=STEEL[7])
    d.polygon([(cx, 2), (cx + 11, 22), (cx + 13, 50), (cx + 8, 58), (cx, 58)], fill=STEEL[5])
    d.line([(cx, 8), (cx, 56)], fill=STEEL[4])
    # cockpit
    d.polygon([(cx, 8), (cx + 6, 20), (cx - 6, 20)], fill=BLUE[2]); d.polygon([(cx, 9), (cx + 2, 16), (cx - 3, 16)], fill=BLUE[4]); px(im, cx - 2, 12, BLUE[5])
    # stripes + panels + lights
    for y in (30, 36): hline(im, cx - 9, y, 18, ORANGE[3]) if y == 30 else hline(im, cx - 10, y, 20, STEEL[4])
    rect(im, cx - 7, 42, 14, 6, STEEL[2]); outline(im, cx - 7, 42, 14, 6, STEEL[4])
    for ex in (cx - 14, cx + 14): rect(im, ex - 4, 50, 8, 8, STEEL[3]); hline(im, ex - 4, 50, 8, STEEL[7]); rect(im, ex - 3, 56, 6, 2, STEEL[0])
    px(im, 7, 54, GREEN[3] if frame % 2 else GREEN[1]); px(im, w - 8, 54, RED[2] if frame % 2 else RED[0])
    return add_outline(im)

def pad():
    w, h = 140, 84
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[2]); outline(im, 0, 0, w, h, STEEL[6]); outline(im, 3, 3, w - 6, h - 6, STEEL[1])
    hz = hazard_strip_img(w - 8, 4); im.alpha_composite(hz, (4, 4)); im.alpha_composite(hz, (4, h - 8))
    d = ImageDraw.Draw(im)
    d.ellipse([w // 2 - 32, h // 2 - 22, w // 2 + 32, h // 2 + 22], outline=ORANGE[3]); d.ellipse([w // 2 - 28, h // 2 - 19, w // 2 + 28, h // 2 + 19], outline=STEEL[5])
    for x in (w // 2 - 10, w // 2 + 8): vline(im, x, h // 2 - 8, 16, ORANGE[3]); vline(im, x + 1, h // 2 - 8, 16, ORANGE[3])
    hline(im, w // 2 - 10, h // 2, 20, ORANGE[3])
    for (x, y) in ((6, 12), (w - 8, 12), (6, h - 14), (w - 8, h - 14)): rect(im, x, y, 3, 3, ORANGE[4])
    return im

def hazard_strip_img(w, h):
    im = new(w, h)
    for x in range(w):
        for y in range(h): px(im, x, y, ORANGE[4] if ((x + y) // 3) % 2 == 0 else STEEL[1])
    return im

def space_gate(frame=0):
    w, h = 120, 44
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[1]); outline(im, 0, 0, w, h, STEEL[6])
    iw, ih = w - 8, h - 14
    sky = new(iw, ih, rgb('#03050e'))                       # everything inside the window is drawn on its own layer, then pasted
    r = random.Random(11)
    for i in range(46):
        x, y = r.randint(1, iw - 2), r.randint(1, ih - 4)
        px(sky, x, y, BLUE[4] if (i + frame) % 5 == 0 else STEEL[6] if i % 3 else STEEL[8])
    d = ImageDraw.Draw(sky)
    d.ellipse([iw - 56, 10, iw + 26, 90], fill=BLUE[1]); d.ellipse([iw - 52, 12, iw + 22, 88], fill=BLUE[2]); d.ellipse([iw - 44, 16, iw + 10, 80], fill=BLUE[3])
    for x in range(iw - 46, iw):
        for y in range(ih - 8, ih):
            if (x + y) % 3 == 0 and 0 <= x < iw: sky.putpixel((x, y), BLUE[4])
    im.alpha_composite(sky, (4, 5))
    rect(im, 4, h - 9, w - 8, 3, TEAL[2] if frame % 2 else TEAL[1])                 # force-field edge
    for x in range(4, w - 4, 8): px(im, x, h - 8, TEAL[4] if (x // 8 + frame) % 2 else TEAL[2])
    for x in (2, w - 4): rect(im, x, 2, 2, h - 4, ORANGE[3])
    hline(im, 0, 1, w, STEEL[8]); im.alpha_composite(hazard_strip_img(w - 8, 3), (4, h - 4))
    return im

def tank():
    w, h = 24, 40
    im = new(w, h); d = ImageDraw.Draw(im)
    rect(im, 2, 4, 20, 32, STEEL[5]); vline(im, 2, 4, 32, STEEL[8]); vline(im, 4, 4, 32, STEEL[7]); vline(im, 21, 4, 32, STEEL[1]); vline(im, 19, 4, 32, STEEL[3])
    d.ellipse([2, 0, 21, 8], fill=STEEL[6]); d.ellipse([2, 30, 21, 39], fill=STEEL[3])
    rect(im, 2, 14, 20, 4, ORANGE[3]); hline(im, 2, 14, 20, ORANGE[4]); d.ellipse([8, 22, 15, 29], fill=STEEL[0], outline=STEEL[8]); px(im, 11, 24, ORANGE[4])
    return add_outline(im)

def screen_map(frame=0):
    w, h = 104, 32
    im = new(w, h)
    rect(im, 0, 0, w, h, STEEL[1]); outline(im, 0, 0, w, h, STEEL[6])
    rect(im, 3, 3, w - 6, h - 6, TEAL[0])
    for x in range(6, w - 4, 10): vline(im, x, 4, h - 8, TEAL[1])
    for y in range(8, h - 4, 8): hline(im, 4, y, w - 8, TEAL[1])
    nodes = [(18, 12), (36, 22), (52, 10), (70, 20), (88, 12)]
    for (a, b) in zip(nodes, nodes[1:]):
        n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for i in range(0, n, 2): px(im, a[0] + (b[0] - a[0]) * i // n, a[1] + (b[1] - a[1]) * i // n, TEAL[2])
    for i, (x, y) in enumerate(nodes):
        rect(im, x - 1, y - 1, 3, 3, ORANGE[4] if i == 3 else TEAL[4])
    tx, ty = nodes[3]; r = 3 + frame % 4
    d = ImageDraw.Draw(im); d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=ORANGE[3])
    sx = 5 + (frame * 24) % (w - 10); vline(im, sx, 4, h - 8, TEAL[3])                  # scan line
    return im

def orion_terminal(frame=0):
    w, h = 32, 46
    im = new(w, h); d = ImageDraw.Draw(im)
    rect(im, 4, 30, 24, 14, STEEL[3]); hline(im, 4, 30, 24, STEEL[7]); hline(im, 4, 43, 24, STEEL[0])
    rect(im, 12, 22, 8, 9, STEEL[4])
    d.ellipse([2, 2, 29, 29], fill=STEEL[1], outline=STEEL[6])
    d.ellipse([5, 5, 26, 26], fill=TEAL[0], outline=TEAL[3] if frame % 2 == 0 else TEAL[2])
    r = 4 + (frame % 4 == 1) + (frame % 4 == 2)
    d.ellipse([15 - r, 15 - r, 15 + r, 15 + r], fill=TEAL[3] if frame % 4 < 3 else TEAL[2]); px(im, 14 - 1, 13, TEAL[4]); px(im, 15 + 1, 14, TEAL[4])
    for i in range(8):
        a = i * math.tau / 8 + frame * .4; px(im, int(15 + 11 * math.cos(a)), int(15 + 11 * math.sin(a)), TEAL[4])
    for x in (7, 11, 21): px(im, x, 38, ORANGE[4] if (x + frame) % 2 else GREEN[3])
    return add_outline(im)

def cryo_terminal(frame=0):
    w, h = 34, 46
    im = new(w, h)
    rect(im, 2, 20, 30, 24, STEEL[3]); hline(im, 2, 20, 30, STEEL[7]); hline(im, 2, 43, 30, STEEL[0]); vline(im, 2, 20, 24, STEEL[1]); vline(im, 31, 20, 24, STEEL[1])
    rect(im, 4, 2, 26, 20, STEEL[1]); outline(im, 4, 2, 26, 20, STEEL[6]); rect(im, 6, 4, 22, 16, rgb('#06202c'))
    for i, x in enumerate((9, 16, 23)):                          # three capsules
        rect(im, x, 6, 4, 12, TEAL[1]); outline(im, x, 6, 4, 12, TEAL[3]); rect(im, x + 1, 9, 2, 6, BLUE[4] if (i + frame) % 2 else BLUE[2])
    for i, x in enumerate((6, 14, 22)): rect(im, x, 28, 6, 3, ORANGE[4] if (i + frame) % 2 else ORANGE[2])
    hline(im, 6, 36, 22, STEEL[1]); hline(im, 6, 38, 14, TEAL[3])
    return add_outline(im)

def all_sprites():
    out = {}
    for s in range(3): out[f'door_{s}'] = door(s)
    out['reactor_off'] = reactor(False, 0)
    for f in range(4): out[f'reactor_on_{f}'] = reactor(True, f)
    for f in range(3): out[f'ship_{f}'] = ship(f)
    out['pad'] = pad(); out['tank'] = tank()
    for f in range(2): out[f'space_gate_{f}'] = space_gate(f); out[f'cryo_terminal_{f}'] = cryo_terminal(f)
    for f in range(4): out[f'screen_map_{f}'] = screen_map(f); out[f'orion_{f}'] = orion_terminal(f)
    return out

if __name__ == '__main__':
    sp = all_sprites()
    pick = [sp['door_0'], sp['door_1'], sp['door_2'], sp['reactor_off'], sp['reactor_on_0'], sp['reactor_on_2'], sp['ship_0'], sp['tank'],
            sp['pad'], sp['space_gate_0'], sp['screen_map_1'], sp['orion_0'], sp['orion_2'], sp['cryo_terminal_0']]
    k = 3; pad_ = 8; maxw = 1500
    sheet = new(maxw, 900, (30, 34, 46, 255)); x = y = pad_; rowh = 0
    for im in pick:
        w, h = im.width * k, im.height * k
        if x + w > maxw - pad_: x = pad_; y += rowh + pad_; rowh = 0
        sheet.alpha_composite(upscale(im, k), (x, y)); x += w + pad_; rowh = max(rowh, h)
    sheet.crop((0, 0, maxw, y + rowh + pad_)).convert('RGB').save('../out/rooms_sheet.png'); print(len(sp), 'sprites')
