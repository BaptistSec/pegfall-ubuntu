from functools import lru_cache
import math
import pygame
from . import bucket as bucket_geometry
from .narrative import operator_warmth
PAPER = (255, 234, 187)
INK = (22, 57, 67)
WOOD = (211, 145, 66)
WOOD_DARK = (130, 78, 41)
LIGHT = (255, 249, 225)
TEAL = (27, 153, 157)
COLORS = {'blue': (38, 151, 219), 'orange': (248, 120, 34), 'green': (79, 187, 70), 'purple': (187, 87, 203)}
RIMS = {v: INK for v in COLORS.values()}
SCALE = 4

def line(s, col, a, b, width=1):
    pygame.draw.line(s, col, tuple((round(v * SCALE) for v in a)), tuple((round(v * SCALE) for v in b)), max(1, round(width * SCALE)))

def circle(s, col, c, r, width=0):
    pygame.draw.circle(s, col, tuple((round(v * SCALE) for v in c)), round(r * SCALE), round(width * SCALE))

def poly(s, col, pts, width=0):
    pygame.draw.polygon(s, col, [(round(x * SCALE), round(y * SCALE)) for (x, y) in pts], round(width * SCALE))

def rect(s, col, r, width=0, rad=0):
    pygame.draw.rect(s, col, pygame.Rect(*(round(v * SCALE) for v in r)), round(width * SCALE), border_radius=round(rad * SCALE))

def surface(w, h):
    return pygame.Surface((round(w * SCALE), round(h * SCALE)), pygame.SRCALPHA)

def finish(s, w, h):
    return pygame.transform.smoothscale(s, (round(w), round(h)))

def paving(s, base, joint, light):
    rect(s, base, (28, 626, 904, 94))
    bands = [(628, 642, 36), (645, 663, 44), (667, 689, 54), (693, 720, 66)]
    wear = [-2, 1, -1, 2, 0, -1, 1]
    for (row, (top, bottom, width)) in enumerate(bands):
        x = 28 - (width // 2 if row % 2 else 9)
        number = 0
        while x < 932:
            delta = wear[(number + row * 2) % len(wear)]
            right = min(932, x + width + delta)
            left = max(28, x)
            joint_x = right - 2
            shade = [-1, 1, 0, 2, 0, -1, 1][(number * 3 + row) % 7]
            if right - left > 10:
                colour = tuple((max(0, min(255, c + shade)) for c in base))
                poly(s, colour, [(left + 2, top + 2), (right - 3, top + 1), (right - 2, bottom - 3), (left + 1, bottom - 1)])
                line(s, joint, (left + 3, bottom), (right - 6, bottom + delta * 0.25), 0.55)
                if number % 3 != 1:
                    line(s, light, (left + 5, top + 1), (right - 8, top + 1), 0.5)
                if right < 932:
                    line(s, joint, (joint_x, top + 3), (joint_x + delta * 0.25, bottom - 3), 0.55)
            x += width + delta
            number += 1

@lru_cache(maxsize=256)
def peg(kind, r, lit=False):
    size = math.ceil(r * 2 + 10)
    c = size // 2
    s = surface(size, size)
    circle(s, INK, (c, c), r)
    color = COLORS.get(kind, COLORS['blue'])
    circle(s, WOOD_DARK, (c, c), max(0.5, r - 0.9))
    circle(s, color, (c - 0.15, c - 0.25), max(0.5, r - 1.8))
    line(s, (193, 160, 110), (c + r * 0.45, c + r * 0.57), (c + r * 0.63, c + r * 0.39), max(0.65, r * 0.09))
    pygame.draw.arc(s, (*INK, 130), pygame.Rect(round((c - r + 2) * 4), round((c - r + 2) * 4), round((r - 2) * 8), round((r - 2) * 8)), math.radians(15), math.radians(90), max(2, round(r * 0.17 * 4)))
    pygame.draw.arc(s, LIGHT, pygame.Rect(round((c - r + 3) * 4), round((c - r + 3) * 4), round((r - 3) * 8), round((r - 3) * 8)), math.radians(100), math.radians(170), max(3, round(r * 0.13 * 4)))
    m = max(1.5, r * 0.27)
    if kind == 'orange':
        circle(s, INK, (c, c), m, 1.2)
    elif kind == 'green':
        poly(s, INK, [(c, c - m - 1), (c + m, c), (c, c + m + 1), (c - m, c)], 1.2)
    elif kind == 'purple':
        line(s, INK, (c - m, c), (c + m, c), 1.3)
        line(s, INK, (c, c - m), (c, c + m), 1.3)
    if r >= 10:
        line(s, (*INK, 100), (c - r * 0.5, c + r * 0.35), (c - r * 0.21, c + r * 0.43), 0.65)
    if lit:
        circle(s, LIGHT, (c, c), max(1, r - 2.1), 1.2)
        for (a, b) in [((c - r - 3, c - 2), (c - r - 5, c - 3)), ((c + r + 3, c - 2), (c + r + 5, c - 3))]:
            line(s, INK, a, b, 1.2)
    return finish(s, size, size)

@lru_cache(maxsize=256)
def block(w, h, angle, kind, lit=False):
    width = round(w) + 8
    height = round(h) + 8
    s = surface(width, height)
    rect(s, INK, (4, 4, w, h), rad=1)
    rect(s, COLORS.get(kind, COLORS['blue']), (5.2, 5.2, max(1, w - 2.4), max(1, h - 2.4)), rad=0.6)
    line(s, LIGHT, (7, 6.5), (w + 1, 6.5), 0.9)
    if w > 14 and h > 8:
        (cx, cy) = (4 + w / 2, 4 + h / 2)
        m = min(2.5, h / 4)
        if kind == 'orange':
            circle(s, INK, (cx, cy), m, 1)
        elif kind == 'green':
            poly(s, INK, [(cx, cy - m), (cx + m, cy), (cx, cy + m), (cx - m, cy)], 1)
        elif kind == 'purple':
            line(s, INK, (cx - m, cy), (cx + m, cy), 1)
            line(s, INK, (cx, cy - m), (cx, cy + m), 1)
    if lit:
        rect(s, LIGHT, (5.5, 5.5, w - 3, h - 3), 1, rad=1)
    return pygame.transform.rotate(finish(s, width, height), -math.degrees(angle))

@lru_cache(maxsize=16)
def ball(r, mode='normal'):
    n = math.ceil(r * 2 + 4)
    c = n // 2
    s = surface(n, n)
    circle(s, INK, (c, c), r)
    col = LIGHT if mode == 'normal' else COLORS['orange'] if mode == 'comet' else COLORS['purple']
    circle(s, col, (c, c), max(1, r - 1.35))
    line(s, (166, 170, 141), (c + 1, c + 1), (c + 1, c + r - 2), 0.8)
    return finish(s, n, n)

@lru_cache(maxsize=64)
def launcher(angle, recoil):
    n = 104
    c = 52
    s = surface(n, n)
    iron = (79, 94, 86)
    shade = (61, 74, 67)
    wood = (139, 123, 94)
    light = (179, 172, 139)
    grain = (112, 105, 83)
    circle(s, shade, (c, c), 15)
    circle(s, iron, (c, c), 13)
    circle(s, (124, 131, 110), (c, c), 8)
    circle(s, shade, (c, c), 3)
    direction = (math.sin(angle), math.cos(angle))
    side = (math.cos(angle), -math.sin(angle))

    def p(off, d):
        return (c + side[0] * off + direction[0] * d, c + side[1] * off + direction[1] * d)
    length = 34 - recoil
    poly(s, shade, [p(-8, -10), p(8, -10), p(6.8, length), p(-6.8, length)])
    poly(s, wood, [p(-6.8, -8), p(6.8, -8), p(5.7, length - 2), p(-5.7, length - 2)])
    poly(s, grain, [p(2.5, -8), p(6.8, -8), p(5.7, length - 2), p(2.8, length - 2)])
    line(s, light, p(-5.7, -5), p(-4.8, length - 6), 0.7)
    line(s, grain, p(-1, -2), p(-1.8, 18), 0.65)
    for d in (4, 20):
        poly(s, iron, [p(-7.5, d - 1.5), p(7.5, d - 1.5), p(7.1, d + 1.5), p(-7.1, d + 1.5)])
        line(s, (145, 151, 125), p(-6.4, d - 1), p(5.7, d - 1), 0.55)
        for off in (-5.2, 5.2):
            circle(s, shade, p(off, d), 0.8)
    poly(s, iron, [p(-7.3, length - 4), p(7.3, length - 4), p(7.3, length), p(-7.3, length)])
    line(s, (41, 53, 48), p(-5.3, length - 0.8), p(5.3, length - 0.8), 2.1)
    line(s, light, p(-6.6, length - 4), p(5.7, length - 4), 0.55)
    circle(s, shade, p(0, -4), 1.7)
    circle(s, light, p(-0.3, -4.3), 0.65)
    return finish(s, n, n)

def draw_bucket(s, cx, flash):
    for obj in bucket_geometry.surfaces(cx):
        if obj.shape == 'circle':
            pygame.draw.circle(s, INK, (round(obj.x), round(obj.y)), round(obj.r))
            pygame.draw.circle(s, LIGHT, (round(obj.x - 1), round(obj.y - 1)), max(1, round(obj.r) - 2))
        else:
            r = pygame.Rect(0, 0, round(obj.w), round(obj.h))
            r.center = (round(obj.x), round(obj.y))
            pygame.draw.rect(s, INK, r, border_radius=1)
            inn = r.inflate(-2, -2)
            if inn.w > 0 and inn.h > 0:
                pygame.draw.rect(s, TEAL, inn)
            if obj.part == 'side':
                pygame.draw.line(s, (151, 180, 158), (r.left + 1, r.top), (r.left + 1, r.bottom - 1), 1)
                for y in [r.top + 8, r.bottom - 9]:
                    pygame.draw.circle(s, WOOD_DARK, (r.centerx, y), 1)
                pygame.draw.line(s, (115, 146, 126), (r.right - 2, r.top + 18), (r.right - 2, r.bottom - 3), 1)
            if obj.part == 'base':
                pygame.draw.line(s, (154, 172, 147), (r.left + 5, r.top + 1), (r.right - 5, r.top + 1), 1)
                pygame.draw.line(s, WOOD, (round(cx - 9), r.centery), (round(cx + 8), r.centery), 2)
                for x in [-7, 7]:
                    pygame.draw.circle(s, INK, (round(cx + x), r.centery), 1)
    if flash > 0:
        color = COLORS['green']
        pygame.draw.line(s, color, (round(cx - 35), 711), (round(cx + 35), 711), 2)

@lru_cache(maxsize=21)
def background(stage=0):
    stage = max(0, min(20, int(stage)))
    s = surface(960, 720)
    sky = (144, 211, 236)
    rect(s, sky, (0, 0, 960, 720))
    for (x, y, w) in [(73, 147, 176), (502, 114, 128), (759, 198, 124)]:
        pygame.draw.ellipse(s, (255, 248, 223), (round(x * SCALE), round(y * SCALE), round(w * SCALE), round(13 * SCALE)))
        pygame.draw.ellipse(s, (255, 248, 223), (round((x + 32) * SCALE), round((y - 8) * SCALE), round(w * 0.4 * SCALE), round(24 * SCALE)))
    circle(s, (255, 217, 100), (791, 143), 33)

    def land(col, points):
        extended = [points[0]] + points + [points[-1]]
        curve = []
        for i in range(1, len(extended) - 2):
            (p0, p1, p2, p3) = extended[i - 1:i + 3]
            for k in range(24):
                t = k / 24
                t2 = t * t
                t3 = t2 * t
                curve.append(tuple((0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in [0, 1])))
        poly(s, col, curve + [points[-1], (960, 720), (0, 720)])
    land((154, 207, 157), [(0, 292), (88, 273), (182, 286), (295, 253), (412, 275), (521, 259), (637, 280), (738, 253), (858, 266), (960, 249)])
    land((117, 190, 134), [(0, 329), (96, 313), (215, 322), (352, 291), (486, 312), (618, 293), (754, 318), (852, 293), (960, 304)])
    land((92, 169, 112), [(0, 397), (127, 359), (254, 368), (384, 340), (514, 357), (643, 337), (798, 368), (960, 341)])
    land((146, 195, 115), [(0, 429), (129, 408), (282, 422), (411, 393), (566, 414), (690, 389), (835, 407), (960, 393)])
    land((186, 211, 124), [(0, 485), (157, 453), (317, 467), (491, 435), (635, 454), (790, 435), (960, 453)])
    land((223, 220, 143), [(0, 546), (151, 513), (321, 527), (468, 498), (637, 511), (798, 490), (960, 508)])
    for (a, b) in [((29, 572), (133, 550)), ((811, 550), (931, 561)), ((42, 626), (143, 609)), ((791, 651), (932, 640))]:
        line(s, (207, 204, 160), a, b, 1)
    _farmyard(s, stage)
    posts = [(37, 594), (148, 579), (259, 571), (370, 568), (481, 573), (592, 578), (703, 572), (814, 565), (925, 569)]
    posts = [(x, y + 32) for (x, y) in posts]
    old = (164, 166, 126)
    new = (178, 157, 117)
    light = (196, 176, 132)
    for (i, ((x, y), (xx, yy))) in enumerate(zip(posts, posts[1:])):
        repaired = i == 1 and stage >= 1 or (i == 3 and stage >= 2) or (i == 6 and stage >= 4)
        col = new if repaired else old
        for height in [20, 40]:
            if not repaired and i == 1:
                line(s, col, (x, y - height), (x + 32, y - height + 7), 4)
                line(s, col, (xx - 21, yy - height - 3), (xx, yy - height), 4)
            elif not repaired and i == 3 and (height == 20):
                line(s, col, (x, y - height), (xx, yy - height + 10), 4)
            else:
                line(s, col, (x, y - height), (xx, yy - height), 4)
                if repaired:
                    line(s, light, (x, y - height - 1.1), (xx, yy - height - 1.1), 0.7)
        if repaired and i == 6:
            line(s, new, (x + 8, y - 18), (xx - 8, yy - 40), 3)
        elif stage < 4 and i == 6:
            line(s, (169, 153, 113), (x + 34, y - 41), (x + 62, y - 40), 6)
            for t in [38, 57]:
                circle(s, (127, 137, 108), (x + t, y - 40), 0.8)
    for (i, (x, y)) in enumerate(posts):
        repaired = i == 2 and stage >= 3
        tilt = 0 if repaired else [0, 0, -8, 0, 0, 0, 0, 0, 0][i]
        col = new if repaired else old
        poly(s, col, [(x - 3, y + 7), (x - 3 + tilt, y - 55), (x + tilt, y - 59), (x + 3 + tilt, y - 54), (x + 3, y + 7)])
        line(s, light if repaired else (178, 180, 140), (x - 1 + tilt, y - 50), (x - 1, y + 4), 0.7)
        for h in [20, 40]:
            circle(s, (125, 135, 105), (x, y - h), 0.8)
    for (x, y) in posts[::2]:
        for (dx, dy) in [(-4, -5), (0, -8), (4, -3)]:
            line(s, (177, 186, 139), (x + 6, y + 5), (x + 6 + dx, y + 5 + dy), 0.8)
    for x in [14, 933]:
        rect(s, INK, (x, 65, 13, 655))
        rect(s, WOOD, (x + 2, 67, 9, 653))
        line(s, (204, 169, 114), (x + 4, 78), (x + 4, 718), 1)
        for y in [139, 304, 526, 677]:
            line(s, WOOD_DARK, (x + 7, y), (x + 5, y + 19), 0.8)
        for y in [97, 357, 612]:
            circle(s, WOOD_DARK, (x + 6, y), 3)
            line(s, LIGHT, (x + 5, y - 1), (x + 7, y + 1), 0.8)
    rect(s, INK, (14, 65, 932, 13))
    rect(s, WOOD, (17, 67, 926, 8))
    rect(s, INK, (0, 0, 960, 65))
    line(s, WOOD, (0, 64), (960, 64), 2)
    return finish(s, 960, 720)

@lru_cache(maxsize=32)
def rail(w, h, angle):
    (n, m) = (round(w) + 6, round(h) + 6)
    s = surface(n, m)
    rect(s, INK, (3, 3, w, h), rad=1)
    rect(s, TEAL, (4.3, 4.3, max(1, w - 2.6), max(1, h - 2.6)), rad=1)
    line(s, (150, 177, 160), (5, 4), (w, 4), 1)
    for x in [7, w - 1]:
        circle(s, WOOD, (x, 3 + h / 2), 1.3)
    return pygame.transform.rotate(finish(s, n, m), -math.degrees(angle))

@lru_cache(maxsize=24)
def bumper(r):
    n = math.ceil(r * 2 + 4)
    c = n // 2
    s = surface(n, n)
    circle(s, INK, (c, c), r)
    circle(s, WOOD, (c, c), r - 1.5)
    circle(s, INK, (c, c), max(1, r - 5))
    circle(s, WOOD, (c, c), max(1, r - 7))
    circle(s, INK, (c, c), 2)
    for (dx, dy) in [(0, -r + 3), (r - 3, 0), (0, r - 3), (-r + 3, 0)]:
        circle(s, LIGHT, (c + dx, c + dy), 1.1)
    return finish(s, n, n)

def _farmyard(s, stage):
    wall = (233, 209, 155) if stage < 19 else (255, 228, 177)
    roof = (177, 113, 76)
    edge = (128, 143, 109)
    timber = (181, 129, 74)
    pale = (249, 225, 174)
    dark = (115, 133, 100)
    poly(s, (209, 196, 143), [(35, 544), (44, 537), (270, 537), (278, 548), (35, 548)])
    poly(s, wall, [(45, 479), (104, 443), (173, 480), (173, 537), (45, 537)])
    poly(s, roof, [(38, 481), (102, 436), (181, 481), (171, 485), (103, 448), (47, 487)])
    line(s, pale, (40, 480), (102, 439), 1)
    rect(s, edge, (144, 440, 12, 26))
    rect(s, pale, (143, 438, 15, 4))
    if stage < 5:
        poly(s, (188, 186, 146), [(113, 448), (133, 458), (124, 470), (106, 460)])
        line(s, edge, (77, 457), (87, 468), 1.5)
    else:
        poly(s, (184, 174, 134), [(106, 448), (133, 463), (124, 472), (100, 458)])
        for (a, b) in [((108, 453), (125, 463)), ((106, 458), (121, 467))]:
            line(s, pale, a, b, 1)
    rect(s, dark, (94, 491, 25, 46), rad=2)
    if stage < 6:
        poly(s, (166, 164, 126), [(97, 493), (116, 495), (114, 536), (96, 536)])
        line(s, pale, (99, 502), (112, 526), 2)
    else:
        rect(s, timber, (97, 493, 20, 44), rad=1)
        for x in [103, 110]:
            line(s, (188, 176, 133), (x, 495), (x, 535), 0.7)
        circle(s, dark, (113, 516), 1.3)
    rect(s, edge, (138, 488, 25, 22))
    rect(s, (96, 188, 194), (141, 491, 19, 16))
    if stage < 7:
        poly(s, timber, [(137, 491), (163, 497), (163, 502), (137, 496)])
    else:
        line(s, pale, (150, 491), (150, 507), 1.5)
        line(s, pale, (141, 499), (160, 499), 1.5)
    if stage >= 8:
        poly(s, (187, 188, 151), [(90, 537), (123, 537), (131, 544), (86, 544)])
        line(s, (213, 209, 169), (91, 538), (121, 538), 1.2)
    poly(s, (215, 194, 143), [(174, 493), (228, 503), (228, 537), (174, 537)])
    for x in [177, 225]:
        line(s, timber, (x, 498), (x, 540), 3)
    poly(s, roof, [(171, 485), (231, 496), (231, 503), (171, 493)])
    line(s, pale, (173, 487), (229, 498), 1)
    if stage < 9:
        poly(s, (215, 194, 143), [(213, 494), (227, 497), (227, 502), (213, 499)])
    else:
        line(s, timber, (211, 494), (224, 497), 2)
    line(s, edge, (174, 537), (230, 537), 1)
    rect(s, (183, 173, 131), (242, 514, 27, 30), rad=5)
    for y in [519, 538]:
        line(s, edge, (243, y), (268, y), 2)
    if stage < 10:
        line(s, dark, (250, 526), (256, 534), 1.4)
        pygame.draw.ellipse(s, (184, 192, 152), (247 * SCALE, 544 * SCALE, 27 * SCALE, 4 * SCALE))
    else:
        pygame.draw.ellipse(s, (205, 203, 164), (242 * SCALE, 510 * SCALE, 27 * SCALE, 7 * SCALE))
        line(s, pale, (245, 514), (266, 514), 1)
    tool = (166, 154, 117) if stage < 13 else (150, 164, 137)
    if stage >= 14:
        for y in [507, 523]:
            line(s, timber, (182, y), (220, y), 2)
        for x in [182, 216]:
            line(s, timber, (x, 501), (x, 533), 2)
    line(s, timber, (193, 503), (187, 535), 2)
    line(s, tool, (184, 508), (201, 512), 4 if stage >= 13 else 2)
    if stage < 13:
        line(s, pale, (185, 510), (194, 512), 1)
    if stage >= 14:
        line(s, timber, (210, 507), (207, 532), 2)
        poly(s, tool, [(204, 507), (214, 507), (216, 513), (203, 513)])
    line(s, timber, (177, 532), (232, 532 if stage >= 15 else 536), 4)
    for x in [182, 226]:
        line(s, timber, (x, 534), (x + (-2 if x == 182 else 2), 549), 3)
    if stage >= 15:
        line(s, pale, (179, 530), (231, 530), 1.2)
        rect(s, edge, (219, 527, 8, 8))
        line(s, pale, (223, 525), (223, 534), 1)
    if stage < 11:
        for (a, b) in [((781, 495), (814, 489)), ((839, 507), (881, 499)), ((857, 478), (906, 480))]:
            line(s, (184, 191, 146), a, b, 3)
    else:
        col = (188, 181, 137) if stage < 12 else (175, 188, 139)
        for i in range(4):
            x = 774 + i * 6
            y = 477 + i * 10
            poly(s, col, [(x, y), (902, y - 8), (916, y - 3), (x + 14, y + 5)])
            line(s, (204, 203, 157), (x + 8, y + 3), (912, y - 4), 1)
    offset = 12 if stage >= 20 else 0

    def p(x, y):
        return (x + offset, y)
    for (a, b) in [((792, 570), (893, 570)), ((800, 576), (893, 576)), ((891, 571), (920, 559))]:
        line(s, timber, p(*a), p(*b), 3)
    if stage < 16:
        circle(s, edge, p(814, 586), 9, 2)
        line(s, timber, p(839, 581), p(857, 593), 3)
    else:
        circle(s, edge, p(814, 584), 10)
        circle(s, pale, p(814, 584), 7)
        for (dx, dy) in [(-6, -5), (-6, 5)]:
            line(s, edge, p(814 + dx, 584 + dy), p(814 - dx, 584 - dy), 1)
        circle(s, timber, p(814, 584), 2)
        line(s, pale, p(800, 568), p(890, 568), 1.5)
    if stage >= 17:
        circle(s, edge, p(879, 584), 10)
        circle(s, pale, p(879, 584), 7)
        for (dx, dy) in [(-6, -5), (-6, 5)]:
            line(s, edge, p(879 + dx, 584 + dy), p(879 - dx, 584 - dy), 1)
        circle(s, timber, p(879, 584), 2)
        rect(s, (184, 170, 125), (800 + offset, 551, 91, 19), rad=2)
        for x in [803, 846, 888]:
            line(s, edge, p(x, 551), p(x, 569), 1)
        line(s, pale, p(802, 553), p(889, 553), 1)
    if stage >= 18:
        for (x, y) in [(807, 536), (841, 536), (825, 523)]:
            rect(s, (194, 181, 136), (x + offset, y, 30, 16), rad=1)
            line(s, pale, p(x + 2, y + 3), p(x + 28, y + 3), 1)
            line(s, timber, p(x + 3, y + 11), p(x + 27, y + 11), 1)
            line(s, timber, p(x + 9, y + 1), p(x + 9, y + 15), 1)
    if stage >= 20:
        line(s, edge, (916, 519), (916, 551), 2)
        poly(s, (194, 184, 139), [(894, 519), (920, 519), (927, 525), (920, 531), (894, 531)])
        line(s, edge, (900, 525), (918, 525), 1)
        line(s, edge, (914, 522), (918, 525), 1)

def crank_hand(hx, hy, side, stride):
    spin = stride * 0.6 + (0.7 if side < 0 else -0.7)
    return (hx + side * 25 + 3.4 * math.cos(spin), hy + 17 + 3.4 * math.sin(spin))

def arm_pose(shoulder, target, side, upper=18.0, fore=20.0):
    dx = target[0] - shoulder[0]
    dy = target[1] - shoulder[1]
    distance = math.hypot(dx, dy)
    if distance < 0.001:
        (dx, dy, distance) = (0, 1, 1)
    reach = min(upper + fore - 0.05, max(abs(upper - fore) + 0.05, distance))
    (ux, uy) = (dx / distance, dy / distance)
    hand = (shoulder[0] + ux * reach, shoulder[1] + uy * reach)
    along = (upper * upper - fore * fore + reach * reach) / (2 * reach)
    bend = math.sqrt(max(0, upper * upper - along * along))
    elbow = (shoulder[0] + ux * along - uy * bend * side, shoulder[1] + uy * along + ux * bend * side)
    return (elbow, hand)

def ease(u):
    return (lambda v: v * v * (3 - 2 * v))(max(0, min(1, u)))

def gesture_weight(t, start, end, ramp=0.28):
    return ease((t - start) / ramp) * ease((end - t) / ramp)

def mix_point(a, b, w):
    return (a[0] + (b[0] - a[0]) * w, a[1] + (b[1] - a[1]) * w)

def pawl_weight(age):
    return max(gesture_weight(age, 0.02, 0.55, 0.16), gesture_weight(age, 0.58, 1.12, 0.16))

def identity_face(s, x, y, age=0, facing=1, scale=1.0, cap=True):
    skin = (190, 155, 121)
    edge = (83, 91, 74)

    def pt(dx, dy):
        return (x + dx * scale * facing, y + dy * scale)

    def path(col, nodes):
        poly(s, col, [pt(*v) for v in nodes])

    def stroke(col, p, q, w):
        line(s, col, pt(*p), pt(*q), w * scale)
    path(skin, [(-11, -13), (3, -15), (10, -9), (10, -3), (17, 3), (11, 6), (9, 15), (1, 19), (-9, 14), (-12, 4)])
    circle(s, (170, 138, 106), pt(-10, 3), 3 * scale)
    stroke(edge, (2, -2), (8, -1), 1.25)
    stroke((117, 109, 85), (8, 0), (10, 6), 0.8)
    stroke((95, 90, 71), (5, 12), (10, 11), 0.85)
    stroke((139, 122, 95), (-5, 12), (2, 16), 0.75)
    hair = (86, 89, 72) if age < 0.5 else (126, 127, 105) if age < 1.5 else (161, 161, 134)
    path(hair, [(-12, 2), (-13, -11), (-4, -18), (7, -15), (12, -9), (7, -9), (1, -12), (-5, -8), (-7, 2)])
    if age > 0.5:
        stroke((133, 121, 95), (-4, -5), (3, -4), 0.7)
        stroke((133, 121, 95), (-3, 7), (1, 9), 0.6)
    if age > 1.5:
        stroke((133, 121, 95), (0, 0), (2, 2), 0.7)
        stroke((150, 139, 112), (-8, 9), (-4, 12), 0.7)
    if cap:
        path((74, 82, 71), [(-15, -10), (-12, -20), (4, -21), (12, -14), (13, -10)])
        stroke((112, 116, 95), (-16, -10), (18, -9), 2)

def warmth_for_exchange(level):
    return operator_warmth(level) if level else 5

def wooden_amount(level):
    return ease((max(1, min(60, level)) - 1) / 59)

def articulated_phase(value, wood):
    unit = math.pi / 2
    cycle = math.floor(value / unit)
    u = value / unit - cycle
    take = 0.98 - 0.65 * wood
    shaped = ease(u / take) if u < take else 1.0
    return value * (1 - wood) + (cycle + shaped) * unit * wood

def routine_settle_duration(level):
    warmth = warmth_for_exchange(level)
    return 0.7 + 1.35 * wooden_amount(level) + 0.16 * (5 - warmth)

def launcher_crew(hub_x, hub_y, angle, phase, stride=0, motion=0, level=0, flight=False, reaction=False, between=False, ground=True, direct_look=False, reset_age=99.0, nod_t=0.0, walking=False, shot_age=99.0, check_age=99.0, finish_t=None, poses=None, dt=1 / 60):
    s = surface(221, 84)
    hx = hub_x - 370
    cloths = [(88, 103, 101), (111, 98, 82)]
    skin = [(189, 155, 121), (170, 140, 111)]
    if ground:
        line(s, WOOD_DARK, (4, 81), (217, 81), 2)
        line(s, (169, 156, 123), (5, 79), (216, 79), 0.8)
        for x in [9, 44, 177, 212]:
            circle(s, INK, (x, 81), 0.9)
    wood = wooden_amount(level)
    gait = articulated_phase(stride, wood)
    sway = math.sin(phase * 1.15) * 0.45 * (1 - wood * 0.9)
    share_active = level == 4 and between and (not flight) and (motion < 0.15) and (not walking) and (3 < phase % 16 < 8) and (finish_t is None)
    share_take = gesture_weight(phase % 16, 3, 8, 0.7) if share_active else 0
    brace = max(0, 1 - shot_age / 0.38)
    check = pawl_weight(check_age) if not flight and motion < 0.15 else 0.0
    if finish_t is not None:
        check = pawl_weight(finish_t - 2.0)
    effort = min(1, abs(angle) / 1.31) * (0.83 if 6 <= level <= 20 else 1.15 if level >= 26 else 1)
    for (idx, side) in enumerate([-1, 1]):
        x = hx + side * 48
        if poses is not None:
            previous = poses.get((idx, 'body_x'), x)
            x = previous + (x - previous) * (1 - math.exp(-max(0, dt) * (11 + wood * 15)))
            x = max(hx + side * 48 - 8, min(hx + side * 48 + 8, x))
            poses[idx, 'body_x'] = x
        x -= side * 12 * share_take
        lean = -side * (2 + effort * 2 + motion) + math.sin(gait + idx * 0.7 * (1 - wood)) * motion * 0.8 * (1 - wood * 0.65)
        social = gesture_weight(phase % 19, 12, 15, 0.55) if between and warmth_for_exchange(level) >= 4 and (level != 4) else 0
        lean -= side * social * (1.6 if idx == 0 else 1.1)
        if idx == 0:
            lean += 12 * check
        build = 2.5 if idx == 0 else -1.3
        warmth = operator_warmth(level) if level else 5
        duration = routine_settle_duration(level)
        reset = max(0, 1 - reset_age / duration)
        lean += side * reset * (2.8 if level >= 36 else 1.2)
        breath = 0 if flight else math.sin(phase * 1.45 + idx * 0.8) * 0.45 * (1 - wood * 0.94)
        if level >= 36 and reset_age < 0.55:
            breath = 0
        lean += side * brace * (1.4 if idx == 0 else 2.1)
        if poses is not None:
            previous = poses.get((idx, 'lean'), lean)
            lean = previous + (lean - previous) * (1 - math.exp(-dt * 16))
            poses[idx, 'lean'] = lean
        head_x = x + lean
        attention = gesture_weight(shot_age, 0.05, 1.8, 0.35) if flight and warmth >= 4 else 0
        head_x += attention * 1.1
        nod = math.sin(max(0, min(1, nod_t / 0.75)) * math.pi) * 1.8 if idx == 1 and level <= 30 else 0
        if idx == 1:
            nod += social * math.sin(max(0, phase % 19 - 12.4) * 2) * 0.8
        if level >= 56:
            head_x += side * 1.4
        if idx == 0:
            lean -= 1.6
            head_x -= 1.6
        else:
            head_x += 0.8
        shoulder = (x + lean, 34 + breath)
        hip = (x, 56)
        ink = (48, 61, 59)
        cloth = cloths[idx]
        flesh = skin[idx]
        for leg in [-1, 1]:
            step = math.sin(gait + idx * 0.7 * (1 - wood) + (math.pi if leg == 1 else 0)) * motion * 2.6
            foot = x + leg * (6 + effort * 2) + step
            knee = x + leg * 4 - side * effort * 1.5
            lift = max(0, math.sin(gait + idx * 0.7 * (1 - wood) + (math.pi if leg == 1 else 0))) * motion * 2
            poly(s, ink, [(x + leg * 4 - 3, 54), (x + leg * 4 + 3, 54), (knee + 3, 66), (foot + 3, 77 - lift), (foot - 3, 77 - lift), (knee - 3, 66)])
            line(s, (104, 109, 98), (x + leg * 4, 58), (knee, 65), 0.7)
            line(s, (65, 76, 72), (knee - 2, 66), (knee + 2, 67), 0.7)
            rect(s, (56, 54, 47), (foot - 4, 75 - lift, 10, 4), rad=1)
            line(s, (150, 139, 109), (foot - 3, 78 - lift), (foot + 5, 78 - lift), 0.65)
        poly(s, ink, [(x - 7 - build, 31), (x + lean - 3, 29), (x + lean + 6 + build, 32), (x + 8 + build, 46), (x + 7 + build, 57), (x - 8 - build, 57), (x - 10 - build, 43)])
        poly(s, cloth, [(x - 6, 33), (x + lean - 2, 31), (x + lean + 4, 34), (x + 6, 47), (x + 5, 55), (x - 6, 55), (x - 8, 43)])
        line(s, (152, 147, 121), (x - 5, 54), (x + 5, 54), 0.55)
        line(s, (60, 72, 71), (x + lean, 35), (x + 1, 53), 0.65)
        for y in [40, 46, 51]:
            circle(s, (179, 167, 131), (x + 1, y), 0.6)
        rect(s, (67, 76, 73), (x - 6, 44, 4, 5), rad=0.5)
        if idx == 0:
            poly(s, (68, 83, 81), [(x - 6, 33), (x - 2, 39), (x - 4, 46), (x - 7, 43)])
            line(s, (146, 150, 126), (x - 6, 35), (x - 4, 40), 0.7)
        else:
            line(s, (74, 77, 66), (x - 4, 34), (x - 2, 52), 1.4)
            line(s, (165, 147, 112), (x - 3, 35), (x - 1, 51), 0.7)
        line(s, (142, 140, 115), (x - 5, 45), (x - 3, 45), 0.5)
        poly(s, (160, 148, 122), [(x + lean - 3, 31), (x + lean, 37), (x + lean + 2, 31)])
        poly(s, (91, 106, 96), [(x + lean - 5, 40), (x + lean + 4, 40), (x + 6, 56), (x - 7, 56)])
        line(s, (176, 161, 121), (x + lean - 4, 40), (x + lean + 3, 40), 0.85)
        rect(s, (142, 135, 103), (x - 4, 49, 4, 4), width=0.5)
        body = s
        s = surface(221, 84)
        rect(s, flesh, (head_x - 2, 25, 4, 7), rad=1)
        identity_face(s, head_x, 20, 2 if idx == 0 else 0, 1, scale=0.43, cap=True)
        music_time = max(0, phase - 0.36) % 32
        whistling = idx == 0 and level in (1, 8, 23, 27, 30) and any((at < music_time < at + 1.6 for at in (1, 4, 7, 10, 17, 20, 23, 26)))
        if idx == 1 and level == 3 and reaction:
            line(s, (91, 80, 62), (head_x - 2, 25), (head_x, 26), 0.7)
            line(s, (91, 80, 62), (head_x, 26), (head_x + 2.5, 24.5), 0.7)
        if idx == 1 and flight and (warmth >= 4):
            circle(s, (55, 66, 58), (head_x + 2, 20.6), 0.6)
        for (dx, dy) in [(-3, 25), (-2, 27), (0, 27), (2, 26)]:
            circle(s, (104, 105, 88), (head_x + dx, dy), 0.3 if idx == 0 else 0.55)
        if whistling:
            circle(s, flesh, (head_x + 0.6, 25.8), 1.7)
            circle(s, (87, 87, 70), (head_x + 0.8, 25.5), 0.85, 0.4)
        if between and (level == 33 and 10 < phase % 23 < 12.6 or (level == 39 and reset_age < 1.2)):
            look = -side if level == 39 else -1
            line(s, (69, 70, 60), (head_x + look, 20), (head_x + look * 3, 20.5), 0.8)
        if between and warmth >= 4 and (12 < phase % 19 < 15) and (level != 4):
            line(s, (69, 70, 60), (head_x - side * 2, 20.5), (head_x - side * 4, 21), 0.7)
            if idx == 1:
                line(s, (118, 112, 91), (head_x + 1, 26), (head_x + 2, 26.4 + math.sin(phase * 2) * 0.4), 0.6)
        body.blit(s, (0, round((nod - attention * 0.8) * SCALE)))
        s = body
        hand = crank_hand(hx, hub_y, side, stride)
        habit = phase % 19
        sharing = share_active
        if walking:
            hand = (x + side * 7 + math.sin(stride + idx) * 3, 61 + math.sin(stride + idx) * 2)
        elif finish_t is not None:
            if idx == 0:
                hand = mix_point(hand, (hx - 12, hub_y + 34), check)
            release = ease((finish_t - (4.8 if idx == 1 else 5.7)) / 1.2)
            hand = mix_point(hand, (x + side * 6, 67), release)
        elif not flight and motion < 0.15:
            if sharing:
                transfer = ease((phase % 16 - 3) / 5)
                take = gesture_weight(phase % 16, 3, 8, 0.7)
                near = idx == (0 if transfer < 0.5 else 1)
                hold = gesture_weight(phase % 16, 3 if idx == 0 else 4.7, 6.3 if idx == 0 else 8, 0.65)
                hand = mix_point(hand, (hx, 59), hold)
            elif idx == 0 and check > 0:
                hand = mix_point(hand, (hx - 12, hub_y + 34), check)
            elif reset > 0 and between:
                w = gesture_weight(reset_age, 0.02, duration, 0.32)
                hand = mix_point(hand, (hx + side * 30, hub_y + 12), w)
            elif between:
                if idx == 0:
                    hand = mix_point(hand, (head_x + 2, 17), gesture_weight(habit, 8, 9.4, 0.42))
                elif level >= 12:
                    hand = mix_point(hand, (x - 4, 34), gesture_weight(habit, 12.4, 14.2, 0.55))
        identity_habit = between and (not flight) and (motion < 0.15) and (15.3 < habit < 16.7) and (not sharing) and (finish_t is None)
        identity_take = gesture_weight(habit, 15.3, 16.7, 0.3) if identity_habit else 0
        hand = mix_point(hand, (x - 2 + 1.5 * math.sin((habit - 15.3) / 1.4 * math.pi * 4) ** 2, 50), identity_take)
        working = min(1, motion + brace)
        support = mix_point((x + side * 7, 68), (hx + side * 15, hub_y + 28), working)
        if finish_t is not None:
            support = mix_point((hx + side * 15, hub_y + 28), (x + side * 7, 68), ease((finish_t - 4.5) / 1.3))
        support = mix_point(support, (x - 3, 51), identity_take)
        (back_elbow, support) = arm_pose((x + lean + side * 4, 36 + breath), support, -side)
        line(s, ink, (x + lean + side * 4, 36 + breath), back_elbow, 4.5)
        line(s, cloth, (x + lean + side * 4, 36 + breath), back_elbow, 3)
        line(s, ink, back_elbow, support, 3.5)
        line(s, cloth, back_elbow, support, 2.4)
        circle(s, flesh, support, 1.7)
        if poses is not None:
            previous = poses.get((idx, 'hand'), hand)
            blend = 1 - math.exp(-dt * 18)
            grip = crank_hand(hx, hub_y, side, stride)
            at_grip = math.dist(hand, grip) < 0.01
            hand = grip if at_grip and poses.get((idx, 'gripping'), True) else mix_point(previous, hand, blend)
            if math.dist(hand, crank_hand(hx, hub_y, side, stride)) < 0.7 and (not walking) and (not check) and (not between):
                hand = crank_hand(hx, hub_y, side, stride)
            poses[idx, 'hand'] = hand
            poses[idx, 'gripping'] = at_grip and math.dist(hand, grip) < 0.7
        arm_root = (x + lean - side * 4, 35 + breath)
        (elbow, hand) = arm_pose(arm_root, hand, -side)
        line(s, ink, arm_root, elbow, 7)
        line(s, cloth, arm_root, elbow, 5)
        line(s, ink, elbow, hand, 6)
        line(s, cloth, elbow, hand, 4)
        circle(s, (121, 116, 93), elbow, 2.8)
        if idx == 1:
            line(s, (168, 157, 125), (elbow[0] + side * 2, elbow[1] + 2), (elbow[0] - side * 2, elbow[1] + 3), 2)
        else:
            line(s, (48, 65, 63), (x - 7, 37), (x - 6, 49), 1.1)
        line(s, (153, 147, 117), (elbow[0] - 1, elbow[1] - 1), (elbow[0] + 1, elbow[1] + 1), 0.5)
        if not walking:
            grip = crank_hand(hx, hub_y, side, stride)
            line(s, INK, (grip[0] - 2, grip[1]), (grip[0] + 2, grip[1]), 2)
        if sharing and idx == (0 if transfer < 0.5 else 1):
            rect(s, (111, 139, 128), (hand[0] - 3, hand[1] - 6, 6, 10), rad=1)
            rect(s, (164, 165, 132), (hand[0] - 1, hand[1] - 8, 3, 3), rad=0.4)
            line(s, (222, 207, 164), (hand[0] - 2, hand[1] - 4), (hand[0] - 2, hand[1] + 2), 0.5)
        circle(s, flesh, hand, 2.4)
        for off in [-0.7, 0.7]:
            line(s, (116, 110, 88), (hand[0] + off, hand[1] - 1), (hand[0] + off, hand[1] + 1), 0.45)
    return finish(s, 221, 84)

def draw_launcher_crew(s, hub_x, hub_y, angle, t, stride=0, motion=0, level=0, flight=False, reaction=False, between=False, direct_look=False, reset_age=99.0, nod_t=0.0, shot_age=99.0, check_age=99.0, poses=None, dt=1 / 60):
    sprite = launcher_crew(hub_x, hub_y, angle, t, stride, motion, level, flight, reaction, between, True, direct_look, reset_age, nod_t, False, shot_age, check_age, poses=poses, dt=dt)
    s.blit(sprite, (370, 0))

def draw_cannon_mount(s, hx, hy, angle, stride, motion=0):
    rail = surface(221, 84)
    radius = math.hypot(34, 12) - 4
    points = [(110 - radius * math.sin(math.radians(d)), 92 - radius * math.cos(math.radians(d))) for d in range(-91, 92, 2)]
    for (aa, bb) in zip(points, points[1:]):
        line(rail, WOOD_DARK, aa, bb, 4.4)
        line(rail, (107, 128, 119), (aa[0], aa[1] - 0.4), (bb[0], bb[1] - 0.4), 2.0)
        line(rail, (205, 200, 161), (aa[0], aa[1] - 1.2), (bb[0], bb[1] - 1.2), 0.65)
    for degree in [-85, -60, -30, 0, 30, 60, 85]:
        rad = math.radians(degree)
        x = 110 - radius * math.sin(rad)
        y = 92 - radius * math.cos(rad)
        line(rail, WOOD_DARK, (x - 3 * math.cos(rad), y + 3 * math.sin(rad)), (x + 3 * math.cos(rad), y - 3 * math.sin(rad)), 2)
        circle(rail, INK, (x, y), 0.6)
    centres = []
    for dx in [-12, 12]:
        centre = (hx - 370 + dx * math.cos(angle), hy + 36 - dx * math.sin(angle))
        centres.append(centre)
        circle(rail, INK, centre, 4.3)
        circle(rail, (178, 176, 137), centre, 3.3)
        circle(rail, (78, 104, 99), centre, 2.5)
        for off in [0, math.pi / 2]:
            v = (math.sin(stride + off) * 2.4, math.cos(stride + off) * 2.4)
            line(rail, (185, 182, 142), (centre[0] - v[0], centre[1] - v[1]), (centre[0] + v[0], centre[1] + v[1]), 0.65)
        circle(rail, INK, centre, 0.9)
        line(rail, WOOD_DARK, (hx - 370 + dx * 0.7, hy + 16), centre, 3.6)
        line(rail, (168, 145, 101), (hx - 370 + dx * 0.7, hy + 16), (centre[0], centre[1] - 1), 1.5)
    line(rail, INK, centres[0], centres[1], 2.4)
    line(rail, (174, 176, 142), (centres[0][0], centres[0][1] - 0.6), (centres[1][0], centres[1][1] - 0.6), 0.65)
    gear = (hx - 370, hy + 36)
    circle(rail, INK, gear, 4.1)
    circle(rail, (169, 145, 102), gear, 2.8)
    for n in range(8):
        p = n * math.pi / 4 + stride * 0.6
        line(rail, INK, (gear[0] + 3.4 * math.sin(p), gear[1] + 3.4 * math.cos(p)), (gear[0] + 4.7 * math.sin(p), gear[1] + 4.7 * math.cos(p)), 1)
    circle(rail, INK, gear, 1)
    for side in [-1, 1]:
        centre = (hx - 370 + side * 25, hy + 17)
        spin = stride * 0.6 + (0.7 if side < 0 else -0.7)
        line(rail, INK, (hx - 370 + side * 12, hy + 29), centre, 2.5)
        circle(rail, (49, 76, 75), centre, 7, 1.8)
        circle(rail, (181, 164, 118), centre, 5.4, 0.8)
        for off in [0, math.pi * 0.5]:
            v = (math.cos(spin + off) * 5.5, math.sin(spin + off) * 5.5)
            line(rail, (104, 130, 118), (centre[0] - v[0], centre[1] - v[1]), (centre[0] + v[0], centre[1] + v[1]), 1.2)
        for n in range(12):
            theta = n * math.pi / 6 + spin
            line(rail, INK, (centre[0] + 6.6 * math.cos(theta), centre[1] + 6.6 * math.sin(theta)), (centre[0] + 7.6 * math.cos(theta), centre[1] + 7.6 * math.sin(theta)), 0.8)
        grip = crank_hand(hx - 370, hy, side, stride)
        circle(rail, (153, 123, 80), grip, 1.8)
        circle(rail, (214, 191, 136), centre, 1.2)
    pawl_tip = (hx - 374, hy + 39 - min(1, max(0, motion)) * 8)
    line(rail, INK, (hx - 384, hy + 34), pawl_tip, 2.6)
    line(rail, TEAL, (hx - 384, hy + 34), pawl_tip, 1.3)
    circle(rail, (187, 176, 128), (hx - 384, hy + 34), 1.2)
    s.blit(finish(rail, 221, 84), (370, 0))

def street_position(left, span, phase):
    p = phase % (2 * span)
    return left + min(p, 2 * span - p)
