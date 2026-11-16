from __future__ import annotations
import json
import math
import os
import random
import tempfile
from dataclasses import dataclass
from . import physics, bucket
from .levels import BLUE, ORANGE, GREEN, Layout, build_levels
(SCREEN_W, SCREEN_H) = (960, 720)
(LAUNCH_X, LAUNCH_Y) = (480.0, 56.0)
DRAIN_Y = 720.0
(BUCKET_W, BUCKET_H) = (bucket.WIDTH, bucket.FLOOR_Y - bucket.MOUTH_Y)
BUCKET_Y = (bucket.MOUTH_Y + bucket.FLOOR_Y) / 2
BUCKET_SPEED = 150.0
START_BALLS = 10
MAX_AIM = math.radians(75)
SCORE = {BLUE: 100, ORANGE: 250, GREEN: 250, 'purple': 500}
BUMPER_SCORE = 25
FEVER_WELLS = (10000, 25000, 50000, 25000, 10000)
POWERS = ('guide', 'comet', 'multiball', 'burst')
BURST_RADIUS = 95
LONG_SHOT_DIST = 550
LONG_SHOT_BONUS = 1000
OFF_WALL_DIST = 400
OFF_WALL_BONUS = 1000
COMET_TIME = 1.85
SHOT_TIME_CAP = 45.0
CASCADE_STAGGER = 0.05
CASCADE_STAGGER_CAP = 0.6
SHOT_REAL_TIME_CAP = 60.0
PROGRESS_STALL_REAL = 12.0

@dataclass(frozen=True)
class PowerPolicy:
    timing: str = 'next_shots'
    shots: int = 2
    effect_seconds: float = COMET_TIME
POWER_POLICIES = {power: PowerPolicy() for power in POWERS}

class Board:
    (left, right, top) = (24.0, 936.0, 70.0)

class Event:
    __slots__ = ('kind', 'data')

    def __init__(self, etype, **data):
        (self.kind, self.data) = (etype, data)

def multiplier_for(cleared: int, total: int) -> int:
    if total <= 0:
        return 1
    f = cleared / total
    if f >= 1.0:
        return 10
    if f >= 0.75:
        return 5
    if f >= 0.5:
        return 3
    if f >= 0.25:
        return 2
    return 1

def peg_visual(peg):
    return {'r': getattr(peg, 'r', physics.PEG_R), 'shape': getattr(peg, 'shape', 'circle'), 'w': getattr(peg, 'w', 0), 'h': getattr(peg, 'h', 0), 'angle': getattr(peg, 'angle', 0)}

class Game:

    def __init__(self, level: Layout, level_index: int=0, balls: int | None=None, seed: int | None=None, save_path: str | None=None, chosen_power: str | None=None):
        if balls is None:
            balls = getattr(level, 'balls', START_BALLS)
        self.level = level
        self.level_index = level_index
        self.pegs = level.pegs
        self.bumpers = getattr(level, 'bumpers', [])
        self.rails = getattr(level, 'rails', [])
        self.rng = random.Random(seed)
        self.save_path = save_path
        self.chosen_power = chosen_power
        self.board = Board()
        self.reset_run(balls)

    def reset_run(self, balls: int=0):
        balls = balls or getattr(self.level, 'balls', START_BALLS)
        for p in self.pegs:
            (p.alive, p.lit, p.flash) = (True, False, 0.0)
        self.score = 0
        self.balls_left = balls
        self.shots_fired = 0
        self.balls_in_flight: list[physics.Ball] = []
        self.aim = 0.0
        self.orange_total = sum((1 for p in self.pegs if p.kind == ORANGE))
        self.orange_cleared = 0
        self.bucket_x = (self.board.left + self.board.right) / 2
        self.bucket_dir = 1.0
        self.state = 'aim'
        self.time_scale = 1.0
        self.fever_well = None
        self.fever_real_t = 0.0
        self.power_queue = []
        self.active_power = None
        self.chain = 0
        self.free_ball_flash = 0.0
        self.shake = 0.0
        self.stars = 0
        self.dying = []
        self._last_drain_x = (self.board.left + self.board.right) / 2
        self.recoil = 0.0
        self.events: list[Event] = []
        self._purple = None
        self._phys_acc = 0.0
        self.shot_t = 0.0
        self.shot_real_t = 0.0
        self._pick_purple()

    @property
    def pending_power(self):
        return self.power_queue[0][0] if self.power_queue else None

    @property
    def powered_shots_remaining(self):
        return sum((shots for (_, shots) in self.power_queue))

    @property
    def guide_shots(self):
        return self.power_queue[0][1] if self.pending_power == 'guide' else 0

    def _store_power(self, power):
        policy = POWER_POLICIES[power]
        if policy.timing != 'next_shots':
            raise ValueError('unsupported power activation timing')
        if self.power_queue and self.power_queue[-1][0] == power:
            self.power_queue[-1][1] += policy.shots
        else:
            self.power_queue.append([power, policy.shots])

    def alive_pegs(self):
        return [p for p in self.pegs if p.alive]

    def collision_pegs(self):
        return self.alive_pegs() + self.bumpers + self.rails

    def oranges_left(self):
        return sum((1 for p in self.pegs if p.alive and p.kind == ORANGE and (not p.lit)))

    def multiplier(self):
        return multiplier_for(self.orange_cleared, self.orange_total)

    def _pick_purple(self):
        blues = [p for p in self.pegs if p.alive and p.kind == BLUE and (not p.lit)]
        self._purple = self.rng.choice(blues) if blues else None

    def is_purple(self, peg) -> bool:
        return peg is self._purple

    def clamp_aim(self, angle: float) -> float:
        return max(-MAX_AIM, min(MAX_AIM, angle))

    def aim_at(self, x: float, y: float):
        if y <= LAUNCH_Y + 4:
            return
        self.aim = self.clamp_aim(math.atan2(x - LAUNCH_X, y - LAUNCH_Y))

    def can_fire(self) -> bool:
        return self.state == 'aim' and self.balls_left > 0 and (not self.balls_in_flight)

    def fire(self) -> bool:
        if not self.can_fire():
            return False
        self.balls_left -= 1
        self.shots_fired += 1
        (vx, vy) = physics.fire_velocity(self.aim)
        self.balls_in_flight = [physics.Ball(LAUNCH_X, LAUNCH_Y, vx, vy)]
        self.recoil = 1.0
        self.state = 'flight'
        self.chain = 0
        self._phys_acc = 0.0
        self.shot_t = 0.0
        self.shot_real_t = 0.0
        self._last_progress_real = 0.0
        self.active_power = self.pending_power
        if self.power_queue:
            self.power_queue[0][1] -= 1
            if self.power_queue[0][1] == 0:
                self.power_queue.pop(0)
        if self.active_power == 'comet':
            self.balls_in_flight[0].comet_t = POWER_POLICIES['comet'].effect_seconds
        elif self.active_power == 'burst':
            self.balls_in_flight[0].burst = True
        elif self.active_power == 'multiball':
            b = self.balls_in_flight[0]
            self.balls_in_flight.append(physics.Ball(b.x, b.y, -b.vx * 0.9 + 60, b.vy * 0.95))
        self.events.append(Event('fire'))
        return True

    def _on_peg_hit(self, ball, peg):
        ball.since_hit = 0.0
        if peg.kind == 'well':
            hit = physics.contact(ball, peg)
            if self.state == 'fever' and peg.part == 'base' and (hit is not None) and (hit[1] < -0.7) and (ball.vy > 0) and (not ball.dead):
                (lo, hi) = bucket.well_bounds(peg.well)
                if lo + bucket.WALL / 2 + ball.r <= ball.x <= hi - bucket.WALL / 2 - ball.r:
                    ball.dead = True
                    self._last_drain_x = ball.x
                    self.fever_well = peg.well
                    points = FEVER_WELLS[peg.well]
                    self.score += points
                    self.events.append(Event('fever_well', well=peg.well, points=points, x=ball.x))
            return
        if peg.kind == 'bucket':
            hit = physics.contact(ball, peg)
            interior = BUCKET_W / 2 - bucket.WALL - ball.r
            if peg.part == 'base' and hit is not None and (hit[1] < -0.7) and (ball.vy > 0) and (abs(ball.x - peg.x) <= interior) and (self.state != 'fever') and (not ball.dead):
                ball.dead = True
                self._last_drain_x = ball.x
                self.balls_left += 1
                self.free_ball_flash = 1.0
                self.shake = max(self.shake, 0.2)
                self.events.append(Event('free_ball', x=ball.x))
            return
        if peg.kind == 'rail':
            peg.flash = 1.0
            return
        if peg.kind == 'bumper':
            peg.flash = 1.0
            self.score += BUMPER_SCORE
            self.events.append(Event('bumper_hit', x=peg.x, y=peg.y, points=BUMPER_SCORE))
            return
        if peg.lit:
            return
        self._last_progress_real = self.shot_real_t
        peg.lit = True
        peg.flash = 1.0
        self.chain += 1
        kind = 'purple' if self.is_purple(peg) else peg.kind
        pts = SCORE[kind] * self.multiplier()
        self.score += pts
        self.events.append(Event('peg_hit', x=peg.x, y=peg.y, kind=kind, points=pts, chain=self.chain))
        if self.chain in (5, 10, 15, 20, 25, 30):
            self.events.append(Event('chain', n=self.chain, x=peg.x, y=peg.y))
        if self.chain == 1:
            dist = math.hypot(peg.x - LAUNCH_X, peg.y - LAUNCH_Y)
            if dist >= LONG_SHOT_DIST:
                self.score += LONG_SHOT_BONUS
                self.events.append(Event('style', text='LONG SHOT', points=LONG_SHOT_BONUS, x=peg.x, y=peg.y))
        if ball.wall_fresh and (not ball.style_wall):
            if math.hypot(peg.x - ball.wall_bx, peg.y - ball.wall_by) >= OFF_WALL_DIST:
                ball.style_wall = True
                self.score += OFF_WALL_BONUS
                self.events.append(Event('style', text='OFF THE WALL', points=OFF_WALL_BONUS, x=peg.x, y=peg.y))
        if ball.burst:
            ball.burst = False
            hit = [p for p in self.alive_pegs() if p is not peg and (not p.lit) and (math.hypot(p.x - peg.x, p.y - peg.y) <= BURST_RADIUS)]
            self.shake = max(self.shake, 0.5)
            self.events.append(Event('burst', x=peg.x, y=peg.y, n=len(hit)))
            for p in hit:
                self._on_peg_hit(ball, p)
        if peg.kind == ORANGE:
            self.orange_cleared += 1
            if self.oranges_left() == 0:
                self.state = 'fever'
                self.time_scale = 0.28
                self.shake = max(self.shake, 0.45)
                self.events.append(Event('fever'))
        elif peg.kind == GREEN:
            power = self.chosen_power or POWERS[(self.level_index + self.shots_fired) % len(POWERS)]
            self._store_power(power)
            self.shake = max(self.shake, 0.25)
            self.events.append(Event('power', power=power, shots=POWER_POLICIES[power].shots, x=peg.x, y=peg.y))

    def _move_bucket(self, dt):
        old = self.bucket_x
        self.bucket_x += self.bucket_dir * BUCKET_SPEED * dt
        lo = self.board.left + BUCKET_W / 2
        hi = self.board.right - BUCKET_W / 2
        if self.bucket_x > hi:
            self.bucket_x = hi - (self.bucket_x - hi)
            self.bucket_dir = -1.0
        elif self.bucket_x < lo:
            self.bucket_x = lo + (lo - self.bucket_x)
            self.bucket_dir = 1.0
        return (self.bucket_x - old) / dt if dt > 0 else 0.0

    def step(self, dt: float):
        raw_dt = dt
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt * 1.5)
        if self.recoil > 0:
            self.recoil = max(0.0, self.recoil - dt * 4)
        for d in self.dying:
            if len(d) > 4 and d[4] >= 0:
                d[4] -= dt
                if d[4] < 0:
                    self.events.append(Event('peg_pop', x=d[0], y=d[1], run=d[5]))
            else:
                d[3] -= dt * 2.2
        self.dying = [d for d in self.dying if d[3] > 0]
        if self.state == 'fever':
            self.fever_real_t += raw_dt
            self.time_scale = 0.28 + 0.72 * min(1.0, max(0.0, (self.fever_real_t - 1.0) / 0.8))
        dt *= self.time_scale
        if self.state not in ('flight', 'fever') or not self.balls_in_flight:
            self._move_bucket(dt)
        for p in self.pegs:
            if p.flash > 0:
                p.flash = max(0.0, p.flash - dt * 3)
        for bp in self.bumpers + self.rails:
            if bp.flash > 0:
                bp.flash = max(0.0, bp.flash - dt * 3)
        if self.free_ball_flash > 0:
            self.free_ball_flash = max(0.0, self.free_ball_flash - dt * 2)
        if self.state in ('flight', 'fever') and self.balls_in_flight:
            self._phys_acc = min(self._phys_acc + dt, 0.12)
            self.shot_real_t += raw_dt
            h = 1 / 120
            while self._phys_acc >= h and self.balls_in_flight:
                self._phys_acc -= h
                self.shot_t += h
                bucket_vx = self._move_bucket(h)
                physical = self.collision_pegs()
                if self.state != 'fever':
                    physical += bucket.surfaces(self.bucket_x, bucket_vx)
                else:
                    physical += bucket.well_surfaces()
                physics.step_balls(self.balls_in_flight, physical, self.board, h, self._on_peg_hit)
                survivors = []
                for b in self.balls_in_flight:
                    if b.dead:
                        continue
                    b.since_hit += h
                    support = b.resting_on
                    if b.resting_t >= 0.45 and support is not None and support.alive:
                        (support.alive, support.lit) = (False, False)
                        self.dying.append([support.x, support.y, support.kind, 1.0, -1, 0, peg_visual(support)])
                        self.events.append(Event('peg_pop', x=support.x, y=support.y, run=0))
                        (b.resting_on, b.resting_t) = (None, 0.0)
                    if b.y - b.r > DRAIN_Y:
                        self._ball_drained(b)
                    elif b.since_hit > 15.0:
                        self.events.append(Event('stalled', x=b.x, y=b.y))
                    else:
                        survivors.append(b)
                self.balls_in_flight = survivors
            stalled_out = self.shot_t > SHOT_TIME_CAP or self.shot_real_t > SHOT_REAL_TIME_CAP or self.shot_real_t - self._last_progress_real > PROGRESS_STALL_REAL
            if stalled_out:
                for b in self.balls_in_flight:
                    if not b.drop:
                        b.drop = True
                        self.events.append(Event('stalled', x=b.x, y=b.y))
            if not self.balls_in_flight:
                self._shot_over()

    def _ball_drained(self, ball):
        self._last_drain_x = ball.x

    def _shot_over(self):
        removed = [p for p in self.pegs if p.lit]
        removed.sort(key=lambda p: (p.x - self._last_drain_x) ** 2 + (p.y - DRAIN_Y) ** 2)
        for (i, p) in enumerate(removed):
            self.dying.append([p.x, p.y, 'purple' if self.is_purple(p) else p.kind, 1.0, min(i * CASCADE_STAGGER, CASCADE_STAGGER_CAP), i, peg_visual(p)])
            p.alive = False
            p.lit = False
        if removed:
            self.events.append(Event('clear', count=len(removed)))
        self.chain = 0
        self.active_power = None
        if self.state == 'fever':
            self.time_scale = 1.0
            self.state = 'won'
            self.stars = 1 + (self.score >= self.level.star2) + (self.score >= self.level.star3)
            self.events.append(Event('won', score=self.score, stars=self.stars))
            self._record_progress()
            return
        self._pick_purple()
        if self.oranges_left() == 0:
            self.state = 'won'
            self.stars = 1 + (self.score >= self.level.star2) + (self.score >= self.level.star3)
            self.events.append(Event('won', score=self.score, stars=self.stars))
            self._record_progress()
        elif self.balls_left <= 0:
            self.state = 'lost'
            self.events.append(Event('lost', score=self.score))
        else:
            self.state = 'aim'

    def _record_progress(self):
        if not self.save_path:
            return
        try:
            save_progress(self.save_path, {self.level_index: (self.score, self.stars)})
            self.save_error = None
        except OSError as exc:
            self.save_error = type(exc).__name__

def merge_progress(data, records=(), prefs=None):
    for (idx, (score, stars)) in dict(records).items():
        key = str(idx)
        data.setdefault('best', {})[key] = max(data.get('best', {}).get(key, 0), score)
        data.setdefault('stars', {})[key] = max(data.get('stars', {}).get(key, 0), stars)
        data['unlocked'] = max(data.get('unlocked', 1), idx + 2)
    if prefs:
        data.update(prefs)
    return data

def save_progress(save_path, records=(), prefs=None):
    from .save_lock import profile_write_lock
    with profile_write_lock(save_path):
        return _save_progress_unlocked(save_path, records, prefs)

def _save_progress_unlocked(save_path, records=(), prefs=None):
    data = merge_progress(load_progress(save_path, strict_io=True), records, prefs)
    folder = os.path.dirname(save_path) or '.'
    os.makedirs(folder, exist_ok=True)
    (fd, tmp) = tempfile.mkstemp(prefix='.pegfall-', suffix='.tmp', dir=folder)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, save_path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
    return data

def progress_path(base_dir: str) -> str:
    return os.path.join(base_dir, 'progress.json')

def load_progress(save_path: str, strict_io=False) -> dict:
    try:
        with open(save_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        return {'unlocked': 1, 'best': {}}
    except OSError:
        if strict_io:
            raise
        return {'unlocked': 1, 'best': {}}
    except (ValueError, UnicodeError, RecursionError):
        return {'unlocked': 1, 'best': {}}
    if not isinstance(data, dict):
        return {'unlocked': 1, 'best': {}}

    def records(value, stars=False):
        if not isinstance(value, dict):
            return {}

        def board_key(key):
            if not (isinstance(key, str) and key.isascii() and key.isdigit()):
                return False
            try:
                return str(int(key)) == key
            except ValueError:
                return False
        return {k: v for (k, v) in value.items() if board_key(k) and isinstance(v, int) and (not isinstance(v, bool)) and (1 <= v <= 3 if stars else v >= 0)}
    data['best'] = records(data.get('best'))
    data['stars'] = records(data.get('stars'), stars=True)
    completed = [int(k) for k in data['stars']]
    cur = data.get('unlocked')
    if not isinstance(cur, int) or isinstance(cur, bool):
        cur = 1
    data['unlocked'] = max([1, cur] + [k + 2 for k in completed])
    return data
