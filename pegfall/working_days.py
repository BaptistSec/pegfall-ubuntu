from dataclasses import dataclass

@dataclass(frozen=True)
class WorkingDay:
    opening: str = ''
    younger: str = ''
    older: str = ''
DAYS = tuple((('', '', '') for _ in range(60)))
ENCOUNTERS = {}

def day(level):
    return WorkingDay()

def exchange(level, progress=None):
    return ()
REPRISES = {21: (0, ((360, 340), (600, 340), (480, 520))), 30: (3, ((300, 280), (660, 445), (480, 540))), 37: (8, ((340, 300), (620, 440), (480, 540))), 41: (0, ((310, 410), (650, 410), (480, 285))), 50: (3, ((210, 235), (750, 335), (480, 470))), 57: (8, ((300, 400), (660, 400), (480, 250)))}

def reprise_levels(levels):
    import copy, math
    originals = {idx: copy.deepcopy(levels[idx]) for idx in {v[0] for v in REPRISES.values()}}
    for (idx, (source, locations)) in REPRISES.items():
        lv = copy.deepcopy(originals[source])
        for p in lv.pegs:
            if p.kind == 'orange':
                p.kind = 'blue'
        candidates = [p for p in lv.pegs if p.kind == 'blue' and getattr(p, 'shape', 'circle') == 'circle']
        selected = []
        for (x, y) in locations:
            peg = min((p for p in candidates if p not in selected), key=lambda p: math.hypot(p.x - x, p.y - y))
            peg.kind = 'orange'
            selected.append(peg)
        lv.balls = max(10, lv.balls)
        lv.name = 'Return: ' + lv.name
        lv.hint = "a familiar frame - look again at today's orange goals"
        lv.reprise_of = source
        levels[idx] = lv
    return levels
