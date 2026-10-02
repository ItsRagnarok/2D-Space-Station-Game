"""Global palette for ALL scenes + nearest-neighbour upscale. Reads out/scenes/*_raw.png (native res, UI already on the grid)."""
import os, glob, sys
from PIL import Image
HERE = os.path.dirname(__file__); S = os.path.join(HERE, '..', 'out', 'scenes'); K = 3
N = int(sys.argv[1]) if len(sys.argv) > 1 else 96
raws = sorted(glob.glob(os.path.join(S, '*_raw.png'))); ims = [Image.open(f).convert('RGB') for f in raws]
W = max(i.width for i in ims); mosaic = Image.new('RGB', (W, sum(i.height for i in ims)))
y = 0
for i in ims: mosaic.paste(i, (0, y)); y += i.height
pal = mosaic.quantize(colors=N, method=Image.MEDIANCUT, dither=Image.NONE)
# palette strip for the catalog
sw = Image.new('RGB', (N, 1)); sw.putdata([tuple(pal.getpalette()[i * 3:i * 3 + 3]) for i in range(N)]); sw.save(os.path.join(S, 'palette.png'))
for f, im in zip(raws, ims):
    q = im.quantize(palette=pal, dither=Image.NONE).convert('RGB'); n = os.path.basename(f).replace('_raw.png', '')
    q.save(os.path.join(S, n + '_native.png')); q.resize((q.width * K, q.height * K), Image.NEAREST).save(os.path.join(S, n + '.png'))
    print(n, q.size, len(set(q.getdata())), 'colours')
