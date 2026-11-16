from __future__ import annotations
WIDTH = 104.0
MOUTH_Y = 658.0
FLOOR_Y = 705.0
WALL = 6.0
RIM_R = 5.0

class Surface:
    kind = 'bucket'
    alive = True
    lit = False
    rest = 0.66
    kick = 0.0
    flash = 0.0

    def __init__(self, x, y, vx, part, shape, w=0, h=0, r=0):
        (self.x, self.y, self.vx) = (x, y, vx)
        (self.part, self.shape) = (part, shape)
        (self.w, self.h, self.r) = (w, h, r)
        self.angle = 0.0

def surfaces(cx, vx=0.0):
    out = []
    for sign in (-1, 1):
        x = cx + sign * (WIDTH / 2 - WALL / 2)
        out.append(Surface(x, MOUTH_Y, vx, 'rim', 'circle', r=RIM_R))
        out.append(Surface(x, (MOUTH_Y + FLOOR_Y) / 2, vx, 'side', 'box', w=WALL, h=FLOOR_Y - MOUTH_Y))
    out.append(Surface(cx, FLOOR_Y, vx, 'base', 'box', w=WIDTH, h=WALL))
    return out
WELL_LEFT = 24.0
WELL_RIGHT = 936.0
WELL_COUNT = 5
WELL_WIDTH = (WELL_RIGHT - WELL_LEFT) / WELL_COUNT

def well_bounds(index):
    return (WELL_LEFT + index * WELL_WIDTH, WELL_LEFT + (index + 1) * WELL_WIDTH)

def well_surfaces():
    out = []
    for index in range(WELL_COUNT + 1):
        x = WELL_LEFT + index * WELL_WIDTH
        for (part, shape, y, w, h, r) in (('rim', 'circle', MOUTH_Y, 0, 0, RIM_R), ('side', 'box', (MOUTH_Y + FLOOR_Y) / 2, WALL, FLOOR_Y - MOUTH_Y, 0)):
            obj = Surface(x, y, 0, part, shape, w, h, r)
            obj.kind = 'well'
            obj.well = None
            out.append(obj)
    for index in range(WELL_COUNT):
        (lo, hi) = well_bounds(index)
        obj = Surface((lo + hi) / 2, FLOOR_Y, 0, 'base', 'box', hi - lo, WALL)
        obj.kind = 'well'
        obj.well = index
        out.append(obj)
    return out
