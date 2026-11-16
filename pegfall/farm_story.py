from .narrative import FARM
REWARDS = tuple(((day.title, day.surface, (28, 430, 904, 210)) for day in FARM))

def visual_stage(level_index, state):
    return min(20, max(0, int(level_index)) + (state == 'won'))
