from __future__ import annotations
import math
import os
import random
import sys
import pygame
from . import physics, bucket, art_style, farm_story, life_story, life_art, farm_world, village_world, city_world
from .game import SCREEN_W, SCREEN_H, LAUNCH_X, LAUNCH_Y, BUCKET_W, BUCKET_H, BUCKET_Y, DRAIN_Y, FEVER_WELLS, Game
from .levels import BLUE, ORANGE, GREEN
PEG_R = physics.PEG_R
INK = (255, 246, 220)
DIM = (150, 158, 190)
PEG_COLORS = {kind: (color, art_style.INK) for (kind, color) in art_style.COLORS.items()}
LIT_SCALE = 1.35
LEVEL_SKIES = [((12, 14, 40), (52, 30, 84)), ((8, 22, 46), (20, 66, 96)), ((24, 10, 42), (84, 26, 90)), ((6, 30, 34), (16, 80, 74)), ((24, 10, 6), (138, 60, 14)), ((10, 12, 34), (30, 40, 96)), ((16, 8, 36), (58, 20, 96)), ((20, 10, 16), (90, 34, 40)), ((8, 16, 44), (24, 54, 120)), ((4, 6, 18), (40, 16, 64)), ((6, 26, 22), (20, 90, 70)), ((28, 12, 4), (158, 88, 20))]

def _lerp(a, b, t):
    return tuple((int(a[i] + (b[i] - a[i]) * t) for i in range(3)))

def make_background(top, bottom, seed=7):
    return art_style.background()

def make_peg_sprite(base, rim, lit=False, purple_ring=False):
    kind = min(PEG_COLORS, key=lambda k: sum(((base[i] - PEG_COLORS[k][0][i]) ** 2 for i in range(3))))
    return art_style.peg(kind, PEG_R, lit)

class Particles:

    def __init__(self):
        self.items = []

    def burst(self, x, y, color, n=14, speed=170):
        for i in range(n):
            a = random.uniform(0, 2 * math.pi)
            v = random.uniform(0.3, 1.0) * speed
            self.items.append([x, y, math.cos(a) * v, math.sin(a) * v, random.uniform(0.35, 0.7), color, random.uniform(2, 4)])

    def step(self, dt):
        alive = []
        for (x, y, vx, vy, life, color, size) in self.items:
            life -= dt
            if life > 0:
                vy += 300 * dt
                alive.append([x + vx * dt, y + vy * dt, vx, vy, life, color, size])
        self.items = alive

    def draw(self, surf):
        for (x, y, vx, vy, life, color, size) in self.items:
            a = max(0, min(255, int(255 * life * 2)))
            r = max(1, int(size * life * 2))
            pygame.draw.circle(surf, color, (int(x), int(y)), r)
FEVER_ZOOM_MAX = 1.9
FEVER_ZOOM_RAMP = 0.6
FEVER_FIT_MARGIN = 60

def fever_zoom(t: float) -> float:
    u = max(0.0, min(1.0, t / FEVER_ZOOM_RAMP))
    u = u * u * (3 - 2 * u)
    return 1.0 + (FEVER_ZOOM_MAX - 1.0) * u

def fever_camera(ball_xy, zoom: float) -> tuple[int, int, int, int]:
    (vw, vh) = (SCREEN_W / zoom, SCREEN_H / zoom)
    cx = min(max(ball_xy[0], vw / 2), SCREEN_W - vw / 2)
    cy = min(max(ball_xy[1], vh / 2), SCREEN_H - vh / 2)
    return (int(cx - vw / 2), int(cy - vh / 2), int(vw), int(vh))

class Popups:
    FAN_STEP = 20
    FAN_CEILING = 72
    FAN_FLOOR = SCREEN_H - 30
    VISIBLE_LIFE = 0.35

    def __init__(self, font, big_font=None):
        self.items = []
        self.font = font
        self.big_font = big_font or font

    def _rect(self, x, y, text, big):
        f = self.big_font if big else self.font
        img = f.render(text, True, INK)
        half = img.get_width() // 2 + 6
        x = min(max(x, half), SCREEN_W - half)
        return img.get_rect(center=(int(x), int(y)))

    def _collides(self, rect):
        return any((life > self.VISIBLE_LIFE and rect.colliderect(self._rect(ox, oy, t, b)) for (ox, oy, t, _c, life, b) in self.items))

    def add(self, x, y, text, color=INK, big=False):
        fresh = self._rect(x, y, text, big)
        self.items = [it for it in self.items if not (it[4] <= 0.5 and fresh.colliderect(self._rect(it[0], it[1], it[2], it[5])))]
        r = fresh
        while self._collides(r) and r.top - self.FAN_STEP >= self.FAN_CEILING:
            r = r.move(0, -self.FAN_STEP)
        if self._collides(r):
            r = fresh
            while self._collides(r) and r.bottom + self.FAN_STEP <= self.FAN_FLOOR:
                r = r.move(0, self.FAN_STEP)
        self.items.append([x, r.centery, text, color, 1.0, big])

    def step(self, dt):
        alive = []
        for (x, y, text, color, life, big) in self.items:
            life -= dt * 0.8
            if life > 0:
                alive.append([x, y - 34 * dt, text, color, life, big])
        self.items = alive

    def draw(self, surf, font, big_font=None):
        for (x, y, text, color, life, big) in self.items:
            f = big_font if big and big_font is not None else font
            img = f.render(text, True, color)
            half = img.get_width() // 2 + 6
            x = min(max(x, half), surf.get_width() - half)
            alpha = max(0, min(255, int(255 * life)))
            img.set_alpha(alpha)
            shadow = f.render(text, True, (12, 12, 30))
            shadow.set_alpha(alpha)
            plaque = img.get_rect(center=(int(x), int(y))).inflate(8, 4)
            pygame.draw.rect(surf, art_style.INK, plaque, border_radius=3)
            surf.blit(shadow, shadow.get_rect(center=(int(x) + 1, int(y) + 2)))
            surf.blit(img, img.get_rect(center=(int(x), int(y))))

def _font_path() -> str:
    base = getattr(sys, '_MEIPASS', None)
    if base:
        return os.path.join(base, 'pegfall', 'assets', 'fonts', 'LiberationSans-Bold.ttf')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts', 'LiberationSans-Bold.ttf')

def _make_icon() -> 'pygame.Surface':
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.circle(s, (16, 10, 40), (32, 32), 32)
    pygame.draw.circle(s, (52, 34, 96), (32, 32), 32, 2)
    pygame.draw.circle(s, (255, 170, 40), (30, 34), 15)
    pygame.draw.circle(s, (255, 216, 130), (30, 34), 8)
    pygame.draw.circle(s, (235, 240, 255), (45, 13), 5)
    return s

def launcher_pivot(angle):
    return (round(LAUNCH_X - 34 * math.sin(angle)), round(LAUNCH_Y - 34 * math.cos(angle)))

class SoftPopups(Popups):
    MAX_ALPHA = 150
    DURATION = 0.85

    def step(self, dt):
        self.items = [[x, y - 16 * dt, text, color, life - dt / self.DURATION, big] for (x, y, text, color, life, big) in self.items if life - dt / self.DURATION > 0]

    def draw(self, surf, font=None, big_font=None):
        for (x, y, text, color, life, big) in self.items:
            base = self.font.render(text, True, color)
            scale = 0.84 + 0.16 * max(0, min(1, life))
            img = pygame.transform.smoothscale(base, (max(1, round(base.get_width() * scale)), max(1, round(base.get_height() * scale))))
            alpha = round(self.MAX_ALPHA * max(0, min(1, life / 0.75)))
            img.set_alpha(alpha)
            half = img.get_width() // 2 + 4
            x = min(max(x, half), surf.get_width() - half)
            shadow = self.font.render(text, True, (10, 34, 43))
            shadow = pygame.transform.smoothscale(shadow, img.get_size())
            shadow.set_alpha(round(alpha * 0.8))
            surf.blit(shadow, shadow.get_rect(center=(round(x) + 1, round(y) + 1)))
            surf.blit(img, img.get_rect(center=(round(x), round(y))))

class Renderer:

    def __init__(self, headless=False, fullscreen=False):
        flags = 0 if headless else pygame.HWSURFACE | pygame.DOUBLEBUF
        self.headless = headless
        self.fullscreen = False
        self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
        pygame.display.set_caption('Pegfall')
        try:
            self._desktop_size = pygame.display.get_desktop_sizes()[0]
        except Exception:
            info = pygame.display.Info()
            self._desktop_size = (info.current_w, info.current_h)
        if not headless:
            pygame.display.set_icon(_make_icon())
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
        self.side_active = False
        self._meter_game = None
        self._score_display = 0.0
        self._meter_message = ''
        self._meter_message_t = 0.0
        if fullscreen:
            self.set_fullscreen(True)
        fp = _font_path()
        self.font_s = pygame.font.Font(fp, 13)
        self.font_m = pygame.font.Font(fp, 19)
        self.font_l = pygame.font.Font(fp, 34)
        self.font_xl = pygame.font.Font(fp, 59)
        self._frame = pygame.Surface((SCREEN_W, SCREEN_H))
        self._fever_t = 0.0
        self._fever_cam_pos = None
        self._fever_zoom = 1.0
        self.backgrounds = [make_background(t, b, seed=11 + i) for (i, (t, b)) in enumerate(LEVEL_SKIES)]
        self.sprites = {}
        for (kind, (base, rim)) in PEG_COLORS.items():
            self.sprites[kind, False] = make_peg_sprite(base, rim, False)
            self.sprites[kind, True] = make_peg_sprite(_lerp(base, (255, 255, 255), 0.35), rim, True)
        self.particles = Particles()
        self.popups = self.new_popups()
        self.confetti = []
    CONFETTI_COLORS = ((255, 220, 120), (250, 170, 80), (140, 240, 170), (150, 190, 255), (255, 150, 90), (240, 240, 250))

    def step_confetti(self, dt, active):
        active = False
        if not active:
            self.confetti = []
            return
        room = 160 - len(self.confetti)
        if room > 0:
            for _ in range(min(3, room)):
                self.confetti.append([random.uniform(30, 930), -8.0, random.uniform(90, 170), random.uniform(0, 2 * math.pi), random.choice(self.CONFETTI_COLORS)])
        t = pygame.time.get_ticks() / 1000.0
        alive = []
        for (x, y, vy, phase, color) in self.confetti:
            y += vy * dt
            x += math.sin(t * 3 + phase) * 40 * dt
            if y < 730:
                alive.append([x, y, vy, phase, color])
        self.confetti = alive

    def _peg_sprite(self, game, peg):
        kind = 'purple' if game.is_purple(peg) else peg.kind
        return self.sprites[kind if kind in PEG_COLORS else BLUE, peg.lit]

    def new_popups(self):
        return SoftPopups(self.font_s, self.font_s)

    def _shape_sprite(self, game, peg):
        if getattr(peg, 'shape', 'circle') == 'box':
            kind = 'purple' if game.is_purple(peg) else peg.kind
            return self._block_sprite(peg.w, peg.h, peg.angle, kind, peg.lit)
        kind = 'purple' if game.is_purple(peg) else peg.kind
        return art_style.peg(kind, getattr(peg, 'r', PEG_R), peg.lit)

    @staticmethod
    def _block_sprite(w, h, angle, kind, lit=False):
        return art_style.block(w, h, angle, kind, lit)

    def draw_board(self, game: Game, level_index: int, aim_points=None, dt: float=1 / 60, lost_pulse: float | None=None):
        self._crew_dt = dt
        if not hasattr(self, '_scene_elapsed'):
            self._scene_elapsed = 0.0
            self._loading_t = 0.0
        if not hasattr(self, '_crew_last_x'):
            self._crew_poses = {}
            self._crew_last_x = launcher_pivot(game.aim)[0]
            self._crew_stride = self._crew_motion = 0.0
        if game is not getattr(self, '_last_game', None):
            self.particles = Particles()
            self.popups = self.new_popups()
            self.confetti = []
            self._fever_cam_pos = None
            self._last_game = game
            self._score_display = 0.0
            self._board_ticks = pygame.time.get_ticks()
            self._shake_offset = (0, 0)
            self._crew_last_x = launcher_pivot(game.aim)[0]
            self._crew_stride = 0.0
            self._crew_motion = 0.0
            self._scene_elapsed = 0.0
            self._loading_t = 0.0
            self._crew_was_flight = False
            self._crew_reset_age = 99.0
            self._crew_shot_score = game.score
            self._crew_nod_t = 0.0
            self._crew_reaction_t = 0.0
            self._crew_shot_age = 99.0
            self._crew_stop_age = 99.0
            self._crew_was_moving = False
        if not hasattr(self, '_crew_was_flight'):
            self._crew_was_flight = False
            self._crew_reset_age = 99.0
            self._crew_shot_score = game.score
            self._crew_nod_t = 0.0
        if not hasattr(self, '_crew_stop_age'):
            self._crew_shot_age = 99.0
            self._crew_stop_age = 99.0
            self._crew_was_moving = False
        if dt > 0:
            self._scene_elapsed += dt
            flight = bool(game.balls_in_flight)
            if flight and (not self._crew_was_flight):
                self._crew_shot_score = game.score
                self._crew_shot_age = 0.0
            self._crew_shot_age += dt
            self._crew_stop_age += dt
            if self._crew_was_flight and (not flight) and (game.state == 'aim'):
                self._crew_reset_age = 0.0
                earned = game.score - self._crew_shot_score
                threshold = 500 if level_index < 20 else 2500
                if level_index < 30 and earned >= threshold:
                    self._crew_nod_t = 0.75
            self._crew_was_flight = flight
            self._crew_reset_age += dt
            self._crew_nod_t = max(0, self._crew_nod_t - dt)
            if game.state == 'won' and level_index in (19, 39):
                self._loading_t += dt
            self._board_ticks = pygame.time.get_ticks()
            crew_x = launcher_pivot(game.aim)[0]
            travel = crew_x - self._crew_last_x
            self._crew_stride += travel * 0.22
            self._crew_motion = max(min(1, abs(travel) / max(1, dt * 40)), self._crew_motion * math.exp(-dt * 9))
            moving = self._crew_motion > 0.15
            if self._crew_was_moving and (not moving):
                self._crew_stop_age = 0.0
            self._crew_was_moving = moving
            self._crew_last_x = crew_x
            self._crew_reaction_t = max(0, getattr(self, '_crew_reaction_t', 0) - dt)
        s = self._frame
        s.blit(farm_world.background(level_index + 1) if level_index < 20 else village_world.background(level_index + 1) if level_index < 40 else city_world.background(level_index + 1), (0, 0))
        if level_index < 20:
            farm_world.draw_weather(s, level_index + 1, self._scene_elapsed)
            farm_world.draw_life(s, level_index + 1, self._scene_elapsed)
        if 20 <= level_index < 40:
            village_world.draw_life(s, level_index + 1, self._scene_elapsed)
            if level_index == 20 and self._scene_elapsed < 3.5 and (not game.shots_fired):
                village_world.draw_arrival(s, self._scene_elapsed)
        if level_index >= 40:
            city_world.draw_life(s, level_index + 1, self._scene_elapsed)
            city_world.draw_final_days(s, level_index + 1, self._scene_elapsed)
            if level_index == 40 and self._scene_elapsed < 3.5 and (not game.shots_fired):
                city_world.draw_arrival(s, self._scene_elapsed)
            if level_index == 45 and self._scene_elapsed < 3.5 and (not game.shots_fired):
                city_world.draw_morning(s, self._scene_elapsed)
        if level_index == 19 and game.state == 'won':
            farm_world.draw_loading(s, self._loading_t)
        if level_index == 39 and game.state == 'won':
            farm_world.draw_loading(s, self._loading_t)
        from . import campaign_life
        campaign_life.draw(s, level_index + 1, self._scene_elapsed)
        pygame.draw.line(s, art_style.WOOD_DARK, (24, 70), (24, SCREEN_H), 2)
        pygame.draw.line(s, art_style.WOOD_DARK, (936, 70), (936, SCREEN_H), 2)
        if aim_points:
            for (i, (x, y)) in enumerate(aim_points):
                r = 3 if i % 2 == 0 else 2
                pygame.draw.circle(s, art_style.TEAL, (int(x), int(y)), r)
        ang = game.aim
        rec = getattr(game, 'recoil', 0.0) * 7
        sprite = art_style.launcher(round(ang, 3), round(rec, 1))
        s.blit(sprite, sprite.get_rect(center=launcher_pivot(ang)))
        for peg in game.pegs:
            if not peg.alive:
                continue
            spr = self._shape_sprite(game, peg)
            s.blit(spr, spr.get_rect(center=(int(peg.x), int(peg.y))))
            if peg.flash > 0:
                r = int(getattr(peg, 'r', PEG_R) + 3)
                ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ring, art_style.INK + (int(200 * peg.flash),), (r + 2, r + 2), r, 2)
                s.blit(ring, ring.get_rect(center=(int(peg.x), int(peg.y))))
            if lost_pulse is not None and peg.kind == ORANGE:
                ph = lost_pulse * 3 % 1.0
                r = int(getattr(peg, 'r', PEG_R) + 4 + ph * 8)
                alpha = int(170 * (1 - ph))
                if alpha > 8:
                    ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.circle(ring, (255, 168, 60, alpha), (r + 2, r + 2), r, 2)
                    s.blit(ring, ring.get_rect(center=(int(peg.x), int(peg.y))))
        if game.oranges_left() == 1 and game.state in ('aim', 'flight'):
            last = next((p for p in game.pegs if p.alive and (not p.lit) and (p.kind == ORANGE)), None)
            if last is not None:
                r = round(getattr(last, 'r', PEG_R) + 7)
                pygame.draw.circle(s, (255, 225, 130), (round(last.x), round(last.y)), r, 1)
        pulse = self._board_ticks % 2400 / 2400.0
        for bp in getattr(game, 'bumpers', []):
            (bx, by) = (int(bp.x), int(bp.y))
            br = int(bp.r)
            sprite = art_style.bumper(br)
            s.blit(sprite, sprite.get_rect(center=(bx, by)))
            if bp.flash > 0:
                r = int(br + (1 - bp.flash) * 26)
                ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ring, (255, 240, 180, int(220 * bp.flash)), (r + 2, r + 2), r, 2)
                s.blit(ring, ring.get_rect(center=(bx, by)))
        for rail in game.rails:
            rail_surf = art_style.rail(rail.w, rail.h, rail.angle)
            s.blit(rail_surf, rail_surf.get_rect(center=(round(rail.x), round(rail.y))))
        for d in game.dying:
            (dx, dy, dkind, t) = (d[0], d[1], d[2], d[3])
            kind = dkind if dkind in PEG_COLORS else BLUE
            visual = d[6] if len(d) > 6 else {}
            if visual.get('shape') == 'box':
                spr = self._block_sprite(visual['w'], visual['h'], visual['angle'], kind, True)
            else:
                spr = self.sprites[kind, True]
                ratio = visual.get('r', PEG_R) / PEG_R
                if ratio != 1:
                    spr = pygame.transform.smoothscale(spr, tuple((max(1, round(v * ratio)) for v in spr.get_size())))
            if len(d) > 4 and d[4] > 0:
                ghost = spr.copy()
                ghost.set_alpha(170)
                s.blit(ghost, ghost.get_rect(center=(int(dx), int(dy))))
                continue
            scale = 0.6 + 0.8 * max(0.1, t)
            pop = pygame.transform.smoothscale(spr, tuple((max(1, round(v * scale)) for v in spr.get_size())))
            pop.set_alpha(int(220 * t))
            s.blit(pop, pop.get_rect(center=(int(dx), int(dy))))
        for ball in game.balls_in_flight:
            for (i, (tx, ty)) in enumerate(ball.trail):
                a = int(10 + 150 * i / max(1, len(ball.trail)))
                col = (255, 150, 90) if ball.burst else (189, 161, 110) if ball.comet_t > 0 else (127, 144, 121)
                pygame.draw.circle(s, col, (int(tx), int(ty)), max(1, int(ball.r * i / max(1, len(ball.trail)) * 0.8)))
            if ball.burst:
                body = (255, 110, 80)
            elif ball.comet_t > 0:
                body = (255, 190, 90)
            else:
                body = (245, 248, 255)
            if ball.burst:
                pygame.draw.circle(s, (255, 150, 90), (int(ball.x), int(ball.y)), int(ball.r) + 4, 2)
            mode = 'burst' if ball.burst else 'comet' if ball.comet_t > 0 else 'normal'
            sprite = art_style.ball(ball.r, mode)
            s.blit(sprite, sprite.get_rect(center=(int(ball.x), int(ball.y))))
        if game.state in ('fever', 'won'):
            for surf in bucket.well_surfaces():
                col = (235, 190, 100)
                if surf.shape == 'circle':
                    pygame.draw.circle(s, col, (round(surf.x), round(surf.y)), round(surf.r))
                else:
                    rect = pygame.Rect(0, 0, round(surf.w), round(surf.h))
                    rect.center = (round(surf.x), round(surf.y))
                    pygame.draw.rect(s, col, rect, border_radius=2)
            for (i, points) in enumerate(FEVER_WELLS):
                (lo, hi) = bucket.well_bounds(i)
                if game.fever_well == i:
                    glow = pygame.Surface((round(hi - lo - 6), round(bucket.FLOOR_Y - bucket.MOUTH_Y - 4)), pygame.SRCALPHA)
                    glow.fill((255, 220, 100, 65))
                    s.blit(glow, (round(lo + 3), round(bucket.MOUTH_Y + 2)))
                col = (255, 235, 150) if i == 2 else (230, 195, 120)
                img = self.font_s.render(f'{points // 1000}k', True, col)
                pos = (round((lo + hi) / 2), round(bucket.MOUTH_Y + 23))
                rect = img.get_rect(center=pos).inflate(18, 8)
                pygame.draw.rect(s, art_style.INK, rect, border_radius=4)
                s.blit(img, img.get_rect(center=pos))
        else:
            art_style.draw_bucket(s, game.bucket_x, game.free_ball_flash)
        if game.state == 'fever':
            pulse = 0.5 + 0.5 * math.sin(self._board_ticks / 180.0)
            glow = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            glow.fill((255, 190, 80, int(14 + 12 * pulse)))
            s.blit(glow, (0, 0))
            for (x, y, vy, phase, color) in self.confetti:
                pygame.draw.rect(s, color, (int(x), int(y), 3, 5))
        self._meter_game = game
        self._meter_message_t = max(0, self._meter_message_t - dt)
        delta = game.score - self._score_display
        if dt > 0:
            self._score_display += delta * min(1.0, dt * 9)
        if abs(game.score - self._score_display) < 1:
            self._score_display = float(game.score)
        if game.state == 'fever':
            self._fever_t += dt
            if game.balls_in_flight:
                xs = [b.x for b in game.balls_in_flight]
                ys = [b.y for b in game.balls_in_flight]
                self._fever_cam_pos = (sum(xs) / len(xs), sum(ys) / len(ys))
        else:
            self._fever_t = max(0.0, self._fever_t - dt * (FEVER_ZOOM_RAMP / 0.35))
        shake = 0.0
        if dt > 0:
            self._shake_offset = (int(random.uniform(-1, 1) * 12 * shake), int(random.uniform(-1, 1) * 12 * shake)) if shake > 0 else (0, 0)
        (ox, oy) = self._shake_offset
        zoom = fever_zoom(self._fever_t)
        if game.state == 'fever' and len(game.balls_in_flight) > 1:
            xs = [b.x for b in game.balls_in_flight]
            ys = [b.y for b in game.balls_in_flight]
            spread_x = max(xs) - min(xs)
            spread_y = max(ys) - min(ys)
            if spread_x > 1:
                zoom = min(zoom, (SCREEN_W - 2 * FEVER_FIT_MARGIN) / spread_x)
            if spread_y > 1:
                zoom = min(zoom, (SCREEN_H - 2 * FEVER_FIT_MARGIN) / spread_y)
        if self._fever_cam_pos is not None:
            landing = max(0.0, min(1.0, (self._fever_cam_pos[1] - 480) / 100))
            zoom = min(zoom, 1.0 + (FEVER_ZOOM_MAX - 1.0) * (1.0 - landing))
        zoom = 1.0
        self._fever_zoom = zoom
        if zoom > 1.001 and self._fever_cam_pos is not None:
            view = fever_camera(self._fever_cam_pos, zoom)
            zoomed = pygame.transform.smoothscale(self._frame.subsurface(view).copy(), (SCREEN_W, SCREEN_H))
            self.screen.fill((4, 6, 16))
            self.screen.blit(zoomed, (ox, oy))
        else:
            self.screen.fill((4, 6, 16))
            self.screen.blit(self._frame, (ox, oy))
        self.popups.step(dt)
        self.popups.draw(self.screen)
        self._hud(game, self.screen)

    def draw_life_reward(self, game: Game, level_index: int, progress=None):
        if game.state == 'won':
            self.caption(f'{game.score:,} points. The board is complete.', (480, 617))
            self.caption('Enter - next day    R - replay    M - menu', (480, 665))

    def caption(self, text, center):
        img = self.font_s.render(text, True, art_style.LIGHT)
        rect = img.get_rect(center=center)
        pygame.draw.rect(self.screen, art_style.INK, rect.inflate(20, 10), border_radius=5)
        self.screen.blit(img, rect)

    def _hud(self, game: Game, target=None):
        s = target if target is not None else self._frame
        (hub_x, hub_y) = launcher_pivot(game.aim)
        (left, right) = (370, 590)
        pygame.draw.rect(s, art_style.INK, (0, 0, left + 1, 65))
        pygame.draw.rect(s, art_style.INK, (right, 0, SCREEN_W - right, 65))
        sky = (farm_world.background(game.level_index + 1) if game.level_index < 20 else village_world.background(game.level_index + 1) if game.level_index < 40 else city_world.background(game.level_index + 1)).get_at((480, 85))[:3]
        pygame.draw.rect(s, sky, (left, 0, right - left + 1, 84))
        pygame.draw.line(s, art_style.WOOD, (left, 0), (left, 64), 2)
        pygame.draw.line(s, art_style.WOOD, (right, 0), (right, 64), 2)
        pygame.draw.line(s, art_style.WOOD, (0, 64), (left, 64), 2)
        pygame.draw.line(s, art_style.WOOD, (right, 64), (SCREEN_W, 64), 2)
        if game.level_index == 3:
            pygame.draw.line(s, (130, 112, 78), (397, 7), (564, 7), 4)
            pygame.draw.line(s, (197, 175, 121), (397, 5), (564, 5), 1)
            for post in (396, 565):
                pygame.draw.line(s, (148, 128, 87), (post, 7), (post, 77), 2)
        if not (game.level_index in (19, 39) and game.state == 'won') and (not (game.level_index in (20, 40) and self._scene_elapsed < 3.5 and (not game.shots_fired))):
            art_style.draw_cannon_mount(s, hub_x, hub_y, game.aim, self._crew_stride, self._crew_motion)
            idle = getattr(game, 'shots_fired', 0) > 0 and (not game.balls_in_flight) and (game.state == 'aim')
            if not (game.level_index == 45 and self._scene_elapsed < 3.5 and (not game.shots_fired)):
                art_style.draw_launcher_crew(s, hub_x, hub_y, game.aim, self._scene_elapsed, self._crew_stride, self._crew_motion, game.level_index + 1, len(game.balls_in_flight) > 0, getattr(self, '_crew_reaction_t', 0) > 0, idle, getattr(self, '_look54_t', 0) > 0, getattr(self, '_crew_reset_age', 99.0), getattr(self, '_crew_nod_t', 0.0), getattr(self, '_crew_shot_age', 99.0), min(getattr(self, '_crew_stop_age', 99.0), getattr(self, '_crew_reset_age', 99.0)), getattr(self, '_crew_poses', None), getattr(self, '_crew_dt', 1 / 60))
            sprite = art_style.launcher(round(game.aim, 3), round(getattr(game, 'recoil', 0.0) * 4, 1))
            s.blit(sprite, sprite.get_rect(center=launcher_pivot(game.aim)))
        self._draw_header_feedback(s, game)
        for ball in game.balls_in_flight:
            if ball.y - ball.r < 82:
                mode = 'burst' if ball.burst else 'comet' if ball.comet_t > 0 else 'normal'
                sprite = art_style.ball(ball.r, mode)
                s.blit(sprite, sprite.get_rect(center=(int(ball.x), int(ball.y))))

    def _draw_header_feedback(self, s, g):
        carton = pygame.Rect(24, 8, 222, 42)
        pygame.draw.rect(s, art_style.WOOD_DARK, carton, border_radius=4)
        pygame.draw.rect(s, art_style.WOOD, carton, 2, border_radius=4)
        count = max(0, g.balls_left)
        capacity = max(count, getattr(g.level, 'balls', count))
        cols = min(16, max(1, (capacity + 1) // 2))
        for i in range(min(capacity, cols * 2)):
            (x, y) = (36 + i % cols * 12, 20 + i // cols * 16)
            pygame.draw.circle(s, (67, 79, 68), (x, y), 5, 1)
            if i < count:
                pygame.draw.circle(s, art_style.LIGHT, (x, y), 4)
        score = self.font_m.render(f'{g.score:,}', True, art_style.LIGHT)
        s.blit(score, score.get_rect(midright=(925, 30)))

    @staticmethod
    def _star(s, cx, cy, rad, col):
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = rad if i % 2 == 0 else rad * 0.42
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        pygame.draw.polygon(s, col, pts)
        pygame.draw.polygon(s, (120, 80, 20), pts, 2)

    def _text(self, s, font, msg, color, center):
        dark = font.render(msg, True, (4, 6, 16))
        (cx, cy) = center
        for (dx, dy) in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            s.blit(dark, dark.get_rect(center=(cx + dx, cy + dy)))
        img = font.render(msg, True, color)
        s.blit(img, img.get_rect(center=(cx, cy)))

    def overlay(self, title, lines, title_color=INK, stars=0, peek=()):
        s = self.screen
        dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dim.fill((4, 6, 16, 190))
        s.blit(dim, (0, 0))
        for (px_, py_) in peek:
            spr = self.sprites['orange', False]
            s.blit(spr, spr.get_rect(center=(int(px_), int(py_))))
            r = PEG_R + 6
            ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring, (255, 168, 60, 200), (r + 2, r + 2), r, 2)
            s.blit(ring, ring.get_rect(center=(int(px_), int(py_))))
        self._text(s, self.font_xl, title, title_color, (SCREEN_W // 2, 210))
        y = 300
        if stars:
            gap = 74
            x0 = SCREEN_W // 2 - gap * (stars - 1) // 2
            for i in range(stars):
                self._star(s, x0 + i * gap, y, 26, (255, 220, 120))
            y += 70
        else:
            y += 30
        for line in lines:
            self._text(s, self.font_m, line, DIM, (SCREEN_W // 2, y))
            y += 40

    def set_fullscreen(self, flag):
        flag = bool(flag)
        if flag == self.fullscreen or self.headless:
            return
        if flag:
            self._pin_window_position((0, 0))
            try:
                disp = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
            except Exception:
                return
            self.display = disp
            self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
            self.fullscreen = True
            self._pin_window_position((0, 0))
        else:
            try:
                disp = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.HWSURFACE | pygame.DOUBLEBUF)
            except Exception:
                return
            self.display = disp
            self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
            self.fullscreen = False
            (dw, dh) = self._desktop_size
            self._pin_window_position((max(0, (dw - SCREEN_W) // 2), max(0, (dh - SCREEN_H) // 2)))
        pygame.display.set_caption('Pegfall')
    _sdl2_window_keepalive = []

    @staticmethod
    def _pin_window_position(pos):
        try:
            from pygame._sdl2 import video as _video
            win = _video.Window.from_display_module()
            Renderer._sdl2_window_keepalive.append(win)
            win.position = (int(pos[0]), int(pos[1]))
        except Exception:
            pass
        pygame.display.set_icon(_make_icon())

    def to_logical(self, pos):
        (dw, dh) = self.display.get_size()
        scale = min(dw / SCREEN_W, dh / SCREEN_H)
        (ox, oy) = ((dw - SCREEN_W * scale) / 2, (dh - SCREEN_H * scale) / 2)
        return ((pos[0] - ox) / scale, (pos[1] - oy) / scale)

    def composed_frame(self):
        return self.screen.copy()

    def present(self):
        canvas = self.screen
        (dw, dh) = self.display.get_size()
        scale = min(dw / SCREEN_W, dh / SCREEN_H)
        (w, h) = (int(SCREEN_W * scale), int(SCREEN_H * scale))
        self.display.fill((4, 6, 12))
        if (w, h) == canvas.get_size():
            self.display.blit(canvas, ((dw - w) // 2, (dh - h) // 2))
        else:
            signature = ((w, h), canvas.get_bitsize(), canvas.get_masks())
            if getattr(self, '_present_signature', None) != signature:
                self._present_buffer = pygame.Surface((w, h), 0, canvas)
                self._present_signature = signature
            pygame.transform.smoothscale(canvas, (w, h), self._present_buffer)
            self.display.blit(self._present_buffer, ((dw - w) // 2, (dh - h) // 2))
        pygame.display.flip()
