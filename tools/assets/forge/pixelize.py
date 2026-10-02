"""Raw 3D renders -> game-scale pixel sprites (crop, box-downscale, palette-quantise, outline). Usage: pixelize.py"""
import os, sys, glob, json
from PIL import Image, ImageEnhance, ImageFilter
HERE = os.path.dirname(__file__); RAW = os.path.join(HERE, '..', 'out', 'lib_raw'); LIB = os.path.join(HERE, '..', 'library')
os.makedirs(LIB, exist_ok=True)
# target heights in game pixels (by name prefix)
H = {'cabinet': 46, 'console': 32, 'tank': 40, 'crate': 28, 'generator': 36, 'locker': 42, 'reactor': 96, 'crystal': 30,
     'tentacle': 58, 'rosette': 26, 'mushroom': 20, 'incubator': 52, 'flower': 24, 'asteroid': 40, 'ship_freighter': 72, 'ship_explorer': 54}
OUTLINE = (12, 12, 18, 255)
def pixelize(path, h=None, colors=22, outline=True, sat=1.25):
    name = os.path.splitext(os.path.basename(path))[0]
    h = h or next((v for k, v in sorted(H.items(), key=lambda kv: -len(kv[0])) if name.startswith(k)), 32)
    im = Image.open(path).convert('RGBA'); im = im.crop(im.getbbox())
    w = max(2, round(im.width * h / im.height)); im = im.resize((w, h), Image.BOX)
    a = im.split()[3].point(lambda v: 255 if v > 110 else 0)
    rgb = ImageEnhance.Color(im.convert('RGB')).enhance(sat); rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
    rgb = rgb.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB'); rgb.putalpha(a)
    if outline:
        out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0)); m = Image.new('L', (w + 2, h + 2), 0); m.paste(a, (1, 1)); m = m.filter(ImageFilter.MaxFilter(3))
        ol = Image.new('RGBA', out.size, OUTLINE); ol.putalpha(m); out.alpha_composite(ol); out.alpha_composite(rgb, (1, 1)); rgb = out
    return name, rgb
if __name__ == '__main__':
    man = {}
    for f in sorted(glob.glob(os.path.join(RAW, '*.png'))):
        n, im = pixelize(f); im.save(os.path.join(LIB, n + '.png')); man[n] = {'w': im.width, 'h': im.height}
    json.dump(man, open(os.path.join(LIB, 'manifest.json'), 'w'), indent=1); print(len(man), 'sprites')
