from dataclasses import dataclass
from functools import lru_cache
import math
import pygame
from . import art_style as a

@dataclass(frozen=True)
class Day:
    situation: str
    visit: bool
    company: bool
    delivery: bool
    music: str
    perspective: float
    start: float
SITUATIONS = (('first-trade', 'bench', 'repair', 'rain-shelter', 'delivery'), ('paint', 'bench', 'repair', 'lamplight', 'busy'), ('delivery', 'bench', 'stock', 'tea', 'paint'), ('shelter', 'paint', 'tea', 'packing', 'packing'), ('unpacking', 'repair', 'bench', 'paint', 'busy'), ('shop', 'tea', 'busy', 'room', 'shop'), ('delivery', 'bench', 'festival', 'stock', 'room'), ('shop', 'shelter', 'tea', 'packing', 'farewell'), ('unpacking', 'repair', 'trade', 'paint', 'busy'), ('shop', 'fitout', 'trade', 'saturday', 'tea'), ('shop', 'tea', 'delivery', 'shelter', 'stock'), ('room', 'still', 'trade', 'tea', 'celebration'))
MUSIC = (('motif-whistle', 'motif-soft', 'motif-warm', 'motif-soft', 'motif-warm'), ('motif-soft', 'motif-soft', 'motif-whistle', 'motif-soft', 'motif-soft'), ('motif-quiet', 'motif-quiet', 'motif-quiet', 'motif-soft', 'motif-warm'), ('motif-soft', 'motif-warm', 'motif-warm', 'motif-soft', 'motif-warm'), ('village-early',) * 5, ('village-mid', 'village-early', 'village-early', 'village-mid', 'village-late'), ('village-late', 'village-late', 'village-festival', 'village-late', 'village-late'), ('village-late', 'village-mid', 'village-early', 'village-early', 'village-early'), ('city-solo', 'city-solo', 'city-solo', 'city-solo', 'city-spaced'), ('city-spaced', 'city-spaced', 'city-spaced', 'city-solo', 'city-spaced'), ('city-spaced', 'city-solo', 'city-spaced', 'city-spaced', 'city-spaced'), ('city-solo', 'city-spaced', 'city-spaced', 'city-solo', 'city-solo'))
PERSPECTIVE = (0, 0, 0, 0, 0, 0.08, 0.12, 0.1, 0.12, 0.16, 0.3, 0.5, 0.65, 0.7, 0.58, 0.45, 0.3, 0.18, 0.22, 0.15, 0.2, 0.22, 0.28, 0.42, 0.5, 0.58, 0.63, 0.68, 0.54, 0.42, 0.6, 0.72, 0.8, 0.76, 0.7, 0.55, 0.42, 0.27, 0.2, 0.18, 0.22, 0.3, 0.4, 0.5, 0.6, 0.68, 0.78, 0.85, 0.75, 0.66, 0.5, 0.42, 0.58, 0.7, 0.62, 0.4, 0.35, 0.52, 0.42, 0.3)

def day(level):
    level = max(1, min(60, int(level)))
    i = level - 1
    kind = SITUATIONS[i // 5][i % 5]
    return Day(kind, kind not in ('stock', 'room', 'still'), kind in ('bench', 'tea', 'busy', 'festival', 'shelter', 'rain-shelter', 'farewell', 'celebration', 'saturday'), kind in ('delivery', 'packing', 'unpacking', 'fitout', 'stock'), MUSIC[i // 5][i % 5], PERSPECTIVE[i], 1.5 + i * 7 % 11 * 0.31)

def schedule(level):
    d = day(level)
    return tuple(((at, name) for (at, name) in ((d.start + 3.5, 'door'), (d.start + 10.5, 'cup'), (d.start + 20.5, 'wheel')) if (name != 'door' or d.visit) and (name != 'cup' or d.visit) and (name != 'wheel' or level >= 11)))

def source_state(level, t):
    d = day(level)
    clock = max(0, t)
    return (d, clock, clock - d.start)

@lru_cache(maxsize=1024)
def figure(role, age, facing, pose, step=0):
    s = a.surface(64, 96)
    x = 32
    y = 88
    young = role in ('child', 'Kit')
    scale = 0.65 + 0.35 * age if young else 1
    coat = (154, 105, 78) if role == 'parent' else (190, 157, 73) if role == 'Kit' else (76, 118, 132) if role == 'child' else (115, 130, 116)

    def pt(dx, dy):
        return (x + dx * scale * facing, y + dy * scale)

    def line(c, p, q, w):
        a.line(s, c, pt(*p), pt(*q), w * scale)

    def poly(c, points):
        a.poly(s, c, [pt(*p) for p in points])
    swing = math.sin(step * math.pi / 24) * 4 if pose == 'walk' else 0
    for side in [-1, 1]:
        line((65, 78, 67), (side * 5, -27), (side * 7 + side * swing, -2), 5)
        line((57, 63, 52), (side * 7 + side * swing, -2), (side * 7 + side * swing + 5, 0), 4)
    poly(coat, [(-11, -56), (10, -56), (13, -28), (-12, -28)])
    line((191, 165, 128), (0, -63), (0, -54), 7)
    a.circle(s, (190, 163, 126), pt(0, -66), 8 * scale)
    poly((96, 100, 81) if age < 0.6 else (155, 154, 129), [(-8, -65), (-8, -73), (1, -76), (8, -69), (7, -67), (2, -71), (-3, -69), (-4, -64)])
    if role == 'parent':
        line((186, 155, 88), (-7, -56), (8, -53), 4)
        line((186, 155, 88), (6, -54), (7, -43), 3)
        line((224, 208, 153), (6, -46), (8, -46), 1)
    if young:
        line((107, 112, 89), (-9, -72), (10, -72), 2)
    for side in [-1, 1]:
        shoulder = (side * 8, -53)
        target = (side * 11 - swing * 0.35, -32)
        if pose in ('cup', 'repair', 'carry'):
            target = (side * 5 + 10, -42)
        (elbow, hand) = a.arm_pose(shoulder, target, -side, 12, 13)
        line(coat, shoulder, elbow, 5)
        line((185, 158, 122), elbow, hand, 3)
    if pose == 'carry':
        poly((171, 145, 102), [(2, -44), (18, -44), (18, -30), (2, -30)])
        line((222, 204, 158), (10, -44), (10, -30), 1)
    if pose == 'cup':
        poly((224, 211, 170), [(9, -43), (15, -43), (15, -38), (9, -38)])
    return a.finish(s, 64, 96)

def person(s, x, y, role, age, t, pose='stand', face=1, size=1):
    im = figure(role, round(age, 1), face, pose, int(t) % 48 if pose == 'walk' else 0)
    if size != 1:
        im = pygame.transform.smoothscale(im, (round(64 * size), round(96 * size)))
    s.blit(im, (round(x - 32 * size), round(y - 88 * size)))

def table(s, x, y, used=False):
    pygame.draw.rect(s, (147, 122, 87), (x, y, 55, 4), border_radius=1)
    for xx in (x + 4, x + 49):
        pygame.draw.line(s, (122, 111, 83), (xx, y + 3), (xx, y + 18), 2)
    for xx in (x + 14, x + 39):
        pygame.draw.rect(s, (227, 214, 172), (xx, y - 4, 4, 4), border_radius=1)
        pygame.draw.circle(s, (227, 214, 172), (xx + 5, y - 2), 2, 1)
    pygame.draw.ellipse(s, (217, 195, 140), (x + 24, y - 2, 10, 2))

def visitor_state(level, t):
    (d, clock, u) = source_state(level, t)
    if not d.visit or u < 0:
        return None
    arrival = a.ease(u / 5)
    x = 950 - 115 * arrival
    y = 612
    moving = 0 < u < 5
    distance = 950 - x
    face = -1
    if d.company and u >= 11:
        f = a.ease((u - 11) / 18)
        x = 835 - 549 * f
        y = 612 + 11 * f
        distance = 115 + 549 * f
        moving = 11 < u < 29
    elif not d.company and u >= 25:
        f = a.ease((u - 25) / 10)
        x = 835 + 115 * f
        distance = 115 + 115 * f
        face = 1
        moving = 25 < u < 35
        if u >= 35:
            return None
    pose = 'walk' if moving else 'cup' if d.company and u >= 29 or 7 < u < 10 else 'carry' if d.situation in ('paint', 'repair') else 'stand'
    return dict(x=x, y=y, pose=pose, face=face, phase=distance * 1.5, size=0.4)

def draw(s, level, t):
    (d, clock, u) = source_state(level, t)
    age = (level - 1) / 59
    table(s, 220, 605, used=clock > 24)
    grown = level >= 41
    v = visitor_state(level, t)
    if v:
        person(s, v['x'], v['y'], 'child' if grown else 'parent', age, v['phase'], v['pose'], face=v['face'], size=v['size'])
        if d.company and (not grown or level >= 49):
            person(s, v['x'] - 20, v['y'] + 1, 'child' if not grown else 'Kit', min(1, (level - 1) / 30) if not grown else 0, v['phase'] + 0.7, v['pose'] if v['pose'] == 'walk' else 'stand', face=v['face'], size=0.4)
    if d.company and grown:
        person(s, 228, 623, 'parent', age, 0, 'cup' if clock > 13 else 'stand', face=1, size=0.4)
    elif d.situation in ('room', 'stock', 'still'):
        person(s, 280, 623, 'parent', age, 0, 'repair', face=-1, size=0.4)
    if level >= 11:
        q = a.ease((u - 19) / 9)
        x = 100 + 60 * q
        pygame.draw.rect(s, (145, 122, 85), (round(x), 603, 33, 5))
        for xx in (x + 5, x + 28):
            pygame.draw.circle(s, (72, 88, 74), (round(xx), 614), 6, 1)
            angle = q * 15
            pygame.draw.line(s, (120, 128, 99), (round(xx - 5 * math.cos(angle)), round(614 - 5 * math.sin(angle))), (round(xx + 5 * math.cos(angle)), round(614 + 5 * math.sin(angle))), 1)
        if d.delivery:
            pygame.draw.rect(s, (175, 148, 103), (round(x + 5), 591, 21, 12))
        person(s, x - 9, 618, 'worker', age, q * 60 * 1.5, 'walk' if 19 < u < 28 else 'stand', face=1, size=0.4)
    if d.situation in ('repair', 'paint', 'fitout'):
        pygame.draw.rect(s, (146, 120, 81), (802, 569, 27, 16))
        pygame.draw.rect(s, (181, 195, 158), (805, 572, 21, 10))
        if 3.5 < u < 12:
            pygame.draw.line(s, (121, 112, 83), (815, 566), (820, 557), 2)
            pygame.draw.line(s, (189, 170, 113), (818, 559), (821, 555), 3)
    if d.situation in ('packing', 'unpacking', 'farewell'):
        for n in range(3):
            xx = 751 + n * 40
            pygame.draw.rect(s, (165, 139, 98), (xx, 621 - n % 2 * 10, 31, 23))
            pygame.draw.line(s, (221, 198, 143), (xx + 15, 622 - n % 2 * 10), (xx + 15, 641 - n % 2 * 10), 1)
    if d.company and u > 26:
        pygame.draw.ellipse(s, (184, 153, 105), (245, 603, 8, 2))
    (bx, by) = (918, 552)
    pygame.draw.line(s, (133, 118, 82), (bx, by - 11), (bx, by), 2)
    pygame.draw.arc(s, (185, 159, 98), (bx - 4, by - 4, 8, 8), 0, math.pi, 2)
    ring = abs(u - 3.5) < 0.45 and d.visit
    pygame.draw.line(s, (112, 106, 76), (bx, by + 1), (bx + (2 if ring else 0), by + 5), 1)
    if d.visit and 9 < u < 25:
        for xx in (843, 862):
            pygame.draw.rect(s, (225, 212, 170), (xx, 559, 7, 7), border_radius=2)
