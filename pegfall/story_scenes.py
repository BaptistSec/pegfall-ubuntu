from functools import lru_cache
import math
import pygame
from . import art_style as a, farm_world, village_world, city_world
DURATIONS = {'opening': 12.0, 'farm': 10.0, 'village': 12.0, 'ending': 18.0}
CARDS = ()
INK = (64, 74, 65)
SKIN = (190, 155, 121)

def ease(t):
    return a.ease(max(0, min(1, t)))

def mix(x, y, t):
    return x + (y - x) * ease(t)

def level_for(scene):
    return {'opening': 1, 'farm': 20, 'village': 40, 'ending': 60}[scene]

def camera_box(t):
    u = ease(t / 1.7)
    w = round(960 - 320 * u)
    h = round(w * 0.75)
    return pygame.Rect(round((960 - w) * 0.68), round((720 - h) * 0.96), w, h)

def visibility(scene, t):
    duration = DURATIONS[scene]
    return min(ease(t / 0.55), ease((duration - t) / 0.55))

@lru_cache(maxsize=4)
def backdrop(level):
    source = (farm_world if level <= 20 else village_world if level <= 40 else city_world).background(level)
    frame = source.copy()
    pygame.draw.polygon(frame, (193, 189, 155), [(0, 593), (960, 593), (960, 720), (0, 720)])
    return frame

def person(s, x, y, who='self', pose='rest', face=1, age=0, hand=None, t=0, gesture=0, hand_weight=1, look=None, effort=0, pleasure=0):
    p = a.surface(240, 190)
    cx = 110
    self_character = who in ('self', 'owner')
    look = face if look is None else look
    old = age >= 1.5
    cloth = (88, 103, 101) if old and self_character else (111, 98, 82) if self_character else {'Mara': (154, 105, 78), 'Tom': (76, 118, 132), 'Kit': (190, 157, 73)}.get(who, (137, 157, 157))
    build = 4 if old else -1 if age < 0.5 else 1
    lean = 2 + age * 2 + effort * 5 - pleasure * 2
    if pose == 'work':
        lean += 7
    hx = cx + lean
    hy = 21 + math.sin(t * 1.4) * 0.25 + effort * 2 - pleasure + pleasure * 3 * math.sin(max(0, t - 5.6) * 1.3)
    seat = pose == 'sit'
    pygame.draw.ellipse(p, (134, 139, 113, 100), (round((cx - 30) * a.SCALE), round(145 * a.SCALE), round(65 * a.SCALE), round(4 * a.SCALE)))
    for side in [-1, 1]:
        root = (cx + side * 10, 96)
        phase = (t + (0.5 if side > 0 else 0)) % 1
        step = 14 - 56 * phase if phase < 0.5 else -14 + 56 * (phase - 0.5)
        lift = 0 if phase < 0.5 else math.sin((phase - 0.5) * math.pi * 2) * 9
        foot = (cx + side * 14 + step * face if pose == 'walk' else cx + side * 14, 140 - lift if pose == 'walk' else 144)
        if seat:
            foot = (cx + side * 12 + 21, 137)
        (knee, foot) = a.arm_pose(root, foot, -face, 24.2, 24.2)
        a.line(p, (66, 77, 68), root, knee, 11)
        a.line(p, (66, 77, 68), knee, foot, 9)
        a.line(p, (116, 123, 104), (root[0] + 2, root[1] + 4), (knee[0] + 2, knee[1] - 3), 0.8)
        a.rect(p, (52, 57, 48), (foot[0] - 5, foot[1] - 3, 18, 7), rad=2)
    if not self_character:
        if who in ('Mara', 'customer', 'visitor'):
            a.poly(p, cloth, [(cx - 15, 93), (cx + 16, 93), (cx + 25, 139), (cx - 24, 139)])
    a.poly(p, cloth, [(hx - 17 - build, 48), (hx + 16 + build, 48), (cx + 22 + build, 100), (cx - 22 - build, 100)])
    a.line(p, (166, 160, 126), (hx, 51), (cx, 99), 1)
    for yy in [65, 77, 89]:
        a.circle(p, (184, 173, 136), (hx - 2, yy), 1)
    a.poly(p, (211, 201, 163), [(hx - 10, 46), (hx + 8, 46), (hx + 2, 62)])
    a.rect(p, SKIN, (hx - 6, 36, 13, 14), rad=2)
    if self_character:
        a.identity_face(p, hx, hy + 8, age, look, scale=1.0, cap=True)
        if pleasure > 0.05:
            a.line(p, (95, 90, 71), (hx + look * 5, hy + 20), (hx + look * 10, hy + 19 - pleasure * 2), 0.9)
        a.poly(p, (91, 106, 96), [(hx - 12, 64), (hx + 9, 64), (cx + 14, 98), (cx - 16, 98)])
        a.line(p, (176, 161, 121), (hx - 8, 63), (hx + 7, 63), 2)
        a.rect(p, (142, 135, 103), (cx - 9, 86, 8, 7), width=1)
    else:
        a.circle(p, (184, 156, 121), (hx, hy + 8), 12)
        a.poly(p, (91, 83, 70), [(hx - 12, hy + 8), (hx - 11, hy - 4), (hx + 6, hy - 7), (hx + 13, hy + 3), (hx + 10, hy + 12), (hx + 6, hy + 1)])
        if who in ('Mara', 'customer', 'visitor'):
            a.circle(p, (91, 83, 70), (hx - face * 12, hy + 9), 5)
        if who == 'Mara':
            a.line(p, (212, 182, 123), (hx - 14, hy + 26), (hx + 14, hy + 30), 6)
        a.poly(p, (184, 156, 121), [(hx + face * 9, hy + 5), (hx + face * 15, hy + 11), (hx + face * 9, hy + 15)])
        a.line(p, (181, 145, 88), (hx - 9, hy + 23), (hx + 10, hy + 26), 4)
    for side in [-1, 1]:
        shoulder = (hx + side * (15 + build * 0.3), 54)
        target = (cx + side * 20, 109)
        if gesture > 0:
            pulse = math.sin(gesture * math.pi * 4) ** 2
            at = (cx - 4 + (5 * pulse if side == 1 else 0), 82 if side == 1 else 85)
            weight = ease(gesture / 0.18) * ease((1 - gesture) / 0.18)
            target = a.mix_point(target, at, weight)
        elif hand is not None and side == face:
            target = a.mix_point(target, (hand[0] - (x - 110), hand[1] - (y - 150)), hand_weight)
        (elbow, target) = a.arm_pose(shoulder, target, side if hand is not None and side == face and (not gesture) else -side, 27.0, 29.0)
        a.line(p, cloth, shoulder, elbow, 10)
        a.line(p, (171, 147, 116), elbow, target, 7)
        a.circle(p, SKIN, target, 4)
        a.line(p, (119, 123, 100), shoulder, elbow, 0.7)
        if gesture > 0 and side == 1:
            a.line(p, (113, 107, 85), (target[0] - 3, target[1]), (target[0] + 3, target[1]), 1)
    s.blit(a.finish(p, 240, 190), (round(x - 110), round(y - 150)))

def table(s, x=240, y=567, w=175):
    pygame.draw.rect(s, (128, 104, 74), (x + 9, y + 12, 10, 64))
    pygame.draw.rect(s, (128, 104, 74), (x + w - 19, y + 12, 10, 64))
    pygame.draw.rect(s, (179, 148, 103), (x, y, w, 16), border_radius=3)
    pygame.draw.line(s, (228, 204, 156), (x + 3, y + 2), (x + w - 3, y + 2), 2)

def ledger(s, x=293, y=555, closed=False):
    pygame.draw.polygon(s, (91, 100, 80), [(x, y - 12), (x + 42, y - 8), (x + 40, y + 8), (x - 2, y + 3)])
    if not closed:
        pygame.draw.polygon(s, (228, 215, 175), [(x + 2, y - 10), (x + 39, y - 6), (x + 37, y + 5), (x, y + 1)])
        for n in range(3):
            pygame.draw.line(s, (140, 139, 108), (x + 6, y - 6 + n * 3), (x + 28, y - 3 + n * 3), 1)

def cashbox(s, x=352, y=552, coins=2):
    pygame.draw.rect(s, (109, 129, 112), (x, y, 47, 19), border_radius=2)
    pygame.draw.polygon(s, (88, 107, 93), [(x, y), (x + 47, y), (x + 44, y - 14), (x + 3, y - 16)])
    for n in range(coins):
        pygame.draw.circle(s, (195, 167, 94), (x + 5 + n % 6 * 6, y + 3 - n // 6 * 4), 3)
    pygame.draw.rect(s, (192, 166, 105), (x + 21, y + 11, 6, 4))

def board(s, x=560, y=390, developed=0, spin=0):
    pygame.draw.rect(s, (128, 104, 74), (x - 104, y - 151, 208, 285), border_radius=5)
    pygame.draw.rect(s, (201, 205, 173), (x - 97, y - 144, 194, 271), border_radius=2)
    for row in range(7):
        for col in range(5):
            px = x - 65 + col * 31 + (8 if row % 2 else 0)
            py = y - 57 + row * 24
            pygame.draw.circle(s, (193, 124, 61) if (row + col) % 6 == 0 else (76, 121, 130), (px, py), 4)
    from pathlib import Path
    label = pygame.font.Font(str(Path(__file__).resolve().parent / 'assets/fonts/LiberationSans-Bold.ttf'), 13).render('THE BRASS LANTERN', True, (71, 84, 70))
    pygame.draw.rect(s, (213, 196, 145), (x - 103, y - 172, 206, 20))
    s.blit(label, label.get_rect(center=(x, y - 162)))
    for dx in [-61, -20, 21, 62]:
        pygame.draw.rect(s, (120, 112, 82), (x + dx - 16, y + 108, 33, 14), 2)
    cannon = a.launcher(0, 0)
    s.blit(cannon, cannon.get_rect(center=(x, y - 112)))
    for dx in [-95, 95]:
        pygame.draw.line(s, (116, 104, 76), (x + dx, y + 128), (x + dx, y + 244), 6)
    for dx in [-60, 60]:
        pygame.draw.line(s, (85, 99, 84), (x + dx, y - 112), (x + dx, y + 190), 3)
        pygame.draw.line(s, (85, 99, 84), (x + dx, y - 112), (x, y - 112), 3)
        centre = (x + dx, y + 190)
        pygame.draw.circle(s, INK, centre, 14, 3)
        for theta in [spin, spin + math.pi / 2]:
            v = (math.cos(theta) * 11, math.sin(theta) * 11)
            pygame.draw.line(s, (123, 133, 106), (round(centre[0] - v[0]), round(centre[1] - v[1])), (round(centre[0] + v[0]), round(centre[1] + v[1])), 2)
        pygame.draw.circle(s, (184, 160, 112), centre, 3)
    pygame.draw.line(s, (151, 123, 84), (x - 94, y + 219), (x + 94, y + 219), 5)
    if developed:
        pygame.draw.line(s, (219, 192, 130), (x - 105, y - 152), (x + 105, y - 152), 3)

def spanner(s, x, y):
    pygame.draw.line(s, (86, 102, 94), (round(x - 5), round(y + 7)), (round(x + 5), round(y - 7)), 4)
    pygame.draw.arc(s, (86, 102, 94), (round(x), round(y - 14), 11, 11), 0.1, 4.5, 3)

def gesture_window(t, start, end, ramp):
    return ease((t - start) / ramp) * ease((end - t) / ramp)

def gesture_age(t, start, length=1.5):
    return (t - start) / length if start < t < start + length else 0

def scene_beat(scene, t):
    return next((label for (end, label) in BEATS[scene] if t < end), BEATS[scene][-1][1])
BEATS = {'opening': ((3, 'repair'), (6, 'mother-and-child-arrive'), (10, 'child-plays'), (12, 'shared-delight')), 'farm': ((3, 'lift-together'), (7, 'load-cart'), (10, 'leave-together')), 'village': ((3, 'tea-arrives'), (7, 'work-takes-attention'), (12, 'cup-left-with-room-beside-it')), 'ending': ((4, 'last-turn'), (8, 'put-tools-away'), (12, 'join-the-table'), (18, 'share-the-evening'))}

def coin(s, start, end, u):
    u = max(0, min(1, u))
    x = mix(start[0], end[0], u)
    y = mix(start[1], end[1], u)
    pygame.draw.circle(s, (167, 143, 89), (round(x), round(y)), 5)
    pygame.draw.circle(s, (220, 194, 125), (round(x - 1), round(y - 1)), 3)
BALL_PATH = ((560, 312), (534, 333), (570, 357), (542, 381), (580, 405), (551, 429), (578, 453), (551, 477), (580, 498), (581, 511))

def played_ball(s, elapsed):
    if elapsed < 0:
        return
    u = min(1, elapsed / 2.5) * (len(BALL_PATH) - 1)
    i = min(len(BALL_PATH) - 2, int(u))
    v = u - i
    x = BALL_PATH[i][0] + (BALL_PATH[i + 1][0] - BALL_PATH[i][0]) * v
    y = BALL_PATH[i][1] + (BALL_PATH[i + 1][1] - BALL_PATH[i][1]) * v
    pygame.draw.circle(s, (65, 79, 69), (round(x), round(y)), 6)
    pygame.draw.circle(s, (235, 227, 187), (round(x - 1), round(y - 1)), 4)

def cart(s, x, y):
    for dx in [10, 116]:
        pygame.draw.circle(s, INK, (round(x + dx), y + 17), 14, 4)
    pygame.draw.rect(s, (145, 120, 86), (round(x), y - 6, 130, 14))
    pygame.draw.line(s, (145, 120, 86), (round(x), y), (round(x - 25), y - 40), 5)

def actor(s, x, y, who='owner', age=0, scale=1.0, pose='rest', face=1, t=0, hand=None, weight=1.0, pleasure=0, speed=65):
    layer = pygame.Surface((240, 190), pygame.SRCALPHA)
    local = None if hand is None else (110 + (hand[0] - x) / scale, 150 + (hand[1] - y) / scale)
    person(layer, 110, 150, who, pose, face, age, local, t * speed / (56 * scale) if pose == 'walk' else t, 0, weight, face, 0, pleasure)
    size = (round(240 * scale), round(190 * scale))
    s.blit(pygame.transform.smoothscale(layer, size), (round(x - 110 * scale), round(y - 150 * scale)))

def travel(start, end, t, begin, duration):
    u = max(0, min(1, (t - begin) / duration))
    return (start + (end - start) * u, 'walk' if 0 < u < 1 else 'rest')

def mug(s, x, y):
    pygame.draw.rect(s, (224, 211, 167), (round(x - 7), round(y - 12), 14, 13), border_radius=2)
    pygame.draw.circle(s, (224, 211, 167), (round(x + 9), round(y - 6)), 4, 2)
    pygame.draw.ellipse(s, (112, 104, 79), (round(x - 6), round(y - 13), 12, 4))

def tea_table(s):
    table(s, 240, 570, 168)
    for x in [275, 328, 380]:
        mug(s, x, 570)

@lru_cache(maxsize=5)
def empty_stage(scene):
    return backdrop(level_for(scene)).copy()

def scene_frame(scene, t):
    t = max(0, min(t, DURATIONS[scene]))
    s = empty_stage(scene).copy()
    board(s, 560, 390, scene != 'opening', max(0, min(2.5, t - 6)) * 2.5 if scene == 'opening' else max(0, min(2.5, t)) * 2.5 if scene == 'ending' else 0)
    if scene == 'opening':
        weight = 1 - ease((t - 2) / 1.0)
        actor(s, 456, 640, age=0, t=t, hand=(500, 580), weight=weight, pleasure=ease((t - 8) / 2))
        if t < 3:
            spanner(s, mix(500, 468, t - 2), mix(580, 605, t - 2))
        (tx, walk) = travel(920, 655, t, 1, 4)
        (mx, mwalk) = travel(995, 728, t, 1, 4)
        actor(s, mx, 640, 'Mara', face=-1, t=t, pose=mwalk, hand=(690, 593), weight=gesture_window(t, 5, 10, 0.7))
        actor(s, tx, 640, 'Tom', scale=0.65, face=-1, t=t, pose=walk, hand=(620, 580), weight=gesture_window(t, 5.5, 9.5, 0.7))
        if t >= 6:
            played_ball(s, t - 6)
    elif scene == 'farm':
        cart(s, 590, 595)
        u = max(0, min(1, (t - 3) / 3))
        cx = 520 + 130 * u
        cy = 580 - 15 * ease(t / 2)
        if t >= 7:
            cy = 565 + 11 * ease((t - 7) / 1)
        moving = 3 < t < 6
        actor(s, cx - 64, 640, age=0.45, face=1, t=t, pose='walk' if moving else 'rest', hand=(cx - 23, cy), weight=1 - ease((t - 8) / 0.6))
        actor(s, cx + 64, 640, 'Tom', scale=0.86, face=-1, t=t, pose='walk' if moving else 'rest', hand=(cx + 23, cy), weight=1 - ease((t - 8) / 0.6))
        pygame.draw.rect(s, (148, 119, 78), (round(cx - 25), round(cy - 13), 50, 27), border_radius=2)
        pygame.draw.line(s, (207, 176, 119), (round(cx - 22), round(cy - 7)), (round(cx + 22), round(cy - 7)), 2)
        actor(s, 805, 640, 'Mara', face=-1, t=t)
    elif scene == 'village':
        table(s, 240, 570, 168)
        actor(s, 456, 640, age=1, face=1, t=t, hand=(500, 580), weight=gesture_window(t, 2, 11, 0.5))
        (mx, walk) = travel(170, 328, t, 0, 3)
        actor(s, mx, 640, 'Mara', age=1, face=1, t=t, pose=walk, hand=(365, 570), weight=gesture_window(t, 3, 5, 0.5))
        mug(s, 365 if t >= 4 else mx + 27, 570)
        actor(s, 750, 640, 'Tom', face=-1, t=t)
        mug(s, 292, 570)
    else:
        table(s, 240, 570, 205)
        for x in [275, 328, 380] if t < 14 else [275, 328]:
            mug(s, x, 570)
        actor(s, 215, 640, 'Mara', age=2, face=1, t=t)
        (ox, walk) = travel(456, 410, t, 7, 2)
        cup = (380 + 20 * ease((t - 14) / 1), 570 - 27 * ease((t - 14) / 1))
        actor(s, ox, 640, age=2, face=1 if t < 7 else -1, t=t, pose=walk, speed=23, hand=(500, 580) if t < 7 else cup, weight=1 - ease((t - 4) / 2) if t < 7 else ease((t - 11) / 1), pleasure=0.5)
        if t < 8:
            actor(s, 730, 640, 'Tom', face=-1, t=t)
            actor(s, 650, 640, 'Kit', scale=0.65, face=-1, t=t, hand=(620, 580), weight=1 - ease((t - 3) / 1))
            if t < 3:
                played_ball(s, t)
        else:
            (tx, twalk) = travel(730, 330, t, 8, 6)
            (kx, kwalk) = travel(650, 275, t, 8, 6)
            yy = 640 + 20 * ease((t - 8) / 0.7) - 20 * ease((t - 14) / 0.7)
            actor(s, tx, yy, 'Tom', face=-1 if t < 14 else 1, t=t, pose='walk' if 8 < t < 14.7 else 'rest', speed=400 / 6)
            actor(s, kx, yy + 6, 'Kit', scale=0.65, face=-1 if t < 14 else 1, t=t, pose='walk' if 8 < t < 14.7 else 'rest', speed=375 / 6)
        if t >= 14:
            mug(s, *cup)
    if scene == 'ending' and t > 4:
        amount = max(0, min(1, (t - 4) / 2))
        height = round(267 * amount)
        pygame.draw.rect(s, (139, 131, 99), (463, 247, 194, height))
        for yy in range(250, 247 + height, 18):
            pygame.draw.line(s, (164, 153, 114), (465, yy), (655, yy), 1)
        pygame.draw.line(s, (102, 100, 79), (463, 247 + height), (657, 247 + height), 5)
    return s

def scene_camera(scene, age, hold=False):
    return pygame.Rect(140, 160, 720, 540)

def draw(s, scene, t, font, small, hint=True, hold=False):
    age = max(0, min(t, DURATIONS[scene]))
    raw = scene_frame(scene, age)
    s.blit(pygame.transform.smoothscale(raw.subsurface(scene_camera(scene, age)), (960, 720)), (0, 0))
    if hint and age < 2:
        label = small.render('Enter / Esc - skip', True, (43, 63, 54))
        s.blit(label, label.get_rect(center=(480, 692)))
