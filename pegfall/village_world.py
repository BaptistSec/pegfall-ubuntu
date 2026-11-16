from functools import lru_cache
from pathlib import Path
import math
import pygame
from . import art_style as a, farm_world
from .narrative import village_day
SKY = (195, 212, 199)
INK = (87, 105, 96)
STONE = (189, 183, 158)
WALL = (222, 207, 166)
WOOD = (151, 116, 80)
PALE = (241, 222, 179)
TEAL = (113, 151, 141)

def text(s, words, x, y, size=13, col=INK):
    font = pygame.font.Font(str(Path(__file__).resolve().parent / 'assets/fonts/LiberationSans-Bold.ttf'), round(size * a.SCALE))
    s.blit(font.render(words, True, col), (round(x * a.SCALE), round(y * a.SCALE)))

def business_sign(s, x, y, w, h, size):
    font = pygame.font.Font(str(Path(__file__).resolve().parent / 'assets/fonts/LiberationSans-Bold.ttf'), round(size * a.SCALE))
    im = font.render('THE BRASS LANTERN', True, INK)
    factor = min(1, w * a.SCALE / im.get_width(), h * a.SCALE / im.get_height())
    im = pygame.transform.smoothscale(im, (max(1, round(im.get_width() * factor)), max(1, round(im.get_height() * factor))))
    s.blit(im, im.get_rect(center=(round((x + w / 2) * a.SCALE), round((y + h / 2) * a.SCALE))))

def window(s, x, y, w, h, lit=False):
    a.rect(s, WOOD, (x - 2, y - 2, w + 4, h + 4), rad=1)
    a.rect(s, (236, 209, 144) if lit else (148, 179, 169), (x, y, w, h))
    a.line(s, PALE, (x + w / 2, y), (x + w / 2, y + h), 1.5)
    a.line(s, PALE, (x, y + h * 0.52), (x + w, y + h * 0.52), 1.5)
    a.line(s, (173, 158, 121), (x - 4, y + h + 3), (x + w + 4, y + h + 3), 2)

def crate(s, x, y, w=25, h=19):
    a.rect(s, (179, 149, 105), (x, y, w, h), rad=1)
    for yy in [y + 3, y + h - 3]:
        a.line(s, PALE, (x + 2, yy), (x + w - 2, yy), 1)
    a.line(s, WOOD, (x + 4, y + 4), (x + w - 4, y + h - 4), 1)

def cart(s, x, y):
    a.line(s, WOOD, (x - 4, y), (x + 66, y), 3)
    for dx in [7, 49]:
        a.circle(s, INK, (x + dx, y + 10), 8, 1.5)
        for off in [-4, 4]:
            a.line(s, WOOD, (x + dx - off, y + 6), (x + dx + off, y + 14), 1)
    a.rect(s, (167, 138, 95), (x, y - 19, 60, 18), rad=1)
    a.line(s, WOOD, (x + 57, y - 7), (x + 82, y - 19), 2)

def bunting(s, x1, y1, x2, y2):
    a.line(s, INK, (x1, y1), (x2, y2), 0.7)
    for n in range(1, 11):
        t = n / 11
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t + 5 * math.sin(t * math.pi)
        a.poly(s, [(174, 130, 107), (172, 158, 102), (115, 150, 146)][n % 3], [(x - 4, y), (x + 4, y), (x, y + 9)])

def village_roofscape(s):
    for (k, (x, y, w, h)) in enumerate([(28, 413, 73, 68), (108, 393, 69, 88), (183, 430, 70, 51), (698, 418, 76, 65), (781, 391, 72, 92), (862, 425, 71, 58)]):
        wall = [(180, 185, 162), (190, 188, 162), (173, 182, 160)][k % 3]
        a.poly(s, (145, 161, 143), [(x + w - 9, y + 8), (x + w + 5, y + 1), (x + w + 5, y + h), (x + w - 9, y + h)])
        a.rect(s, wall, (x, y, w - 9, h))
        a.poly(s, (155, 143, 119), [(x - 4, y), (x + w * 0.43, y - 25), (x + w + 5, y + 1), (x + w - 3, y + 7), (x + w * 0.43, y - 16), (x + 3, y + 7)])
        a.line(s, (197, 181, 144), (x + 2, y + 6), (x + w - 4, y + 6), 1.4)
        a.rect(s, (167, 161, 134), (x + 9, y - 18, 9, 20))
        a.rect(s, (151, 150, 126), (x + 7, y - 20, 13, 3))
        for xx in [x + 12, x + 39]:
            if xx + 12 < x + w - 7:
                a.rect(s, (138, 158, 143), (xx, y + 19, 12, 20))
                a.line(s, (208, 203, 162), (xx + 5, y + 19), (xx + 5, y + 38), 0.8)
                a.line(s, (153, 155, 126), (xx - 2, y + 40), (xx + 15, y + 40), 1.1)
        for n in range(4):
            xx = x + 5 + n * 14
            yy = y - 3 - abs(xx - (x + w * 0.43)) * 0.36
            a.line(s, (176, 160, 129), (xx, yy), (xx + 8, yy + 3), 0.8)

def village_shop_depth(s, level):
    if level >= 26:
        a.poly(s, (153, 131, 98), [(746, 604), (926, 604), (935, 613), (737, 613)])
        a.line(s, (222, 206, 164), (746, 605), (927, 605), 1.8)
        a.poly(s, (99, 122, 109), [(756, 540), (765, 544), (765, 581), (756, 589)])
        a.line(s, (210, 187, 139), (754, 596), (922, 596), 3)
        a.line(s, (137, 121, 87), (754, 601), (922, 601), 1.5)
        for n in range(7):
            xx = 752 + n * 25
            a.line(s, (195, 159, 116), (xx, 464 - abs(xx - 832) * 0.12), (xx + 12, 468 - abs(xx - 832) * 0.12), 0.8)
    else:
        a.poly(s, (153, 135, 101), [(748, 607), (922, 607), (929, 613), (741, 613)])

def village_lanes(s):
    for mirror in [False, True]:

        def pt(x, y):
            return (960 - x if mirror else x, y)

        def poly(col, nodes):
            a.poly(s, col, [pt(x, y) for (x, y) in nodes])
        poly((177, 177, 145), [(218, 472), (251, 476), (255, 533), (217, 555)])
        poly((192, 190, 153), [(219, 483), (241, 486), (246, 532), (217, 547)])
        poly((169, 174, 144), [(235, 456), (252, 463), (252, 505), (238, 495)])
        a.line(s, (207, 202, 162), pt(236, 459), pt(236, 493), 1)
        for yy in [481, 492, 507, 526]:
            a.line(s, (175, 177, 143), pt(219, yy), pt(245, yy + 4), 0.7)
        poly((180, 176, 140), [(28, 500), (42, 504), (42, 594), (28, 604)])
        a.line(s, (142, 151, 124), pt(31, 511), pt(31, 588), 1.4)
        a.line(s, (217, 203, 160), pt(34, 516), pt(34, 583), 0.7)
    a.poly(s, (196, 190, 154), [(28, 627), (255, 627), (298, 636), (932, 634), (932, 644), (282, 644), (248, 634), (28, 637)])
    for x in range(37, 924, 47):
        a.line(s, (181, 178, 145), (x, 634), (x + 27, 635), 0.65)
        a.line(s, (208, 200, 162), (x + 2, 638), (x + 22, 639), 0.5)

def village_joinery(s, level):
    if level < 26:
        for x in [752, 917]:
            a.line(s, (119, 113, 82), (x, 515), (x, 606), 2)
            a.line(s, (211, 184, 134), (x + 2, 517), (x + 2, 602), 0.8)
        for n in range(7):
            x = 760 + n * 24
            a.line(s, (142, 130, 93), (x, 589), (x, 603), 0.7)
    else:
        a.poly(s, (134, 124, 93), [(926, 478), (936, 487), (936, 603), (926, 606)])
        a.line(s, (187, 164, 119), (929, 490), (929, 599), 1)
        a.line(s, (231, 212, 166), (746, 604), (924, 604), 1.2)
        for x in [753, 918]:
            for y in [522, 575]:
                a.rect(s, (103, 119, 101), (x, y, 7, 2))
        if level >= 32:
            a.line(s, (221, 204, 160), (750, 488), (919, 488), 2)
            for x in [775, 812, 849, 886]:
                a.line(s, (173, 148, 106), (x, 592), (x, 603), 0.8)
        if level >= 35:
            a.poly(s, (172, 162, 122), [(927, 512), (938, 517), (938, 584), (927, 590)])
            a.line(s, (208, 192, 145), (930, 520), (930, 579), 0.7)

def village_business_growth(s, level):
    if level >= 23:
        a.poly(s, (185, 171, 127), [(741, 613), (932, 613), (933, 621), (739, 621)])
        a.line(s, (229, 211, 165), (744, 614), (928, 614), 1.5)
    if level >= 28:
        a.rect(s, (172, 153, 113), (749, 433, 175, 6))
    if level >= 29:
        a.rect(s, (199, 185, 142), (751, 408, 171, 26))
        for y in [414, 425]:
            a.line(s, (183, 170, 129), (753, y), (920, y), 0.7)
    if level >= 30:
        a.rect(s, (218, 201, 156), (751, 383, 171, 95))
        a.poly(s, (211, 195, 151), [(750, 384), (835, 350), (924, 384)])
        a.poly(s, (159, 119, 90), [(739, 384), (835, 344), (933, 384), (924, 392), (835, 356), (750, 392)])
        a.line(s, (230, 211, 165), (751, 395), (921, 395), 1.5)
        for x in [771, 796, 821, 846, 871, 896]:
            y = 357 + abs(x - 835) * 0.34
            a.line(s, (180, 140, 102), (x, y), (x + 9, y + 4), 0.7)
    if level >= 31:
        for x in [769, 861]:
            a.rect(s, (151, 142, 106), (x, 401, 41, 28))
            a.rect(s, (113, 145, 132), (x + 3, 404, 35, 22))
            a.line(s, (231, 213, 167), (x + 20, 404), (x + 20, 426), 1)
    if level >= 33:
        for x in [767, 859]:
            a.line(s, (175, 153, 109), (x, 431), (x + 46, 431), 2)
        a.line(s, (232, 213, 166), (750, 438), (923, 438), 2)
    if level >= 35:
        for x in [747, 916]:
            a.rect(s, (118, 151, 133), (x, 443, 9, 35))
            a.line(s, (221, 207, 157), (x, 445), (x, 476), 1)
        a.line(s, (163, 143, 100), (750, 443), (924, 443), 2)
    if level >= 37:
        a.rect(s, (128, 154, 135), (756, 452, 160, 19))
        for x in range(759, 916, 26):
            a.line(s, (207, 204, 158), (x, 454), (x, 469), 1)
        a.line(s, (233, 216, 167), (750, 494), (924, 494), 2)
    if level >= 39:
        a.line(s, (234, 214, 164), (739, 386), (932, 386), 1.5)
        for x in [750, 921]:
            a.rect(s, (189, 169, 122), (x, 397, 3, 37))

@lru_cache(maxsize=4)
def background(level):
    level = max(21, min(40, int(level)))
    d = village_day(level - 1)
    s = a.surface(960, 720)
    sky = (172, 191, 190) if d.rain else SKY
    a.rect(s, sky, (0, 0, 960, 720))
    a.circle(s, (243, 226, 175), (806, 174), 25)
    for (x, w, h) in [(29, 81, 66), (113, 66, 84), (182, 71, 55), (700, 76, 65), (779, 77, 80), (860, 74, 59)]:
        a.rect(s, (164, 185, 173), (x, 480 - h, w, h))
        a.poly(s, (141, 167, 158), [(x - 5, 480 - h), (x + w / 2, 460 - h), (x + w + 5, 480 - h)])
    village_roofscape(s)
    a.poly(s, (207, 200, 166), [(0, 494), (294, 488), (489, 508), (720, 490), (960, 497), (960, 720), (0, 720)])
    a.paving(s, (200, 192, 158), (187, 182, 150), (207, 199, 165))
    village_lanes(s)
    a.rect(s, (207, 193, 153), (43, 467, 170, 129))
    a.poly(s, (160, 119, 91), [(34, 468), (127, 421), (222, 468), (213, 476), (127, 434), (43, 476)])
    a.line(s, (227, 211, 169), (50, 478), (205, 478), 2)
    for x in [61, 81, 101, 121, 141, 161, 181, 201]:
        y = 435 + abs(x - 127) * 0.46
        a.line(s, (180, 140, 103), (x, y), (x + 7, y + 4), 0.7)
    a.line(s, WOOD, (43, 475), (212, 475), 1.5)
    a.line(s, (166, 155, 119), (204, 477), (204, 545), 1.4)
    for (x, y) in [(51, 493), (186, 483), (177, 537), (49, 581), (188, 590)]:
        a.line(s, (196, 179, 140), (x, y), (x + 8, y), 0.7)
        a.line(s, (235, 218, 178), (x + 2, y + 2), (x + 7, y + 2), 0.5)
    a.rect(s, WOOD, (58, 548, 35, 48), rad=1)
    a.line(s, PALE, (61, 553), (61, 590), 1)
    a.circle(s, INK, (87, 574), 1)
    for yy in [552, 588]:
        a.rect(s, INK, (59, yy, 9, 2), rad=0.4)
    a.line(s, PALE, (56, 546), (95, 546), 2)
    a.rect(s, (145, 167, 148), (111, 549, 82, 38))
    text(s, 'PROVISIONS', 113, 554, 10)
    for x in [117, 132, 149, 171]:
        crate(s, x, 574, 12, 10)
    a.rect(s, WOOD, (86, 480, 80, 51))
    a.rect(s, (112, 128, 115) if level < 29 else (224, 198, 133), (89, 483, 74, 45))
    if level >= 29:
        a.rect(s, (166, 141, 102), (94, 516, 46, 6))
        a.line(s, WOOD, (98, 521), (98, 527), 2)
        a.line(s, WOOD, (137, 521), (137, 527), 2)
        a.line(s, WOOD, (149, 503), (149, 526), 2)
        a.line(s, WOOD, (145, 515), (155, 515), 2)
        a.poly(s, PALE, [(145, 501), (153, 501), (157, 508), (141, 508)])
        a.rect(s, (186, 155, 111), (100, 489, 13, 14), 1)
        a.line(s, PALE, (102, 491), (110, 501), 0.7)
    for x in [89, 162]:
        a.line(s, PALE, (x, 483), (x, 528), 2)
    a.line(s, PALE, (126, 483), (126, 528), 2)
    a.line(s, PALE, (89, 505), (163, 505), 1.4)
    a.line(s, (169, 148, 108), (82, 533), (169, 533), 2)
    for xx in [87, 165]:
        a.line(s, WOOD, (xx, 485), (xx, 526), 0.65)
    for x in [44, 79, 113, 149, 185]:
        a.poly(s, (182, 175, 141), [(x, 599), (x + 26, 599), (x + 29, 606), (x - 2, 607)])
    a.line(s, (235, 217, 175), (45, 480), (45, 594), 1)
    a.line(s, (183, 172, 134), (210, 480), (210, 594), 1)
    a.line(s, (186, 174, 135), (45, 595), (211, 595), 1.3)
    for xx in [66, 78]:
        a.line(s, (124, 111, 81), (xx, 556), (xx, 587), 0.65)
        a.line(s, (189, 162, 113), (xx + 2, 558), (xx + 2, 584), 0.5)
    for (xx, yy) in [(49, 512), (190, 520), (178, 545), (97, 591)]:
        a.line(s, (195, 180, 140), (xx, yy), (xx + 8, yy), 0.6)
    if level >= 26:
        a.rect(s, (226, 205, 160), (746, 467, 180, 137))
        a.poly(s, (158, 114, 85), [(735, 468), (832, 427), (937, 468), (925, 476), (832, 440), (746, 476)])
        for xx in [766, 790, 814, 838, 862, 886, 910]:
            yy = 440 + abs(xx - 832) * 0.35
            a.line(s, (177, 131, 92), (xx, yy), (xx + 8, yy + 4), 0.7)
        a.line(s, WOOD, (744, 474), (927, 474), 1.7)
        a.rect(s, (156, 152, 116), (753, 490, 166, 109))
        a.rect(s, (103, 123, 111), (758, 496, 156, 96))
        a.line(s, (242, 221, 176), (748, 478), (748, 600), 0.9)
        a.line(s, (188, 170, 130), (923, 478), (923, 600), 1)
        a.line(s, (135, 134, 101), (760, 499), (760, 591), 1.1)
        a.line(s, (179, 185, 144), (762, 498), (909, 498), 0.65)
        for xx in [750, 920]:
            for yy in [513, 556, 594]:
                a.circle(s, WOOD, (xx, yy), 0.8)
        if level >= 32:
            a.rect(s, (113, 151, 141), (747, 478, 12, 125))
            a.rect(s, (113, 151, 141), (914, 478, 11, 125))
            a.line(s, PALE, (748, 480), (748, 601), 1)
        if level >= 35:
            a.rect(s, (186, 172, 128), (888, 514, 21, 59))
            a.rect(s, (82, 104, 95), (891, 518, 15, 55))
            a.line(s, PALE, (888, 514), (909, 514), 1)
    else:
        for x in [750, 920]:
            a.line(s, WOOD, (x, 483), (x, 604), 4)
        a.line(s, WOOD, (746, 483), (924, 483), 4)
    a.poly(s, (158, 152, 108) if level < 23 else (139, 160, 139), [(741, 480), (832, 467), (930, 480), (920, 495), (750, 495)])
    for x in range(757, 924, 19):
        a.line(s, (216, 205, 160), (x, 480), (x + 5, 491), 1.8)
    if level == 21:
        a.line(s, (108, 114, 91), (779, 482), (789, 490), 1)
        a.line(s, PALE, (784, 481), (780, 489), 1)
    if level >= 22:
        a.rect(s, (183, 154, 108), (747, 563, 177, 40))
        a.line(s, PALE, (750, 566), (920, 566), 1)
        for x in [751, 794, 837, 880, 920]:
            a.line(s, WOOD, (x, 568), (x, 600), 0.8)
    else:
        a.rect(s, (154, 127, 91), (747, 572, 177, 30))
        a.line(s, WOOD, (748, 572), (924, 572), 3)
    if level >= 24:
        a.rect(s, (169, 128, 84), (767, 497, 134, 26), rad=2)
        a.rect(s, PALE, (770, 500, 128, 20), rad=1)
        business_sign(s, 773, 502, 122, 16, 18)
    else:
        a.rect(s, PALE, (802, 526, 65, 20), rad=1)
        business_sign(s, 805, 529, 59, 13, 11)
    for xx in [760, 805, 849, 892]:
        yy = 578 if level >= 22 else 582
        a.line(s, (156, 132, 94), (xx, yy), (xx, 597), 0.55)
        a.line(s, (207, 180, 127), (xx + 3, yy + 3), (xx + 3, 594), 0.55)
    for xx in [752, 919]:
        a.circle(s, WOOD, (xx, 576), 0.85)
        a.circle(s, WOOD, (xx, 598), 0.85)
    a.line(s, (125, 114, 84), (749, 602), (922, 602), 1)
    for x in [751, 921]:
        a.circle(s, PALE, (x, 499), 1)
        a.line(s, WOOD, (x, 500), (x + 3, 512), 0.7)
    if level >= 23:
        a.line(s, PALE, (749, 560), (923, 560), 1.4)
        for x in [752, 923]:
            a.line(s, WOOD, (x, 559), (x, 566), 1.3)
    a.rect(s, WOOD, (762, 531, 29, 28), rad=1)
    a.rect(s, (119, 151, 135), (765, 534, 23, 22), rad=1)
    for (x, y) in [(770, 538), (782, 542), (774, 550)]:
        a.circle(s, PALE, (x, y), 1.5)
    if level >= 25:
        crate(s, 846, 546, 33, 16)
        for x in [851, 861, 871]:
            a.circle(s, PALE, (x, 545), 2.5)
    if level >= 26:
        a.line(s, INK, (755, 609), (919, 609), 2)
        a.line(s, PALE, (757, 607), (917, 607), 0.6)
    if level >= 27:
        a.line(s, (151, 136, 100), (797, 533), (908, 533), 2)
        for x in [804, 820, 838, 859, 878]:
            a.rect(s, (188, 159, 109), (x, 536, 11, 18), rad=1)
        a.circle(s, PALE, (906, 539), 2, 1)
        a.line(s, PALE, (906, 541), (906, 546), 1)
        a.poly(s, (168, 174, 145), [(901, 545), (911, 545), (913, 563), (899, 563)])
    if level >= 30:
        a.line(s, WOOD, (766, 494), (902, 494), 2)
        a.line(s, PALE, (769, 493), (900, 493), 0.7)
    if level >= 31:
        cart(s, 52, 622)
    if level >= 34:
        crate(s, 797, 581, 28, 16)
    if level >= 36:
        crate(s, 851, 584, 33, 17)
    if level >= 38:
        a.line(s, PALE, (749, 605), (926, 605), 1)
        crate(s, 889, 578, 29, 23)
    if level >= 39:
        for (x, y) in [(682, 609), (709, 624), (682, 589)]:
            crate(s, x, y, 27, 19)
    if level == 40:
        cart(s, 784, 641)
    if d.festival:
        bunting(s, 35, 416, 236, 442)
        bunting(s, 701, 438, 931, 408)
    for x in [20, 940]:
        a.line(s, a.WOOD, (x, 70), (x, 720), 8)
        a.line(s, a.PAPER, (x - 2, 77), (x - 2, 720), 1)
    a.line(s, a.WOOD, (20, 73), (940, 73), 8)
    village_shop_depth(s, level)
    village_joinery(s, level)
    village_business_growth(s, level)
    return a.finish(s, 960, 720)

def draw_life(s, level, t):
    d = village_day(level - 1)
    for n in range(d.crowd):
        speed = (10 + n % 3 * 2) * (1 if n % 2 else -1)
        phase = n * 47 + t * speed
        (left, span) = (280, 444)
        y = 583 + n % 3 * 9
        if d.festival:
            (left, span) = (290, 371)
            speed = 10 + n % 2 * 2
            phase = n * 29 + t * speed
            y = 516 + n % 2 * 7
        x = a.street_position(left, span, phase)
        face = farm_world.street_facing(left, span, phase, speed)
        tmp = a.surface(28, 44)
        farm_world.visitor(tmp, 14, 38, n, phase=abs(phase) * math.pi / 6, facing=face, scale=0.94)
        s.blit(a.finish(tmp, 28, 44), (round(x) - 14, y - 38))
    if d.rain:
        rain = pygame.Surface((960, 720), pygame.SRCALPHA)
        for n in range(28):
            x = 32 + n * 43 % 190 if n % 2 else 741 + n * 39 % 181
            y = 92 + (n * 71 + t * 139) % 510
            pygame.draw.line(rain, (193, 205, 197, 60), (x, y), (x - 2, y + 8), 1)
        s.blit(rain, (0, 0))

def draw_arrival(s, t):
    progress = min(1, t / 3.5)
    x = 781 - 36 * progress
    y = 622 + 13 * progress
    cart_layer = a.surface(110, 50)
    cart(cart_layer, 13, 30)
    s.blit(a.finish(cart_layer, 110, 50), (777, 595))
    crew = a.launcher_crew(480, 33, 0, t, progress * 14, 0.9, 21, False, False, False, False)
    group = pygame.Surface((221, 84), pygame.SRCALPHA)
    group.blit(crew, (0, 0))
    cannon = a.launcher(0.75, 0)
    group.blit(cannon, cannon.get_rect(center=(110, 39)))
    small = pygame.transform.smoothscale(group, (133, 51))
    s.blit(small, (round(x - 46), round(y - 46)))
    for dx in [-8, 8]:
        pygame.draw.circle(s, INK, (round(x + dx), round(y - 22)), 3, 1)
    pygame.draw.line(s, WOOD, (727, 639), (851, 639), 2)
    pygame.draw.line(s, (195, 185, 142), (727, 637), (851, 637), 1)
