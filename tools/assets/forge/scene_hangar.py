"""Scene: hangar, freighter docking (reference 4). v2 with the 3D asset library."""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(__file__))
from scenekit import *
W, H = 320, 262; rng = random.Random(9)
FL = [(13, 11, 9), (21, 18, 14), (29, 25, 19), (39, 34, 26), (52, 45, 34)]
a = np.zeros((H, W, 3))
for y in range(H):
    for x in range(W):
        t = 1 if rng.random() < .7 else (2 if rng.random() < .8 else 3)
        if x % 16 == 0 or y % 16 == 0: t = 0
        elif x % 16 == 1 or y % 16 == 1: t = min(4, t + 1)
        a[y, x] = FL[t]
im = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im)
OR = (255, 160, 40); ORD = (120, 60, 10)
def rail(x0, y0, x1, y1):
    for yy in range(y0, y1):
        for xx in range(x0, x1): d.point((xx, yy), fill=(OR if (xx + yy) % 8 < 4 else ORD) + (255,))
# walls
d.rectangle((0, 0, W, 54), fill=(20, 22, 28, 255)); d.rectangle((0, 0, 36, H), fill=(20, 22, 28, 255)); d.rectangle((W - 36, 0, W, H), fill=(20, 22, 28, 255))
for yy in (8, 14): d.line((0, yy, W, yy), fill=OR + (255,)); d.line((0, yy + 1, W, yy + 1), fill=ORD + (255,))
x = 38
i = 0
while x < W - 70:
    s = spr('cabinet_%d' % (1 + i % 3), 48 + (i % 2) * 6); shadow(im, x + s.width // 2, 56, s.width // 2 + 1, 2, .6); paste(im, s, x, 56 - s.height); x += s.width + 1; i += 1
rail(36, 56, W - 36, 59); rail(36, 56, 39, H - 30); rail(W - 39, 56, W - 36, H - 30)
# side machinery
for y, nm, hh in ((70, 'generator_1', 38), (116, 'locker', 42), (166, 'generator_1', 38)):
    s = spr(nm, hh); paste(im, s, 3, y); 
for y, nm, hh in ((70, 'tank_3a6aa8', 40), (118, 'cabinet_2', 46), (172, 'tank_4a8a5a', 40)):
    s = spr(nm, hh); paste(im, s, W - 3 - s.width, y)
add_glow(im, 20, 100, 30, OR, .3); add_glow(im, W - 20, 150, 30, OR, .3)
# pad
PX, PY, PW, PH = 54, 74, 190, 126
shadow(im, PX + PW // 2, PY + PH // 2, PW // 2 + 6, PH // 2 + 4, .6)
rng2 = random.Random(3)
ST = [(34, 38, 46), (46, 51, 60), (60, 66, 76), (74, 80, 92)]
for yy in range(PH):
    for xx in range(PW):
        t = 2 if (xx // 14 + yy // 14) % 2 else 1
        if rng2.random() < .05: t += 1
        d.point((PX + xx, PY + yy), fill=ST[min(t, 3)] + (255,))
d.rectangle((PX, PY, PX + PW, PY + PH), outline=(8, 10, 14, 255))
for i in range(PW):
    for dy in (4, 5, 6, 7):
        c = (255, 200, 70) if ((i + dy) // 5) % 2 == 0 else (10, 10, 12); d.point((PX + i, PY + dy - 1), fill=c + (255,)); d.point((PX + i, PY + PH - dy), fill=c + (255,))
for j in range(PH):
    for dx in (4, 5, 6, 7):
        c = (255, 200, 70) if ((j + dx) // 5) % 2 == 0 else (10, 10, 12); d.point((PX + dx - 1, PY + j), fill=c + (255,)); d.point((PX + PW - dx, PY + j), fill=c + (255,))
d.rectangle((PX + 16, PY + 16, PX + PW - 16, PY + PH - 16), outline=OR + (255,))
for cx, cy in ((PX + 16, PY + 16), (PX + PW - 30, PY + 16), (PX + 16, PY + PH - 30), (PX + PW - 30, PY + PH - 30)):
    d.rectangle((cx, cy, cx + 13, cy + 1), fill=(255, 230, 140, 255)); d.rectangle((cx, cy, cx + 1, cy + 13), fill=(255, 230, 140, 255))
d.text((PX + PW - 54, PY + PH - 38), '03', font=ImageFont.truetype(FD + 'DejaVuSansMono-Bold.ttf', 15), fill=(255, 200, 70, 255))
# freighter
ship = spr('ship_freighter', 76); sx = PX + (PW - ship.width) // 2 - 16; sy = PY + (PH - ship.height) // 2 - 2
shadow(im, sx + ship.width // 2, sy + ship.height - 6, ship.width // 2 - 8, 11, .5)
add_glow(im, sx + 8, sy + ship.height - 26, 34, (50, 110, 255), 1.0); add_glow(im, sx + 30, sy + ship.height - 10, 30, (50, 110, 255), 1.0)
paste(im, ship, sx, sy)
# crates, astronauts
for x0, y0, nm in ((42, 206, 'crate_d4660c'), (62, 212, 'crate_7a8090'), (264, 62, 'crate_d4660c'), (280, 80, 'crate_7a8090')):
    s = spr(nm, 26); shadow(im, x0 + s.width // 2, y0 + s.height - 1, s.width // 2, 3, .5); paste(im, s, x0, y0)
for x0, y0 in ((44, 152), (230, 190)):
    paste(im, atlas('odysseus_eva_down_idle_0') if x0 < 100 else atlas('odysseus_eva_up_idle_0'), x0, y0)
for lx, ly in ((56, 66), (244, 66), (56, 206), (244, 206), (150, 60)): add_glow(im, lx, ly, 26, OR, .35); d.rectangle((lx - 1, ly - 1, lx + 1, ly + 1), fill=(255, 230, 150, 255))
a_ = np.asarray(im.convert('RGB')).astype(float); y, x = np.ogrid[:H, :W]; v = np.clip((np.maximum(abs(x - W / 2) / (W / 2), abs(y - H / 2) / (H / 2)) - .72) / .28, 0, 1) ** 2
a_ *= (1 - .45 * v[..., None]); im = Image.fromarray(a_.astype(np.uint8)).convert('RGBA')
from pixui import *
C = (47, 229, 190); WH = (255, 255, 255); TX = (235, 255, 245); W_, H_ = im.size
pbox(im, 237, 23, 316, 120, C); ptext(im, 243, 27, 'ARRIVAL', (120, 255, 235), 8); ptext(im, 248, 38, 'Freighter-7', WH, 10)
ImageDraw.Draw(im).line((241, 52, 312, 52), fill=C + (255,)); ptext(im, 243, 55, 'Cargo:', (150, 200, 195), 8)
for i, (t, v, c) in enumerate((('Iron', '120', (150, 160, 175)), ('Silicon', '60', (240, 190, 60)), ('Food', '40', (240, 170, 60)))):
    yy = 66 + i * 12; psq(im, 243, yy + 1, c, 6); ptext(im, 252, yy, t, TX, 8); ptext(im, 310, yy, v, WH, 8, 'r')
ImageDraw.Draw(im).line((241, 104, 312, 104), fill=C + (255,)); ptext(im, 243, 106, 'Docking...', (120, 255, 235), 8)
pcaption(im, '4.  NAVE CARE VIN ȘI PLEACĂ', 'Primești nave comerciale, cu resurse, misiuni sau cereri speciale.', 'Fii pregătit și gestionează spațiul de andocare.', C)
im.convert('RGB').save(os.path.join(OUT, 'hangar_raw.png')); print('ok')
