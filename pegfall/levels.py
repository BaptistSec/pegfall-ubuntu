from __future__ import annotations
import math
(BLUE, ORANGE, GREEN) = ('blue', 'orange', 'green')

class Peg:
    __slots__ = ('x', 'y', 'kind', 'alive', 'lit', 'flash', 'r')

    def __init__(self, x: float, y: float, kind: str):
        (self.x, self.y, self.kind) = (x, y, kind)
        self.r = 11.0
        self.alive = True
        self.lit = False
        self.flash = 0.0

class Block(Peg):
    shape = 'box'
    __slots__ = ('w', 'h', 'angle', 'rest')

    def __init__(self, x, y, w, h, kind=BLUE, angle=0.0):
        super().__init__(x, y, kind)
        (self.w, self.h, self.angle) = (w, h, angle)
        self.rest = 0.8

class Rail:
    shape = 'box'

    def __init__(self, x, y, w, h, angle=0.0):
        (self.x, self.y, self.w, self.h, self.angle) = (x, y, w, h, angle)
        (self.kind, self.alive, self.flash) = ('rail', True, 0.0)
        (self.rest, self.kick) = (0.8, 0.0)

class Bumper:
    __slots__ = ('x', 'y', 'r', 'alive', 'kind', 'rest', 'kick', 'flash')

    def __init__(self, x: float, y: float):
        (self.x, self.y) = (x, y)
        self.r = 14.0
        self.alive = True
        self.kind = 'bumper'
        self.rest = 0.9
        self.kick = 420.0
        self.flash = 0.0

class Layout:

    def __init__(self, name: str, subtitle: str, pegs: list[Peg], balls: int=10, star2: int=20000, star3: int=40000, hint: str='', bumpers: list[Bumper] | None=None, rails=None):
        (self.name, self.subtitle, self.pegs) = (name, subtitle, pegs)
        self.balls = balls
        self.star2 = star2
        self.star3 = star3
        self.hint = hint
        self.bumpers = bumpers or []
        self.rails = rails or []

def _dedupe(pts):
    out = []
    for (x, y, k) in sorted(pts, key=lambda p: p[2] == BLUE):
        if all(((x - a) ** 2 + (y - b) ** 2 > 26 ** 2 for (a, b, _) in out)):
            out.append((x, y, k))
    return out

def _ring(cx, cy, r, n, kind, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cy + r * math.sin(a0 + 2 * math.pi * i / n), kind) for i in range(n)]

def _arc(cx, cy, r, n, kind, a0, a1):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / max(1, n - 1)), cy + r * math.sin(a0 + (a1 - a0) * i / max(1, n - 1)), kind) for i in range(n)]

def _row(x0, y, n, kind, gap=44):
    return [(x0 + i * gap, y, kind) for i in range(n)]

def _col(x, y0, n, kind, gap=44):
    return [(x, y0 + i * gap, kind) for i in range(n)]

def _grid(x0, y0, cols, rows, kind, gx=52, gy=48, skip=None):
    pts = []
    for r in range(rows):
        for c in range(cols):
            if skip and skip(c, r):
                continue
            pts.append((x0 + c * gx + (26 if r % 2 else 0), y0 + r * gy, kind))
    return pts

def _spiral(cx, cy, r0, r1, n, kind, turns=1.6, a0=-math.pi / 2):
    pts = []
    for i in range(n):
        t = i / max(1, n - 1)
        a = a0 + turns * 2 * math.pi * t
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a), kind))
    return pts

def _mk(name, sub, pts, balls=10, star2=20000, star3=40000, hint='', bumpers=()):
    return Layout(name, sub, [Peg(x, y, k) for (x, y, k) in _dedupe(pts)], balls, star2, star3, hint, [Bumper(x, y) for (x, y) in bumpers])

def _new_boards() -> list[Layout]:
    N = []
    pts = _arc(300, 400, 150, 9, BLUE, -0.5, 1.2)
    pts += _arc(660, 400, 150, 9, BLUE, math.pi - 1.2, math.pi + 0.5)
    pts += [(300, 280, ORANGE), (480, 340, ORANGE), (660, 280, ORANGE)]
    pts += [(480, 480, GREEN)]
    N.append(_mk('Ember Path', 'Follow the embers', pts, star2=30000, star3=55000, hint='bank softly off the arcs - embers reward a patient aim'))
    pts = []
    for i in range(5):
        pts += _col(220 + i * 130, 180 + i % 2 * 60, 5, BLUE)
    pts += [(285, 480, ORANGE), (415, 480, ORANGE), (545, 480, ORANGE), (675, 480, ORANGE)]
    pts += [(480, 300, GREEN)]
    N.append(_mk('Loom', 'Weave the threads', pts, balls=11, star2=22000, star3=42000))
    pts = []
    for (cx, cy) in ((250, 260), (480, 420), (710, 260)):
        pts += _ring(cx, cy, 52, 7, BLUE)
        pts.append((cx, cy, ORANGE))
    pts += _row(230, 580, 11, BLUE, gap=50)
    pts += [(480, 610, ORANGE)]
    pts += [(480, 260, GREEN)]
    N.append(_mk('Tide Pools', 'Every pool hides a light', pts, star2=20000, star3=40000))
    pts = []
    for r in range(4):
        y = 200 + r * 110
        x0 = 150 if r % 2 == 0 else 240
        pts += _row(x0, y, 7, BLUE, gap=90)
    pts += [(195, 255, ORANGE), (765, 365, ORANGE), (195, 475, ORANGE), (765, 585, ORANGE)]
    pts += [(480, 310, GREEN)]
    N.append(_mk('Switchback', 'Turn on the bumpers', pts, star2=40000, star3=70000, hint='the side bumpers open the corner oranges', bumpers=[(120, 420), (840, 420)]))
    pts = _ring(300, 300, 70, 8, BLUE) + _ring(660, 300, 70, 8, BLUE)
    pts += _ring(480, 490, 80, 9, BLUE, 0.35)
    pts += [(300, 230, ORANGE), (300, 370, ORANGE), (660, 230, ORANGE), (660, 370, ORANGE), (480, 570, ORANGE)]
    pts += [(480, 300, GREEN)]
    N.append(_mk('Orrery', 'Set the worlds turning', pts, star2=40000, star3=75000))
    pts = []
    for r in range(6):
        n = 9 - r
        for c in range(n):
            pts.append((480 + (c - (n - 1) / 2) * 80 + (40 if r % 2 else 0), 170 + r * 66, BLUE))
    pts += [(350, 560, ORANGE), (480, 610, ORANGE), (610, 560, ORANGE), (480, 490, ORANGE)]
    pts += [(480, 240, GREEN)]
    N.append(_mk('Frostline', 'Dig for the deep lights', pts, balls=11, star2=40000, star3=75000))
    pts = _spiral(480, 380, 30, 230, 18, BLUE, turns=1.6)
    pts += _spiral(480, 380, 30, 230, 18, BLUE, turns=-1.6)
    pts += _spiral(480, 380, 70, 200, 5, ORANGE, turns=1.6, a0=-math.pi / 2 + 0.5)
    pts += [(480, 380, GREEN)]
    N.append(_mk('Helix', 'Two ways round', pts, balls=11, star2=45000, star3=80000))
    pts = _col(380, 180, 9, BLUE, gap=45) + _col(580, 180, 9, BLUE, gap=45)
    pts += [(480, 220, ORANGE), (480, 360, ORANGE), (480, 500, ORANGE), (300, 600, ORANGE), (660, 600, ORANGE)]
    pts += _row(200, 620, 3, BLUE, gap=50) + _row(660, 620, 3, BLUE, gap=50)
    pts += [(480, 420, GREEN)]
    N.append(_mk('Gauntlet', 'Run the channel', pts, balls=12, star2=22000, star3=42000, hint='the gate bumpers guard the centre oranges - slip between them', bumpers=[(380, 340), (580, 340), (380, 520), (580, 520)]))
    pts = []
    for r in range(8):
        for c in range(3):
            pts.append((428 + c * 52, 180 + r * 56, BLUE))
    pts += _arc(240, 380, 110, 8, BLUE, -1.2, 1.2) + _arc(720, 380, 110, 8, BLUE, math.pi - 1.2, math.pi + 1.2)
    pts += [(480, 250, ORANGE), (430, 390, ORANGE), (530, 390, ORANGE), (480, 530, ORANGE)]
    pts += [(200, 300, GREEN), (760, 300, GREEN)]
    N.append(_mk('Monolith', 'Wake the standing stone', pts, balls=12, star2=40000, star3=80000))
    pts = _ring(480, 380, 260, 18, BLUE)
    pts += _grid(340, 250, 5, 3, BLUE, gx=70, gy=90)
    pts += [(480, 120, ORANGE), (220, 380, ORANGE), (740, 380, ORANGE), (480, 640, ORANGE), (350, 250, ORANGE), (610, 250, ORANGE)]
    pts += [(170, 560, GREEN), (790, 560, GREEN)]
    N.append(_mk('Eventide', 'The whole sky at once', pts, balls=13, star2=45000, star3=80000, bumpers=[(350, 470), (610, 470)]))
    return N

def _finale_boards() -> list[Layout]:
    N = []
    pts = []
    for i in range(7):
        x = 190 + i * 97
        pts += _col(x, 160 + i % 2 * 78, 6, BLUE, gap=48)
    pts += [(238, 330, ORANGE), (335, 360, ORANGE), (432, 330, ORANGE), (529, 360, ORANGE), (626, 330, ORANGE), (723, 360, ORANGE)]
    pts += [(480, 560, GREEN)]
    N.append(_mk('Aurora', 'Hang the curtains', pts, balls=9, star2=40000, star3=75000, hint='thread a channel - the corner bumpers send the ball back up', bumpers=[(140, 590), (820, 590)]))
    pts = _arc(660, 300, 270, 16, BLUE, math.pi * 0.6, math.pi * 1.28)
    pts += _arc(660, 300, 200, 12, BLUE, math.pi * 0.6, math.pi * 1.28)
    pts += _ring(660, 300, 52, 8, BLUE) + _ring(660, 300, 26, 5, BLUE)
    for a in (0.65, 0.75, 0.85, 1.05, 1.25):
        pts.append((660 + 235 * math.cos(math.pi * a), 300 + 235 * math.sin(math.pi * a), ORANGE))
    pts += [(712, 300, ORANGE), (660, 352, ORANGE)]
    pts += [(660, 300, GREEN)]
    N.append(_mk("Comet's Wake", 'Chase the tail', pts, balls=9, star2=45000, star3=80000, hint='the bumper at the tail tip flings the ball back along the lane', bumpers=[(660, 610)]))
    pts = _arc(480, 660, 320, 19, BLUE, math.pi * 1.04, math.pi * 1.96)
    pts += _arc(480, 660, 250, 15, BLUE, math.pi * 1.02, math.pi * 1.98)
    pts += _arc(480, 660, 180, 11, BLUE, math.pi * 1.05, math.pi * 1.95)
    for a in (1.15, 1.35, 1.65, 1.85):
        pts.append((480 + 285 * math.cos(math.pi * a), 660 + 285 * math.sin(math.pi * a), ORANGE))
    for a in (1.25, 1.5, 1.75):
        pts.append((480 + 215 * math.cos(math.pi * a), 660 + 215 * math.sin(math.pi * a), ORANGE))
    pts += [(480, 550, ORANGE)]
    pts += [(120, 300, GREEN), (840, 300, GREEN)]
    N.append(_mk('Daybreak', 'Raise the last sun', pts, balls=11, star2=45000, star3=85000, hint='the horizons hide the powers - a wide bank shot pays for itself', bumpers=[(170, 600), (790, 600)]))
    return N

def _afterglow_boards() -> list[Layout]:
    N = []
    pts = []
    for (cx, cy) in ((220, 220), (740, 220), (220, 520), (740, 520)):
        pts += _ring(cx, cy, 46, 6, BLUE)
    pts += [(480, 220, ORANGE), (220, 370, ORANGE), (740, 370, ORANGE), (480, 520, ORANGE), (480, 370, ORANGE)]
    pts += [(480, 600, GREEN)]
    N.append(_mk('Meteor Belt', 'Slingshot the void', pts, balls=10, star2=40000, star3=75000, hint='the hub bumpers fling the ball into the open lanes', bumpers=[(480, 292), (480, 448)]))
    pts = []
    for i in range(8):
        a = 0.7 + i * 0.093
        pts.append((140 + 420 * math.cos(a), 90 + 420 * math.sin(a), BLUE))
    for i in range(8):
        a = math.pi - 0.7 - i * 0.093
        pts.append((820 + 420 * math.cos(a), 90 + 420 * math.sin(a), BLUE))
    a = 1.47
    pts.append((140 + 420 * math.cos(a), 90 + 420 * math.sin(a), ORANGE))
    pts.append((820 - 420 * math.cos(a), 90 + 420 * math.sin(a), ORANGE))
    pts += [(300, 520, ORANGE), (660, 520, ORANGE), (480, 470, ORANGE)]
    pts += [(480, 600, GREEN)]
    N.append(_mk('Wingspan', 'On two great wings', pts, balls=10, star2=45000, star3=80000, hint='the wingtips hug the walls - a long bank shot pays for itself'))
    pts = _arc(280, 680, 210, 12, BLUE, math.pi * 1.05, math.pi * 1.95)
    pts += _arc(680, 680, 210, 12, BLUE, math.pi * 1.05, math.pi * 1.95)
    pts += _arc(280, 680, 140, 8, BLUE, math.pi * 1.07, math.pi * 1.93)
    pts += _arc(680, 680, 140, 8, BLUE, math.pi * 1.07, math.pi * 1.93)
    for cx in (280, 680):
        for a in (1.25, 1.5, 1.75):
            pts.append((cx + 175 * math.cos(math.pi * a), 680 + 175 * math.sin(math.pi * a), ORANGE))
    pts += [(480, 560, ORANGE), (480, 460, ORANGE)]
    pts += [(480, 240, GREEN), (480, 640, GREEN)]
    N.append(_mk('Twin Suns', 'Two dawns at once', pts, balls=9, star2=45000, star3=85000, hint='the valley bumpers turn a spent ball into a cross-shot', bumpers=[(430, 645), (530, 645)]))
    return N

def build_classic_levels() -> list[Layout]:
    L = []
    pts = _arc(480, 430, 190, 13, BLUE, math.pi, 2 * math.pi)
    pts += _arc(480, 430, 120, 9, BLUE, math.pi, 2 * math.pi)
    pts += [(480, 330, ORANGE), (395, 390, ORANGE), (565, 390, ORANGE)]
    pts += [(480, 520, GREEN)]
    L.append(_mk('First Light', 'Wake the dawn pegs', pts, star2=20000, star3=40000, hint='clear every orange peg - catch the ball in the bucket for a free shot'))
    pts = _col(300, 200, 7, BLUE) + _col(660, 200, 7, BLUE)
    pts += _row(344, 300, 7, BLUE) + _row(344, 460, 7, BLUE)
    pts += [(480, 380, ORANGE), (300, 560, ORANGE), (660, 560, ORANGE)]
    pts += [(480, 240, GREEN)]
    L.append(_mk('Twin Gates', 'Thread the middle', pts, star2=30000, star3=45000, hint='the purple peg is worth 5x a blue peg - it moves after every shot'))
    pts = _ring(480, 360, 70, 7, BLUE) + _ring(480, 360, 130, 11, BLUE, 0.28)
    pts += _ring(480, 360, 190, 15, BLUE, 0.14) + _ring(480, 360, 250, 19, BLUE, 0.07)
    pts += _ring(480, 360, 130, 3, ORANGE, 0.9) + [(480, 610, ORANGE)]
    pts += [(480, 360, GREEN)]
    L.append(_mk('Carousel', 'Round and round', pts, star2=24000, star3=45000, hint='green pegs grant powers: guide, comet, multiball, burst'))
    pts = []
    for i in range(8):
        (x0, y0) = (150 + i * 94, 150 + i % 3 * 36)
        pts += [(x0 + j * 16, y0 + j * 54, BLUE) for j in range(6)]
    pts += _row(180, 600, 11, BLUE, gap=60)
    pts += [(230, 520, ORANGE), (418, 492, ORANGE), (606, 520, ORANGE), (794, 492, ORANGE), (480, 600, ORANGE)]
    pts += [(480, 300, GREEN)]
    L.append(_mk('Rainfall', 'Mind the gaps', pts, star2=40000, star3=70000, hint='follow the streaks down into the puddles'))
    pts = []
    for i in range(6):
        pts.append((170 + i * 42, 180 + i * 44, BLUE))
        pts.append((790 - i * 42, 180 + i * 44, BLUE))
    for i in range(5):
        pts.append((160 + i * 30, 492 + i * 33, BLUE))
        pts.append((800 - i * 30, 492 + i * 33, BLUE))
    pts += [(450, 505, BLUE), (510, 505, BLUE), (420, 605, BLUE), (540, 605, BLUE)]
    pts += [(480, 470, ORANGE), (420, 560, ORANGE), (540, 560, ORANGE), (480, 630, ORANGE)]
    pts += [(480, 300, GREEN)]
    L.append(_mk('Hourglass', 'Everything falls through', pts, star2=32000, star3=55000))
    pts = []
    for (cx, cy, n) in ((260, 240, 6), (700, 220, 6), (480, 420, 7), (250, 560, 5), (710, 560, 5)):
        pts += _ring(cx, cy, 46, n, BLUE)
    pts += [(260, 240 - 46, ORANGE), (700, 220 - 46, ORANGE), (480, 420 - 46, ORANGE), (250, 560 - 46, ORANGE), (710, 560 - 46, ORANGE)]
    pts += [(260, 240, BLUE), (700, 220, BLUE), (480, 420, BLUE), (250, 560, BLUE), (710, 560, BLUE)]
    pts += [(480, 250, GREEN)]
    L.append(_mk('Constellation', 'Join the dots', pts, star2=18000, star3=36000))
    pts = _spiral(480, 380, 30, 240, 30, BLUE, turns=1.9)
    pts += _spiral(480, 380, 60, 210, 5, ORANGE, turns=1.9, a0=-math.pi / 2 + 0.7)
    pts += [(480, 380, GREEN)]
    L.append(_mk('Undertow', 'Ride the spiral', pts, star2=30000, star3=55000))
    pts = [pt for pt in _row(120, 480, 19, BLUE, gap=44) if not 420 <= pt[0] <= 540]
    pts += _col(164, 260, 5, BLUE) + _col(796, 260, 5, BLUE) + _col(480, 300, 4, BLUE)
    pts += _row(120, 220, 5, BLUE) + _row(736, 220, 5, BLUE) + _row(436, 260, 3, BLUE)
    pts += [(164, 180, ORANGE), (796, 180, ORANGE), (480, 220, ORANGE), (480, 560, ORANGE)]
    pts += [(440, 505, BLUE), (520, 505, BLUE)]
    pts += [(340, 400, GREEN), (620, 400, GREEN)]
    L.append(_mk('Battlements', 'Storm the keep', pts, star2=37000, star3=65000, hint='bank shots off the gate bumpers to storm the towers', bumpers=[(250, 400), (710, 400)]))
    pts = _ring(300, 300, 70, 10, BLUE) + _ring(300, 300, 32, 5, BLUE)
    pts += _ring(640, 280, 84, 12, BLUE) + _ring(640, 280, 38, 6, BLUE)
    pts += _ring(470, 490, 76, 11, BLUE) + _ring(470, 490, 34, 5, BLUE)
    pts += [(300, 300, ORANGE), (640, 280, ORANGE), (470, 490, ORANGE), (480, 380, ORANGE)]
    pts += [(480, 170, GREEN)]
    L.append(_mk('Nebula', 'Where the clouds meet', pts, star2=35000, star3=60000, hint='the bright knots hide at the heart of each cloud'))
    pts = _arc(700, 220, 90, 10, BLUE, math.pi * 0.5, math.pi * 1.5)
    pts += _arc(730, 235, 70, 7, BLUE, math.pi * 0.5, math.pi * 1.5)
    for (cx, cy) in ((200, 180), (330, 320), (180, 470), (420, 520), (560, 380)):
        pts += [(cx - 32, cy, BLUE), (cx + 32, cy, BLUE), (cx, cy - 32, BLUE), (cx, cy + 32, BLUE)]
    pts += [(150 + i * 46, 640 - i * 34, BLUE) for i in range(14)]
    pts += [(200, 180, ORANGE), (330, 320, ORANGE), (180, 470, ORANGE), (420, 520, ORANGE), (560, 380, ORANGE), (700, 220, ORANGE)]
    pts += [(200, 400, GREEN), (760, 400, GREEN)]
    L.append(_mk('Last Light', 'Clear the night sky', pts, balls=12, star2=40000, star3=65000, hint='the bright stars are the ones that matter'))
    pts = []
    for b in range(3):
        y_base = 240 + b * 140
        for i in range(13):
            pts.append((130 + i * 60, y_base + 42 * math.sin(i * 0.9 + b * 1.7), BLUE))
    pts += [(310, 258, ORANGE), (670, 365, ORANGE), (490, 411, ORANGE), (730, 513, ORANGE)]
    pts += [(480, 600, GREEN)]
    L.append(_mk('Drift', 'Sands on the wind', pts, star2=22000, star3=42000, hint='ride a crest downhill and let the slopes gather the ball'))
    pts = _ring(480, 380, 250, 16, BLUE) + _ring(480, 380, 120, 8, BLUE, 0.39)
    pts += _ring(480, 380, 185, 6, ORANGE, 0.15)
    pts += [(480, 380, GREEN), (480, 130, ORANGE), (480, 630, ORANGE)]
    L.append(_mk('Corona', 'Walk into the sun', pts, balls=13, star2=28000, star3=50000))
    pts = _ring(480, 380, 90, 8, BLUE) + _ring(480, 380, 185, 14, BLUE, 0.22)
    pts += [(480, 380, ORANGE), (480, 290, ORANGE), (480, 470, ORANGE), (390, 380, ORANGE), (570, 380, ORANGE)]
    pts += [(300, 180, GREEN), (660, 180, GREEN)]
    L.append(_mk('Umbra', 'Cross the shadow', pts, balls=12, star2=30000, star3=55000))
    pts = []
    for i in range(5):
        pts += _row(180 + i * 62, 150 + i * 84, 6, BLUE, gap=64)
    pts += [(250, 470, BLUE), (710, 470, BLUE)]
    pts += [(250, 540, ORANGE), (480, 590, ORANGE), (710, 540, ORANGE), (365, 470, ORANGE), (595, 470, ORANGE)]
    pts += [(480, 320, GREEN)]
    L.append(_mk('Cascade', 'Ride the fall', pts, balls=12, star2=30000, star3=55000))
    pts = []
    for r in range(7):
        span = 3 - abs(3 - r)
        for c in range(span * 2 + 1):
            pts.append((480 + (c - span) * 62 + (31 if r % 2 else 0), 140 + r * 76, BLUE))
    pts += [(480, 140, ORANGE), (480, 596, ORANGE), (294, 368, ORANGE), (697, 368, ORANGE), (480, 368, ORANGE)]
    pts += [(170, 560, GREEN), (790, 560, GREEN)]
    L.append(_mk('Zenith', 'The highest light', pts, balls=13, star2=30000, star3=50000, hint='bank shots off the golden bumpers to reach the far pegs', bumpers=[(190, 300), (770, 300)]))
    (ember, loom, tide, switch, orrery, frost, helix, gauntlet, monolith, eventide) = _new_boards()
    (aurora, comet, daybreak) = _finale_boards()
    (belt, wingspan, twins) = _afterglow_boards()
    return [L[0], ember, L[1], loom, L[2], L[3], tide, L[4], L[5], switch, L[6], orrery, L[7], frost, L[8], helix, L[9], L[10], gauntlet, L[11], monolith, L[12], eventide, L[13], L[14], aurora, comet, daybreak, twins, belt, wingspan]

def build_r6_levels() -> list[Layout]:
    levels = build_classic_levels()
    for idx in (0, 3, 12):
        old = levels[idx]
        goals = [p for p in old.pegs if p.kind in (ORANGE, GREEN)]
        pts = []
        blocks = []
        rails = []
        if idx == 0:
            pts = _arc(480, 430, 190, 22, BLUE, math.pi, 2 * math.pi)
            pts += _arc(480, 430, 145, 17, BLUE, math.pi, 2 * math.pi)
            pts += _arc(480, 430, 95, 12, BLUE, math.pi, 2 * math.pi)
            pts += _arc(480, 430, 240, 26, BLUE, math.pi * 1.08, math.pi * 1.92)
            blocks = [Block(x, 560, 28, 12) for x in (320, 356, 392, 568, 604, 640)]
            hint = 'choose a sunrise lane - blue blocks bounce and clear like pegs'
        elif idx == 3:
            for col in range(7):
                pts += _col(210 + col * 90, 170 + col % 2 * 35, 9, BLUE, gap=33)
            blocks = [Block(x, 535, 26, 12) for x in (225, 261, 387, 423, 549, 585, 711, 747)]
            rails = [Rail(140, 390, 100, 12, math.radians(-65)), Rail(820, 390, 100, 12, math.radians(65))]
            hint = 'weave down the narrow chains or bank off the silver side rails'
        else:
            pts += _col(160, 170, 11, BLUE, gap=30)
            pts += _col(800, 170, 11, BLUE, gap=30)
            pts += _col(480, 270, 8, BLUE, gap=30)
            pts += _row(160, 220, 8, BLUE, gap=30)
            pts += _row(590, 220, 8, BLUE, gap=30)
            pts += _row(140, 490, 10, BLUE, gap=30)
            pts += _row(550, 490, 10, BLUE, gap=30)
            blocks = [Block(x, 565, 26, 12) for x in (260, 296, 332, 628, 664, 700)]
            rails = [Rail(300, 305, 96, 12, math.radians(24)), Rail(660, 305, 96, 12, math.radians(-24))]
            hint = 'bank from the silver ledges - the courtyard and side lanes stay open'
        pegs = list(goals)
        for (x, y, kind) in pts:
            if idx == 0 and y < 380:
                lane_x = [480 + (p.x - 480) * (y - 56) / (p.y - 56) for p in goals if p.kind == ORANGE and y < p.y]
                if any((abs(x - a) < 19 for a in lane_x)):
                    continue
            if all((math.hypot(x - p.x, y - p.y) >= 21 for p in pegs)):
                pegs.append(Peg(x, y, kind))
        pegs += blocks
        for peg in pegs:
            peg.r = 7.0
        levels[idx] = Layout(old.name, old.subtitle, pegs, old.balls, old.star2, old.star3, hint, old.bumpers, rails)
    return levels

def build_levels() -> list[Layout]:
    from .life_levels import life_boards
    levels = build_r6_levels() + life_boards()
    (levels[8].pegs[1].x, levels[8].pegs[1].y) = (680, 190)
    (levels[12].pegs[0].x, levels[12].pegs[1].x) = (300, 660)
    (levels[16].pegs[0].x, levels[16].pegs[0].y) = (280, 200)
    levels[16].pegs[15].y = 110
    levels[16].pegs[21].y = 100
    from .working_days import reprise_levels
    return reprise_levels(levels)
