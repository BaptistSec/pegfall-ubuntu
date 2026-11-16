import math
import pygame
from . import art_style as a, city_world, story_scenes
CREDITS = ('PEGFALL', 'A Tidycade Game', 'Published by Tidy Desk Software', 'Created by William Baptist', 'Contributions: Marko "glok029" Gläser', 'Contributions: Jean Bromley', 'Contributions: JamesRussian', 'Contributions: Kerrie Wainwright', 'Contributions: Hagen Lotz', 'Typeface: Liberation Sans', 'Font licensed under SIL Open Font License 1.1', 'Thank you for playing')
CREDITS_START = 18.0
LINE_SECONDS = 4.0
END_TIME = CREDITS_START + LINE_SECONDS * len(CREDITS) + 4.0

def credit_at(t):
    age = t - CREDITS_START
    if age < 0 or age >= LINE_SECONDS * len(CREDITS):
        return (None, 0)
    index = int(age // LINE_SECONDS)
    phase = age % LINE_SECONDS
    alpha = a.ease(phase) if phase < 1 else a.ease(4 - phase) if phase > 3 else 1
    return (CREDITS[index], round(alpha * 255))

def draw(s, t, font, show_story=False, small=None):
    story_scenes.draw(s, 'ending', min(t, 18.0), font, small or font, hint=show_story and t < CREDITS_START, hold=True)
    (line, alpha) = credit_at(t)
    if line and alpha:
        veil = pygame.Surface((960, 720), pygame.SRCALPHA)
        veil.fill((22, 37, 34, round(alpha * 0.25)))
        s.blit(veil, (0, 0))
        if line == 'PEGFALL':
            title = font.render('P E G F A L L', True, (246, 209, 130))
            text = pygame.transform.smoothscale(title, (title.get_width() * 2, title.get_height() * 2))
            dark = font.render('P E G F A L L', True, (28, 43, 39))
            shadow = pygame.transform.smoothscale(dark, text.get_size())
        else:
            text = font.render(line, True, (255, 241, 205))
            shadow = font.render(line, True, (28, 43, 39))
        text.set_alpha(alpha)
        shadow.set_alpha(alpha)
        s.blit(shadow, shadow.get_rect(center=(481, 362)))
        s.blit(text, text.get_rect(center=(480, 360)))
    if t >= END_TIME:
        hint = font.render('Enter - replay final level     M / Esc - menu', True, (255, 241, 205))
        s.blit(hint, hint.get_rect(center=(480, 682)))
