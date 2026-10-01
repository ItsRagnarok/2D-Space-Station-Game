"""Floor tiles + back wall for the research module."""
from core import *

T = 16

def floor_tile(seed, kind='plain'):
    r = random.Random(seed)
    im = new(T, T)
    base = STEEL[r.choice([3, 3, 4, 4, 3])]
    rect(im, 0, 0, T, T, base)
    # top/left highlight, bottom/right shadow = beveled plate
    hline(im, 0, 0, T, STEEL[5]); vline(im, 0, 0, T, STEEL[5])
    hline(im, 0, T - 1, T, STEEL[1]); vline(im, T - 1, 0, T, STEEL[1])
    hline(im, 1, T - 2, T - 2, STEEL[2]); vline(im, T - 2, 1, T - 2, STEEL[2])
    # rivets
    for (x, y) in ((2, 2), (T - 4, 2), (2, T - 4), (T - 4, T - 4)):
        px(im, x, y, STEEL[6]); px(im, x + 1, y + 1, STEEL[1])
    # scuffs
    for _ in range(r.randint(2, 5)):
        x, y = r.randint(3, T - 5), r.randint(3, T - 5)
        px(im, x, y, STEEL[2]); 
        if r.random() < .5: px(im, x + 1, y, STEEL[2])
    if r.random() < .3:
        x, y = r.randint(4, T - 7), r.randint(4, T - 5)
        hline(im, x, y, r.randint(2, 4), STEEL[5])
    if kind == 'grate':
        for y in range(4, T - 3, 2):
            hline(im, 3, y, T - 6, STEEL[1]); hline(im, 3, y + 1, T - 6, STEEL[4])
    if kind == 'vent':
        outline(im, 2, 2, T - 4, T - 4, ORANGE[2])
        rect(im, 3, 3, T - 6, T - 6, ORANGE[0])
        for y in range(5, T - 4, 3):
            hline(im, 4, y, T - 8, ORANGE[3]); hline(im, 4, y + 1, T - 8, ORANGE[1])
    return im

def hazard_strip(w, h=4):
    im = new(w, h)
    for x in range(w):
        for y in range(h):
            on = ((x + y) // 3) % 2 == 0
            px(im, x, y, ORANGE[4] if on else STEEL[1])
    return im

def build_floor(W, H, y0, special):
    im = new(W, H)
    for ty in range((H - y0) // T + 1):
        for tx in range(W // T + 1):
            kind = special.get((tx, ty), 'plain')
            paste(im, floor_tile(tx * 131 + ty * 17, kind), tx * T, y0 + ty * T)
    return im

def wall_panel(W, h):
    """Back wall seen from the front (3/4 view): panels, trim, orange baseboard strip."""
    im = new(W, h)
    rect(im, 0, 0, W, h, STEEL[2])
    for x in range(0, W, 24):
        vline(im, x, 0, h - 5, STEEL[1]); vline(im, x + 1, 0, h - 5, STEEL[4])
    hline(im, 0, 0, W, STEEL[1]); hline(im, 0, 1, W, STEEL[5])
    hline(im, 0, 5, W, STEEL[1]); hline(im, 0, 6, W, STEEL[3])
    # baseboard with warm light strip
    rect(im, 0, h - 5, W, 5, STEEL[1])
    hline(im, 0, h - 4, W, ORANGE[2]); hline(im, 0, h - 3, W, ORANGE[3])
    hline(im, 0, h - 1, W, STEEL[0])
    for x in range(6, W, 40):
        hline(im, x, h - 4, 12, ORANGE[4])
    return im
