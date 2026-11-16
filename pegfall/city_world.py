from functools import lru_cache
import math
import pygame
from . import art_style as a, farm_world
from .village_world import window, crate, cart, text, business_sign
from .narrative import city_day
INK = (82, 104, 105)
STONE = (202, 196, 176)
PALE = (245, 229, 191)
WOOD = (149, 116, 83)
SKY = (176, 207, 215)

def tower(s, x, y, w, h, kind=0):
    wall = [(211, 204, 181), (200, 197, 175), (219, 207, 181)][kind % 3]
    a.rect(s, wall, (x, y, w, h))
    a.rect(s, (157, 157, 139), (x - 3, y - 4, w + 6, 8))
    for xx in range(round(x + 11), round(x + w - 12), 28):
        for yy in range(round(y + 18), round(y + h - 26), 40):
            a.rect(s, (120, 151, 150), (xx, yy, 15, 24), rad=1)
            a.line(s, PALE, (xx + 7, yy), (xx + 7, yy + 22), 0.7)
            a.line(s, (166, 160, 139), (xx - 2, yy + 26), (xx + 18, yy + 26), 1.4)
            a.line(s, (163, 184, 172), (xx + 2, yy + 2), (xx + 6, yy + 2), 0.65)
            a.line(s, (101, 130, 130), (xx + 14, yy + 1), (xx + 14, yy + 23), 0.8)
    for yy in range(round(y + 9), round(y + h - 4), 40):
        a.line(s, (185, 183, 163), (x + 1, yy), (x + w - 1, yy), 0.65)
    a.line(s, (231, 221, 190), (x + 2, y + 1), (x + 2, y + h - 2), 1.3)
    a.line(s, (175, 173, 153), (x + w - 2, y + 5), (x + w - 2, y + h - 1), 1.2)
    a.line(s, PALE, (x - 2, y - 4), (x + w + 2, y - 4), 1)
    a.line(s, (173, 173, 151), (x - 1, y + 6), (x + w - 1, y + 6), 1)
    for yy in range(round(y + 13), round(y + h - 7), 20):
        for xx in [x + 3, x + w - 10]:
            a.line(s, (186, 182, 158), (xx, yy), (xx + 7, yy), 0.55)

def city_stone_street(s):
    for (k, (x, y, w, h)) in enumerate([(29, 333, 64, 220), (96, 294, 61, 259), (160, 359, 63, 194), (741, 351, 59, 202), (805, 287, 59, 266), (868, 325, 65, 228)]):
        a.rect(s, (145, 168, 166), (x + w - 10, y, 10, h))
        a.line(s, (183, 197, 185), (x + 2, y + 3), (x + 2, y + h), 1.3)
        a.rect(s, (132, 156, 153), (x - 3, y - 6, w + 6, 7))
        a.line(s, (184, 197, 182), (x - 3, y - 6), (x + w + 3, y - 6), 1.2)
        a.rect(s, (146, 166, 161), (x + 7, y - 17, w - 16, 11))
        for xx in range(x + 10, x + w - 12, 20):
            for yy in range(y + 15, y + h - 16, 35):
                a.rect(s, (135, 158, 156), (xx, yy, 10, 18))
                a.line(s, (166, 184, 174), (xx + 3, yy + 2), (xx + 3, yy + 15), 0.7)
                a.line(s, (125, 151, 148), (xx - 1, yy + 19), (xx + 12, yy + 19), 1)
        for yy in range(y + 9, y + h, 35):
            a.line(s, (160, 180, 172), (x, yy), (x + w - 10, yy), 0.7)
    for (x, w) in [(30, 164), (738, 194)]:
        a.poly(s, (175, 173, 150), [(x, 614), (x + w, 614), (x + w + 5, 623), (x - 5, 623)])
        a.line(s, (225, 214, 183), (x, 615), (x + w, 615), 1.4)
        for xx in range(x + 9, x + w, 30):
            a.line(s, (158, 161, 143), (xx, 616), (xx - 2, 622), 0.75)

def city_frontage_depth(s, level):
    if level < 46:
        return
    y = 436 if level < 51 else 414 if level < 56 else 395
    for x in [748, 919]:
        a.rect(s, (189, 183, 153), (x, y + 11, 7, 78 if level < 51 else 92))
        a.line(s, (237, 226, 190), (x, y + 11), (x, y + 83), 1.4)
    a.line(s, (68, 99, 94), (764, 539), (908, 539), 2)
    a.line(s, (193, 167, 113), (764, 584), (909, 584), 2)
    a.poly(s, (140, 140, 116), [(750, 613), (925, 613), (933, 622), (740, 622)])
    a.line(s, (235, 219, 180), (751, 613), (925, 613), 1.7)
    if level >= 51:
        for x in [768, 869]:
            a.rect(s, (146, 151, 129), (x, y + 51, 37, 4))
            a.line(s, (237, 224, 188), (x, y + 51), (x + 36, y + 51), 1)
    if level >= 56:
        for x in [748, 918]:
            a.rect(s, (219, 207, 169), (x - 2, y + 6, 12, 4))
            a.rect(s, (177, 177, 147), (x - 2, 493, 12, 4))
        a.line(s, (238, 221, 175), (746, 500), (928, 500), 2)

def city_street_depth(s, level):
    for side in [0, 1]:

        def pt(x, y):
            return (960 - x if side else x, y)

        def poly(col, nodes):
            a.poly(s, col, [pt(x, y) for (x, y) in nodes])
        poly((167, 176, 157), [(183, 403), (211, 418), (211, 581), (183, 610)])
        poly((179, 184, 160), [(185, 413), (204, 424), (204, 579), (185, 598)])
        a.line(s, (206, 206, 174), pt(185, 413), pt(185, 598), 1.2)
        for yy in range(433, 581, 24):
            a.line(s, (162, 172, 151), pt(187, yy), pt(205, yy + 7), 0.7)
        for yy in [448, 489, 530]:
            poly((144, 164, 151), [(191, yy), (200, yy + 3), (200, yy + 23), (191, yy + 22)])
            a.line(s, (190, 196, 165), pt(193, yy + 4), pt(193, yy + 19), 0.7)
    a.poly(s, (187, 185, 161), [(28, 620), (190, 620), (274, 645), (932, 645), (932, 657), (266, 654), (185, 631), (28, 631)])
    a.line(s, (223, 213, 183), (29, 621), (187, 621), 1.1)
    a.line(s, (218, 209, 179), (190, 623), (274, 647), 1)
    for n in range(9):
        x = 32 + n * 21
        a.line(s, (169, 173, 151), (x, 622), (x - 2, 629), 0.7)
    for x in range(290, 930, 58):
        a.line(s, (172, 176, 153), (x, 647), (x + 2, 655), 0.7)
    a.poly(s, (92, 117, 109), [(53, 555), (61, 560), (61, 603), (53, 609)])
    a.line(s, (176, 181, 150), (63, 556), (63, 604), 1.1)
    a.line(s, (170, 172, 145), (51, 610), (90, 610), 2)
    for y in [615, 620]:
        a.line(s, (196, 193, 164), (45, y), (98, y), 1.3)

def city_counter_finish(s, level):
    if level >= 46:
        a.poly(s, (79, 104, 97), [(768, 542), (775, 545), (775, 580), (768, 583)])
        a.poly(s, (139, 126, 94), [(774, 582), (906, 582), (910, 587), (767, 587)])
        a.line(s, (218, 193, 139), (775, 582), (906, 582), 1.2)
    if level >= 51:
        for x in [752, 916]:
            a.rect(s, (177, 175, 144), (x, 480, 8, 18))
            a.line(s, (235, 221, 181), (x, 481), (x + 7, 481), 1)
    if level >= 56:
        for x in [756, 913]:
            a.line(s, (182, 158, 111), (x, 509), (x, 607), 1.4)
        a.line(s, (234, 216, 167), (760, 610), (914, 610), 2)

def city_premises_growth(s, level):
    if level >= 43:
        a.poly(s, (182, 176, 147), [(753, 615), (930, 615), (932, 624), (745, 624)])
    if level >= 49:
        a.line(s, (235, 218, 179), (742, 431), (932, 431), 2)
    if level >= 51:
        for x in [763, 861]:
            a.rect(s, (153, 155, 129), (x - 2, 428, 44, 40))
            a.rect(s, (145, 169, 149), (x + 2, 431, 36, 33))
            a.line(s, (233, 219, 178), (x + 20, 431), (x + 20, 464), 1.2)
            a.line(s, (233, 219, 178), (x + 2, 445), (x + 37, 445), 1)
    if level >= 53:
        for x in [746, 918]:
            a.rect(s, (207, 197, 160), (x, 423, 9, 69))
            a.line(s, (239, 226, 187), (x, 424), (x, 489), 1.3)
        a.line(s, (222, 205, 162), (744, 472), (930, 472), 2)
    if level >= 55:
        a.rect(s, (221, 208, 172), (747, 398, 180, 16))
        a.rect(s, (177, 176, 146), (740, 390, 194, 8))
        a.line(s, (238, 224, 185), (741, 389), (933, 389), 2)
        a.rect(s, (213, 202, 166), (747, 379, 180, 10))
        a.rect(s, (220, 207, 168), (782, 370, 109, 10))
        a.line(s, (183, 178, 144), (749, 384), (925, 384), 0.9)
    if level >= 56:
        a.rect(s, (228, 217, 187), (757, 400, 160, 67))
        for x in [762, 862]:
            a.rect(s, (180, 174, 137), (x - 2, 405, 46, 50))
            a.rect(s, (222, 200, 144), (x + 2, 409, 38, 42))
            a.line(s, (243, 224, 175), (x + 21, 410), (x + 21, 450), 1.2)
            a.line(s, (242, 224, 178), (x + 3, 429), (x + 39, 429), 1)
        for x in [745, 918]:
            a.rect(s, (206, 195, 154), (x, 400, 11, 63))
            a.line(s, (239, 223, 181), (x, 402), (x, 460), 1.2)
    if level >= 57:
        for x in [748, 918]:
            a.rect(s, (187, 176, 137), (x - 3, 457, 17, 6))
        a.line(s, (237, 218, 170), (742, 399), (932, 399), 2)
    if level >= 59:
        a.rect(s, (179, 163, 119), (807, 374, 60, 13))
        a.rect(s, (225, 207, 157), (810, 377, 54, 7))
        for x in [751, 921]:
            a.rect(s, (220, 207, 167), (x, 371, 6, 17))
    if level >= 60:
        a.line(s, (244, 223, 174), (743, 391), (931, 391), 1)
        a.line(s, (238, 219, 168), (745, 624), (929, 624), 2)

@lru_cache(maxsize=4)
def background(level):
    level = max(41, min(60, int(level)))
    d = city_day(level - 1)
    s = a.surface(960, 720)
    sky = (218, 211, 181) if d.evening else SKY
    a.rect(s, sky, (0, 0, 960, 720))
    a.circle(s, (245, 226, 169), (801, 178 if not d.evening else 255), 26)
    for (x, y, w, h) in [(29, 333, 64, 220), (96, 294, 61, 259), (160, 359, 63, 194), (741, 351, 59, 202), (805, 287, 59, 266), (868, 325, 65, 228)]:
        a.rect(s, (151, 177, 175), (x, y, w, h))
        a.rect(s, (140, 163, 161), (x - 3, y - 5, w + 6, 6))
    city_stone_street(s)
    a.poly(s, (199, 193, 168), [(0, 550), (244, 533), (479, 554), (712, 534), (960, 548), (960, 720), (0, 720)])
    city_street_depth(s, level)
    tower(s, 39, 388, 143, 223, 0)
    a.rect(s, (123, 139, 129), (52, 552, 36, 59), rad=1)
    a.line(s, PALE, (58, 556), (58, 603), 1)
    a.circle(s, WOOD, (82, 583), 1.1)
    for yy in [562, 598]:
        a.rect(s, INK, (54, yy, 9, 2), rad=0.3)
    a.line(s, (183, 183, 155), (51, 612), (90, 612), 1.7)
    a.rect(s, (158, 153, 125), (99, 553, 67, 58))
    a.rect(s, (179, 189, 166), (102, 556, 61, 38))
    text(s, 'GENERAL', 108, 563, 10)
    for x in [106, 126, 147]:
        crate(s, x, 596, 15, 12)
    a.paving(s, STONE, (190, 185, 163), (209, 203, 183))
    if level < 46:
        for x in [767, 912]:
            a.line(s, WOOD, (x, 508), (x, 614), 3)
        a.poly(s, (150, 164, 140), [(759, 510), (832, 489), (919, 510), (912, 521), (766, 521)])
        a.rect(s, (160, 131, 95), (764, 583, 153, 29))
        a.line(s, PALE, (768, 585), (913, 585), 1)
        a.rect(s, WOOD, (781, 543, 41, 38), rad=1)
        a.rect(s, (109, 151, 142), (785, 547, 33, 30), rad=1)
        for (x, y) in [(791, 553), (810, 558), (799, 570)]:
            a.circle(s, PALE, (x, y), 1.6)
        if level >= 42:
            a.poly(s, (130, 157, 139), [(744, 605), (748, 562), (765, 564), (769, 606)])
            a.line(s, PALE, (751, 571), (759, 590), 1)
            a.line(s, (168, 153, 115), (754, 616), (926, 616), 2)
        if level >= 44:
            a.rect(s, PALE, (785, 521, 116, 22), rad=1)
            business_sign(s, 789, 524, 108, 16, 16)
        for xx in [771, 798, 827, 856, 884, 910]:
            a.line(s, (177, 181, 147), (xx, 511), (xx + 3, 519), 0.65)
        for xx in [768, 914]:
            a.circle(s, PALE, (xx, 522), 1)
            a.line(s, WOOD, (xx, 523), (xx + 2, 535), 0.7)
        for xx in [771, 806, 844, 880, 910]:
            a.line(s, (130, 117, 86), (xx, 590), (xx, 608), 0.6)
        a.line(s, (203, 180, 132), (769, 586), (912, 586), 1)
        a.line(s, (136, 119, 87), (768, 610), (913, 610), 1)
        if level >= 45:
            crate(s, 847, 571, 32, 12)
    else:
        x = 747
        y = 436 if level < 51 else 414 if level < 56 else 395
        wall = (220, 207, 178) if level < 51 else (228, 217, 187)
        a.rect(s, wall, (x, y, 180, 177 + (436 - y)))
        a.rect(s, (164, 166, 143), (741, y - 6, 192, 9))
        a.line(s, PALE, (742, y - 8), (932, y - 8), 1.5)
        window(s, 763, y + 14, 40, 34, d.evening)
        window(s, 862, y + 14, 41, 34, d.evening)
        a.rect(s, (101, 138, 129), (755, 507, 165, 102))
        a.rect(s, (97, 117, 108), (765, 537, 144, 49))
        for xx in [751, 915]:
            a.rect(s, (141, 159, 138), (xx, 496, 12, 119))
            a.line(s, PALE, (xx + 2, 499), (xx + 2, 609), 1)
        a.rect(s, (175, 143, 97), (760, 508, 152, 26), rad=1)
        a.rect(s, PALE, (763, 511, 146, 20), rad=1)
        business_sign(s, 767, 514, 138, 15, 17)
        a.rect(s, (181, 155, 111), (762, 586, 150, 24))
        a.line(s, PALE, (765, 588), (909, 588), 1)
        for xx in [767, 804, 842, 880, 908]:
            a.line(s, WOOD, (xx, 590), (xx, 606), 0.7)
        a.line(s, (241, 229, 195), (749, y + 3), (924, y + 3), 1.3)
        a.line(s, (190, 181, 150), (750, y + 7), (924, y + 7), 0.8)
        for xx in [749, 922]:
            a.line(s, (190, 184, 153), (xx, y + 12), (xx, 491), 1)
            for yy in range(y + 22, 490, 23):
                a.line(s, (201, 190, 157), (xx - 1, yy), (xx + 4, yy), 0.7)
        for xx in [758, 916]:
            a.line(s, PALE, (xx, 508), (xx, 610), 0.8)
            for yy in [543, 577, 604]:
                a.circle(s, WOOD, (xx + 1, yy), 0.8)
        a.line(s, (75, 104, 99), (765, 539), (765, 583), 1.3)
        a.line(s, (162, 174, 142), (767, 539), (906, 539), 0.7)
        for xx in [773, 809, 847, 885]:
            a.line(s, (157, 132, 94), (xx, 592), (xx, 605), 0.6)
            a.line(s, (207, 181, 129), (xx + 3, 594), (xx + 3, 602), 0.55)
        a.line(s, (98, 115, 103), (756, 612), (920, 612), 2)
        a.line(s, (227, 212, 170), (757, 614), (919, 614), 0.8)
        for xx in [764, 909]:
            a.circle(s, WOOD, (xx, 515), 1)
        if level >= 47:
            a.rect(s, WOOD, (771, 543, 31, 36), rad=1)
            a.rect(s, (132, 167, 148), (774, 546, 25, 30), rad=1)
            for (xx, yy) in [(781, 550), (792, 556), (782, 568)]:
                a.circle(s, PALE, (xx, yy), 1.5)
            for xx in [817, 835, 854, 874]:
                crate(s, xx, 563, 13, 15)
        if 50 <= level < 56:
            a.rect(s, WOOD, (748, 474, 177, 25), rad=1)
            a.rect(s, (218, 198, 151), (751, 477, 171, 18), rad=1)
            business_sign(s, 755, 479, 163, 14, 15)
        if level >= 51:
            for xx in [752, 920]:
                a.line(s, WOOD, (xx, 477), (xx, 500), 1)
                a.rect(s, (192, 169, 116), (xx - 4, 487, 8, 11), rad=1)
                a.rect(s, (236, 210, 146), (xx - 2, 489, 4, 7), rad=0.5)
        if level >= 52:
            a.line(s, WOOD, (865, 545), (901, 545), 1)
            for xx in [874, 891]:
                a.rect(s, (231, 219, 175), (xx, 538, 6, 6), rad=1)
                a.circle(s, PALE, (xx + 6, 541), 2, 1)
            a.line(s, (158, 140, 105), (875, 538), (879, 538), 0.8)
        if level >= 55:
            a.line(s, PALE, (761, 614), (922, 614), 1.5)
        if level >= 56:
            for xx in [748, 922]:
                a.rect(s, (188, 177, 140), (xx, 503, 6, 112))
                a.line(s, PALE, (xx + 1, 505), (xx + 1, 611), 1)
            a.line(s, WOOD, (741, 468), (933, 468), 2)
            a.poly(s, (139, 160, 136), [(740, 468), (836, 459), (933, 468), (923, 476), (749, 476)])
        if level >= 59:
            a.rect(s, (195, 175, 126), (794, 594, 39, 12), rad=1)
            for xx in [800, 811, 822]:
                a.circle(s, PALE, (xx, 593), 2.4)
    if level >= 43:
        crate(s, 697, 610, 27, 19)
    if level >= 48:
        a.line(s, (179, 166, 133), (744, 620), (930, 620), 1)
    if level >= 53:
        a.line(s, PALE, (763, 583), (906, 583), 0.6)
    if level >= 54:
        a.line(s, (154, 144, 111), (739, 623), (928, 623), 0.6)
    if level == 60:
        for xx in [751, 790, 833, 876, 922]:
            a.line(s, WOOD, (xx, 462), (xx, 474), 0.7)
            a.rect(s, (211, 182, 117), (xx - 2, 472, 5, 7), rad=1)
            a.circle(s, (241, 212, 146), (xx, 475), 1)
    for x in [20, 940]:
        a.line(s, a.WOOD, (x, 70), (x, 720), 8)
        a.line(s, a.PAPER, (x - 2, 77), (x - 2, 720), 1)
    a.line(s, a.WOOD, (20, 73), (940, 73), 8)
    city_frontage_depth(s, level)
    city_counter_finish(s, level)
    city_premises_growth(s, level)
    return a.finish(s, 960, 720)

def draw_life(s, level, t):
    d = city_day(level - 1)
    for n in range(d.crowd):
        velocity = (11 + n % 5) * (1 if n % 2 else -1)
        phase = n * 37 + level * 19 + t * velocity
        x = a.street_position(233, 498, phase)
        y = 579 + n % 3 * 11
        kind = (n * 3 + level) % 6
        face = farm_world.street_facing(233, 498, phase, velocity)
        tmp = a.surface(28, 44)
        farm_world.visitor(tmp, 14, 38, kind, phase=abs(phase) * math.pi / 6, facing=face, scale=0.94)
        h = 37 + (n * 7 + level) % 6
        s.blit(pygame.transform.smoothscale(a.finish(tmp, 28, 44), (25, h)), (round(x) - 12, y - h + 10))
    for x in [48, 919]:
        pygame.draw.line(s, (137, 138, 119), (x, 337), (x, 360), 1)
        wave = 0 if d.still else math.sin(t * 0.6 + x) * 1.5
        pygame.draw.polygon(s, (170, 166, 128), [(x, 338), (x + 11, round(341 + wave)), (x, 345)])

def draw_arrival(s, t):
    p = min(1, t / 3.5)
    base = pygame.Surface((221, 84), pygame.SRCALPHA)
    crew = a.launcher_crew(480, 32, 0, t, p * 14, 1.0, 41, False, False, False, False)
    base.blit(crew, (0, 0))
    machine = a.launcher(0.6, 0)
    base.blit(machine, machine.get_rect(center=(110, 35)))
    s.blit(pygame.transform.smoothscale(base, (133, 51)), (round(748 - p * 24), round(581 + p * 13)))
    pygame.draw.line(s, WOOD, (744, 641), (893, 639), 2)

def draw_morning(s, t):
    p = min(1, max(0, t / 3.5))
    crew = a.launcher_crew(480, 26, 0, t, p * 18, 0.65, 46, ground=False, walking=True)
    s.blit(pygame.transform.smoothscale(crew, (133, 51)), (round(178 + p * 51), 557))

def draw_final_days(s, level, t):
    if level < 56:
        return
    pygame.draw.rect(s, (67, 90, 82), (767, 540, 139, 41))
    pygame.draw.polygon(s, (169, 151, 108), [(767, 540), (906, 540), (898, 547), (775, 547)])
    pygame.draw.polygon(s, (93, 109, 91), [(767, 540), (775, 547), (775, 581), (767, 581)])
    pygame.draw.line(s, (227, 202, 141), (775, 581), (905, 581), 2)
    for xx in (786, 820, 854, 888):
        pygame.draw.line(s, (146, 133, 95), (xx, 551), (xx, 569), 2)
        pygame.draw.circle(s, (227, 206, 157), (xx, 550), 2)
    for xx in (783, 855):
        pygame.draw.rect(s, (184, 171, 123), (xx, 555, 31, 14))
        pygame.draw.line(s, (228, 207, 151), (xx + 1, 556), (xx + 29, 556))
    if level == 60:
        pygame.draw.line(s, (132, 113, 76), (744, 455), (928, 455), 1)
        for (n, xx) in enumerate(range(751, 925, 17)):
            pygame.draw.polygon(s, [(181, 122, 93), (182, 164, 112), (116, 150, 135)][n % 3], [(xx, 455), (xx + 9, 455), (xx + 5, 465)])
        for xx in (752, 920):
            pygame.draw.rect(s, (125, 110, 77), (xx - 3, 484, 7, 15))
            pygame.draw.rect(s, (244, 211, 132), (xx - 1, 487, 3, 9))

def draw_ending(s, t):
    from . import finale
    font = pygame.font.Font(None, 28)
    finale.draw(s, t, font)
