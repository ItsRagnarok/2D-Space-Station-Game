"""Build everything the game loads: one atlas (PNG + Phaser JSON hash), light/vignette textures, HUD icons.
Run:  python3 build_game_assets.py      (from tools/assets/forge)  -> ../../../public/assets/"""
import os, json, math
from core import *
import odysseus, hydroponics, station_rooms, station_exterior, objects as o
from scene_base import floor_tile, wall_panel, hazard_strip

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'public', 'assets')
os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)

sprites = {}
# character: station suit + spacewalk suit (left = mirrored at runtime)
for outfit in ('station', 'eva', 'yellow', 'green'):    # yellow/green = crew, recoloured from the same masters
    sprites.update(odysseus.all_frames(outfit))
# hydroponics set
sprites.update(hydroponics.all_sprites())
sprites.update(station_rooms.all_sprites())
sprites.update(station_exterior.all_sprites())
for i in range(12): sprites[f'globe_{i:02d}'] = o.globe(i * math.pi * 2 / 12)
# shared props reused from the research module
for i in range(4): sprites[f'console_{i}'] = o.console(i)
for i in range(2):
    sprites[f'rack_{i}'] = o.rack(i); sprites[f'locker_{i}'] = o.locker(i); sprites[f'bench_{i}'] = o.bench(i); sprites[f'drone_{i}'] = o.drone(i)
sprites['crate_steel'] = o.crate('steel'); sprites['crate_orange'] = o.crate('o'); sprites['pipes_v'] = o.pipes_v(104)
for i in range(3): sprites[f'generator_{i}'] = o.generator(i / 3)
# tiles
for i in range(6): sprites[f'floor_{i}'] = floor_tile(i * 131 + 7)
sprites['floor_vent'] = floor_tile(5, 'vent'); sprites['floor_grate'] = floor_tile(9, 'grate')
sprites['wall_120'] = wall_panel(120, 44)
sprites['hazard_104'] = hazard_strip(104, 3)

# ---- lights (alpha masks, dithered in steps; white) ----
def radial(S):
    im = new(S, S); c = S / 2
    for y in range(S):
        for x in range(S):
            d = math.hypot(x + .5 - c, y + .5 - c) / c
            if d >= 1: continue
            lvl = (1 - d) ** 1.25 + (bay(x, y) - .5) * .22
            a = 255 if lvl > .70 else 190 if lvl > .50 else 125 if lvl > .30 else 60 if lvl > .12 else 0
            if a: im.putpixel((x, y), (255, 255, 255, a))
    return im
def cone(L, Hh, half=math.radians(30)):
    im = new(L, Hh); cy = Hh / 2
    for y in range(Hh):
        for x in range(L):
            vx, vy = x + .5, y + .5 - cy
            d = math.hypot(vx, vy)
            if d < 1 or d >= L: continue
            ang = abs(math.atan2(vy, vx))
            if ang > half: continue
            lvl = (1 - d / L) ** .65 * (.55 + .45 * (1 - ang / half)) + (bay(x, y) - .5) * .22
            a = 255 if lvl > .62 else 190 if lvl > .42 else 120 if lvl > .22 else 0
            if a: im.putpixel((x, y), (255, 255, 255, a))
    return im
sprites['light_radial_64'] = radial(64); sprites['light_radial_32'] = radial(32); sprites['light_cone'] = cone(96, 112)
# soft ground shadow (hard-edged ellipse)
sh = new(20, 8); ImageDraw.Draw(sh).ellipse([0, 0, 19, 7], fill=(0, 0, 0, 120)); sprites['shadow_20'] = sh

# ---- pack into one atlas ----
def pack(items, maxw=1024, pad=2):
    order = sorted(items.items(), key=lambda kv: (-kv[1].height, -kv[1].width))
    x = y = pad; rowh = 0; place = {}
    for name, im in order:
        if x + im.width + pad > maxw: x = pad; y += rowh + pad; rowh = 0
        place[name] = (x, y); x += im.width + pad; rowh = max(rowh, im.height)
    H = 1
    while H < y + rowh + pad: H *= 2
    atlas = new(maxw, H)
    frames = {}
    for name, (px_, py_) in place.items():
        im = items[name]; atlas.alpha_composite(im, (px_, py_))
        frames[name] = {'frame': {'x': px_, 'y': py_, 'w': im.width, 'h': im.height}, 'rotated': False, 'trimmed': False,
                        'spriteSourceSize': {'x': 0, 'y': 0, 'w': im.width, 'h': im.height}, 'sourceSize': {'w': im.width, 'h': im.height}}
    return atlas, {'frames': frames, 'meta': {'image': 'orbital.png', 'size': {'w': maxw, 'h': H}, 'scale': '1'}}

atlas, meta = pack(sprites)
atlas.save(os.path.join(OUT, 'orbital.png'), optimize=True)
json.dump(meta, open(os.path.join(OUT, 'orbital.json'), 'w'))

# ---- vignette (separate texture, stepped + dithered, cold tint) ----
VW, VH = 384, 220
vg = new(VW, VH)
for y in range(VH):
    for x in range(VW):
        dx, dy = (x - VW / 2) / (VW / 2), (y - VH / 2) / (VH / 2)
        lvl = dx * dx * .62 + dy * dy * .95 + (bay(x, y) - .5) * .22
        a = 0 if lvl < .34 else 40 if lvl < .50 else 95 if lvl < .66 else 150 if lvl < .84 else 205
        if a: vg.putpixel((x, y), (3, 5, 14, a))
vg.save(os.path.join(OUT, 'vignette.png'))

# ---- HUD icons (16x16-ish, cropped from the masters) ----
def icon(im, name):
    bb = im.getbbox(); c = im.crop(bb); s = max(c.width, c.height)
    sq = new(s, s); sq.alpha_composite(c, ((s - c.width) // 2, (s - c.height) // 2)); sq.save(os.path.join(OUT, 'icons', name + '.png'))
icon(hydroponics.crystal(3, 'blue', 0), 'crystal'); icon(hydroponics.crystal(3, 'amber', 0), 'rare')
icon(hydroponics.flora(3, 'green', 0), 'flora'); icon(hydroponics.mushroom(3, 'purple', 0), 'mush')
bolt = new(12, 14)
for (x, y) in ((7, 0), (6, 1), (5, 2), (4, 3), (3, 4), (2, 5), (3, 6), (4, 6), (5, 6), (5, 7), (4, 8), (4, 9), (3, 10), (3, 11), (2, 12)):
    for dx in range(0, 3): px(bolt, x + dx, y, ORANGE[4] if dx else ORANGE[3])
bolt.save(os.path.join(OUT, 'icons', 'energy.png'))
station_exterior.stars_tile().save(os.path.join(OUT, 'stars_tile.png')); station_exterior.planet().save(os.path.join(OUT, 'planet_rock.png'))
print('atlas', atlas.size, len(sprites), 'frames ->', OUT)
