"""Odysseus — master sprite per direction (down / up / right), everything else derived in code.

Derivations (no extra drawing): left = mirror of right (done at runtime with flipX),
outfits = palette swaps (+ small overlays), walk cycle = leg/arm/bob offsets on the master torso.
Canvas 16x24, feet touch y=22.
"""
from core import *

W_, H_ = 16, 24
OX, OY = 2, 1

OUTFITS = {
    # station suit: white, teal chest panel, dark gloves
    'station': dict(W='#e8edf3', L='#ffffff', S='#97a3b8', A='#25d0cf', P='#7f8aa0', p='#566178', B='#2e333d', G='#2e333d', K='#4e5562', M='#25d0cf', V='#10243a', v='#58a4ff'),
    # spacewalk (EVA): bulky white, orange trims, gold visor
    'eva': dict(W='#f2f2ea', L='#ffffff', S='#aeb4c6', A='#e8902a', P='#f2f2ea', p='#aeb4c6', B='#e8902a', G='#e8902a', K='#d4d9e4', M='#e8902a', V='#4a3208', v='#ffd070'),
    # crew colours (same masters, other palette)
    'yellow': dict(W='#f0c030', L='#ffe27a', S='#b88a14', A='#6a3a0a', P='#2f5f8f', p='#1f3f66', B='#2e333d', G='#e8b890', K='#8a5e10', M='#e8902a', V='#10243a', v='#58a4ff'),
    'green': dict(W='#38c068', L='#86f0a8', S='#1f7a42', A='#e8f6ff', P='#3a5a8a', p='#223a5e', B='#2e333d', G='#e8b890', K='#1f7a42', M='#e8f6ff', V='#10243a', v='#58a4ff'),
}

FRONT = [
"....OOOO....", "..OOLLLWOO..", ".OLLWWWWWSO.", ".OLWVVVVVSO.", "OLWVvvVVVVSO", "OLWVVVVVVVSO", ".OWVVVVVVSO.",
".OWWSSSSSSO.", "..OOWWWWOO..", ".OAAWWWWAAO.", "OWOWWAAWWOSO", "OWOWWAAWWOSO", "OWOSWWWWSOSO", "OGOSWWWWSOGO", ".OOPPPPPPOO.",
]
def _back():
    rows = []
    for i, r in enumerate(FRONT):
        r = r.replace('V', 'W').replace('v', 'W')
        if i in (3, 4, 5): r = r[:4] + 'WSWSW' + r[9:] if False else r
        if i == 6: r = r.replace('WWWWWW', 'WSSSSW')
        if i in (10, 11, 12): r = r.replace('WWAAWW', 'KKMMKK').replace('WWWWWW', 'KKKKKK').replace('SWWWWS', 'SKKKKS')
        if i == 9: r = r.replace('AA', 'KK')
        rows.append(r)
    rows[4] = 'OLWWWWWWWWSO'; rows[5] = 'OLWWWSSWWWSO'   # helmet back: neck seal line
    return rows
BACK = _back()
SIDE = [
"....OOOO....", "...OLLLWO...", "..OLLWWWWO..", "..OLWWWVVVO.", "..OLWWVvvVVO", "..OWWWVVVVVO", "..OWWWWVVVO.",
"..OWSSSSSSO.", "...OOWWWOO..", "..OKKWWWWO..", ".OKKKWWWWWO.", ".OKMKWWAWWO.", ".OKKKWWWSWO.", ".OKKOSWWSGO.", "..OOOPPPPO..",
]
TORSO = {'down': FRONT, 'up': BACK, 'right': SIDE}

def _pal(outfit):
    d = OUTFITS[outfit]
    p = {k: rgb(v) for k, v in d.items()}
    p['O'] = STEEL[0]
    return p

def _torso_img(dirn, outfit):
    rows = [r.ljust(12, '.') for r in TORSO[dirn]]
    return ascii_sprite(rows, _pal(outfit))

def _leg(im, x0, top, bottom, pal):
    """One leg: outline | body body | outline, boots in the last rows."""
    for y in range(top, bottom + 1):
        k = bottom - y
        body = pal['B'] if k in (1, 2) else pal['p'] if k == 3 else pal['P']
        if k == 0:
            for dx in range(4): px(im, x0 + dx, y, pal['O'])
            continue
        px(im, x0, y, pal['O']); px(im, x0 + 3, y, pal['O'])
        px(im, x0 + 1, y, body); px(im, x0 + 2, y, body)

def _leg_side(im, hip_x, top, bottom, foot_dx, pal, far=False):
    """Side-view leg: slants from the hip to the foot; boot has a toe pointing right (forward)."""
    body = pal['p'] if far else pal['P']
    n = max(1, bottom - top)
    for y in range(top, bottom + 1):
        x0 = hip_x + int(round(foot_dx * (y - top) / n))
        k = bottom - y
        if k == 0:
            for dx in range(0, 5): px(im, x0 + dx, y, pal['O'])
            continue
        col = pal['B'] if k in (1, 2) else (pal['p'] if k == 3 else body)
        px(im, x0, y, pal['O'])
        for dx in (1, 2): px(im, x0 + dx, y, col)
        if k in (1, 2): px(im, x0 + 3, y, col); px(im, x0 + 4, y, pal['O'])
        else: px(im, x0 + 3, y, pal['O'])

def frame_img(outfit='station', dirn='down', anim='idle', frame=0):
    pal = _pal(outfit)
    torso = _torso_img(dirn, outfit)
    bob = 1 if (anim == 'walk' and frame in (1, 3)) else 0
    if anim == 'idle' and frame == 1: bob = 0
    # --- arms: cut them out and re-paste with a swing offset ---
    if dirn in ('down', 'up'):
        L = (0, 10, 3, 4); R = (9, 10, 3, 4)       # x, y, w, h patches (rows 10..13)
        swing = {0: (0, 0), 1: (-1, 1), 2: (0, 0), 3: (1, -1)}[frame % 4] if anim == 'walk' else (0, 0)
        if anim == 'act': swing = (-2, -2) if frame % 2 == 0 else (-3, -3)
        out = torso.copy()
        for (x, y, w, h), dy in ((L, swing[0]), (R, swing[1])):
            patch = torso.crop((x, y, x + w, y + h))
            ImageDraw.Draw(out).rectangle([x, y, x + w - 1, y + h - 1], fill=CLEAR)
            out.alpha_composite(patch, (x, y + dy))
        torso = out
    else:
        patch = torso.crop((8, 11, 11, 14))
        out = torso.copy(); ImageDraw.Draw(out).rectangle([8, 11, 10, 13], fill=CLEAR)
        dy = 0 if anim == 'walk' else (-1 if anim == 'act' else 0)
        dx = ((1 + frame % 2) if anim == 'act' else {0: -1, 1: 0, 2: 1, 3: 0}[frame % 4] if anim == 'walk' else 0)
        out.alpha_composite(patch, (8 + dx, 11 + dy)); torso = out

    im = new(W_, H_)
    im.alpha_composite(torso, (OX, OY - bob))
    # --- legs ---
    top = OY + 15 - bob - 1 + 1       # hips row is torso row 14
    floor = OY + 21
    if dirn in ('down', 'up'):
        lx, rx = OX + 2, OX + 6
        la = ra = floor
        if anim == 'walk':
            if frame % 4 == 1: la = floor - 1
            if frame % 4 == 3: ra = floor - 1
        _leg(im, lx, top, la, pal); _leg(im, rx, top, ra, pal)
    else:
        hx = OX + 4
        if anim == 'walk':
            f = frame % 4
            near_dx, far_dx = {0: (3, -3), 1: (0, 0), 2: (-3, 3), 3: (0, 0)}[f]
            near_b = floor - (1 if f == 1 else 0); far_b = floor - (1 if f == 3 else 0)
            _leg_side(im, hx, top, far_b, far_dx, pal, far=True)     # far leg first, near leg on top
            _leg_side(im, hx, top, near_b, near_dx, pal)
        else:
            _leg_side(im, hx - 1, top, floor, 0, pal, far=True); _leg_side(im, hx, top, floor, 0, pal)
    if outfit == 'eva':   # derived overlays: helmet lamp + shoulder stripes
        if dirn == 'down': px(im, OX + 2, OY + 2 - bob, rgb('#fff6b0')); px(im, OX + 9, OY + 2 - bob, rgb('#fff6b0'))
        if dirn == 'right': px(im, OX + 9, OY + 2 - bob, rgb('#fff6b0'))
    return im

ANIMS = {'idle': 2, 'walk': 4, 'act': 2}
DIRS = ('down', 'up', 'right')

def all_frames(outfit):
    out = {}
    for d in DIRS:
        for a, n in ANIMS.items():
            for f in range(n):
                out[f'odysseus_{outfit}_{d}_{a}_{f}'] = frame_img(outfit, d, a, f)
    return out

if __name__ == '__main__':
    import sys
    k = 6
    rows = []
    for outfit in ('station', 'eva'):
        for d in DIRS:
            fr = [frame_img(outfit, d, 'walk', f) for f in range(4)] + [frame_img(outfit, d, 'idle', 0), frame_img(outfit, d, 'act', 0)]
            rows.append(fr)
    sheet = new(6 * (W_ * k + 10) + 10, len(rows) * (H_ * k + 10) + 10, (40, 46, 60, 255))
    for r, fr in enumerate(rows):
        for c, im in enumerate(fr):
            sheet.alpha_composite(upscale(im, k), (10 + c * (W_ * k + 10), 10 + r * (H_ * k + 10)))
    sheet.convert('RGB').save('../out/odysseus_sheet.png'); print(sheet.size)
