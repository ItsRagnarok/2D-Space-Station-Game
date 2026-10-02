"""Cut AI pieces on flat background into separate pixel sprites at game scale."""
import sys, os
from PIL import Image
from scipy import ndimage
import numpy as np
HERE = os.path.dirname(__file__); P = os.environ.get('PIECES_DIR') or os.path.join(HERE, '..', 'out', 'hangar', 'pieces')
def cut(name, target_h=34):
    im = Image.open(os.path.join(P, name + '.png')).convert('RGB'); a = np.array(im).astype(int)
    bg = np.median(a[300:320, 250:290].reshape(-1, 3), axis=0)
    a[:24] = bg; a[-24:] = bg; a[:, :24] = bg; a[:, -24:] = bg
    fg = (np.abs(a - bg).sum(axis=2) > 40)
    fg = ndimage.binary_closing(fg, iterations=3); lab, n = ndimage.label(fg); out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if h < 60 or w < 60: continue
        m = ndimage.binary_fill_holes(lab[sl] == i + 1)
        crop = np.dstack([a[sl].astype(np.uint8), (m * 255).astype(np.uint8)]); c = Image.fromarray(crop, 'RGBA')
        s = target_h / h; c = c.resize((max(1, round(w * s)), target_h), Image.BOX)
        al = c.split()[3].point(lambda v: 255 if v > 128 else 0); c.putalpha(al)
        f = os.path.join(P, f'{name}_{len(out)}.png'); c.save(f); out.append(f)
    return out
if __name__ == '__main__':
    for n in sys.argv[1:]: print(n, cut(n))
