"""Scene: Exploration mission on an alien planet (reference 5)."""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(__file__))
from scenekit import *
W, H = 320, 213; rng = random.Random(12)
n = noise(W, H, 60, 3, 21) * 0.85 + noise(W, H, 14, 2, 5) * 0.15
# base ground: dark violet-teal, with lighter patches
ground = ramp_map(noise(W, H, 20, 4, 7), [(0, (30, 26, 44)), (0.5, (48, 42, 64)), (1, (70, 62, 84))])
plateau_m = n > 0.58; pool_m = n < 0.40
img = ground.copy()
# plateau: dark purple rock, lit top edge, cliff face
rock = ramp_map(noise(W, H, 10, 4, 3), [(0, (34, 20, 48)), (0.6, (62, 36, 74)), (1, (96, 56, 104))])
img[plateau_m] = rock[plateau_m]
down = np.zeros_like(plateau_m); down[1:] = plateau_m[:-1] & ~plateau_m[1:]   # bottom edge pixel row
top = np.zeros_like(plateau_m); top[:-1] = plateau_m[1:] & ~plateau_m[:-1]
face = plateau_m.copy()
for k in range(1, 9):
    sh = np.zeros_like(plateau_m); sh[k:] = plateau_m[:-k] & ~plateau_m[k:]; img[sh] = (22, 14, 34) if k < 7 else (30, 20, 44)
edge = np.zeros_like(plateau_m); edge[:-1] = plateau_m[:-1] & ~plateau_m[1:]; img[edge] = (140, 82, 150)
# glowing teal pool (low area)
img[pool_m] = ramp_map(noise(W, H, 8, 3, 2), [(0, (10, 90, 96)), (1, (60, 220, 200))])[pool_m]
pe = np.zeros_like(pool_m); pe[1:] = pool_m[1:] & ~pool_m[:-1]; img[pe] = (190, 255, 240)
img = dither_post(img, 28)
im = Image.fromarray(img.astype(np.uint8), 'RGB').convert('RGBA')
# ground detail: grass tufts, pebbles, spores
d = ImageDraw.Draw(im)
for _ in range(160):
    x, y = rng.randrange(W), rng.randrange(H)
    if plateau_m[y, x] or pool_m[y, x]: continue
    c = rng.choice([(70, 150, 60), (90, 190, 70), (150, 110, 50), (60, 120, 110), (110, 90, 130)]); d.point((x, y), fill=c + (255,))
    if rng.random() < .5: d.point((x, y - 1), fill=c + (255,))
def place(s, x, y, glowc=None, gr=22, sh=True):
    if sh: shadow(im, x + s.width // 2, y + s.height - 2, s.width // 2 + 2, 3, 0.55)
    if glowc: add_glow(im, x + s.width // 2, y + s.height // 2, gr, glowc, 0.55)
    paste(im, s, x, y)
# flora + crystals
for x, y, nm, h in [(96, 20, 'crystal_3fa0ff_1', 28), (6, 100, 'crystal_3fa0ff_2', 30), (190, 96, 'crystal_3fa0ff_1', 36), (60, 178, 'crystal_3fa0ff_2', 24), (178, 30, 'crystal_3fff9a_1', 24), (270, 150, 'crystal_b44cff_1', 20)]:
    place(spr(nm, h), x, y, (40, 120, 255) if '3fa0ff' in nm else ((40, 255, 140) if '3fff9a' in nm else (180, 60, 255)), 24)
for x, y, s_, hh in [(214, 26, 1, 48), (252, 40, 2, 40)]:
    place(spr('tentacle_%d' % s_, hh), x, y, (255, 60, 200), 30)
for x, y in [(118, 144), (230, 96), (70, 70), (150, 190), (290, 190)]:
    place(spr('mushroom_ff8a2a', 13), x, y, (255, 150, 40), 16)
for x, y, nm in [(158, 150, 'rosette_2fbf5a_1'), (250, 70, 'rosette_2fbf5a_1'), (30, 40, 'rosette_1a8a8a_1'), (120, 100, 'rosette_2fbf5a_1')]:
    place(spr(nm, 20), x, y, (90, 255, 90), 14)
# ship with green headlamp beam
ship = spr('ship_explorer', 40, flip=False); sx, sy = 104, 70
poly = Image.new('L', im.size, 0); ImageDraw.Draw(poly).polygon([(sx + 38, sy + 18), (150, 100), (176, 132)], fill=255)
poly = poly.filter(ImageFilter.GaussianBlur(1)); beam = np.asarray(poly).astype(float) / 255 * 0.5; a = np.asarray(im.convert('RGB')).astype(float)
a[..., 1] = np.clip(a[..., 1] + beam * 140, 0, 255); a[..., 0] = np.clip(a[..., 0] + beam * 40, 0, 255); im = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
add_glow(im, sx + 2, sy + 22, 18, (60, 120, 255), 0.9); add_glow(im, sx + 38, sy + 18, 12, (120, 255, 120), 0.9)
shadow(im, sx + 22, sy + 38, 22, 4, 0.5); paste(im, ship, sx, sy)
# astronaut + target brackets on the crystal
ast = atlas('odysseus_eva_down_idle_0'); ax, ay = 124, 132; shadow(im, ax + ast.width // 2, ay + ast.height - 1, 6, 2, .5); paste(im, ast, ax, ay)
d = ImageDraw.Draw(im); bx, by = 186, 98
for ox, oy, sx_, sy_ in ((0, 0, 1, 1), (38, 0, -1, 1), (0, 40, 1, -1), (38, 40, -1, -1)):
    d.line((bx + ox, by + oy, bx + ox + 6 * sx_, by + oy), fill=(110, 255, 150, 255)); d.line((bx + ox, by + oy, bx + ox, by + oy + 6 * sy_), fill=(110, 255, 150, 255))
# vignette
a = np.asarray(im.convert('RGB')).astype(float); y, x = np.ogrid[:H, :W]; v = np.clip((np.maximum(abs(x - W / 2) / (W / 2), abs(y - H / 2) / (H / 2)) - .65) / .35, 0, 1) ** 2
a *= (1 - 0.5 * v[..., None]); im = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
# HUD at 3x
K = 3; big = im.resize((W * K, H * K), Image.NEAREST).convert('RGBA'); d = ImageDraw.Draw(big, 'RGBA'); G = (60, 230, 120)
hud_panel(d, (14, 14, 290, 196), accent=G); d.text((30, 24), 'EXPLORATION MISSION', font=font(15), fill=(230, 255, 240))
rows = (('Scan the area', None, True), ('Collect 3/6 crystals', .5, False), ('Harvest alien flora', .33, False), ('Return to station', None, False))
yy = 54
for t, p, done in rows:
    d.ellipse((28, yy, 44, yy + 16), outline=G + (255,), width=2)
    if done: d.line((32, yy + 8, 36, yy + 12), fill=G + (255,), width=2); d.line((36, yy + 12, 42, yy + 4), fill=G + (255,), width=2)
    d.text((54, yy - 1), t, font=font(14, False), fill=(235, 255, 245))
    if p: d.rectangle((54, yy + 20, 220, yy + 24), outline=G + (255,)); d.rectangle((54, yy + 20, 54 + int(166 * p), yy + 24), fill=G + (255,)); d.text((230, yy + 14), '3/6' if p > .4 else '1/3', font=font(11, False), fill=(200, 255, 220))
    yy += 26 if not p else 36
hud_panel(d, (W * K - 220, 14, W * K - 14, 150), accent=G); d.ellipse((W * K - 80, 26, W * K - 36, 70), fill=(80, 40, 120, 255))
for (x, y) in ((W * K - 190, 100), (W * K - 150, 50), (W * K - 100, 112)): d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(240, 220, 60, 255))
d.line((W * K - 190, 100, W * K - 150, 50), fill=(240, 220, 60, 255)); d.line((W * K - 150, 50, W * K - 100, 112), fill=(240, 220, 60, 255))
hud_panel(d, (W * K - 120, 168, W * K - 14, 330), accent=G)
for i, (c, t) in enumerate(((90, '4/6'), (210, '1/2'), (110, '2/4'))):
    yy = 184 + i * 48; d.polygon([(W * K - 100, yy + 28), (W * K - 90, yy), (W * K - 80, yy + 28)], fill=(60, 160, 255, 255) if i == 0 else ((200, 60, 230, 255) if i == 1 else (80, 230, 90, 255)))
    d.text((W * K - 64, yy + 4), t, font=font(18), fill=(235, 255, 245))
hud_panel(d, (14, H * K - 130, 300, H * K - 14), accent=G)
for i, (p, t) in enumerate(((1.0, '100%'), (.85, '85%'))):
    yy = H * K - 112 + i * 34; d.rectangle((110, yy + 4, 250, yy + 16), outline=G + (255,)); d.rectangle((110, yy + 4, 110 + int(140 * p), yy + 16), fill=G + (255,)); d.text((258, yy), t, font=font(13), fill=(235, 255, 245))
d.text((110, H * K - 44), '12°C', font=font(16), fill=(235, 255, 245)); d.polygon([(40, H * K - 112), (52, H * K - 80), (28, H * K - 80)], fill=G + (255,)); d.rectangle((34, H * K - 80, 46, H * K - 40), fill=G + (255,))
hud_panel(d, (W * K - 320, H * K - 104, W * K - 14, H * K - 14), accent=G); d.line((W * K - 160, H * K - 104, W * K - 160, H * K - 14), fill=G + (255,), width=2)
d.polygon([(W * K - 296, H * K - 50), (W * K - 282, H * K - 90), (W * K - 268, H * K - 50)], fill=(60, 160, 255, 255)); d.text((W * K - 248, H * K - 76), 'CRYSTAL', font=font(13), fill=(235, 255, 245)); d.text((W * K - 248, H * K - 56), '+1', font=font(16), fill=(255, 255, 255))
pts = [(W * K - 150 + i * 6, H * K - 60 - int(math.sin(i * .5) * 14 * (1 if i % 7 else 1.6))) for i in range(24)]
d.line(pts, fill=G + (255,), width=2)
big.convert('RGB').save(os.path.join(OUT, 'explore.png')); im.convert('RGB').save(os.path.join(OUT, 'explore_native.png')); print('ok')
