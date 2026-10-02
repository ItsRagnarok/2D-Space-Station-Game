"""Scene: orbital station overview (reference 1)."""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(__file__))
from scenekit import *
W, H = 320, 300; rng = random.Random(2)
im = Image.new('RGBA', (W, H), (3, 5, 16, 255))
n1 = noise(W, H, 70, 4, 11); arr = (n1[..., None] ** 2.4) * np.array([26, 36, 100]) * 1.5 + np.array([3, 5, 16])
im = Image.fromarray(np.clip(np.floor(arr / 9) * 9 + 3, 0, 255).astype(np.uint8)).convert('RGBA'); stars(im, 260, 6)
# planet bottom-left
pl = planet(52, (30, 70, 120), (70, 150, 200), (170, 225, 245), seed=9, craters=0, bands=1.0); paste(im, pl, -40, 206); add_glow(im, 12, 250, 70, (60, 110, 200), .25)
d = ImageDraw.Draw(im)
OR = (255, 160, 40); ORD = (120, 60, 10)
def hull(x, y, w, h, tint=(26, 34, 44)):
    d.rectangle((x - 3, y - 3, x + w + 2, y + h + 2), fill=(10, 14, 20, 255)); d.rectangle((x - 2, y - 2, x + w + 1, y + h + 1), outline=ORD + (255,)); d.rectangle((x - 1, y - 1, x + w, y + h), outline=OR + (255,))
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=tint + (255,))
    for i in range(x + 4, x + w - 2, 9): d.point((i, y - 3), fill=(255, 230, 140, 255)); d.point((i, y + h + 2), fill=(255, 230, 140, 255))
    for j in range(y + 4, y + h - 2, 9): d.point((x - 3, j), fill=(255, 230, 140, 255)); d.point((x + w + 2, j), fill=(255, 230, 140, 255))
    for yy in range(y, y + h, 8): d.line((x, yy, x + w - 1, yy), fill=(tint[0] + 8, tint[1] + 8, tint[2] + 10, 255))
def corridor(x, y, w, h):
    d.rectangle((x, y, x + w, y + h), fill=(20, 26, 34, 255), outline=ORD + (255,)); 
    if w > h: d.line((x, y + h // 2, x + w, y + h // 2), fill=(255, 190, 80, 255))
    else: d.line((x + w // 2, y, x + w // 2, y + h), fill=(255, 190, 80, 255))
# solar arrays + antennas (behind)
for x, y, w, h in ((10, 8, 36, 20), (60, 4, 26, 14), (200, 6, 44, 22), (236, 36, 30, 16)):
    d.rectangle((x, y, x + w, y + h), fill=(24, 50, 100, 255), outline=(90, 130, 200, 255))
    for i in range(x + 5, x + w, 6): d.line((i, y, i, y + h), fill=(50, 90, 160, 255))
    for j in range(y + 5, y + h, 6): d.line((x, j, x + w, j), fill=(50, 90, 160, 255))
# corridors
corridor(118, 100, 14, 32); corridor(118, 168, 14, 20); corridor(188, 112, 10, 14); corridor(88, 120, 30, 14); corridor(150, 66, 14, 28); corridor(150, 196, 22, 22)
# modules
hull(16, 74, 84, 84, (20, 38, 30))   # hydroponics (left)
hull(122, 76, 66, 46, (28, 34, 40)); hull(118, 126, 74, 66, (24, 32, 40))  # command + hub
hull(196, 84, 72, 76, (34, 28, 36))   # lab (right)
hull(98, 206, 120, 58, (22, 24, 30))  # hangar
hull(122, 28, 72, 36, (26, 30, 38))   # top storage
# hydroponics content
for i in range(2):
    for j in range(2):
        x = 24 + i * 38; y = 82 + j * 36; d.rectangle((x, y, x + 30, y + 28), fill=(16, 30, 18, 255), outline=(60, 230, 120, 255)); add_glow(im, x + 15, y + 14, 26, (50, 220, 80), .5)
        for k in range(4):
            paste(im, spr(rng.choice(['rosette_2fbf5a_1', 'rosette_1a8a8a_1', 'flower_f0c020', 'crystal_b44cff_1']), 12), x + 2 + (k % 2) * 14, y + 3 + (k // 2) * 12)
d.rectangle((24, 150, 92, 152), fill=(120, 255, 160, 255))
# reactor hub (centre)
cx, cy = 155, 159
for r, c in ((26, (20, 60, 70)), (20, (30, 120, 130)), (13, (60, 230, 220)), (6, (230, 255, 250))): d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c + (255,))
add_glow(im, cx, cy, 44, (60, 230, 230), .85)
for a_ in range(0, 360, 45): d.line((cx + math.cos(math.radians(a_)) * 15, cy + math.sin(math.radians(a_)) * 15, cx + math.cos(math.radians(a_)) * 26, cy + math.sin(math.radians(a_)) * 26), fill=(255, 190, 80, 255))
# command content (consoles)
for i in range(5): d.rectangle((128 + i * 11, 86, 135 + i * 11, 94), fill=(20, 120, 130, 255), outline=(60, 230, 220, 255))
d.rectangle((138, 100, 172, 112), fill=(20, 40, 50, 255), outline=(255, 150, 60, 255)); d.rectangle((145, 104, 165, 108), fill=(60, 230, 220, 255))
# lab content
for i in range(3):
    d.rectangle((204, 94 + i * 22, 224, 108 + i * 22), fill=(60, 30, 80, 255), outline=(255, 90, 200, 255)); add_glow(im, 214, 101 + i * 22, 18, (255, 70, 190), .5)
d.ellipse((234, 104, 260, 130), fill=(30, 20, 40, 255), outline=(255, 150, 60, 255)); add_glow(im, 247, 117, 22, (255, 120, 220), .6)
# top storage
for i in range(5): paste(im, spr('crate_d4660c' if i % 2 else 'crate_7a8090', 14), 130 + i * 12, 40)
# hangar: pad + ship
d.rectangle((126, 214, 190, 258), fill=(30, 32, 40, 255), outline=(255, 190, 80, 255))
for i in range(130, 188, 6): d.line((i, 216, i + 3, 216), fill=(255, 210, 90, 255)); d.line((i, 256, i + 3, 256), fill=(255, 210, 90, 255))
fs = spr('ship_freighter', 28); add_glow(im, 140, 244, 14, (60, 120, 255), .8); paste(im, fs, 138, 224)
# flying ships (right)
for x, y, hh, fl in ((270, 168, 22, False), (240, 206, 24, False), (284, 236, 20, True)):
    s = spr('ship_explorer', hh, flip=fl); add_glow(im, x + 2, y + hh - 6, 16, (60, 120, 255), .8); paste(im, s, x, y)
# station small details: lights on hull
for _ in range(30):
    x, y = rng.randrange(14, 300), rng.randrange(26, 266)
    if im.getpixel((x, y))[2] > 20 and im.getpixel((x, y))[0] < 60: pass
# vignette
a = np.asarray(im.convert('RGB')).astype(float); y, x = np.ogrid[:H, :W]; v = np.clip((np.maximum(abs(x - W / 2) / (W / 2), abs(y - H / 2) / (H / 2)) - .75) / .25, 0, 1) ** 2
a *= (1 - .4 * v[..., None]); im = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
K = 3; big = im.resize((W * K, H * K), Image.NEAREST).convert('RGBA'); d = ImageDraw.Draw(big, 'RGBA'); G = (60, 230, 160)
hud_panel(d, (22, 20, 350, 190), accent=G); d.text((72, 30), 'ORBITAL STATION', font=font(17), fill=(235, 255, 240)); d.rectangle((72, 62, 330, 70), outline=G + (255,)); d.rectangle((72, 62, 72 + 200, 70), fill=G + (255,))
for i, (t, v, c) in enumerate((('Energy', '78%', (240, 220, 60)), ('Crew', '12/14', (80, 230, 120)), ('Resources', '4.2k', (240, 190, 60)))):
    yy = 88 + i * 30; d.rectangle((40, yy + 2, 54, yy + 18), fill=c + (255,)); d.text((68, yy), t, font=font(15, False), fill=(235, 255, 245)); d.text((250, yy), v, font=font(15), fill=(255, 255, 255))
for i, t in enumerate(('FARMING', 'MISSIONS', 'SHIPS', 'RESEARCH', 'STATION')):
    y0 = 24 + i * 60; hud_panel(d, (W * K - 112, y0, W * K - 10, y0 + 46), accent=G, r=6); d.text((W * K - 104, y0 + 14), t, font=font(13), fill=(235, 255, 245))
caption_bar(big, '1.  STAȚIA TA SPAȚIALĂ', 'Administrează și extinde stația. Construiește camere noi,', 'optimizează producția și pregătește-te pentru misiuni.', h=78, accent=G)
big.convert('RGB').save(os.path.join(OUT, 'station.png')); im.convert('RGB').save(os.path.join(OUT, 'station_native.png')); print('ok')
