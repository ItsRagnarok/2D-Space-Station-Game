"""Scene: the reactor, heart of the station (story: it keeps losing energy; crystals feed it)."""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(__file__))
from scenekit import *
W, H = 320, 270; rng = random.Random(14)
a = ramp_map(noise(W, H, 16, 3, 3), [(0, (12, 16, 22)), (1, (30, 38, 48))])
for y in range(H):
    for x in range(W):
        if x % 16 == 0 or y % 16 == 0: a[y, x] = (6, 9, 13)
        elif x % 16 == 1 or y % 16 == 1: a[y, x] = a[y, x] * 1.3
im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(im)
CY = (60, 230, 230); cx, cy = 160, 150
# floor conduits glowing toward the core (energy lines)
for ang in range(0, 360, 45):
    r = math.radians(ang)
    for t in range(44, 130, 1):
        x = int(cx + math.cos(r) * t); y = int(cy + math.sin(r) * t * .78)
        if 0 <= x < W and 0 <= y < H and (t // 4) % 2: d.point((x, y), fill=(40, 170, 180, 255)); 
# outer ring platform
for rr, c in ((92, (34, 42, 52)), (84, (22, 28, 36)), (60, (44, 54, 66))):
    d.ellipse((cx - rr, cy - int(rr * .78), cx + rr, cy + int(rr * .78)), fill=c + (255,), outline=(8, 12, 16, 255))
for i in range(24):
    r = math.radians(i * 15); x = cx + math.cos(r) * 88; y = cy + math.sin(r) * 88 * .78; d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=(255, 190, 70, 255) if i % 2 else (90, 70, 40, 255))
add_glow(im, cx, cy + 4, 120, CY, .55)
# back wall: cabinets + generators, some dark (power loss), some lit
for i, x in enumerate(range(8, 312, 38)):
    s = spr('cabinet_%d' % (1 + i % 3), 48 + (i % 2) * 8); lit = i % 3 != 1
    if not lit:
        arr = np.asarray(s).astype(float); arr[..., :3] *= .45; s = Image.fromarray(arr.astype(np.uint8), 'RGBA')
    paste(im, s, x, 6)
d.line((0, 66, W, 66), fill=(255, 150, 40, 255)); d.line((0, 67, W, 67), fill=(100, 50, 10, 255))
# side machines
for y, nm, h in ((88, 'generator_1', 40), (146, 'tank_3a6aa8', 42), (200, 'generator_1', 40)):
    for x in (10, 262):
        s = spr(nm, h); shadow(im, x + s.width // 2, y + s.height - 1, s.width // 2 + 2, 3, .55); paste(im, s, x + (0 if x < 100 else 0), y)
add_glow(im, 30, 110, 26, (255, 150, 40), .3); add_glow(im, 284, 220, 26, (255, 150, 40), .3)
# the core
core = spr('reactor_core', 118, sat=1.2); shadow(im, cx, cy + 36, 54, 14, .45); paste(im, core, cx - core.width // 2, cy - core.height // 2 - 6)
add_glow(im, cx, cy - 20, 60, (200, 255, 250), .6)
# crystal feed hopper (front) with crystals
s = spr('crate_7a8090', 24); paste(im, s, 70, 214); paste(im, spr('crystal_3fa0ff_1', 22), 76, 200); paste(im, spr('crystal_b44cff_2', 18), 90, 206)
add_glow(im, 90, 214, 22, (80, 160, 255), .4)
# astronaut approaching with a crystal
ast = atlas('odysseus_eva_right_idle_0') if True else None; ax, ay = 108, 196; shadow(im, ax + ast.width // 2, ay + ast.height - 1, 6, 2, .5); paste(im, ast, ax, ay)
# emergency red lights
for x in (6, 308): add_glow(im, x, 8, 16, (255, 60, 60), .6); d.rectangle((x - 1, 6, x + 1, 9), fill=(255, 120, 120, 255))
# stronger vignette = the station is losing power
a_ = np.asarray(im.convert('RGB')).astype(float); y, x = np.ogrid[:H, :W]; dd = np.sqrt(((x - cx) / (W * .55)) ** 2 + ((y - cy) / (H * .6)) ** 2); v = np.clip((dd - .35) / .65, 0, 1) ** 1.6
a_ *= (1 - .72 * v[..., None]); im = Image.fromarray(a_.astype(np.uint8)).convert('RGBA')
K = 3; big = im.resize((W * K, H * K), Image.NEAREST).convert('RGBA'); d = ImageDraw.Draw(big, 'RGBA')
hud_panel(d, (26, 22, 380, 112), accent=CY); d.text((60, 32), 'REACTOR CORE', font=font(18), fill=(235, 255, 250)); d.text((300, 32), '42%', font=font(18), fill=(255, 220, 120))
d.rectangle((60, 66, 340, 78), outline=CY + (255,)); d.rectangle((60, 66, 60 + int(280 * .42), 78), fill=(255, 200, 70, 255)); d.text((60, 86), 'Energy dropping  -1% / 3 s', font=font(12, False), fill=(255, 190, 130))
hud_panel(d, (W * K - 250, 22, W * K - 14, 200), accent=CY); d.text((W * K - 232, 32), 'FUEL', font=font(15), fill=(235, 255, 250))
for i, (t, v, c, g) in enumerate((('Crystal Buds', '+20%', (60, 160, 255), 'x2'), ('Rare Ore', '+30%', (200, 80, 255), 'x1'), ('Bio Fuel', '+10%', (240, 200, 60), 'x3'))):
    yy = 66 + i * 40; d.polygon([(W * K - 230, yy + 22), (W * K - 220, yy), (W * K - 210, yy + 22)], fill=c + (255,)); d.text((W * K - 196, yy), t, font=font(14, False), fill=(235, 255, 245)); d.text((W * K - 196, yy + 18), g, font=font(11, False), fill=(160, 200, 200)); d.text((W * K - 84, yy + 2), v, font=font(15), fill=(255, 255, 255))
d.rounded_rectangle((330, H * K - 150, 630, H * K - 100), 8, fill=(4, 22, 24, 232), outline=CY + (255,), width=2); d.text((350, H * K - 138), '[E]  Alimentează reactorul', font=font(15), fill=(235, 255, 250))
caption_bar(big, '0.  INIMA STAȚIEI', 'Reactorul pierde energie fără oprire. Fără el, stația se stinge.', 'Hrănește-l cu cristale înainte să rămâi doar cu lanterna.', h=84, accent=CY)
big.convert('RGB').save(os.path.join(OUT, 'reactor.png')); im.convert('RGB').save(os.path.join(OUT, 'reactor_native.png')); print('ok')
