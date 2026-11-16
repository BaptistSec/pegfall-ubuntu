from functools import lru_cache
import math
from pathlib import Path
import pygame
from . import art_style as a
from .narrative import farm_day
SKY = (158, 210, 220)
FIELD = (220, 216, 153)
WALL = (233, 211, 162)
INK = (81, 103, 88)
WOOD = (170, 126, 78)
PALE = (249, 230, 184)
ROOF = (163, 105, 76)

def rect(s, c, r, rad=0):
    a.rect(s, c, r, rad=rad)

def person(s, x, y, kind=0, arm=0, stride=0):
    coat = [(123, 139, 117), (150, 130, 99), (112, 140, 135), (167, 149, 113)][kind % 4]
    a.circle(s, (194, 170, 133), (x, y - 18), 3.4)
    a.poly(s, coat, [(x - 4, y - 14), (x + 4, y - 14), (x + 5, y - 2), (x - 5, y - 2)])
    a.line(s, INK, (x - 2, y - 2), (x - 3 + stride, y + 6), 1.6)
    a.line(s, INK, (x + 2, y - 2), (x + 3 - stride, y + 6), 1.6)
    for side in [-1, 1]:
        shoulder = (x + side * 3, y - 12)
        target = (x + 8, y - 8 - arm) if side == 1 else (x - 6, y - 5)
        (elbow, hand) = a.arm_pose(shoulder, target, side, 4, 4.5)
        a.line(s, coat, shoulder, elbow, 1.7)
        a.line(s, coat, elbow, hand, 1.7)
VISITOR_COATS = ((119, 139, 117), (149, 127, 97), (105, 137, 133), (163, 146, 109), (121, 131, 125), (147, 139, 118))

def visitor(s, x, y, kind=0, phase=0, facing=1, walking=True, scale=1):

    def pt(dx, dy):
        return (x + dx * scale * facing, y + dy * scale)

    def path(col, points):
        a.poly(s, col, [pt(*p) for p in points])

    def stroke(col, p, q, w):
        a.line(s, col, pt(*p), pt(*q), w * scale)

    def dot(col, p, r):
        a.circle(s, col, pt(*p), r * scale)
    coat = VISITOR_COATS[kind % len(VISITOR_COATS)]
    edge = (81, 98, 89)
    skin = (191, 164, 128)
    pygame.draw.ellipse(s, (109, 122, 98, 52), pygame.Rect(round((x - 6 * scale) * a.SCALE), round((y - 1 * scale) * a.SCALE), round(13 * scale * a.SCALE), round(3 * scale * a.SCALE)))
    swing = math.sin(phase) * 2.1 if walking else 0
    lift = max(0, math.cos(phase)) * 1.1 if walking else 0
    bob = abs(math.sin(phase)) * 0.35 if walking else 0
    back_shoulder = (-2, -17)
    back_target = (-4 - swing * 0.4, -9)
    (back_elbow, back_hand) = a.arm_pose(back_shoulder, back_target, -1, 4.4, 4.6)
    stroke((113, 126, 111), back_shoulder, back_elbow, 2.1)
    stroke((113, 126, 111), back_elbow, back_hand, 2.1)
    path((92, 107, 101), [(-2, -10), (1, -9), (1 + swing * 0.65, -4), (-3 - swing, 0), (-5 - swing, -0.4), (-2 - swing * 0.3, -5)])
    stroke((70, 83, 77), (-5 - swing, 0), (-1 - swing, 0.1), 1.7)
    path((110, 119, 106), [(0, -10), (3, -9), (4 - swing * 0.4, -5), (3 + swing, -lift), (1 + swing, -lift), (1 - swing * 0.2, -5)])
    stroke((70, 83, 77), (1 + swing, -lift), (5 + swing, -lift), 1.7)
    path(coat, [(-3, -23 - bob), (1, -24 - bob), (4, -20 - bob), (4, -13), (5, -9), (-4, -9), (-4, -18)])
    stroke((137, 151, 128), (-2, -21 - bob), (-2, -13), 0.6)
    stroke((91, 109, 97), (2, -18), (2, -10), 0.65)
    path((180, 155, 119), [(-1, -26 - bob), (2, -26 - bob), (2, -22 - bob), (-1, -22 - bob)])
    dot(skin, (0.5, -28 - bob), 3)
    path(skin, [(2, -29 - bob), (4, -27.5 - bob), (2, -26 - bob)])
    path((112, 113, 91), [(-2.3, -28.8 - bob), (-1.5, -31 - bob), (1.3, -31.2 - bob), (3, -29.2 - bob), (0.8, -29.7 - bob)])
    if kind % 3 == 1:
        stroke((110, 113, 94), (-3, -29.7 - bob), (4, -29.7 - bob), 1.2)
        path((127, 125, 99), [(-2, -30), (0, -33), (2.5, -32), (3, -30)])
    if kind % 3 == 2:
        stroke((163, 153, 112), (-2, -23 - bob), (2, -22 - bob), 1.3)
    shoulder = (2, -21 - bob)
    (elbow, hand) = a.arm_pose(shoulder, (3 + swing * 0.6, -10), 1, 6.0, 6.0)
    stroke(coat, shoulder, elbow, 2.4)
    stroke(coat, elbow, hand, 2)
    dot(skin, hand, 1)

def street_facing(left, span, phase, velocity):
    u = phase % (span * 2)
    return (1 if velocity >= 0 else -1) * (1 if u < span else -1)

def sign(s, x, y, painted, scale=1):
    for dx in [5, 91]:
        a.line(s, WOOD, (x + dx, y), (x + dx, y + 52), 2)
    rect(s, (158, 122, 77), (x, y, 96, 29), 2)
    rect(s, PALE, (x + 2, y + 2, 92, 24), 1)
    if painted:
        font = pygame.font.Font(str(Path(__file__).resolve().parent / 'assets/fonts/LiberationSans-Bold.ttf'), round(17 * a.SCALE))
        im = font.render('THE BRASS LANTERN', True, (63, 91, 79))
        factor = min(84 * a.SCALE / im.get_width(), 14 * a.SCALE / im.get_height())
        im = pygame.transform.smoothscale(im, (round(im.get_width() * factor), round(im.get_height() * factor)))
        s.blit(im, im.get_rect(center=(round((x + 48) * a.SCALE), round((y + 14) * a.SCALE))))
    else:
        for dx in [14, 31, 50, 69]:
            a.line(s, (193, 166, 119), (x + dx, y + 9), (x + dx + 9, y + 18), 1)

def dog(s, x, y):
    a.poly(s, (144, 128, 90), [(x - 8, y - 7), (x + 6, y - 7), (x + 10, y - 3), (x + 5, y + 1), (x - 8, y + 1)])
    a.circle(s, (132, 116, 81), (x + 9, y - 7), 4)
    a.poly(s, (94, 100, 73), [(x + 8, y - 10), (x + 6, y - 5), (x + 5, y - 11)])
    for xx in [x - 5, x + 4]:
        a.line(s, (119, 112, 82), (xx, y), (xx - 1, y + 5), 1.6)
    a.line(s, (133, 120, 85), (x - 8, y - 6), (x - 12, y - 10), 1.6)

def painted_pasture(s, level):
    a.poly(s, (216, 211, 148), [(28, 648), (92, 636), (174, 638), (239, 652), (194, 650), (93, 644), (28, 655)])
    a.poly(s, (214, 208, 144), [(741, 687), (823, 678), (932, 684), (932, 691), (827, 685), (755, 694)])
    for side in [0, 1]:
        for n in range(18):
            x = 31 + n * 11 % 198 + (700 if side else 0)
            y = 646 + n * 17 % 65
            col = [(182, 185, 123), (194, 193, 130), (201, 198, 135)][n % 3]
            a.line(s, col, (x, y), (x - 2, y - 3 - n % 3), 0.65)
            if n % 3 == 0:
                a.line(s, col, (x, y), (x + 3, y - 4), 0.6)
    for (x, y, w) in [(45, 490, 47), (164, 505, 66)]:
        a.poly(s, (225, 206, 154), [(x, y), (x + w, y + 2), (x + w - 5, y + 7), (x + 4, y + 5)])
        for n in range(4):
            a.line(s, (199, 180, 128), (x + 4 + n * 14, y + 11 + n % 2 * 4), (x + 11 + n * 14, y + 11 + n % 2 * 4), 0.8)
    a.poly(s, (218, 193, 139), [(147, 491), (157, 497), (157, 550), (147, 553)])
    a.line(s, (247, 224, 175), (44, 491), (44, 549), 1.5)
    a.poly(s, (183, 161, 113), [(228, 508), (239, 508), (239, 551), (228, 553)])
    a.line(s, (222, 197, 143), (162, 509), (162, 549), 1.2)
    for xx in [54, 72, 90, 108, 126, 144]:
        yy = 449 + abs(xx - 99) * 0.61
        a.line(s, (192, 130, 90), (xx, yy), (xx + 8, yy + 4), 1.6)
    for xx in [169, 185, 201, 217, 233]:
        yy = 480 + abs(xx - 200) * 0.52
        a.line(s, (187, 133, 92), (xx, yy), (xx + 6, yy + 4), 1.2)
    if level >= 8:
        a.poly(s, (181, 174, 115), [(755, 554), (916, 554), (907, 564), (767, 566)])
        for n in range(9):
            a.line(s, (201, 190, 128), (768 + n * 16, 558), (778 + n * 15, 559), 0.7)

def rural_distance(s):
    for side in [0, 1]:

        def pts(nodes):
            return [(960 - x if side else x, y) for (x, y) in nodes]
        a.poly(s, (133, 163, 119), pts([(28, 424), (53, 416), (79, 421), (105, 412), (130, 421), (160, 419), (190, 428), (224, 431), (224, 441), (28, 446)]))
        a.poly(s, (151, 176, 127), pts([(28, 427), (53, 420), (77, 426), (104, 418), (129, 428), (159, 424), (190, 432), (223, 436), (219, 440), (28, 441)]))
        for (x, y, w) in [(48, 375, 25), (192, 393, 19)]:
            a.line(s, (140, 147, 103), (960 - x if side else x, y + 20), (960 - x if side else x, y + 56), 2.3)
            crown = [(x - w, y + 16), (x - w + 1, y + 1), (x - w * 0.45, y - 3), (x - w * 0.35, y - 15), (x + w * 0.1, y - 20), (x + w * 0.5, y - 11), (x + w * 0.9, y - 8), (x + w, y + 8), (x + w * 0.65, y + 21), (x, y + 24)]
            rounded = []
            for (j, node) in enumerate(crown):
                prev = crown[j - 1]
                nxt = crown[(j + 1) % len(crown)]
                start = ((prev[0] + node[0]) / 2, (prev[1] + node[1]) / 2)
                end = ((node[0] + nxt[0]) / 2, (node[1] + nxt[1]) / 2)
                for k in range(8):
                    t = k / 7
                    u = 1 - t
                    rounded.append((u * u * start[0] + 2 * u * t * node[0] + t * t * end[0], u * u * start[1] + 2 * u * t * node[1] + t * t * end[1]))
            a.poly(s, (132, 162, 116), pts(rounded))
            a.poly(s, (147, 174, 122), pts([(x - w + 4, y + 2), (x - w * 0.35, y - 3), (x - w * 0.2, y - 13), (x + w * 0.08, y - 15), (x + w * 0.4, y - 7), (x + w * 0.7, y - 5), (x + w * 0.6, y + 3), (x, y + 6)]))
    for side in [0, 1]:
        for n in range(5):
            x = 31 + n * 37 if not side else 929 - n * 37
            y = 442 + n * 0.7
            a.line(s, (152, 160, 108), (x, y - 8), (x, y + 5), 0.85)
        a.line(s, (157, 164, 111), (31 if not side else 929, 439), (193 if not side else 767, 444), 0.8)

def farm_yard_depth(s, level):
    a.poly(s, (210, 202, 140), [(65, 554), (86, 554), (174, 624), (238, 720), (198, 720), (146, 632)])
    a.poly(s, (224, 216, 155), [(69, 555), (79, 555), (161, 629), (214, 720), (205, 720), (153, 631)])
    for n in range(13):
        x = 49 + n * 31 % 164
        y = 635 + n * 13 % 72
        a.line(s, (199, 197, 132), (x, y), (x + 8 + n % 5, y - 1), 0.65)
    if level >= 7:
        a.poly(s, (143, 132, 88), [(29, 491), (253, 492), (253, 499), (29, 498)])
        for x in range(35, 250, 22):
            a.poly(s, (187, 167, 106), [(x, 492), (x + 13, 492), (x + 11, 499), (x + 2, 498)])
    if level >= 14:
        a.line(s, (223, 205, 148), (197, 631), (241, 631), 2)
        a.line(s, (121, 129, 96), (239, 580), (239, 630), 1.5)
    if level >= 16:
        a.poly(s, (184, 164, 111), [(40, 477), (95, 477), (102, 485), (40, 485)])
        for x in [40, 68, 95]:
            a.line(s, (132, 119, 81), (x + 2, 455), (x + 2, 478), 1)
        a.line(s, (203, 183, 125), (40, 456), (95, 456), 1)

def farm_attraction_growth(s, level):
    if level >= 4:
        a.poly(s, (199, 190, 130), [(751, 611), (927, 611), (932, 626), (745, 626)])
        a.line(s, (231, 220, 158), (751, 613), (925, 613), 1.3)
    if level >= 6:
        for x in [757, 922]:
            a.rect(s, (156, 137, 88), (x, 552, 4, 61))
            a.line(s, (210, 190, 129), (x, 554), (x, 609), 1)
        a.line(s, (162, 141, 91), (755, 552), (929, 552), 3)
    if level >= 8:
        a.poly(s, (165, 143, 96), [(744, 554), (838, 524), (933, 554), (925, 562), (838, 536), (752, 562)])
        a.line(s, (205, 182, 122), (752, 558), (924, 558), 1.5)
        for x in [773, 800, 827, 854, 881, 908]:
            y = 537 + abs(x - 838) * 0.29
            a.line(s, (187, 164, 109), (x, y), (x + 10, y + 3), 0.8)
    if level >= 10:
        a.rect(s, (173, 146, 94), (755, 587, 173, 26))
        a.line(s, (226, 206, 142), (754, 586), (929, 586), 3)
        for x in [762, 804, 846, 888, 924]:
            a.line(s, (139, 129, 86), (x, 591), (x, 610), 0.8)
    if level >= 12:
        a.poly(s, (184, 173, 115), [(760, 564), (790, 564), (790, 583), (760, 583)])
        a.rect(s, (131, 151, 118), (794, 565, 119, 17))
        for x in range(805, 910, 26):
            a.line(s, (196, 186, 127), (x, 566), (x, 581), 0.8)
    if level >= 14:
        a.line(s, (231, 211, 146), (748, 560), (929, 560), 2)
        for x in [756, 922]:
            a.line(s, (132, 132, 91), (x, 563), (x + 11 if x == 756 else x - 11, 575), 2)
        a.rect(s, (196, 180, 118), (796, 591, 88, 17))
        a.line(s, (225, 207, 141), (799, 593), (880, 593), 1)
    if level >= 16:
        a.rect(s, (119, 150, 127), (758, 568, 5, 17))
        a.rect(s, (119, 150, 127), (917, 568, 5, 17))
        a.line(s, (232, 214, 150), (756, 615), (928, 615), 2)
    if level >= 18:
        a.poly(s, (163, 112, 78), [(33, 456), (70, 435), (107, 456), (101, 462), (70, 444), (39, 462)])
        a.rect(s, (226, 204, 150), (41, 462, 56, 17))
        a.rect(s, (130, 167, 151), (51, 465, 16, 12))
        a.rect(s, (130, 167, 151), (73, 465, 16, 12))
        a.line(s, (242, 222, 170), (42, 480), (97, 480), 1.6)
    if level >= 19:
        a.line(s, (225, 205, 140), (752, 552), (928, 552), 1)
        for x in [770, 811, 852, 893]:
            a.rect(s, (195, 169, 108), (x, 562, 15, 3))

@lru_cache(maxsize=4)
def background(level, developed=True):
    level = max(1, min(20, int(level)))
    d = farm_day(level - 1)
    s = a.surface(960, 720)
    sky = (172, 196, 195) if d.weather == 'rain' else (210, 209, 174) if d.weather == 'evening' else SKY
    rect(s, sky, (0, 0, 960, 720))
    a.circle(s, (249, 226, 164), (792, 145), 30)
    for (x, y, w) in [(112, 143, 78), (545, 121, 50), (818, 204, 67)]:
        a.poly(s, (240, 233, 198), [(x - w, y), (x - w * 0.5, y - 5), (x - w * 0.2, y - 10), (x + w * 0.2, y - 9), (x + w * 0.5, y - 3), (x + w, y), (x + w * 0.3, y + 4), (x - w * 0.5, y + 3)])

    def sweep(points):
        path = []
        for (p0, p1, p2, p3) in points:
            for n in range(25):
                t = n / 24
                u = 1 - t
                path.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0], u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
        return path
    for (yy, col) in [(288, (154, 188, 145)), (340, (135, 174, 128)), (392, (123, 162, 117))]:
        nodes = [(0, yy + 25), (155, yy - 9), (322, yy + 9), (485, yy - 3), (665, yy + 21), (805, yy + 3), (960, yy + 18)]
        curves = []
        for j in range(len(nodes) - 1):
            p0 = nodes[max(0, j - 1)]
            p1 = nodes[j]
            p2 = nodes[j + 1]
            p3 = nodes[min(len(nodes) - 1, j + 2)]
            curves.append((p1, (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6), (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6), p2))
        ridge = sweep(curves)
        a.poly(s, col, ridge + [(960, 720), (0, 720)])
    a.poly(s, (140, 177, 131), sweep([((0, 378), (92, 351), (184, 345), (290, 366))]) + [(181, 369), (87, 375), (0, 389)])
    a.poly(s, (128, 166, 121), sweep([((666, 422), (759, 400), (851, 404), (960, 417))]) + [(960, 428), (844, 416), (748, 419), (666, 431)])
    yard = sweep([((0, 461), (140, 447), (231, 445), (345, 461)), ((345, 461), (520, 486), (667, 449), (780, 461)), ((780, 461), (848, 465), (903, 467), (960, 472))])
    a.poly(s, FIELD, yard + [(960, 720), (0, 720)])
    a.poly(s, (215, 212, 149), sweep([((515, 475), (635, 463), (751, 467), (873, 475))]) + [(884, 479), (748, 474), (609, 475)])
    for (start, end) in [((39, 643), (83, 637)), ((104, 659), (146, 655)), ((47, 686), (91, 681)), ((814, 644), (861, 648)), ((870, 673), (921, 679)), ((796, 694), (837, 696))]:
        a.line(s, (209, 206, 143), start, end, 0.75)
        a.line(s, (226, 221, 159), (start[0] + 3, start[1] + 2), (end[0] - 5, end[1] + 2), 0.55)
    if developed:
        rural_distance(s)
    if developed:
        farm_yard_depth(s, level)
    a.poly(s, (208, 203, 145), [(35, 498), (240, 466), (348, 475), (45, 529)])
    if d.neighbour:
        person(s, 289, 463, 2, arm=9)
    a.poly(s, (203, 189, 132), [(30, 551), (244, 551), (269, 566), (28, 567)])
    rect(s, WALL, (43, 480, 112, 73))
    a.poly(s, ROOF, [(35, 483), (99, 440), (164, 483), (157, 489), (99, 451), (43, 490)])
    rect(s, (189, 184, 145), (119, 445, 8, 26))
    rect(s, WOOD if level >= 12 else (150, 151, 116), (64, 511, 22, 42), 1)
    a.line(s, PALE, (68, 514), (79, 542), 1)
    a.circle(s, INK, (81, 535), 1)
    rect(s, INK, (108, 502, 28, 23))
    rect(s, (122, 178, 171), (111, 505, 22, 17))
    a.line(s, PALE, (122, 506), (122, 521), 1)
    rect(s, (205, 183, 134), (160, 496, 78, 57))
    a.poly(s, ROOF, [(155, 495), (200, 472), (244, 497), (239, 502), (200, 481), (162, 502)])
    if level < 4:
        a.poly(s, sky, [(204, 477), (221, 485), (216, 491), (201, 483)])
    rect(s, (153, 143, 102), (181, 521, 35, 32))
    a.line(s, PALE, (198, 522), (198, 550), 1)
    for x in [185, 191, 204, 210]:
        a.line(s, (137, 133, 95), (x, 524), (x, 550), 0.6)
    for y in [526, 545]:
        a.line(s, (189, 165, 112), (182, y), (214, y), 1)
    a.line(s, (180, 160, 111), (182, 548), (196, 525), 1)
    a.line(s, (180, 160, 111), (201, 525), (215, 548), 1)
    for (x, y) in [(57, 492), (87, 483), (134, 532), (47, 539)]:
        a.line(s, (209, 190, 141), (x, y), (x + 7, y), 0.6)
    for x in [64, 81, 97, 113, 130]:
        yy = 448 + abs(x - 99) * 0.58
        a.line(s, (177, 122, 82), (x, yy), (x + 5, yy + 4), 0.65)
    a.line(s, (245, 224, 179), (46, 492), (46, 549), 1)
    a.line(s, (189, 171, 125), (152, 491), (152, 549), 1.2)
    a.line(s, (183, 158, 110), (43, 550), (155, 550), 1.5)
    for (x, y) in [(51, 510), (91, 546), (139, 493), (142, 541)]:
        a.line(s, (199, 181, 132), (x, y), (x + 7, y), 0.6)
        a.line(s, (238, 218, 168), (x, y + 1), (x + 5, y + 1), 0.5)
    for x in [70, 76]:
        a.line(s, (131, 132, 98), (x, 516), (x, 546), 0.6)
    a.line(s, (244, 223, 173), (108, 527), (138, 527), 1.2)
    a.line(s, (178, 160, 115), (108, 529), (138, 529), 0.65)
    for x in [164, 173, 224, 234]:
        a.line(s, (189, 169, 119), (x, 509), (x, 548), 0.6)
    for x in [184, 211]:
        for y in [528, 545]:
            a.circle(s, (112, 121, 90), (x, y), 0.8)
    for yy in [521, 544]:
        rect(s, (114, 122, 92), (65, yy, 7, 2))
    a.line(s, INK, (79, 532), (83, 532), 1)
    for x in [45, 67, 89, 111, 133]:
        a.poly(s, (192, 184, 133), [(x, 554), (x + 15, 554), (x + 18, 559), (x - 2, 560)])
    if d.weather == 'rain':
        rect(s, (244, 208, 132), (111, 505, 22, 17))
        a.line(s, (177, 141, 82), (122, 506), (122, 521), 1)
    sign(s, 34, 585, level >= 2)
    if level >= 5:
        rect(s, (174, 141, 91), (145, 591, 38, 23))
        a.line(s, PALE, (146, 595), (181, 595), 1)
        for x in [151, 161, 171]:
            a.circle(s, (236, 219, 169), (x, 590), 3)
    if level >= 6:
        rect(s, (163, 143, 98), (188, 616, 27, 13), 1)
        for x in [194, 207]:
            a.circle(s, (102, 129, 111), (x, 615), 4, 1)
            a.circle(s, PALE, (x, 615), 1)
    if level >= 7:
        for x in [28, 258]:
            a.line(s, WOOD, (x, 484), (x, 571), 3)
        a.poly(s, (167, 151, 99), [(26, 484), (153, 467), (262, 484), (253, 492), (151, 478), (30, 491)])
        for x in range(34, 256, 22):
            a.line(s, (219, 200, 139), (x, 484), (x + 10, 487), 3)
        a.line(s, (144, 132, 87), (30, 491), (253, 492), 1)
        for x in [29, 257]:
            a.line(s, (214, 192, 131), (x - 1, 497), (x - 1, 562), 0.6)
            for yy in [503, 559]:
                a.circle(s, (110, 115, 79), (x, yy), 0.85)
    if level >= 8:
        for x in [749, 786, 823, 860, 897, 929]:
            a.line(s, (156, 146, 95), (x, 505), (x, 539), 2)
        for y in [514, 529]:
            a.line(s, (164, 150, 97), (748, y), (930, y), 2)
        a.poly(s, (206, 194, 139), [(748, 541), (932, 541), (925, 552), (747, 553)])
        a.poly(s, (187, 160, 123), [(791, 529), (817, 529), (821, 535), (811, 540), (793, 538)])
    if level >= 9:
        a.line(s, INK, (34, 475), (258, 477), 1)
        for x in [53, 108, 166, 222]:
            a.line(s, INK, (x, 477), (x, 488), 1)
            rect(s, (202, 164, 94), (x - 3, 488, 7, 9), 1)
            rect(s, (246, 216, 141), (x - 1, 490, 3, 5), 1)
    if level >= 11:
        for y in [575, 585, 595]:
            a.line(s, (179, 173, 113), (787, y), (925, y + 8), 1)
    if level >= 13:
        for x in [754, 810, 869, 925]:
            a.line(s, (151, 145, 95), (x, 558), (x, 592), 2)
        for y in [569, 583]:
            a.line(s, (161, 149, 97), (754, y), (929, y), 2)
    if level >= 14:
        rect(s, (127, 132, 99), (197, 578, 41, 53), 2)
        rect(s, (160, 156, 112) if level < 17 else (96, 143, 139), (200, 581, 35, 47), 1)
        for (x, y) in [(206, 590), (225, 596), (213, 612)]:
            a.circle(s, (208, 185, 125), (x, y), 2)
    if level >= 15:
        for x in [773, 796, 821, 849, 877, 905]:
            a.line(s, (180, 162, 81), (x, 591), (x, 608), 1)
            a.poly(s, (205, 177, 92), [(x - 4, 593), (x, 582), (x + 4, 593)])
    if level >= 16:
        for x in [40, 68, 95]:
            a.line(s, WOOD, (x, 451), (x, 481), 1.5)
        a.line(s, WOOD, (36, 455), (104, 455), 2)
        a.line(s, WOOD, (42, 478), (94, 455), 1)
    if level >= 18:
        a.line(s, PALE, (46, 459), (98, 459), 2)
        rect(s, (189, 162, 113), (247, 553, 18, 9))
    if level >= 19:
        rect(s, (170, 146, 96), (151, 616, 33, 15), 2)
        for y in [621, 625]:
            a.line(s, PALE, (155, y), (179, y), 1)
    rect(s, (167, 152, 104), (246, 529, 20, 30), 3)
    for yy in [535, 552]:
        a.line(s, (117, 133, 99), (247, yy), (265, yy), 1.3)
    a.line(s, PALE, (250, 532), (250, 548), 0.6)
    a.line(s, WOOD, (154, 495), (240, 507), 1)
    for x in [35, 130, 247, 370, 479, 595, 714, 827, 929]:
        a.line(s, (162, 157, 104), (x, 555), (x, 610), 3)
    for y in [569, 589]:
        a.line(s, (170, 161, 106), (35, y), (929, y + 2), 2)
    if level < 3:
        rect(s, FIELD, (132, 565, 108, 30))
        a.line(s, (166, 155, 103), (139, 590), (194, 577), 2)
        a.line(s, (166, 155, 103), (202, 590), (235, 593), 2)
    if d.dog:
        dog(s, 276, 606)
    if level == 20:
        a.line(s, WOOD, (747, 625), (896, 625), 3)
        for x in [770, 863]:
            a.circle(s, INK, (x, 642), 10, 2)
        rect(s, (181, 153, 104), (750, 604, 136, 20))
        a.line(s, INK, (764, 599), (875, 583), 3)
        a.circle(s, INK, (818, 594), 11, 2)
        rect(s, (212, 194, 146), (781, 594, 32, 12), 2)
    if developed:
        farm_attraction_growth(s, level)
    painted_pasture(s, level)
    for x in [20, 940]:
        a.line(s, WOOD, (x, 70), (x, 720), 8)
        a.line(s, PALE, (x - 2, 77), (x - 2, 720), 1)
    a.line(s, WOOD, (20, 73), (940, 73), 8)
    return a.finish(s, 960, 720)

def draw_weather(s, level, t):
    if farm_day(level - 1).weather != 'rain':
        return
    rain = pygame.Surface((960, 720), pygame.SRCALPHA)
    for n in range(32):
        x = 32 + n * 53 % 210 if n % 2 else 740 + n * 47 % 185
        y = 85 + (n * 71 + t * 150) % 530
        pygame.draw.line(rain, (190, 207, 195, 65), (x, y), (x - 3, y + 9), 1)
    s.blit(rain, (0, 0))

@lru_cache(maxsize=1)
def title_scene():
    s = pygame.transform.smoothscale(background(2, False).subsurface((0, 420, 960, 210)), (960, 200)).copy()
    tmp = pygame.Surface((960, 84), pygame.SRCALPHA)
    a.draw_cannon_mount(tmp, 480, 22, 0, 0)
    tmp.blit(a.launcher_crew(480, 22, 0, 0, 0, 0, 1, False, False), (370, 0))
    cannon = a.launcher(0, 0)
    tmp.blit(cannon, cannon.get_rect(center=(480, 22)))
    s.blit(tmp.subsurface((370, 0, 221, 84)), (637, 83))
    pygame.draw.rect(s, (119, 85, 51), (327, 41, 306, 95), border_radius=5)
    pygame.draw.rect(s, (202, 165, 105), (330, 44, 300, 89), 2, border_radius=4)
    for x in [339, 619]:
        for y in [52, 124]:
            pygame.draw.circle(s, (77, 82, 61), (x, y), 2)
    return s

def draw_title(s):
    s.blit(title_scene(), (0, 0))

def draw_life(s, level, t):
    count = farm_day(level - 1).crowd
    for n in range(count):
        if level in (10, 20):
            x = 333 + n * 39 + math.sin(t * 0.45 + n * 1.9) * 0.8
            y = 567 + n % 3 * 2
            walking = False
            face = 1
        else:
            velocity = (1 if n % 2 else -1) * (9 + n % 3 * 1.5)
            phase = n * 43 + t * velocity
            x = a.street_position(318, 400, phase)
            y = 567 + n % 3 * 2
            face = street_facing(318, 400, phase, velocity)
            walking = True
        tmp = a.surface(28, 42)
        visitor(tmp, 14, 36, n, phase=abs(phase) * math.pi / 6 if walking else 0, facing=face, walking=walking, scale=0.88)
        s.blit(a.finish(tmp, 28, 42), (round(x) - 14, y - 36))
    if level in (1, 3, 17):
        (x, y) = (292, 451)
        angle = math.sin(t * 1.7) * 0.3
        pygame.draw.line(s, (112, 140, 135), (x, y), (x + 4 + round(angle * 5), y - 6), 2)

def draw_loading(s, t):
    pygame.draw.line(s, (163, 128, 78), (744, 649), (810, 605), 4)
    pygame.draw.line(s, (223, 197, 135), (743, 647), (810, 603), 1)
    progress = min(1, max(0, t / 3.0))
    x = 744 + progress * 66
    y = 649 - progress * 44
    temp = pygame.Surface((221, 100), pygame.SRCALPHA)
    crew = a.launcher_crew(480, 33, 0, t, progress * 13, 0.7, 20, False, False, False, False)
    temp.blit(crew, (0, 10))
    cannon = a.launcher(0.8, 0)
    temp.blit(cannon, cannon.get_rect(center=(110, 39)))
    for dx in [-12, 12]:
        pygame.draw.circle(temp, (82, 102, 87), (110 + dx, 53), 4, 1)
    small = pygame.transform.smoothscale(temp, (133, 60))
    s.blit(small, (round(x - 47), round(y - 53)))
