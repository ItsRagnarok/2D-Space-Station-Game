"""Research module scene: composes the separate sprites (y-sorted, lit) at a given time t."""
from core import *
import objects as o
from scene_base import *

W, H = 320, 180
WALL_H = 40

def make_static():
    sc = new(W, H, STEEL[0])
    special = {(2, 5): 'vent', (3, 5): 'vent', (1, 3): 'grate', (11, 6): 'vent', (12, 7): 'grate', (9, 4): 'vent', (4, 8): 'grate'}
    paste(sc, build_floor(W, H, WALL_H, special), 0, 0)
    # platform around the generator + globe: hazard-edged plate
    plate = new(112, 70)
    rect(plate, 0, 0, 112, 70, STEEL[2]); outline(plate, 0, 0, 112, 70, STEEL[5]); outline(plate, 2, 2, 108, 66, STEEL[1])
    for x in range(6, 106, 6): px(plate, x, 4, STEEL[4])
    paste(plate, hazard_strip(104, 3), 4, 63)
    for (x, y) in ((1, 1), (106, 1), (1, 64), (106, 64)):
        rect(plate, x, y, 5, 5, ORANGE[3]); rect(plate, x + 1, y + 1, 3, 3, ORANGE[1])
    paste(sc, plate, 52, 78)
    # cables from the generator toward the wall consoles
    for i, (x, y) in enumerate(((70, 77), (70, 70), (71, 63), (73, 56), (76, 50))):
        rect(sc, x, y, 2, 7, STEEL[1])
    wp = wall_panel(W, WALL_H + 4)
    # orange pipe running along the upper wall (left and right of the central display)
    for (x0, x1) in ((0, 124), (228, W)):
        rect(wp, x0, 7, x1 - x0, 4, ORANGE[2]); hline(wp, x0, 7, x1 - x0, ORANGE[4]); hline(wp, x0, 10, x1 - x0, ORANGE[0])
        for x in range(x0 + 10, x1, 36):
            rect(wp, x, 6, 4, 6, STEEL[4]); hline(wp, x, 6, 4, STEEL[7]); hline(wp, x, 11, 4, STEEL[0]); px(wp, x + 1, 8, TEAL[4])
    # wide wall display: starfield + ringed planet
    rect(wp, 126, 3, 100, 13, STEEL[0]); outline(wp, 126, 3, 100, 13, STEEL[6]); outline(wp, 127, 4, 98, 11, STEEL[2])
    rect(wp, 128, 5, 96, 9, rgb('#050a1c'))
    r = random.Random(7)
    for _ in range(26): px(wp, r.randint(129, 222), r.randint(6, 12), BLUE[4] if r.random() < .3 else STEEL[6])
    for (x, y, c) in ((172, 8, BLUE[2]), (173, 8, BLUE[3]), (174, 8, BLUE[3]), (172, 9, BLUE[2]), (173, 9, BLUE[3]), (174, 9, BLUE[4]), (172, 10, BLUE[1]), (173, 10, BLUE[2]), (174, 10, BLUE[2])):
        px(wp, x, y, c)
    hline(wp, 169, 9, 9, ORANGE[3])
    paste(sc, wp, 0, 0)
    for y in range(3):
        for x in range(W):
            p = sc.getpixel((x, WALL_H + 4 + y)); sc.putpixel((x, WALL_H + 4 + y), lerp(p, (0, 0, 0, 255), .55 - .15 * y))
    return sc

STATIC = None

def render(t=0.0, with_people=True):
    """t in seconds. Everything animated is a function of t so any frame can be rendered."""
    global STATIC
    if STATIC is None:
        STATIC = make_static()
    sc = STATIC.copy()
    # deep-space ambient: darker overall, shadows pulled toward blue-black
    for y in range(H):
        for x in range(W):
            p = sc.getpixel((x, y))
            sc.putpixel((x, y), (int(p[0] * .66 + 2), int(p[1] * .70 + 4), int(p[2] * .82 + 10), p[3]))
    f2 = int(t * 2)          # 2 fps flicker
    f4 = int(t * 4)
    ph = (t / 3.0) % 1.0     # 3 s breathing for glows

    # ---- things that stand against the wall (drawn before people) ----
    items = []   # (feet_y, image, x, y)
    for (x, fr) in ((6, 0), (54, 1), (102, 2), (150, 3), (198, 0)):
        c = o.console(f4 + fr)
        items.append((WALL_H + 6, c, x, WALL_H + 6 - c.height))
    r = o.rack(f4)
    items.append((WALL_H + 6, r, 252, WALL_H + 6 - r.height))
    r2 = o.rack(f4 + 1)
    items.append((WALL_H + 6, r2, 272, WALL_H + 6 - r2.height))
    # left lockers + right pipe bundle
    for y in (62, 106):
        l = o.locker(f2)
        items.append((y + l.height, l, 1, y))
    pv = o.pipes_v(104); items.append((144, pv, 306, 44))
    # generator, pedestal, globe
    g = o.generator(ph); items.append((78 + 54, g, 60, 80))
    ped = o.pedestal(ph); items.append((134, ped, 134, 114))
    # lab bench + plant + crates
    b = o.bench(f2); items.append((130, b, 178, 104))
    pj = o.plant_jar(f2); items.append((146, pj, 222, 124))
    for (x, y, k, fy) in ((254, 152, 'steel', 166), (270, 152, 'o', 166), (262, 140, 'steel', 168)):
        cr = o.crate(k); items.append((fy, cr, x, y))
    b2 = o.bench(f2 + 1); items.append((120, b2, 262, 92))

    # ---- people ----
    people = []
    if with_people:
        bob = lambda i: (f2 + i) % 2
        people = [
            ('white', 'point', bob(0), 154, 98),
            ('yellow', 'work', f4 % 2, 160, 38),
            ('yellow', 'work', (f4 + 1) % 2, 112, 38),
            ('green', 'idle', bob(1), 196, 76),
            ('white', 'idle', bob(0), 84, 140),
            ('yellow', 'idle', bob(1), 150, 142),
        ]
        for (sch, pose, fr, x, y) in people:
            a = o.astronaut(sch, pose, fr)
            items.append((y + a.height, a, x, y))
    # drone hovering with a small bob
    dr = o.drone(f4)
    dy = 58 + int(round(2 * math.sin(t * 2.2)))
    items.append((200, dr, 196 + int(round(8 * math.sin(t * .7))), dy))

    # shadows first (on the floor), then sprites sorted by feet
    for (fy, im, x, y) in items:
        if im.height <= 24 and im.width <= 16 and fy < 200:
            shadow(sc, x + im.width / 2, fy - 1, im.width * .42, 2, .5)       # people / small things
    shadow(sc, 60 + 33, 78 + 54 - 4, 33, 4, .55)
    shadow(sc, 134 + 9, 132, 10, 2, .55)
    shadow(sc, dr.width / 2 + 196 + int(round(8 * math.sin(t * .7))), 104, 5, 2, .45)

    gl = o.globe(t * 0.6 + 1.3)
    for (fy, im, x, y) in sorted(items, key=lambda i: i[0]):
        paste(sc, im, x, y)
        if im is ped:                                  # draw the globe right above its emitter
            paste(sc, gl, 141 - gl.width // 2, 100 - gl.height // 2)

    # ---- light ----
    k = .85 + .15 * math.sin(t * 2.1)
    glow(sc, 141, 100, 66, BLUE[3], 1.15 * k)
    glow(sc, 93, 102, 48, TEAL[3], .62 * (.8 + .2 * math.sin(ph * 6.28)))
    for x in (150, 202, 112, 80, 28):
        glow(sc, x, 38, 26, TEAL[3], .35)
    glow(sc, 8, 85, 26, ORANGE[3], .6); glow(sc, 8, 128, 26, ORANGE[3], .6)
    glow(sc, 40, 128, 18, ORANGE[3], .3); glow(sc, 168, 142, 16, ORANGE[3], .22)
    glow(sc, 228, 140, 20, GREEN[3], .35)
    glow(sc, 100, 44, 40, ORANGE[3], .18)
    # strong vignette in dithered steps: dark, cold edges keep the eye on the lit centre
    for y in range(H):
        for x in range(W):
            dx, dy2 = (x - W / 2) / (W / 2), (y - H / 2) / (H / 2)
            v = dx * dx * .62 + dy2 * dy2 * .95
            lvl = v + (bay(x, y) - .5) * .22
            m = 1.0 if lvl < .30 else .82 if lvl < .46 else .64 if lvl < .62 else .46 if lvl < .80 else .30
            if m < 1:
                p = sc.getpixel((x, y))
                sc.putpixel((x, y), (int(p[0] * m), int(p[1] * m), int(p[2] * m + (1 - m) * 14), 255))
    return sc

if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '../out/scene.png'
    im = render(0.0)
    im.save(out.replace('.png', '_native.png'))
    upscale(im, 3).convert('RGB').save(out)
    print('saved', out)
