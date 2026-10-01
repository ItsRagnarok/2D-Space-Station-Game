"""App icons (PWA / apple-touch-icon): the blue crystal on a dark teal-glow background. Nearest-neighbour scaled."""
import os
from core import *
import hydroponics
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'public', 'pwa'))
os.makedirs(OUT, exist_ok=True)
cr = hydroponics.crystal(3, 'blue', 0); cr = cr.crop(cr.getbbox())
def make(size):
    bg = new(size, size, (3, 6, 14, 255))
    cx = cy = size / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy) / (size * .55)
            if d < 1:
                lvl = (1 - d) ** 1.6 + (bay(x // 4, y // 4) - .5) * .2
                if lvl > .5: bg.putpixel((x, y), (10, 52, 80, 255))
                elif lvl > .28: bg.putpixel((x, y), (6, 30, 52, 255))
    k = max(1, int(size * .66 // max(cr.width, cr.height)))
    sp = upscale(cr, k)
    bg.alpha_composite(sp, ((size - sp.width) // 2, (size - sp.height) // 2 + size // 40))
    return bg
for s in (180, 192, 512): make(s).convert('RGB').save(os.path.join(OUT, f'icon-{s}.png'))
print('icons ok')
