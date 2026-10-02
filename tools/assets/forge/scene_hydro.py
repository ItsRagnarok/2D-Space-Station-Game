"""Scene: Hydroponics / alien botanical garden (reference 2)."""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(__file__))
from scenekit import *
from core import rect, outline, hline, vline, STEEL
W, H = 320, 292; rng = random.Random(4)
im = Image.new('RGBA', (W, H), (8, 14, 16, 255))
# floor: dark teal metal tiles
a = np.zeros((H, W, 3)); base = noise(W, H, 18, 3, 6)
a[:] = ramp_map(base, [(0, (14, 24, 26)), (1, (28, 44, 46))])
for y in range(H):
    for x in range(W):
        if x % 16 == 0 or y % 16 == 0: a[y, x] = (8, 14, 16)
        elif x % 16 == 1 or y % 16 == 1: a[y, x] = a[y, x] * 1.35
im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im)
def bevel_box(x, y, w, h, col=(40, 50, 56), hi=(90, 104, 112), lo=(14, 18, 22)):
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=col + (255,)); d.line((x, y, x + w - 1, y), fill=hi + (255,)); d.line((x, y, x, y + h - 1), fill=hi + (255,))
    d.line((x, y + h - 1, x + w - 1, y + h - 1), fill=lo + (255,)); d.line((x + w - 1, y, x + w - 1, y + h - 1), fill=lo + (255,))
# back wall band with machinery
d.rectangle((0, 0, W, 56), fill=(18, 26, 28, 255))
for x in range(0, W, 24):
    bevel_box(x, 6, 22, 44, (30, 40, 44)); 
    for k in range(3): d.rectangle((x + 4, 12 + k * 12, x + 17, 18 + k * 12), fill=(10, 16, 18, 255)); d.point((x + 6 + rng.randrange(10), 14 + k * 12), fill=rng.choice([(255, 160, 40), (90, 255, 140), (60, 230, 230)]) + (255,))
d.line((0, 56, W, 56), fill=(255, 160, 40, 255)); d.line((0, 57, W, 57), fill=(120, 60, 10, 255))
# big grow tank (top centre): glass + glowing green water + tiny plants
tx0, ty0, tx1, ty1 = 70, 22, 250, 74
bevel_box(tx0 - 4, ty0 - 4, tx1 - tx0 + 8, ty1 - ty0 + 8, (36, 48, 52)); 
for y in range(ty0, ty1):
    t = (y - ty0) / (ty1 - ty0)
    for x in range(tx0, tx1): d.point((x, y), fill=(int(40 + 40 * t), int(200 - 30 * t), int(70 + 10 * t), 255))
for x in range(tx0 + 6, tx1 - 6, 14):
    s = spr('rosette_2fbf5a_%d' % rng.choice((1, 2)), rng.choice((14, 18)), sat=1.0); paste(im, s, x, ty1 - s.height - 2)
for x in range(tx0 + 10, tx1, 22): d.line((x, ty0, x, ty1), fill=(200, 255, 220, 120))
add_glow(im, 160, 60, 120, (40, 200, 90), 0.5)
# left incubators column
for i, (c, y) in enumerate((('4aff6a', 70), ('ffd84a', 118), ('3fe8ff', 166), ('4aff6a', 214))):
    s = spr('incubator_' + c, 46); shadow(im, 30 + s.width // 2, y + s.height - 2, 18, 4, .5); paste(im, s, 12, y)
    add_glow(im, 12 + s.width // 2, y + s.height // 2, 34, {'4aff6a': (40, 200, 80), 'ffd84a': (230, 190, 40), '3fe8ff': (40, 200, 230)}[c], 0.22)
# planters
def planter(x, y, w, h, rim, glowc, plants):
    shadow(im, x + w // 2, y + h + 2, w // 2 + 4, 5, .5)
    d.rectangle((x - 3, y - 3, x + w + 2, y + h + 2), fill=(rim[0] // 3, rim[1] // 3, rim[2] // 3, 255), outline=rim + (255,))
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=(22, 18, 24, 255))
    for yy in range(y, y + h, 4): d.line((x, yy, x + w - 1, yy), fill=(30, 26, 34, 255))
    add_glow(im, x + w // 2, y + h // 2, max(w, h), glowc, 0.4)
    n = len(plants); 
    for i, (nm, hh) in enumerate(plants):
        s = spr(nm, hh); px_ = x + (i % 2) * (w // 2) + (w // 2 - s.width) // 2; py_ = y + (i // 2) * (h // 2) + (h // 2) - s.height + 2
        shadow(im, px_ + s.width // 2, py_ + s.height - 1, s.width // 2, 2, .5); add_glow(im, px_ + s.width // 2, py_ + s.height // 2, 14, glowc, .5); paste(im, s, px_, py_)
TEAL = (60, 230, 220); PUR = (170, 90, 255)
planter(88, 100, 58, 54, TEAL, (40, 200, 190), [('rosette_1a8a8a_1', 22), ('rosette_1a8a8a_1', 20), ('rosette_2fbf5a_1', 22), ('rosette_1a8a8a_1', 24)])
planter(162, 100, 58, 54, PUR, (150, 70, 230), [('crystal_b44cff_1', 24), ('crystal_3fa0ff_1', 22), ('crystal_b44cff_2', 22), ('crystal_3fa0ff_2', 24)])
planter(88, 176, 58, 54, (255, 190, 50), (230, 170, 40), [('flower_f0c020', 22), ('flower_ff6a3a', 22), ('flower_f0c020', 24), ('flower_c04cff', 22)])
planter(162, 176, 58, 54, PUR, (150, 70, 230), [('crystal_b44cff_2', 24), ('crystal_b44cff_1', 24), ('rosette_8a3ad0_1', 22), ('crystal_3fa0ff_1', 22)])
# right side machines
for y, nm, h in ((72, 'cabinet_2', 46), (126, 'generator_1', 36), (170, 'cabinet_3', 46), (222, 'tank_4a8a5a', 38)):
    s = spr(nm, h); xx = 264 - (s.width - 28) // 2; shadow(im, xx + s.width // 2, y + s.height - 1, s.width // 2 + 2, 3, .55); paste(im, s, xx, y)
add_glow(im, 284, 150, 30, (255, 150, 40), .4)
for x, y in ((236, 262), (258, 268)): s = spr('crate_d4660c', 22); paste(im, s, x, y)
# astronaut
ast = atlas('odysseus_eva_down_idle_0'); ax, ay = 148, 156; shadow(im, ax + ast.width // 2, ay + ast.height - 1, 7, 2, .5); paste(im, ast, ax, ay)
# vignette
a = np.asarray(im.convert('RGB')).astype(float); y, x = np.ogrid[:H, :W]; v = np.clip((np.maximum(abs(x - W / 2) / (W / 2), abs(y - H / 2) / (H / 2)) - .7) / .3, 0, 1) ** 2
a *= (1 - .45 * v[..., None]); im = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
K = 3; big = im.resize((W * K, H * K), Image.NEAREST).convert('RGBA'); d = ImageDraw.Draw(big, 'RGBA'); G = (60, 230, 120)
hud_panel(d, (26, 22, 400, 92), accent=G); d.text((78, 34), 'HYDROPONICS', font=font(19), fill=(235, 255, 240)); d.text((330, 34), '78%', font=font(19), fill=(235, 255, 240))
d.rectangle((78, 64, 316, 74), outline=G + (255,)); d.rectangle((78, 64, 78 + int(238 * .78), 74), fill=G + (255,)); d.polygon([(40, 56), (52, 36), (62, 56), (52, 66)], fill=G + (255,))
hud_panel(d, (W * K - 270, 14, W * K - 14, 196), accent=G); d.text((W * K - 252, 24), 'HARVEST', font=font(15), fill=(235, 255, 240))
for i, (t, v, c) in enumerate((('Alien Flora', '12', (80, 220, 90)), ('Crystal Buds', '8', (240, 220, 80)), ('Bio Fuel', '5', (230, 200, 60)), ('Food', '3', (240, 170, 60)))):
    yy = 56 + i * 32; d.polygon([(W * K - 250, yy + 18), (W * K - 242, yy), (W * K - 234, yy + 18)], fill=c + (255,)); d.text((W * K - 218, yy), t, font=font(15, False), fill=(235, 255, 245)); d.text((W * K - 52, yy), v, font=font(16), fill=(255, 255, 255))
caption_bar(big, '2.  FARMING ÎN SPAȚIU', 'Cultivă plante extraterestre, cristale și resurse rare.', 'Folosește-le pentru combustibil, hrană și upgrade-uri.', h=84, accent=G)
big.convert('RGB').save(os.path.join(OUT, 'hydro.png')); im.convert('RGB').save(os.path.join(OUT, 'hydro_native.png')); print('ok')
