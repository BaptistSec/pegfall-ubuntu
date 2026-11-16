from .farm_story import REWARDS as FARM_REWARDS
from .narrative import VILLAGE, CITY
REWARDS = FARM_REWARDS + tuple(((day.title, day.surface, (28, 420, 904, 220)) for day in VILLAGE)) + tuple(((day.title, day.surface, (28, 380, 904, 260)) for day in CITY))
CHAPTERS = ((0, 20, 'A LITTLE GROUND', 'Farm wages, a rented cottage and a small plot.'), (20, 30, 'A PLACE IN THE VILLAGE', 'Regular repair work, a modest rented home.'), (30, 40, 'THE PRICE OF LEAVING', 'A tiny shop. Everything saved goes towards the city.'), (40, 50, 'AT THE BOTTOM AGAIN', 'A bare city room, yard wages and borrowed space.'), (50, 60, 'A SECURE FOOTHOLD', 'Independent work and a small city workshop.'))

def scene_state(level_index, state):
    idx = max(0, min(59, int(level_index)))
    chapter = next((i for (i, c) in enumerate(CHAPTERS) if c[0] <= idx < c[1]))
    (start, stop, *_) = CHAPTERS[chapter]
    return (chapter, idx - start + (state == 'won'))

def chapter_for(level_index):
    idx = max(0, min(59, int(level_index)))
    return next((c for c in CHAPTERS if c[0] <= idx < c[1]))
assert len(REWARDS) == 60
