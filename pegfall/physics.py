from __future__ import annotations
import math
GRAVITY = 560.0
FIRE_SPEED = 480.0
BALL_R = 6.0
PEG_R = 11.0
RESTITUTION = 0.74
AIR_DRAG = 0.08
CONTACT_FRICTION = 0.025
SETTLE_SPEED = 45.0
WALL_RESTITUTION = 0.72
MAX_SPEED = 2100.0
SUBSTEP_PX = 3.5

class Ball:
    __slots__ = ('x', 'y', 'vx', 'vy', 'r', 'comet_t', 'burst', 'drop', 'dead', 'trail', 'since_hit', 'wall_bx', 'wall_by', 'wall_fresh', 'style_wall', 'resting_on', 'resting_t')

    def __init__(self, x: float, y: float, vx: float, vy: float):
        (self.x, self.y) = (x, y)
        (self.vx, self.vy) = (vx, vy)
        self.r = BALL_R
        self.comet_t = 0.0
        self.burst = False
        self.drop = False
        self.dead = False
        self.trail: list[tuple[float, float]] = []
        self.since_hit = 0.0
        self.wall_bx = 0.0
        self.wall_by = 0.0
        self.wall_fresh = False
        self.resting_on = None
        self.resting_t = 0.0
        self.style_wall = False

    @property
    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)

def fire_velocity(angle: float) -> tuple[float, float]:
    return (math.sin(angle) * FIRE_SPEED, math.cos(angle) * FIRE_SPEED)

def contact(ball, peg):
    if getattr(peg, 'shape', 'circle') != 'box':
        (dx, dy) = (ball.x - peg.x, ball.y - peg.y)
        dist = math.hypot(dx, dy)
        overlap = ball.r + getattr(peg, 'r', PEG_R) - dist
        if overlap < 0:
            return None
        if dist < 1e-09:
            return (0.0, -1.0, overlap)
        return (dx / dist, dy / dist, overlap)
    (c, s) = (math.cos(peg.angle), math.sin(peg.angle))
    (dx, dy) = (ball.x - peg.x, ball.y - peg.y)
    (x, y) = (c * dx + s * dy, -s * dx + c * dy)
    (hx, hy) = (peg.w / 2, peg.h / 2)
    (qx, qy) = (max(-hx, min(hx, x)), max(-hy, min(hy, y)))
    (nx, ny) = (x - qx, y - qy)
    dist = math.hypot(nx, ny)
    if dist > ball.r:
        return None
    if dist > 1e-09:
        (nx, ny, depth) = (nx / dist, ny / dist, ball.r - dist)
    elif hx - abs(x) < hy - abs(y):
        (nx, ny, depth) = (1.0 if x >= 0 else -1.0, 0.0, ball.r + hx - abs(x))
    else:
        (nx, ny, depth) = (0.0, 1.0 if y >= 0 else -1.0, ball.r + hy - abs(y))
    return (c * nx - s * ny, s * nx + c * ny, depth)

def _bounce_off_peg(ball: Ball, peg) -> None:
    hit = contact(ball, peg)
    if hit is None:
        return
    (nx, ny, overlap) = hit
    rest = getattr(peg, 'rest', RESTITUTION)
    if getattr(peg, 'shape', 'circle') != 'box' and abs(nx) < 0.015:
        nx = 0.025 if peg.x >= 480.0 else -0.025
        ny = math.copysign(math.sqrt(1.0 - nx * nx), ny)
    if overlap > 0:
        ball.x += nx * overlap
        ball.y += ny * overlap
    surface_vx = getattr(peg, 'vx', 0.0)
    relative_vx = ball.vx - surface_vx
    vn = relative_vx * nx + ball.vy * ny
    if vn < 0:
        (tx, ty) = (relative_vx - vn * nx, ball.vy - vn * ny)
        restitution = rest if -vn >= SETTLE_SPEED else 0.0
        ball.vx = surface_vx + tx * (1 - CONTACT_FRICTION) - restitution * vn * nx
        ball.vy = ty * (1 - CONTACT_FRICTION) - restitution * vn * ny
        kick = getattr(peg, 'kick', 0.0)
        if kick:
            speed = ball.speed
            if 1e-06 < speed < kick:
                ball.vx *= kick / speed
                ball.vy *= kick / speed
        speed = ball.speed
        if speed > MAX_SPEED:
            ball.vx *= MAX_SPEED / speed
            ball.vy *= MAX_SPEED / speed

def step_balls(balls: list[Ball], pegs, board, dt: float, on_peg_hit) -> None:
    for ball in balls:
        if ball.dead:
            continue
        support = None
        dist = ball.speed * dt
        n = max(1, int(dist / SUBSTEP_PX) + 1)
        h = dt / n
        for substep in range(n):
            if ball.comet_t > 0:
                ball.comet_t -= h
            damp = math.exp(-AIR_DRAG * h)
            ball.vx *= damp
            ball.vy *= damp
            ball.vy += GRAVITY * h
            ball.x += ball.vx * h
            ball.y += ball.vy * h
            if ball.x - ball.r < board.left:
                ball.x = board.left + ball.r
                ball.vx = abs(ball.vx) * WALL_RESTITUTION
                (ball.wall_bx, ball.wall_by, ball.wall_fresh) = (ball.x, ball.y, True)
            elif ball.x + ball.r > board.right:
                ball.x = board.right - ball.r
                ball.vx = -abs(ball.vx) * WALL_RESTITUTION
                (ball.wall_bx, ball.wall_by, ball.wall_fresh) = (ball.x, ball.y, True)
            if ball.y - ball.r < board.top:
                ball.y = board.top + ball.r
                if ball.vy < 0:
                    ball.vy = -ball.vy * WALL_RESTITUTION
            for peg in pegs:
                if ball.drop and peg.kind not in ('bucket', 'well'):
                    continue
                if not peg.alive:
                    continue
                final_x = peg.x
                peg.x -= getattr(peg, 'vx', 0.0) * (dt - (substep + 1) * h)
                try:
                    if contact(ball, peg) is not None:
                        on_peg_hit(ball, peg)
                        if ball.dead:
                            break
                        if ball.comet_t <= 0 or peg.kind in ('rail', 'bucket', 'well'):
                            _bounce_off_peg(ball, peg)
                            if getattr(peg, 'lit', False) and ball.speed < 90 and (ball.y < peg.y):
                                support = peg
                finally:
                    peg.x = final_x
            if ball.dead:
                break
            if len(ball.trail) == 0 or (ball.x - ball.trail[-1][0]) ** 2 + (ball.y - ball.trail[-1][1]) ** 2 > 64:
                ball.trail.append((ball.x, ball.y))
                if len(ball.trail) > 14:
                    ball.trail.pop(0)
        if support is not None and support is ball.resting_on:
            ball.resting_t += dt
        else:
            (ball.resting_on, ball.resting_t) = (support, 0.0)

def predict_path(x: float, y: float, angle: float, pegs, board, seconds: float=1.35, dt: float=1 / 240) -> list[tuple[float, float]]:
    (vx, vy) = fire_velocity(angle)
    ghost = Ball(x, y, vx, vy)
    pts = []
    steps = int(seconds / dt)
    for i in range(steps):
        step_balls([ghost], pegs, board, dt, lambda b, p: None)
        if i % 12 == 0:
            pts.append((ghost.x, ghost.y))
        if ghost.y > 760:
            break
    return pts
