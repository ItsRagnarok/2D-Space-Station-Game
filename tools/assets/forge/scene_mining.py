"""Scene: Active mission, asteroid mining (reference 3)."""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(__file__))
from scenekit import *
W, H = 320, 240; rng = random.Random(8)
im = Image.new('RGBA', (W, H), (4, 6, 18, 255))
# nebula: deep blue / violet clouds
n1 = noise(W, H, 60, 4, 4); n2 = noise(W, H, 40, 3, 9)
arr = np.zeros((H, W, 3))
arr += (n1[..., None] ** 2.2) * np.array([30, 40, 110]) * 1.4 + (n2[..., None] ** 2.6) * np.array([60, 20, 90]) * 1.2
arr = np.floor(arr / 10) * 10 + np.array([4, 6, 18]); im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
stars(im, 320, 2)
# planet (right) with ring
pl = planet(40, (70, 34, 24), (170, 96, 40), (240, 190, 90), seed=5, ring=((110, 150, 190), 0.28), craters=18, bands=0.5)
px, py = 212, 30; paste(im, pl, px, py); add_glow(im, px + pl.width // 2, py + pl.height // 2 + 6, 90, (60, 80, 140), 0.25)
# path (dashed green) from ship to planet marker + target ring
pts = [(118, 142), (150, 120), (178, 96), (205, 78), (226, 62), (238, 52)]
d = ImageDraw.Draw(im)
for (a, b), (c, e) in zip(pts[:-1], pts[1:]):
    steps = int(math.hypot(c - a, e - b) / 4)
    for i in range(0, steps, 2): d.point((int(a + (c - a) * i / steps), int(b + (e - b) * i / steps)), fill=(80, 240, 120, 255))
tx, ty = 238, 52
d.ellipse((tx - 8, ty - 8, tx + 8, ty + 8), outline=(80, 255, 140, 255)); d.ellipse((tx - 2, ty - 2, tx + 2, ty + 2), fill=(80, 255, 140, 255))
for ang in (0, 90, 180, 270):
    r = math.radians(ang); d.line((tx + math.cos(r) * 8, ty + math.sin(r) * 8, tx + math.cos(r) * 12, ty + math.sin(r) * 12), fill=(80, 255, 140, 255))
d.ellipse((190, 86, 197, 93), fill=(80, 240, 120, 255))
# far asteroids (small, dim) then mid then near (large)
far = [(20, 30, 12), (60, 10, 10), (95, 52, 14), (300, 120, 12), (270, 180, 14), (150, 20, 11), (200, 200, 12), (10, 120, 13)]
for x, y, s in far:
    a = spr('asteroid_%d' % rng.randint(1, 8), s, flip=rng.random() < .5, sat=0.8); a = Image.eval(a, lambda v: v)
    arr = np.asarray(a).astype(float); arr[..., :3] *= 0.55; paste(im, Image.fromarray(arr.astype(np.uint8), 'RGBA'), x, y)
mid = [(48, 70, 24), (175, 150, 26), (116, 10, 22), (220, 118, 22), (10, 188, 28), (250, 14, 20)]
for x, y, s in mid: paste(im, spr('asteroid_%d' % rng.randint(1, 8), s, flip=rng.random() < .5), x, y)
near = [(140, 196, 52), (92, 82, 44), (8, 150, 40)]
for x, y, s in near:
    a = spr('asteroid_%d' % rng.randint(1, 8), s, flip=rng.random() < .5); shadow_im = im; paste(im, a, x, y)
# ship (explorer) with thruster glow
sh = spr('ship_explorer', 50); sx, sy = 78, 118
add_glow(im, sx + 2, sy + 28, 30, (50, 110, 255), 1.0); add_glow(im, sx + 10, sy + 36, 26, (50, 110, 255), 1.0)
paste(im, sh, sx, sy)
# mining beam
for i in range(0, 40, 2): d.point((sx + sh.width - 2 + i, sy + 10 + i // 5), fill=(120, 255, 190, 255))
# upscale + HUD
big = im.resize((W * 3, H * 3), Image.NEAREST).convert('RGBA'); d = ImageDraw.Draw(big, 'RGBA'); G = (60, 230, 120)
hud_panel(d, (28, 26, 330, 160), accent=G); d.text((60, 36), 'ACTIVE MISSION', font=font(14), fill=(120, 255, 180))
d.text((42, 66), 'Asteroid Mining', font=font(18), fill=(255, 255, 255))
for i, t in enumerate(('Collect 0/20 Rare Ore', 'Return to station', 'Time: 2h 30m')):
    yy = 100 + i * 20; d.ellipse((44, yy + 2, 56, yy + 14), outline=(240, 200, 60, 255), width=2); d.text((66, yy), t, font=font(14, False), fill=(235, 255, 245))
hud_panel(d, (640, 462, 934, 590), accent=G); d.text((660, 470), 'REWARD', font=font(14), fill=(120, 255, 180))
for i, (t, v, c) in enumerate((('Rare Ore', '20', (90, 200, 255)), ('Credits', '1.5k', (240, 190, 60)), ('XP', '250', (240, 190, 60)))):
    yy = 500 + i * 26; d.rectangle((660, yy + 2, 674, yy + 16), fill=c); d.text((686, yy), t, font=font(14, False), fill=(235, 255, 245)); d.text((868, yy), v, font=font(14), fill=(255, 255, 255))
caption_bar(big, '3.  MISIUNI ȘI EXPLORARE', 'Trimite nave pe planete, asteroizi sau stații abandonate.', 'Descoperă resurse, artefacte și noi forme de viață.', h=78, accent=G)
big.convert('RGB').save(os.path.join(OUT, 'mining.png')); im.convert('RGB').save(os.path.join(OUT, 'mining_native.png')); print('ok')
