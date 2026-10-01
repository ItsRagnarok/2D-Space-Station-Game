"""HUD icons (separate PNGs): gear, titanium crystal, circuit chip, credits coin, ship blueprint."""
from core import *

def icon(rows, pal):
    return ascii_sprite(rows, pal)

G = rgb('#2fe58a'); GD = rgb('#145a3a'); T = rgb('#8cf2e6')

def gear():
    rows = ["....GG....GG....",
            "...GGGG..GGGG...",
            "..GGGGGGGGGGGG..",
            "...GGGDDDDGGG...",
            ".GGGGD....DGGGG.",
            ".GGGD......DGGG.",
            "..GGD......DGG..",
            "..GGD......DGG..",
            ".GGGD......DGGG.",
            ".GGGGD....DGGGG.",
            "...GGGDDDDGGG...",
            "..GGGGGGGGGGGG..",
            "...GGGG..GGGG...",
            "....GG....GG...."]
    return icon(rows, {'G': G, 'D': GD})

def crystal():
    rows = ["......BB......",
            ".....BWWB.....",
            "....BWWLWB....",
            "...BWWLLLWB...",
            "..BWLLLLLLWB..",
            "..BLLLLLLLLB..",
            "..BLLLMMLLLB..",
            "..BLLMMMMLLB..",
            "...BLMMMMLB...",
            "....BLMMLB....",
            ".....BLLB.....",
            "......BB......"]
    return icon(rows, {'B': BLUE[1], 'W': BLUE[5], 'L': BLUE[4], 'M': BLUE[3]})

def chip():
    rows = ["..o.o.o.o.o..",
            ".yyyyyyyyyyy.",
            "oyDDDDDDDDDyo",
            ".yDyyyyyyyDy.",
            "oyDyDDDDDyDyo",
            ".yDyDyyyDyDy.",
            "oyDyDyOyDyDyo",
            ".yDyDyyyDyDy.",
            "oyDyDDDDDyDyo",
            ".yDyyyyyyyDy.",
            "oyDDDDDDDDDyo",
            ".yyyyyyyyyyy.",
            "..o.o.o.o.o.."]
    return icon(rows, {'y': ORANGE[4], 'D': ORANGE[1], 'o': ORANGE[3], 'O': ORANGE[5]})

def coin():
    rows = ["....yyyyyy....",
            "..yyYYYYYYyy..",
            ".yYYYooooYYYy.",
            ".yYYoYYYYoYYy.",
            "yYYoYYooYYoYYy",
            "yYYoYoYYoYoYYy",
            "yYYoYoYYoYoYYy",
            "yYYoYYooYYoYYy",
            ".yYYoYYYYoYYy.",
            ".yYYYooooYYYy.",
            "..yyYYYYYYyy..",
            "....yyyyyy...."]
    return icon(rows, {'y': ORANGE[2], 'Y': ORANGE[4], 'o': ORANGE[3]})

def ship_blueprint():
    c = TEAL[3]; d = TEAL[1]
    rows = ["..............CC..............",
            ".............CddC.............",
            "............CddddC............",
            "...........CdCCCCdC...........",
            "..CC......CdC....CdC......CC..",
            ".CddCCCCCCdC......CdCCCCCCddC.",
            "CddddddddddCCCCCCCCdddddddddC.",
            ".CCCCCCCCCCddddddddCCCCCCCCCC.",
            "..........CdddddddC...........",
            "..CCCCCCCCCdCCCCCCdCCCCCCCC...",
            ".CddddddddCdC....CdCddddddddC.",
            "..CCCCCCCCCCC....CCCCCCCCCC...",
            "...........CCCCCCCC...........",
            "..............CC..............",]
    return icon(rows, {'C': c, 'd': d})

ALL = dict(gear=gear, crystal=crystal, chip=chip, coin=coin, ship_blueprint=ship_blueprint)

if __name__ == '__main__':
    import os
    os.makedirs('../out/icons', exist_ok=True)
    for k, f in ALL.items():
        im = f(); im.save(f'../out/icons/{k}.png'); print(k, im.size)
