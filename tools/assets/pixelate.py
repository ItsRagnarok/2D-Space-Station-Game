"""Turn a raw Blender render into pixel art: crop, downscale, quantize to a fixed palette.

Usage: python3 pixelate.py in.png out.png [target_width] [palette_colors]
"""
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
tw = int(sys.argv[3]) if len(sys.argv) > 3 else 48
ncol = int(sys.argv[4]) if len(sys.argv) > 4 else 16

im = Image.open(src).convert("RGBA")
bbox = im.getbbox()
im = im.crop(bbox)
th = max(1, round(im.height * tw / im.width))
small = im.resize((tw, th), Image.BOX)

# Hard alpha so edges stay crisp (no half-transparent pixels).
alpha = small.getchannel("A").point(lambda a: 255 if a > 110 else 0)
rgb = small.convert("RGB").quantize(colors=ncol, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
out = rgb.convert("RGBA")
out.putalpha(alpha)
out.save(dst)
print("sprite", out.size, "colors<=", ncol)
