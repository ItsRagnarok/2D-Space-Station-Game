"""Native-resolution pixel UI: every element is drawn on the game grid (no smoothing, no rounded corners)."""
import os
from PIL import Image, ImageDraw, ImageFont
FD = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'PixelifySans.ttf')
_f = {}
FS = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Silkscreen.ttf')
def F(sz):
    if sz not in _f: _f[sz] = ImageFont.truetype(FD, 10 if sz <= 9 else sz)   # Silkscreen is built for 8 px; Pixelify for larger (has Romanian diacritics)
    return _f[sz]
def ptext(im, x, y, txt, col=(235, 255, 245), size=8, anchor='l'):
    d = ImageDraw.Draw(im); d.fontmode = '1'; f = F(size)
    if anchor == 'r': x = x - int(d.textlength(txt, font=f))
    elif anchor == 'm': x = x - int(d.textlength(txt, font=f)) // 2
    d.text((int(x), int(y)), txt, font=f, fill=tuple(col)[:3] + (255,))
def pbox(im, x0, y0, x1, y1, acc=(47, 229, 190), fill=(4, 22, 24)):
    d = ImageDraw.Draw(im); d.rectangle((x0, y0, x1, y1), fill=fill + (255,)); d.rectangle((x0, y0, x1, y1), outline=acc + (255,))
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)): d.point((cx, cy), fill=fill + (255,))      # notched corners
    dark = tuple(c // 3 for c in acc); d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), outline=dark + (255,))
def pbar(im, x, y, w, h, frac, col, back=(6, 30, 28)):
    d = ImageDraw.Draw(im); d.rectangle((x, y, x + w, y + h), fill=back + (255,), outline=col + (255,))
    if frac > 0: d.rectangle((x + 1, y + 1, x + 1 + max(0, int((w - 2) * frac)), y + h - 1), fill=col + (255,))
def psq(im, x, y, col, s=5): ImageDraw.Draw(im).rectangle((x, y, x + s - 1, y + s - 1), fill=col + (255,), outline=(0, 0, 0, 255))
def ptri(im, x, y, col, s=7):
    d = ImageDraw.Draw(im)
    for i in range(s // 2 + 1): d.line((x + s // 2 - i, y + i * 2, x + s // 2 + i, y + i * 2), fill=col + (255,)); d.line((x + s // 2 - i, y + i * 2 + 1, x + s // 2 + i, y + i * 2 + 1), fill=col + (255,))
def pcircle(im, x, y, col, filled=False, s=7):
    d = ImageDraw.Draw(im); d.ellipse((x, y, x + s - 1, y + s - 1), outline=col + (255,), fill=(col + (255,)) if filled else None)
def pcaption(im, title, l1, l2, acc=(47, 229, 190), h=38):
    W, H = im.size; d = ImageDraw.Draw(im); d.rectangle((0, H - h, W, H), fill=(3, 14, 16, 255)); d.line((0, H - h, W, H - h), fill=acc + (255,))
    ptext(im, 6, H - h + 3, title, (255, 255, 255), 12); ptext(im, 6, H - h + 16, l1, (205, 232, 228), 10); ptext(im, 6, H - h + 26, l2, (205, 232, 228), 10)
