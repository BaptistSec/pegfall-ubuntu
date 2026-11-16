from __future__ import annotations
import json
import math
import random
import os
import shutil
import tempfile
import sys
import pygame
from . import audio, physics, life_story, life_art, farm_world, narrative, city_world, finale, story_scenes
from .game import Game, SCREEN_W, SCREEN_H, LAUNCH_X, LAUNCH_Y, load_progress, progress_path, save_progress, merge_progress
from .guide_preview import GuidePreview
from .levels import build_levels, build_classic_levels, BLUE, ORANGE, GREEN
from .render import Renderer, Popups, INK, DIM, PEG_COLORS
APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0] if getattr(sys, 'frozen', False) else __file__))

def _legacy_save_paths():
    paths = []
    if getattr(sys, 'frozen', False):
        paths.append(progress_path(os.path.dirname(os.path.abspath(sys.executable))))
    paths.append(progress_path(os.path.expanduser('~/.pegfall')))
    return paths

def _copy_progress(source, destination):
    folder = os.path.dirname(destination) or '.'
    os.makedirs(folder, exist_ok=True)
    (fd, tmp) = tempfile.mkstemp(prefix='.pegfall-import-', suffix='.tmp', dir=folder)
    try:
        with os.fdopen(fd, 'wb') as target, open(source, 'rb') as original:
            shutil.copyfileobj(original, target)
            target.flush()
            os.fsync(target.fileno())
        os.replace(tmp, destination)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass

def _save_path(on_migration_error=None, import_source=None):
    if os.name == 'nt':
        base = os.environ.get('LOCALAPPDATA') or os.environ.get('APPDATA') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
    else:
        base = os.environ.get('XDG_DATA_HOME') or os.path.join(os.path.expanduser('~'), '.local', 'share')
    new = progress_path(os.path.join(base, 'pegfall-rc1'))
    if os.path.islink(os.path.dirname(new)) or os.path.islink(new):
        raise OSError('Progress file must not be a symbolic link: ' + new)
    if os.path.exists(new) and os.stat(new).st_nlink > 1:
        raise OSError('Progress file must not be a hard-linked file: ' + new)
    if import_source is not None and (not os.path.exists(new)):
        try:
            _copy_progress(import_source, new)
        except OSError:
            if on_migration_error is not None:
                on_migration_error(import_source)
    return new
WON_SPLASH_HOLD = 0.65
LOST_SPLASH_HOLD = 1.2
COMPANIONS = [('Rotator', None, 'green pegs cycle through all four powers'), ('Sprocket', 'guide', 'guide: aim preview on the next two shots'), ('Comet', 'comet', 'comet: next two shots phase through pegs'), ('Gemini', 'multiball', 'multiball: launch twins on the next two shots'), ('Nova', 'burst', 'burst: next two shots blast their first hit')]

class App:

    def __init__(self, headless=False):
        if headless:
            os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
            os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
        try:
            pygame.init()
            audio.init()
            if not headless:
                audio.prewarm_effects()
            self.clock = pygame.time.Clock()
            self.levels = build_levels()
            self._migration_source = None

            def migration_error(source):
                self._migration_source = source
            self.save = _save_path(on_migration_error=migration_error)
            self._profile_read_failed = False
            try:
                self.progress = load_progress(self._migration_source or self.save, strict_io=True)
            except OSError:
                self._profile_read_failed = True
                self.progress = {'unlocked': 1, 'best': {}, 'stars': {}}
            self.r = Renderer(headless, fullscreen=bool(self.progress.get('fullscreen', False)))
            _v = self.progress.get('volume', 1.0)
            if not isinstance(_v, (int, float)) or isinstance(_v, bool) or (not 0.0 <= _v <= 1.0):
                _v = 1.0
            audio.set_volume(_v)
            audio.set_enabled(not self.progress.get('muted', False))
            self.mode = 'menu'
            self.menu_sel = 0
            self.intro_t = 0.0
            self._won_hold = 0.0
            self._lost_hold = 0.0
            self.game = None
            self.running = True
            self._stars = None
            self._music_mode = None
            self._pending_records = {}
            self._pending_prefs = {}
            self.save_warning = self._migration_source is not None or self._profile_read_failed
            _c = self.progress.get('companion', 0)
            if not isinstance(_c, int) or isinstance(_c, bool) or (not 0 <= _c < len(COMPANIONS)):
                _c = 0
            self.companion = _c
            self.comp_sel = self.companion
        except BaseException:
            try:
                audio.shutdown()
            except Exception:
                pass
            try:
                pygame.quit()
            except Exception:
                pass
            raise

    def _unlocked(self):
        return self.progress.get('unlocked', 1)

    def _twinkle(self, s):
        if self._stars is None:
            rng = random.Random(7)
            self._stars = [(rng.randrange(0, SCREEN_W), rng.randrange(0, SCREEN_H), rng.random() * 2 * math.pi) for _ in range(48)]
        t = pygame.time.get_ticks() / 1000.0
        for (x, y, phase) in self._stars:
            a = 0.5 + 0.5 * math.sin(t * 1.4 + phase)
            c = int(120 + 120 * a)
            s.set_at((x, y), (c, c, min(255, c + 20)))
            if a > 0.85:
                for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if 0 <= x + dx < SCREEN_W and 0 <= y + dy < SCREEN_H:
                        s.set_at((x + dx, y + dy), (c // 2, c // 2, c // 2 + 20))

    def _wrap(self, text, width):
        (lines, cur) = ([], '')
        for word in text.split():
            trial = f'{cur} {word}'.strip()
            if self.r.font_s.size(trial)[0] <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def _menu_preview(self, s):
        lv = self.levels[self.menu_sel]
        (px0, py0, pw, ph) = (16, 235, 232, 430)
        pygame.draw.rect(s, (16, 20, 42), (px0, py0, pw, ph), border_radius=10)
        pygame.draw.rect(s, (70, 80, 130), (px0, py0, pw, ph), 2, border_radius=10)
        name_text = f'Board {self.menu_sel + 1}'
        name_font = self.r.font_m if self.r.font_m.size(name_text)[0] <= pw - 24 else self.r.font_s
        name = name_font.render(name_text, True, (255, 220, 120))
        s.blit(name, name.get_rect(center=(px0 + pw // 2, py0 + 28)))
        subtitle_lines = ['Clear every orange peg']
        sub = self.r.font_s.render(subtitle_lines[0], True, DIM)
        s.blit(sub, sub.get_rect(center=(px0 + pw // 2, py0 + 54)))
        if self.menu_sel >= self._unlocked():
            img = self.r.font_m.render('locked', True, DIM)
            s.blit(img, img.get_rect(center=(px0 + pw // 2, py0 + ph // 2)))
            return
        sc = min((pw - 24) / 880, 170 / 550)
        ox = px0 + 12
        oy = py0 + 74 + max(0, len(subtitle_lines) - 1) * 18
        for p in lv.pegs:
            (base, _rim) = PEG_COLORS.get(p.kind, PEG_COLORS[BLUE])
            r = 4 if p.kind in (ORANGE, GREEN) else 3
            pos = (int(ox + (p.x - 40) * sc), int(oy + (p.y - 90) * sc))
            if getattr(p, 'shape', 'circle') == 'box':
                rect = pygame.Rect(0, 0, max(3, round(p.w * sc)), max(2, round(p.h * sc)))
                rect.center = pos
                pygame.draw.rect(s, base, rect)
            else:
                pygame.draw.circle(s, base, pos, r)
        for bp in lv.bumpers:
            pygame.draw.circle(s, (255, 220, 120), (int(ox + (bp.x - 40) * sc), int(oy + (bp.y - 90) * sc)), 4, 1)
        for rail in getattr(lv, 'rails', []):
            (dx, dy) = (math.cos(rail.angle) * rail.w * 0.5, math.sin(rail.angle) * rail.w * 0.5)
            pygame.draw.line(s, (180, 200, 225), (ox + (rail.x - dx - 40) * sc, oy + (rail.y - dy - 90) * sc), (ox + (rail.x + dx - 40) * sc, oy + (rail.y + dy - 90) * sc), 2)
        y = oy + int(550 * sc) + 22
        lines = [f'balls {lv.balls}', f'2* {lv.star2:,}    3* {lv.star3:,}']
        best = self.progress.get('best', {}).get(str(self.menu_sel))
        if best:
            lines.append(f'best {best:,}')
        for line in lines:
            img = self.r.font_s.render(line, True, DIM)
            s.blit(img, img.get_rect(center=(px0 + pw // 2, y)))
            y += 24

    def _handle_game_events(self):
        for ev in self.game.events:
            k = ev.kind
            d = ev.data
            if k == 'peg_hit':
                self.r.popups.add(d.get('x', 480), d.get('y', 300) - 13, f"+{d.get('points', 0):,}", (255, 245, 210))
            elif k == 'free_ball':
                self.r.popups.add(d.get('x', 480), 650, 'EXTRA BALL', (221, 255, 206))
            elif k == 'fever_well':
                self.r.popups.add(d.get('x', 480), 635, f"+{d.get('points', 0):,}", (255, 222, 130))
            elif k == 'stalled':
                self.r.popups.add(d.get('x', 480), d.get('y', 300) - 13, 'BALL RELEASED', (219, 235, 245))
            elif k == 'power':
                self.r.popups.add(d.get('x', 480), d.get('y', 270) - 14, str(d.get('power', '')).upper(), (229, 217, 255))
            if k == 'bumper_hit':
                pass
                pass
                audio.plink(2)
            elif k == 'peg_hit':
                if self.game.level_index == 2 and (not getattr(self, '_farm_grin_shown', False)):
                    self.r._crew_reaction_t = 0.9
                    self._farm_grin_shown = True
                if d.get('kind') == 'orange':
                    pass
                    pass
                    audio.plink_orange(d['chain'])
                else:
                    pass
                    pass
                    audio.plink(d['chain'])
            elif k == 'fire':
                self.intro_t = 0.0
                audio.fire()
            elif k == 'free_ball':
                pass
                audio.free_ball()
            elif k == 'chain':
                pass
            elif k == 'burst':
                for _ in range(3):
                    pass
                pass
                audio.power()
            elif k == 'style':
                pass
            elif k == 'power':
                pass
                audio.power()
            elif k == 'peg_pop':
                pass
            elif k == 'stalled':
                pass
                audio.stall()
            elif k == 'fever':
                pass
                for _ in range(6):
                    pass
                audio.fever()
            elif k == 'fever_well':
                audio.points_bucket()
                pass
                pass
                self.game.shake = max(self.game.shake, 0.3)
            elif k == 'won':
                self._won_hold = WON_SPLASH_HOLD
                if self._migration_source is not None or getattr(self.game, 'save_error', None):
                    idx = self.game.level_index
                    (score, stars) = self._pending_records.get(idx, (0, 0))
                    self._pending_records[idx] = (max(score, self.game.score), max(stars, self.game.stars))
                if self._pending_records or self._pending_prefs:
                    self._retry_save()
                else:
                    try:
                        self.progress = load_progress(self.save, strict_io=True)
                    except OSError:
                        idx = self.game.level_index
                        self._pending_records[idx] = (self.game.score, self.game.stars)
                        merge_progress(self.progress, self._pending_records)
                        self._profile_read_failed = True
                        self.save_warning = True
                audio.won()
            elif k == 'lost':
                self._lost_hold = LOST_SPLASH_HOLD
                self.r.popups = self.r.new_popups()
                audio.lost()
        self.game.events.clear()

    def _save_pref(self, key, value):
        self.progress[key] = value
        self._pending_prefs[key] = value
        self._retry_save()

    def _restore_profile_options(self):
        vol = self.progress.get('volume', 1.0)
        if not isinstance(vol, (int, float)) or isinstance(vol, bool) or (not 0.0 <= vol <= 1.0):
            vol = 1.0
        audio.set_volume(vol)
        audio.set_enabled(not self.progress.get('muted', False))
        self._music_mode = None
        companion = self.progress.get('companion', 0)
        if not isinstance(companion, int) or isinstance(companion, bool) or (not 0 <= companion < len(COMPANIONS)):
            companion = 0
        self.companion = self.comp_sel = companion
        fullscreen = bool(self.progress.get('fullscreen', False))
        if fullscreen != self.r.fullscreen:
            self.r.set_fullscreen(fullscreen)

    def _retry_save(self):
        recovering_options = self._migration_source is not None or self._profile_read_failed
        if self._migration_source is not None:
            try:
                if not os.path.exists(self.save):
                    _copy_progress(self._migration_source, self.save)
                with open(self.save) as saved:
                    if not isinstance(json.load(saved), dict):
                        raise ValueError('progress file is not a JSON object')
            except (OSError, ValueError, RecursionError):
                self.save_warning = True
                merge_progress(self.progress, self._pending_records, self._pending_prefs)
                return False
            self._migration_source = None
            if self.game is not None and self.game.save_path is None:
                self.game.save_path = self.save
            if not (self._pending_records or self._pending_prefs):
                self.progress = load_progress(self.save)
                self.save_warning = False
        if not (self._pending_records or self._pending_prefs):
            if self._profile_read_failed:
                try:
                    self.progress = load_progress(self.save, strict_io=True)
                except OSError:
                    return False
                self._profile_read_failed = False
                self.save_warning = False
            if recovering_options:
                self._restore_profile_options()
            return True
        try:
            self.progress = save_progress(self.save, self._pending_records, self._pending_prefs)
        except OSError:
            self.save_warning = True
            merge_progress(self.progress, self._pending_records, self._pending_prefs)
            return False
        self._pending_records.clear()
        self._pending_prefs.clear()
        self._profile_read_failed = False
        self.save_warning = False
        if recovering_options:
            self._restore_profile_options()
        if self.game is not None and getattr(self.game, 'save_error', None):
            self.game.save_error = None
        return True

    def _save_notice(self):
        if self.save_warning:
            s = self.r.screen
            pygame.draw.rect(s, (104, 34, 30), (95, 669, 770, 17))
            text = self.r.font_s.render('SAVE FAILED - S retries. Keep this window open to retain unsaved progress.', True, (255, 240, 210))
            s.blit(text, text.get_rect(center=(480, 677)))

    def _sync_music(self):
        if self.mode in ('menu', 'help', 'companion'):
            want = 'menu'
        elif self.mode == 'story':
            want = {'opening': 'menu', 'farm': narrative.music_key(19), 'village': narrative.music_key(39), 'ending': 'finale'}[self._story_scene]
        elif self.mode in ('play', 'pause', 'ending'):
            want = 'finale' if self.menu_sel == 59 and self.game is not None and (self.game.state == 'won') else narrative.music_key(self.menu_sel)
        else:
            want = None
        if want != self._music_mode:
            self._music_mode = want
            if want is None:
                audio.music_stop()
            else:
                audio.music_start(want)

    def _toggle_mute(self):
        muted = not self.progress.get('muted', False)
        audio.set_enabled(not muted)
        self._save_pref('muted', muted)
        self._music_mode = None

    def _toggle_fullscreen(self):
        self.r.set_fullscreen(not self.r.fullscreen)
        self._save_pref('fullscreen', self.r.fullscreen)

    def _volume_step(self, d):
        cur = self.progress.get('volume', 1.0)
        if not isinstance(cur, (int, float)) or isinstance(cur, bool) or (not 0.0 <= cur <= 1.0):
            cur = 1.0
        steps = min(10, max(0, round(cur * 10) + round(d * 10)))
        vol = steps / 10
        audio.set_volume(vol)
        self._save_pref('volume', vol)

    def _common_key(self, e):
        if e.key == pygame.K_s and self.save_warning:
            self._retry_save()
            return True
        if e.key == pygame.K_F11:
            self._toggle_fullscreen()
            return True
        if e.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self._volume_step(-0.1)
            return True
        if e.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
            self._volume_step(0.1)
            return True
        return False

    def _screen_events(self, mode):
        events = pygame.event.get()
        if any((e.type == pygame.QUIT for e in events)):
            self.running = False
            return
        game = self.game
        for event in events:
            if not self.running or self.mode != mode or (mode == 'play' and self.game is not game):
                break
            yield event
    HELP_LINES = [('aim', 'move the mouse, or left / right arrows'), ('fine aim', 'hold shift with the arrows'), ('launch', 'click or space'), ('pause', 'esc   (r restarts, m menu, v mute)'), ('display', 'f11 fullscreen    - / = volume'), ('', ''), ('orange pegs', 'clear them all to win the board'), ('purple peg', 'worth 5x a blue peg - moves after every shot'), ('bumpers', 'gold discs kick the ball back - bank off them'), ('green pegs', 'store power for your next two shots:'), ('  companions', 'pick one before each board'), ('  guide / comet', 'see the path / plough through pegs'), ('  multiball / burst', 'two balls / detonate a cluster'), ('  rotator', 'no single power - cycles all four'), ('bucket', 'catch the ball for a free shot'), ('fever', 'clear the last orange, then land in a well')]

    def _help_step(self, dt):
        self.r.side_active = False
        for e in self._screen_events('help'):
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if self._common_key(e):
                    continue
                if e.key in (pygame.K_ESCAPE, pygame.K_h, pygame.K_RETURN, pygame.K_SPACE):
                    self.mode = 'menu'
        s = self.r.screen
        s.blit(self.r.backgrounds[9], (0, 0))
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((31, 49, 46, 212))
        s.blit(veil, (0, 0))
        self._twinkle(s)
        title = self.r.font_xl.render('HOW TO PLAY', True, (255, 220, 120))
        s.blit(title, title.get_rect(center=(SCREEN_W // 2, 100)))
        panel = pygame.Surface((SCREEN_W - 60, 520), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 12, 30, 170), panel.get_rect(), border_radius=14)
        s.blit(panel, (30, 146))
        y = 166
        for (term, desc) in self.HELP_LINES:
            if not term:
                y += 14
                continue
            t = self.r.font_m.render(term, True, (255, 220, 120))
            s.blit(t, (200, y))
            d = self.r.font_m.render(desc, True, INK)
            s.blit(d, (390, y))
            y += 30
        back = self.r.font_s.render('h / esc - back', True, DIM)
        s.blit(back, back.get_rect(center=(SCREEN_W // 2, SCREEN_H - 26)))
        self._save_notice()
        self.r.present()

    def _menu_step(self, dt):
        for e in self._screen_events('menu'):
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if self._common_key(e):
                    continue
                if e.key == pygame.K_ESCAPE:
                    self.running = False
                elif e.key == pygame.K_v:
                    self._toggle_mute()
                elif e.key == pygame.K_h:
                    self.mode = 'help'
                elif e.key == pygame.K_t:
                    self._save_pref('story_scenes', not self.progress.get('story_scenes', True))
                elif e.key == pygame.K_o:
                    self.mode = 'story_menu'
                elif e.key in (pygame.K_UP, pygame.K_w):
                    self.menu_sel = (self.menu_sel - 1) % self._menu_reachable()
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_sel = (self.menu_sel + 1) % self._menu_reachable()
                elif e.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                    self.menu_sel = self._menu_hop(-1 if e.key in (pygame.K_LEFT, pygame.K_a) else 1)
                elif e.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                    offset = -20 if e.key == pygame.K_PAGEUP else 20
                    self.menu_sel = max(0, min(self._menu_reachable() - 1, self.menu_sel + offset))
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.menu_sel < self._unlocked():
                        self.comp_sel = self.companion
                        self.mode = 'companion'
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                pos = self.r.to_logical(e.pos)
                if 650 <= pos[1] <= 680:
                    if pos[0] < 480:
                        self._save_pref('story_scenes', not self.progress.get('story_scenes', True))
                    else:
                        self.mode = 'story_menu'
                    continue
                idx = self._menu_hit(pos)
                if idx is not None and idx < self._unlocked():
                    self.menu_sel = idx
                    self.comp_sel = self.companion
                    self.mode = 'companion'
            elif e.type == pygame.MOUSEMOTION:
                idx = self._menu_hit(self.r.to_logical(e.pos))
                if idx is not None and idx < self._unlocked():
                    self.menu_sel = idx
        self._menu_draw()

    def _menu_pos(self, i):
        n = len(self.levels)
        if n <= 10:
            return (SCREEN_W // 2, 250 + i * 42)
        if n <= 18:
            gap = min(42, (620 - 230) // n)
            return (SCREEN_W // 2, 230 + i * gap)
        if n > 36:
            local = i % 20
            return ((390, 720)[local // 10], 253 + local % 10 * 39)
        per = (n + 1) // 2
        (col, row) = (0, i) if i < per else (1, i - per)
        gap = min(34, (620 - 235) // per)
        return ((390, 720)[col], 235 + row * gap)

    def _menu_reachable(self):
        return max(1, min(self._unlocked(), len(self.levels)))

    def _menu_hop(self, direction):
        n = len(self.levels)
        if n <= 18:
            return self.menu_sel
        reach = self._menu_reachable()
        if n > 36:
            lo = self.menu_sel // 20 * 20
            target = self.menu_sel + direction * 10
            if not lo <= target < min(lo + 20, n):
                return self.menu_sel
            if target < reach:
                return target
            other_lo = lo + (10 if direction > 0 else 0)
            other_hi = lo + (20 if direction > 0 else 10)
            last = min(other_hi, reach) - 1
            return last if last >= other_lo else self.menu_sel
        per = (n + 1) // 2
        target = self.menu_sel + direction * per
        if not 0 <= target < n:
            return self.menu_sel
        if target < reach:
            return target
        lo = per if direction > 0 else 0
        hi = n if direction > 0 else per
        last = min(reach, hi) - 1
        return last if last >= lo else self.menu_sel

    def _menu_hit(self, pos):
        (x, y) = pos
        n = len(self.levels)
        two_col = n > 18
        visible = range(self.menu_sel // 20 * 20, min(n, (self.menu_sel // 20 + 1) * 20)) if n > 36 else range(n)
        for i in visible:
            (cx, cy) = self._menu_pos(i)
            half = 140 if two_col else 220
            if abs(x - cx) >= half:
                continue
            up = dn = 20
            if i and (n <= 36 or i % 10):
                (px, py) = self._menu_pos(i - 1)
                if px == cx:
                    up = (cy - py) / 2
            if i < n - 1 and (n <= 36 or i % 10 != 9):
                (nx, ny) = self._menu_pos(i + 1)
                if nx == cx:
                    dn = (ny - cy) / 2
            if -up <= y - cy < dn:
                return i
        return None

    def _menu_draw(self):
        self.r.side_active = False
        s = self.r.screen
        s.blit(self.r.backgrounds[9], (0, 0))
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((31, 49, 46, 212))
        s.blit(veil, (0, 0))
        farm_world.draw_title(s)
        title = self.r.font_xl.render('PEGFALL', True, (255, 236, 184))
        s.blit(title, title.get_rect(center=(SCREEN_W // 2, 95)))
        from . import __version__
        self.r.caption('The Brass Lantern  /  ' + __version__, (480, 174))
        if self.progress.get('completed') and all((self.progress.get('stars', {}).get(str(i), 0) >= 1 for i in range(len(self.levels)))):
            badge = self.r.font_s.render('CAMPAIGN COMPLETE', True, (140, 255, 170))
            s.blit(badge, badge.get_rect(center=(SCREEN_W // 2, 194)))
        total_stars = sum((self.progress.get('stars', {}).get(str(i), 0) for i in range(len(self.levels))))
        if total_stars:
            ts = self.r.font_s.render(f'* {total_stars} / {3 * len(self.levels)}', True, (255, 220, 120))
            stars_x = 132 if len(self.levels) > 36 else SCREEN_W // 2
            s.blit(ts, ts.get_rect(center=(stars_x, 216)))
        unlocked = self._unlocked()
        best = self.progress.get('best', {})
        self._menu_preview(s)
        two_col = len(self.levels) > 18
        font = self.r.font_s if two_col else self.r.font_m
        if len(self.levels) > 36:
            page = self.menu_sel // 20
            text = self.r.font_s.render(f'BOARDS {page * 20 + 1}-{min((page + 1) * 20, len(self.levels))}  /  {len(self.levels)}    pgup / pgdn', True, (190, 202, 187))
            s.blit(text, text.get_rect(center=(585, 220)))
        for (i, lv) in enumerate(self.levels):
            if len(self.levels) > 36 and i // 20 != self.menu_sel // 20:
                continue
            (cx, y) = self._menu_pos(i)
            locked = i >= unlocked
            sel = i == self.menu_sel and (not locked)
            col = (255, 220, 120) if sel else (145, 161, 151) if locked else INK
            name = f'Board {i + 1}'
            if two_col:
                while font.size(name)[0] > 182:
                    name = name[:-2].rstrip('.') + '.'
            if locked and (not two_col):
                name += '   (locked)'
            img = font.render(name, True, col)
            if two_col:
                r = img.get_rect(midleft=(cx - 130, y))
            else:
                r = img.get_rect(center=(cx, y))
            s.blit(img, r)
            if not two_col and (not locked) and (str(i) in best):
                b = self.r.font_s.render(f'best {best[str(i)]:,}', True, (190, 202, 187))
                s.blit(b, b.get_rect(center=(SCREEN_W // 2 + 190, y)))
            stars = self.progress.get('stars', {}).get(str(i), 0)
            if not locked:
                sx0 = cx + 65 if two_col else SCREEN_W // 2 - 184
                for k in range(3):
                    sx = sx0 + k * 19
                    if k < stars:
                        self.r._star(s, sx, y, 7, (255, 220, 120))
                    else:
                        pts = []
                        for j in range(10):
                            a = -math.pi / 2 + j * math.pi / 5
                            rr = 7 if j % 2 == 0 else 3
                            pts.append((sx + rr * math.cos(a), y + rr * math.sin(a)))
                        pygame.draw.polygon(s, (132, 151, 132), pts, 1)
        options = self.r.font_s.render('T - Story scenes: ' + ('on' if self.progress.get('story_scenes', True) else 'off') + '          O - Replay story', True, (235, 219, 174))
        s.blit(options, options.get_rect(center=(480, 663)))
        hint = self.r.font_s.render('mouse / arrows + enter - h help - esc quits', True, (190, 202, 187))
        s.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 26)))
        self._save_notice()
        self.r.present()

    @staticmethod
    def _won_lines(g):
        return [f'score {g.score:,}', 'enter - next board    r - replay    m - menu']

    @staticmethod
    def _lost_lines(g):
        left = g.oranges_left()
        return [f"{left} orange peg{('s' if left != 1 else '')} still standing", f'score {g.score:,}', 'r - try again    m - menu']

    def _companion_y(self, i):
        return 290 + i * 62

    def _companion_hit(self, pos):
        (x, y) = pos
        if abs(x - SCREEN_W // 2) >= 330:
            return None
        for i in range(len(COMPANIONS)):
            cy = self._companion_y(i)
            up = (cy - self._companion_y(i - 1)) / 2 if i else 26
            dn = (self._companion_y(i + 1) - cy) / 2 if i < len(COMPANIONS) - 1 else 26
            if -up <= y - cy < dn:
                return i
        return None

    def _companion_step(self, dt):
        self.r.side_active = False
        for e in self._screen_events('companion'):
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if self._common_key(e):
                    continue
                if e.key == pygame.K_ESCAPE:
                    self.mode = 'menu'
                elif e.key in (pygame.K_UP, pygame.K_w):
                    self.comp_sel = (self.comp_sel - 1) % len(COMPANIONS)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.comp_sel = (self.comp_sel + 1) % len(COMPANIONS)
                elif e.key == pygame.K_v:
                    self._toggle_mute()
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.companion = self.comp_sel
                    self._save_pref('companion', self.companion)
                    self._launch_selected()
            elif e.type == pygame.MOUSEMOTION:
                idx = self._companion_hit(self.r.to_logical(e.pos))
                if idx is not None:
                    self.comp_sel = idx
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                idx = self._companion_hit(self.r.to_logical(e.pos))
                if idx is not None:
                    self.companion = idx
                    self._save_pref('companion', self.companion)
                    self._launch_selected()
        s = self.r.screen
        s.blit(self.r.backgrounds[9], (0, 0))
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((31, 49, 46, 212))
        s.blit(veil, (0, 0))
        self._twinkle(s)
        lv = self.levels[self.menu_sel]
        t = self.r.font_l.render('Choose your companion', True, (255, 220, 120))
        s.blit(t, t.get_rect(center=(SCREEN_W // 2, 120)))
        sub = self.r.font_m.render(f'{self.menu_sel + 1}. {narrative.title(self.menu_sel, lv.name)}', True, (235, 240, 224))
        s.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 190)))
        for (i, (name, power, blurb)) in enumerate(COMPANIONS):
            cy = self._companion_y(i)
            sel = i == self.comp_sel
            col = (255, 220, 120) if sel else (190, 195, 230)
            if sel:
                pygame.draw.circle(s, (255, 220, 120), (SCREEN_W // 2 - 310, cy), 5)
            nm = self.r.font_m.render(name, True, col)
            s.blit(nm, nm.get_rect(midleft=(SCREEN_W // 2 - 290, cy)))
            bl = self.r.font_s.render(blurb, True, (230, 235, 250) if sel else (150, 158, 200))
            s.blit(bl, bl.get_rect(midleft=(SCREEN_W // 2 - 290, cy + 24)))
        hint = self.r.font_s.render('up/down - choose    enter - start    esc - back    v - mute', True, (215, 225, 215))
        s.blit(hint, hint.get_rect(center=(SCREEN_W // 2, 664)))
        self._save_notice()
        self.r.present()

    def _story_seen(self, scene):
        return bool(self.progress.get('story_seen_' + scene, False))

    def _launch_selected(self):
        if self.menu_sel == 0 and (not self._story_seen('opening')) and (not self.progress.get('best', {}).get('0')):
            if self.progress.get('story_scenes', True):
                self._begin_story('opening', 0)
                return
            self._save_pref('story_seen_opening', True)
        self._start_level(self.menu_sel)

    def _continue_story_or_level(self):
        scene = {19: 'farm', 39: 'village'}.get(self.menu_sel)
        target = self.menu_sel + 1
        if scene and (not self._story_seen(scene)):
            if self.progress.get('story_scenes', True):
                self._begin_story(scene, target)
                return
            self._save_pref('story_seen_' + scene, True)
        self._start_level(target)

    def _begin_story(self, scene, target=None, replay=False):
        self._story_scene = scene
        self._story_t = 0.0
        self._story_target = target
        self._story_replay = replay
        self._story_blocked = {k for k in (pygame.K_RETURN, pygame.K_ESCAPE) if pygame.key.get_pressed()[k]}
        self.mode = 'story'
        if not replay:
            self._save_pref('story_seen_' + scene, True)

    def _finish_story(self):
        if self._story_replay:
            self.mode = 'story_menu'
        elif self._story_target is not None:
            self._start_level(self._story_target)
        else:
            self.mode = 'menu'

    def _story_step(self, dt):
        self.r.side_active = False
        for e in self._screen_events('story'):
            if e.type == pygame.KEYUP:
                self._story_blocked.discard(e.key)
            elif e.type == pygame.KEYDOWN:
                if self._common_key(e):
                    continue
                if e.key == pygame.K_v:
                    self._toggle_mute()
                elif e.key in (pygame.K_RETURN, pygame.K_ESCAPE) and e.key not in self._story_blocked and (not getattr(e, 'repeat', False)):
                    self._finish_story()
                    return
        if not self.running:
            return
        self._story_t += dt
        if self._story_t >= story_scenes.DURATIONS[self._story_scene]:
            self._finish_story()
            return
        story_scenes.draw(self.r.screen, self._story_scene, self._story_t, self.r.font_m, self.r.font_s)
        self._save_notice()
        self.r.present()

    def _story_menu_step(self, dt):
        self.r.side_active = False
        scenes = ('opening', 'farm', 'village', 'ending')
        for e in self._screen_events('story_menu'):
            if e.type == pygame.KEYDOWN:
                if self._common_key(e):
                    continue
                if e.key in (pygame.K_ESCAPE, pygame.K_o):
                    self.mode = 'menu'
                    return
                if e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self._begin_story(scenes[e.key - pygame.K_1], replay=True)
                    return
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                (x, y) = self.r.to_logical(e.pos)
                idx = round((y - 280) / 72)
                if 180 < x < 780 and 0 <= idx < 4 and (abs(y - (280 + 72 * idx)) < 27):
                    self._begin_story(scenes[idx], replay=True)
                    return
        self.r.screen.fill((37, 62, 57))
        self.r.caption('Replay story', (480, 150))
        for (i, label) in enumerate(('1 - The first customer', '2 - The farm', '3 - The village years', '4 - Closing time')):
            self.r.caption(label, (480, 280 + i * 72))
        self.r.caption('Esc - menu. Replays change no progress.', (480, 650))
        self.r.present()

    def _begin_ending(self):
        unseen = not self._story_seen('ending')
        self._story_ending_show = unseen and self.progress.get('story_scenes', True)
        self._finale_time = 0.0 if self._story_ending_show else finale.CREDITS_START
        self._ending_blocked = {k for k in (pygame.K_RETURN, pygame.K_ESCAPE) if pygame.key.get_pressed()[k]}
        self._save_pref('story_seen_ending', True)
        self.mode = 'ending'

    def _ending_step(self, dt):
        self.r.side_active = False
        for e in self._screen_events('ending'):
            if e.type == pygame.QUIT:
                self.running = False
                return
            elif e.type == pygame.KEYUP:
                getattr(self, '_ending_blocked', set()).discard(e.key)
            elif e.type == pygame.KEYDOWN:
                if e.key in getattr(self, '_ending_blocked', set()) or getattr(e, 'repeat', False):
                    continue
                if self._common_key(e):
                    continue
                if e.key == pygame.K_m:
                    self.mode = 'menu'
                    return
                elif e.key == pygame.K_v:
                    self._toggle_mute()
                elif e.key == pygame.K_r:
                    self._start_level(59)
                    return
                elif e.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    if getattr(self, '_finale_time', 0) < finale.END_TIME:
                        self._finale_time = finale.END_TIME
                    else:
                        if e.key == pygame.K_ESCAPE:
                            self.mode = 'menu'
                        else:
                            self._start_level(59)
                        return
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if getattr(self, '_finale_time', 0) < finale.END_TIME:
                    self._finale_time = finale.END_TIME
                else:
                    self.mode = 'menu'
                    return
        previous = getattr(self, '_finale_time', 0)
        self._finale_time = previous + dt
        for beat in (6.0,):
            if previous < beat <= self._finale_time:
                audio.pawl_seat()
        self._draw_finale()
        self._save_notice()
        self.r.present()

    def _draw_finale(self):
        finale.draw(self.r.screen, self._finale_time, self.r.font_m, show_story=getattr(self, '_story_ending_show', False), small=self.r.font_s)
        if not getattr(self, '_story_ending_show', False) and getattr(self, '_closing_board', None) is not None and (self._finale_time < 1.5):
            old = self._closing_board.copy()
            old.set_alpha(round(255 * (1 - finale.a.ease(self._finale_time / 1.5))))
            self.r.screen.blit(old, (0, 0))

    def _start_level(self, idx):
        self.menu_sel = idx
        self.game = Game(self.levels[idx], level_index=idx, save_path=None if self._migration_source else self.save, seed=None, chosen_power=COMPANIONS[self.companion][1])
        self._farm_grin_shown = False
        self._finale_time = 0.0
        self._closing_board = None
        self._rail_aim = self.game.aim
        self._guide_preview = GuidePreview()
        self.intro_t = 2.8
        self._won_hold = 0.0
        self._lost_hold = 0.0
        self.mode = 'play'

    def _play_step(self, dt):
        self.r.side_active = True
        g = self.game
        for e in self._screen_events('play'):
            if e.type == pygame.QUIT:
                self.running = False
                return
            elif e.type == pygame.KEYDOWN:
                if self._common_key(e):
                    continue
                if e.key == pygame.K_ESCAPE:
                    self.mode = 'pause'
                    self._pause_step(0)
                    return
                elif e.key == pygame.K_v:
                    self._toggle_mute()
                elif e.key in (pygame.K_SPACE,) and g.can_fire() and (self.intro_t > 0) and (g.state == 'aim'):
                    self.intro_t = 0.0
                    break
                elif e.key in (pygame.K_SPACE,) and g.can_fire():
                    g.fire()
                elif e.key in (pygame.K_RETURN, pygame.K_r, pygame.K_m) and g.state == 'won' and (self._won_hold > 0):
                    self._won_hold = 0.0
                    break
                elif e.key in (pygame.K_RETURN, pygame.K_r, pygame.K_m) and g.state == 'lost' and (self._lost_hold > 0):
                    self._lost_hold = 0.0
                    break
                elif e.key == pygame.K_r and g.state in ('won', 'lost'):
                    self._start_level(self.menu_sel)
                elif e.key in (pygame.K_RETURN,) and g.state == 'won':
                    if self.menu_sel == len(self.levels) - 1:
                        self._save_pref('completed', True)
                        self._begin_ending()
                    else:
                        self._continue_story_or_level()
                        return
                elif e.key == pygame.K_m and g.state in ('won', 'lost'):
                    self.mode = 'menu'
            elif e.type == pygame.MOUSEMOTION:
                pos = self.r.to_logical(e.pos)
                if g.state == 'aim' and 0 <= pos[0] < SCREEN_W and (0 <= pos[1] < SCREEN_H):
                    g.aim_at(*pos)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                pos = self.r.to_logical(e.pos)
                if not (0 <= pos[0] < SCREEN_W and 0 <= pos[1] < SCREEN_H):
                    continue
                if g.can_fire() and self.intro_t > 0 and (g.state == 'aim'):
                    self.intro_t = 0.0
                    break
                elif g.can_fire():
                    g.fire()
        if self.mode != 'play':
            return
        g = self.game
        keys = pygame.key.get_pressed()
        fine = 0.25 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            g.aim = g.clamp_aim(g.aim - 1.6 * fine * dt)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            g.aim = g.clamp_aim(g.aim + 1.6 * fine * dt)
        g.step(dt)
        self._handle_game_events()
        self.r.particles.step(dt)
        self.r.popups.step(dt)
        self.r.step_confetti(dt, g.state == 'fever')
        guide = None
        if g.state == 'aim' and (g.guide_shots > 0 or g.pending_power == 'guide'):
            guide = self._guide_preview.points(g, LAUNCH_X, LAUNCH_Y)
        lost_pulse = 1.0 - self._lost_hold / LOST_SPLASH_HOLD if g.state == 'lost' and self._lost_hold > 0 else None
        if abs(g.aim - getattr(self, '_rail_aim', g.aim)) > 0.14:
            audio.rail_step()
            self._rail_aim = g.aim
        self.r.draw_board(g, self.menu_sel, guide, dt=dt, lost_pulse=lost_pulse)
        if self.menu_sel == 59 and g.state == 'won':
            self._finale_time += dt
        audio.scene_step(self.menu_sel, self.r._scene_elapsed)
        if self.menu_sel == 0 and g.state == 'aim' and (g.shots_fired == 0) and (not self.progress.get('best', {}).get('0')):
            fh = self.r.font_s.render('arrows / mouse to aim - space or click to launch', True, (38, 59, 55))
            self.r.caption('Aim with mouse or arrows. Click or space to launch.', (480, SCREEN_H - 56))
        if self.intro_t > 0 and g.state == 'aim':
            self.intro_t -= dt
            lv = self.levels[self.menu_sel]
            dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dim.fill((4, 6, 16, 120))
            self.r.screen.blit(dim, (0, 0))
            title = f'Board {self.menu_sel + 1}'
            t = self.r.font_xl.render(title, True, (255, 240, 195))
            self.r.screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 300)))
        if g.state == 'won':
            if self._won_hold > 0:
                self._won_hold -= dt
            elif self.menu_sel == 59:
                if not self.progress.get('completed', False):
                    self._save_pref('completed', True)
                self._closing_board = self.r.screen.copy()
                self._begin_ending()
                self._draw_finale()
            else:
                self.r.draw_life_reward(g, self.menu_sel, self.progress)
        elif g.state == 'lost':
            if self._lost_hold > 0:
                self._lost_hold -= dt
            else:
                self.r.overlay('OUT OF BALLS', self._lost_lines(g), (250, 120, 120), peek=[(p.x, p.y) for p in g.pegs if p.alive and p.kind == ORANGE])
        self._save_notice()
        self.r.present()

    def _pause_step(self, dt):
        self.r.side_active = True
        for e in self._screen_events('pause'):
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if self._common_key(e):
                    continue
                if e.key == pygame.K_ESCAPE:
                    self.mode = 'play'
                elif e.key == pygame.K_v:
                    self._toggle_mute()
                elif e.key == pygame.K_m:
                    self.mode = 'menu'
                elif e.key == pygame.K_r:
                    self._start_level(self.menu_sel)
        self.r.draw_board(self.game, self.menu_sel, dt=0)
        self.r.overlay('PAUSED', ['esc - resume    r - restart    m - menu    v - mute'])
        self._save_notice()
        self.r.present()

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(120) / 1000.0, 0.05)
                self._sync_music()
                if self.mode == 'menu':
                    self._menu_step(dt)
                elif self.mode == 'help':
                    self._help_step(dt)
                elif self.mode == 'companion':
                    self._companion_step(dt)
                elif self.mode == 'story':
                    self._story_step(dt)
                elif self.mode == 'story_menu':
                    self._story_menu_step(dt)
                elif self.mode == 'ending':
                    self._ending_step(dt)
                elif self.mode == 'play':
                    self._play_step(dt)
                else:
                    self._pause_step(dt)
        finally:
            try:
                audio.shutdown()
            finally:
                pygame.quit()

def main(argv=None):
    if sys.argv[1:] if argv is None else argv:
        return 2
    App().run()
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
