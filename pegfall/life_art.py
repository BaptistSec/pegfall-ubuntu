from functools import lru_cache
import pygame
from . import art_style as a
WALL = (239, 205, 144)
ROOF = (190, 112, 76)
EDGE = (110, 135, 105)
TIMBER = (195, 137, 77)
PALE = (255, 230, 174)
GLASS = (96, 188, 194)

def _home(s, x, y, w=140, h=94, roof=False, door=False, window=False, step=False, clean=False, closed=False):
    wall = (255, 225, 167) if clean else WALL
    a.rect(s, wall, (x, y, w, h))
    a.poly(s, ROOF, [(x - 7, y), (x + w * 0.47, y - 40), (x + w + 7, y), (x + w, y + 5), (x + w * 0.47, y - 30), (x, y + 6)])
    a.line(s, PALE, (x - 4, y - 1), (x + w * 0.47, y - 37), 1)
    if not roof:
        a.poly(s, (193, 191, 155), [(x + w * 0.52, y - 31), (x + w * 0.7, y - 18), (x + w * 0.63, y - 8), (x + w * 0.46, y - 20)])
    else:
        a.poly(s, (186, 176, 139), [(x + w * 0.47, y - 31), (x + w * 0.7, y - 15), (x + w * 0.63, y - 8), (x + w * 0.42, y - 22)])
        a.line(s, PALE, (x + w * 0.48, y - 26), (x + w * 0.64, y - 14), 1)
    dx = x + 25
    dy = y + h - 54
    a.rect(s, EDGE, (dx, dy, 29, 54), rad=2)
    if not door:
        a.poly(s, (169, 169, 136), [(dx + 2, dy + 2), (dx + 27, dy + 5), (dx + 24, dy + 53), (dx + 2, dy + 53)])
        a.line(s, PALE, (dx + 7, dy + 13), (dx + 20, dy + 38), 2)
    else:
        a.rect(s, TIMBER, (dx + 2, dy + 2, 25, 52), rad=1)
        for px in [dx + 9, dx + 18]:
            a.line(s, (198, 181, 139), (px, dy + 4), (px, dy + 51), 0.8)
        a.circle(s, EDGE, (dx + 22, dy + 30), 1.3)
    wx = x + w - 52
    wy = y + 29
    a.rect(s, EDGE, (wx, wy, 35, 29))
    a.rect(s, GLASS, (wx + 3, wy + 3, 29, 23))
    if not window:
        a.poly(s, TIMBER, [(wx - 1, wy + 4), (wx + 36, wy + 12), (wx + 36, wy + 19), (wx - 1, wy + 11)])
    else:
        a.line(s, PALE, (wx + 17, wy + 3), (wx + 17, wy + 26), 1.3)
        a.line(s, PALE, (wx + 3, wy + 14), (wx + 32, wy + 14), 1.3)
    if step:
        a.poly(s, (185, 189, 157), [(dx - 6, y + h), (dx + 35, y + h), (dx + 42, y + h + 7), (dx - 12, y + h + 7)])
        a.line(s, PALE, (dx - 5, y + h + 1), (dx + 34, y + h + 1), 1)
    if closed:
        a.rect(s, (181, 173, 136), (wx, wy, 35, 29))
        for py in [wy + 7, wy + 15, wy + 23]:
            a.line(s, (201, 189, 150), (wx + 2, py), (wx + 33, py), 1)
        a.line(s, PALE, (dx + 3, dy + 15), (dx + 26, dy + 40), 2)

def _bench(s, x, y, strong=False, vise=False):
    a.line(s, TIMBER, (x, y), (x + 103, y if strong else y + 4), 5)
    for px in [x + 9, x + 94]:
        a.line(s, TIMBER, (px, y + 3), (px + (-3 if px == x + 9 else 3), y + 28), 4 if strong else 2)
    if strong:
        a.line(s, PALE, (x, y - 2), (x + 103, y - 2), 1)
        a.line(s, TIMBER, (x + 11, y + 20), (x + 93, y + 20), 3)
    if vise:
        a.rect(s, EDGE, (x + 33, y - 9, 12, 13))
        a.line(s, PALE, (x + 35, y - 12), (x + 35, y + 1), 2)
        a.line(s, EDGE, (x + 30, y - 5), (x + 49, y - 5), 2)

def _tools(s, x, y, rack=False, sound=False, single=False):
    if rack:
        for py in [y, y + 26]:
            a.line(s, TIMBER, (x, py), (x + 76, py), 3)
        for px in [x + 3, x + 73]:
            a.line(s, TIMBER, (px, y - 5), (px, y + 49), 2)
    for (j, (px, dy)) in enumerate([(x + 16, 0), (x + 44, 5)]):
        a.line(s, TIMBER, (px, y + dy - 3), (px - 6, y + dy + 37), 2)
        a.line(s, (149, 165, 140) if sound and (not single or j == 0) else TIMBER, (px - 9, y + dy + 2), (px + 10, y + dy + 7), 4 if sound and (not single or j == 0) else 2)

def _shelf(s, x, y, stock=False, drawers=False):
    for px in [x, x + 91]:
        a.line(s, TIMBER, (px, y), (px, y + 55), 3)
    for py in [y + 10, y + 36, y + 55]:
        a.line(s, TIMBER, (x, py), (x + 91, py), 3)
    if stock:
        for (px, py, w) in [(x + 7, y - 2, 18), (x + 31, y + 14, 28), (x + 63, y + 16, 20)]:
            a.rect(s, (191, 180, 140), (px, py, w, 18))
            a.line(s, PALE, (px + 2, py + 2), (px + w - 2, py + 2), 1)
    if drawers:
        for px in [x + 5, x + 36, x + 66]:
            a.rect(s, (185, 172, 131), (px, y + 39, 24, 12))
            a.line(s, EDGE, (px + 9, y + 44), (px + 16, y + 44), 1)

def _machine(s, x, y):
    _bench(s, x, y + 36, True)
    a.circle(s, EDGE, (x + 66, y + 12), 20, 2)
    for (dx, dy) in [(0, 16), (14, 8), (14, -8)]:
        a.line(s, EDGE, (x + 66 - dx, y + 12 - dy), (x + 66 + dx, y + 12 + dy), 1)
    a.circle(s, TIMBER, (x + 66, y + 12), 3)
    a.rect(s, (178, 174, 139), (x + 13, y + 5, 27, 22), rad=3)
    a.line(s, PALE, (x + 17, y + 8), (x + 35, y + 8), 1)
    a.line(s, TIMBER, (x + 13, y + 27), (x + 85, y + 27), 4)

def _goods(s, x, y, n=3, marked=False):
    for i in range(n):
        px = x + i % 3 * 30
        py = y - i // 3 * 18
        a.rect(s, (194, 180, 135), (px, py, 27, 17), rad=1)
        a.line(s, PALE, (px + 2, py + 3), (px + 25, py + 3), 1)
        a.line(s, TIMBER, (px + 7, py + 1), (px + 7, py + 16), 1)
        if marked:
            a.poly(s, EDGE, [(px + 16, py + 5), (px + 20, py + 8), (px + 16, py + 12), (px + 12, py + 8)], 0.8)

def _mark(s, x, y):
    a.rect(s, (190, 177, 137), (x, y, 62, 20), rad=1)
    a.poly(s, EDGE, [(x + 12, y + 4), (x + 18, y + 10), (x + 12, y + 16), (x + 6, y + 10)], 1)
    for (off, w) in [(25, 27), (25, 19)]:
        a.line(s, (161, 166, 132), (x + off, y + 7 + (w == 19) * 6), (x + off + w, y + 7 + (w == 19) * 6), 1)

def _cart(s, x=799, y=568, goods=0, bedding=False):
    a.line(s, TIMBER, (x - 6, y), (x + 100, y), 3)
    a.line(s, TIMBER, (x + 99, y), (x + 125, y - 12), 2.5)
    a.rect(s, (184, 171, 130), (x, y - 19, 94, 18), rad=1)
    a.line(s, PALE, (x + 2, y - 17), (x + 91, y - 17), 1)
    for px in [x + 14, x + 79]:
        a.circle(s, EDGE, (px, y + 14), 10)
        a.circle(s, PALE, (px, y + 14), 7)
        for (dx, dy) in [(6, 5), (6, -5)]:
            a.line(s, EDGE, (px - dx, y + 14 - dy), (px + dx, y + 14 + dy), 1)
        a.circle(s, TIMBER, (px, y + 14), 2)
    if goods:
        _goods(s, x + 3, y - 36, goods, True)
    if bedding:
        a.rect(s, (191, 199, 167), (x + 23, y - 34, 51, 15), rad=5)
        a.line(s, (165, 180, 148), (x + 47, y - 34), (x + 47, y - 19), 2)
        a.rect(s, TIMBER, (x + 10, y - 28, 19, 8), rad=3)

def _ground(s, city=False, dusk=False):
    if city:
        a.rect(s, (151, 211, 230), (28, 79, 904, 641))
        a.circle(s, (255, 216, 108), (790, 145), 31)
        for (x, y, w, h) in [(30, 321, 72, 113), (94, 285, 80, 149), (174, 348, 61, 86), (742, 338, 66, 96), (798, 273, 72, 161), (864, 304, 68, 130)]:
            col = (137, 187, 187)
            a.rect(s, col, (x, y, w, h))
            a.poly(s, col, [(x - 3, y), (x + w * 0.5, y - 26), (x + w + 3, y)])
            a.rect(s, (172, 209, 200), (x + w * 0.65, y - 37, 9, 25))
        a.poly(s, (216, 207, 160), [(28, 438), (242, 420), (480, 429), (737, 421), (932, 437), (932, 720), (28, 720)])
        a.line(s, (202, 206, 179), (30, 611), (930, 611), 1)
    else:
        a.poly(s, (215, 218, 145), [(28, 413), (218, 422), (480, 410), (730, 422), (932, 415), (932, 720), (28, 720)])
        a.line(s, (198, 202, 164), (29, 610), (930, 610), 1)
    if dusk:
        overlay = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        a.rect(overlay, (192, 160, 128, 19), (28, 79, 904, 641))
        s.blit(overlay, (0, 0))
    for (aa, bb) in [((40, 625), (194, 615)), ((788, 622), (916, 633)), ((55, 669), (151, 659)), ((826, 674), (923, 663))]:
        a.line(s, (202, 204, 173), aa, bb, 0.8)

def _village(s, stage):
    _home(s, 43, 455, 140, 90, stage >= 1, stage >= 2, stage >= 3, stage >= 4)
    _home(s, 782, 453, 142, 95, True, True, True, True)
    a.rect(s, (181, 184, 148), (823, 488, 54, 60))
    a.line(s, PALE, (850, 490), (850, 546), 1)
    if stage >= 5:
        _bench(s, 792, 542, True, stage >= 7)
    if stage >= 6:
        _tools(s, 801, 476, True, True)
    if stage >= 8:
        _shelf(s, 775, 484, True)
    if stage >= 9:
        _goods(s, 858, 525, 2)
    if stage >= 10:
        a.rect(s, (211, 203, 164), (811, 432, 68, 19), rad=1)
        a.circle(s, PALE, (808, 459), 4, 1.5)
        a.line(s, PALE, (812, 459), (829, 459), 2)
        a.line(s, PALE, (824, 459), (824, 464), 2)
    _cart(s, 52, 590)

def _shop(s, stage):
    _home(s, 43, 455, 154, 96, True, stage >= 1, True, True, closed=stage >= 10)
    a.rect(s, EDGE, (112, 484, 69, 49))
    a.rect(s, GLASS, (115, 487, 63, 43))
    if stage < 2:
        a.poly(s, TIMBER, [(111, 489), (182, 509), (182, 516), (111, 496)])
    elif stage < 10:
        a.line(s, PALE, (146, 488), (146, 530), 2)
        a.line(s, PALE, (116, 518), (177, 518), 2)
        a.line(s, (179, 180, 142), (124, 524), (137, 524), 4)
    else:
        a.rect(s, (181, 173, 136), (112, 484, 69, 49))
        for y in [494, 505, 516, 527]:
            a.line(s, PALE, (115, y), (178, y), 1)
    if 4 <= stage < 10:
        _mark(s, 84, 460)
    if stage < 10:
        _bench(s, 791, 541, stage >= 3)
        if stage >= 5:
            _shelf(s, 789, 485, True, stage >= 6)
        if stage >= 7:
            _machine(s, 792, 494)
        if stage >= 8:
            _goods(s, 806, 550, 3 if stage == 8 else 6, True)
    _cart(s, 795, 582, 0, stage >= 9)
    if stage >= 10:
        a.poly(s, (203, 203, 170), [(790, 547), (913, 547), (913, 552), (790, 552)])
        a.line(s, EDGE, (68, 499), (94, 529), 2)
        _mark(s, 804, 550)

def _city_shared(s, stage):
    _home(s, 43, 455, 142, 94, stage >= 2, stage >= 1, stage >= 3, stage >= 4)
    a.rect(s, (205, 207, 179), (780, 446, 144, 100))
    a.line(s, (193, 199, 171), (781, 446), (923, 446), 3)
    _bench(s, 790, 548, stage >= 5)
    if stage >= 6:
        _tools(s, 797, 497, stage >= 7, True, True)
    else:
        _tools(s, 797, 497, False, False)
    if stage >= 8:
        _shelf(s, 830, 556, True)
    if stage >= 9:
        _goods(s, 794, 519, 2)
    if stage >= 10:
        _mark(s, 807, 459)
    _cart(s, 53, 591, bedding=stage < 4)

def _city_work(s, stage):
    _home(s, 43, 455, 142, 94, True, True, True, True, stage >= 9)
    if stage >= 8:
        a.rect(s, (216, 211, 177), (53, 422, 123, 33))
        a.poly(s, ROOF, [(46, 423), (113, 391), (183, 423)])
        for x in [75, 133]:
            a.rect(s, GLASS, (x, 432, 20, 19))
            a.line(s, PALE, (x + 10, 433), (x + 10, 449), 1)
    if stage >= 9:
        a.rect(s, TIMBER, (129, 515, 51, 6))
        a.poly(s, (166, 188, 148), [(134, 515), (137, 503), (145, 511), (151, 498), (157, 510), (166, 502), (173, 515)])
    if stage >= 6:
        _home(s, 778, 455, 146, 91, stage >= 7, True, True, True)
        a.rect(s, (183, 187, 151), (814, 484, 55, 62))
        a.line(s, PALE, (841, 486), (841, 545), 1)
    else:
        a.rect(s, (205, 207, 179), (780, 446, 144, 100))
        a.line(s, (193, 199, 171), (781, 446), (923, 446), 3)
    _mark(s, 807, 459)
    _bench(s, 790, 533 if stage >= 7 else 548, True, stage >= 1)
    if stage >= 2:
        a.line(s, TIMBER, (801, 551), (882, 568), 3)
    if stage < 4:
        _tools(s, 797, 497, True, True, True)
        _shelf(s, 830, 556, True, stage >= 3)
    else:
        _machine(s, 792, 487)
        _shelf(s, 830, 556, True, True)
    if stage >= 5:
        _goods(s, 807, 560, 3, True)
    else:
        _goods(s, 794, 519, 2)
    if stage < 10:
        _cart(s, 53, 591)
    else:
        _cart(s, 797, 593, goods=2)
        for x in [44, 144, 244]:
            a.line(s, (178, 177, 138), (x, 587), (x, 625), 4)
        for y in [598, 614]:
            a.line(s, (181, 180, 143), (44, y), (244, y), 3)

@lru_cache(maxsize=61)
def background(chapter, stage):
    if chapter == 0:
        return a.background(stage)
    stage = max(0, min(10, int(stage)))
    s = pygame.transform.scale(a.background(0), (960 * a.SCALE, 720 * a.SCALE))
    s.set_clip(pygame.Rect(28 * a.SCALE, 79 * a.SCALE, 904 * a.SCALE, 641 * a.SCALE))
    _ground(s, city=chapter >= 3, dusk=chapter == 2 and stage >= 8)
    (_village, _shop, _city_shared, _city_work)[chapter - 1](s, stage)
    s.set_clip(None)
    return a.finish(s, 960, 720)
