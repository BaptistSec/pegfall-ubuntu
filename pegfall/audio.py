from __future__ import annotations
import array
import math
import threading
_mix_lock = threading.RLock()
_audio_gen = 0
_cache: dict[int, object] = {}
_enabled = False
_pg = None
_vol = 1.0
_source_channel_gains = {}
SR = 22050
SCALE = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24]
BASE_HZ = 440.0

def init():
    global _enabled, _pg, SR
    global _atexit_registered
    try:
        import pygame
        pygame.mixer.pre_init(SR, -16, 2, 256)
        pygame.mixer.init()
        got = pygame.mixer.get_init()
        if got:
            SR = got[0]
        _cache.clear()
        _pg = pygame
        _enabled = True
        _stop.clear()
        if not _atexit_registered:
            import atexit
            atexit.register(shutdown)
            _atexit_registered = True
    except Exception:
        _enabled = False

def _tone(hz: float, dur: float, vol: float=0.5, kind: str='sine'):
    if _stop.is_set() or _pg is None:
        return None
    got = _pg.mixer.get_init()
    if not got:
        return None
    key = (int(hz), int(dur * 1000), int(vol * 100), kind)
    if key in _cache:
        return _cache[key]
    n = int(SR * dur)
    decay = 6.0 if dur < 0.3 else 4.0
    ch = got[2]
    pcm = array.array('h', bytes(2 * n * ch))
    grain = 0.0
    seed = 1729
    for i in range(n):
        t = i / SR
        if kind == 'sine':
            w = math.sin(2 * math.pi * hz * t)
        elif kind == 'tri':
            w = 2 * abs(2 * (hz * t % 1) - 1) - 1
        elif kind == 'pad':
            w = math.sin(2 * math.pi * hz * t) + 0.4 * math.sin(2 * math.pi * hz * 1.5 * t)
            attack = min(1.0, t / max(dur / 3.0, 1e-06))
            w *= 0.5 - 0.5 * math.cos(math.pi * attack)
        else:
            w = math.sin(2 * math.pi * hz * t) + 0.4 * math.sin(2 * math.pi * hz * 1.5 * t)
        edge = min(1.0, t / 0.009) * min(1.0, (dur - t) / 0.025)
        if kind == 'mechanical':
            body = math.sin(2 * math.pi * (91 * t + 20 * (1 - math.exp(-t * 35)) / 35))
            latch = (math.sin(2 * math.pi * 1147 * t) + 0.5 * math.sin(2 * math.pi * 1693 * t)) * math.exp(-t * 95)
            spring = 0.13 * math.sin(2 * math.pi * 293 * t) * math.exp(-t * 24)
            if t > 0.07:
                spring += 0.11 * math.sin(2 * math.pi * 173 * (t - 0.07)) * math.exp(-(t - 0.07) * 48)
            w = 0.65 * body * math.exp(-t * 19) + 0.2 * latch + spring
            edge = min(1.0, t / 0.002) * min(1.0, (dur - t) / 0.025)
            decay = 0
        if kind in ('worn_peg', 'worn_objective', 'final_iron', 'bucket_iron', 'settled_iron'):
            seed = 1664525 * seed + 1013904223 & 4294967295
            noise = seed / 2147483648.0 - 1.0
            grain += 0.12 * (noise - grain)
            phase = 2 * math.pi * hz * t
            body = 0.72 * math.sin(phase) * math.exp(-t * 8) + 0.17 * math.sin(phase * 1.43) * math.exp(-t * 13) + 0.08 * math.sin(phase * 2.17) * math.exp(-t * 24)
            grit = grain * (0.55 * math.exp(-t * 28) + 0.16 * math.exp(-t * 6))
            if kind == 'worn_objective':
                body += 0.16 * math.sin(phase * 0.5) * math.exp(-t * 6)
            elif kind == 'final_iron':
                body += 0.28 * math.sin(phase * 0.5) * math.exp(-t * 3.8)
                grit += grain * 0.17 * math.exp(-t * 3)
            elif kind in ('bucket_iron', 'settled_iron'):
                for (at, gain) in ((0.055, 0.22), (0.125, 0.12)):
                    if t >= at:
                        u = t - at
                        body += gain * math.sin(2 * math.pi * hz * 1.79 * u) * math.exp(-u * 35)
                body += 0.34 * math.sin(phase * 0.48) * math.exp(-t * 5)
            w = math.tanh((body + grit) * 1.9) / 1.9
            edge = min(1.0, t / 0.003) * min(1.0, (dur - t) / 0.045)
            decay = 0
        if kind in ('doorbell', 'porcelain', 'cartwheel'):
            if kind == 'doorbell':
                w = (math.sin(2 * math.pi * hz * t) + 0.28 * math.sin(2 * math.pi * hz * 2.71 * t)) * math.exp(-t * 12)
            elif kind == 'porcelain':
                w = (0.6 * math.sin(2 * math.pi * hz * t) + 0.22 * math.sin(2 * math.pi * hz * 1.83 * t)) * math.exp(-t * 65)
            else:
                seed = 1664525 * seed + 1013904223 & 4294967295
                grain += 0.035 * (seed / 2147483648.0 - 1 - grain)
                roll = math.sin(math.pi * t / dur) ** 2
                w = roll * (grain * 0.9 + 0.12 * math.sin(2 * math.pi * hz * t))
            decay = 0
        s = int(max(-0.98, min(0.98, w * math.exp(-t * decay) * vol * edge)) * 32767)
        for c in range(ch):
            pcm[i * ch + c] = s
    try:
        snd = _pg.mixer.Sound(buffer=pcm.tobytes())
    except _pg.error:
        return None
    _cache[key] = snd
    return snd

def prewarm_effects():
    if not _enabled:
        return
    specs = [(105, 0.28, 0.65, 'mechanical'), (98, 0.65, 0.58, 'bucket_iron'), (760, 0.32, 0.29, 'chime'), (180, 0.25, 0.3, 'tri'), (110, 1.05, 0.58, 'final_iron'), (82.41, 0.85, 0.6, 'bucket_iron'), (180, 0.7, 0.4, 'tri'), (67, 0.1, 0.19, 'bucket_iron'), (96, 0.065, 0.13, 'bucket_iron')]
    for semis in SCALE:
        specs.append((147 * 2 ** (semis / 48), 0.32, 0.47, 'worn_peg'))
        specs.append((123.47 * 2 ** (semis / 48), 0.45, 0.51, 'worn_objective'))
    for semis in (0, -5):
        specs.append((73.42 * 2 ** (semis / 12), 0.65, 0.23, 'settled_iron'))
    for spec in specs:
        if _stop.is_set():
            return
        try:
            _tone(*spec)
        except Exception:
            return

def _play(snd):
    if _stop.is_set():
        return
    with _mix_lock:
        if _enabled and snd is not None:
            try:
                snd.set_volume(_vol)
                snd.play()
            except Exception:
                pass

def set_volume(v: float):
    global _vol
    with _mix_lock:
        _vol = min(1.0, max(0.0, float(v)))
        if _pg is not None:
            try:
                _pg.mixer.music.set_volume(_vol * 0.6)
                _pg.mixer.Channel(0).set_volume(_vol * 0.55 * _environment_gain)
                _pg.mixer.Channel(1).set_volume(_vol * 0.6)
            except Exception:
                pass
            for channel in (2, 3, 4):
                gains = _source_channel_gains.get(channel, (0, 0))
                try:
                    _pg.mixer.Channel(channel).set_volume(*gains)
                    _pg.mixer.Channel(channel).set_volume(_vol)
                except Exception:
                    pass
        for (key, snd) in list(_cache.items()):
            try:
                snd.set_volume(1.0 if key[-1] in ('doorbell', 'porcelain', 'cartwheel') else _vol)
            except Exception:
                pass

def set_enabled(flag: bool):
    global _enabled, _audio_gen
    with _mix_lock:
        _enabled = bool(flag) and _pg is not None
        if not _enabled:
            _audio_gen += 1
            music_stop()
            try:
                if _pg is not None:
                    _pg.mixer.stop()
                    _pg.mixer.music.stop()
            except Exception:
                pass

def plink(chain: int):
    if not _enabled:
        return
    semis = SCALE[min(chain - 1, len(SCALE) - 1)]
    _play(_tone(147 * 2 ** (semis / 48), 0.32, 0.47, 'worn_peg'))

def plink_orange(chain: int):
    if not _enabled:
        return
    semis = SCALE[min(chain - 1, len(SCALE) - 1)]
    _play(_tone(123.47 * 2 ** (semis / 48), 0.45, 0.51, 'worn_objective'))

def fire():
    if _enabled:
        _play(_tone(105, 0.28, 0.65, 'mechanical'))

def free_ball():
    if _enabled:
        _play(_tone(98, 0.65, 0.58, 'bucket_iron'))

def power():
    if _enabled:
        _play(_tone(760, 0.32, 0.29, 'chime'))

def stall():
    if _enabled:
        _play(_tone(180, 0.25, 0.3, 'tri'))
_stop = threading.Event()
_threads: list = []
_atexit_registered = False

def _jingle(semis, gap, base, dur, vol, kind):
    if not _enabled:
        return
    gen = _audio_gen

    def run():
        for s in semis:
            if _stop.is_set() or gen != _audio_gen:
                return
            snd = _tone(base * 2 ** (s / 12), dur, vol, kind)
            with _mix_lock:
                if gen != _audio_gen or _stop.is_set():
                    return
                _play(snd)
            if _stop.wait(gap):
                return
    th = threading.Thread(target=run, daemon=True)
    _threads[:] = [worker for worker in _threads if worker.is_alive()]
    _threads.append(th)
    th.start()

def shutdown():
    _stop.set()
    music_stop()
    for th in list(_threads):
        th.join(timeout=1.0)
    _threads.clear()
    try:
        if _pg is not None:
            _pg.mixer.music.stop()
    except Exception:
        pass

def fever():
    if _enabled:
        _play(_tone(110, 1.05, 0.58, 'final_iron'))

def points_bucket():
    if _enabled:
        _play(_tone(82.41, 0.85, 0.6, 'bucket_iron'))

def won():
    _jingle((0, -5), 0.24, 73.42, 0.65, 0.23, 'settled_iron')

def lost():
    if _enabled:
        _play(_tone(180, 0.7, 0.4, 'tri'))
_MUSIC = {'menu': 'farm', 'play': 'farm', 'farm': 'farm', 'village': 'village', 'city': 'city'}
for _day in range(1, 21):
    _MUSIC['farm_%02d' % _day] = 'motif-whistle' if _day in (1, 8) else 'motif-quiet' if _day < 5 else 'motif-soft' if _day < 10 else 'motif-warm'
for _day in range(21, 41):
    _MUSIC['village_%02d' % _day] = 'village-festival' if _day == 33 else 'village-early' if _day < 30 or _day == 40 else 'village-mid' if _day < 35 else 'village-late'
for _day in range(41, 61):
    _MUSIC['city_%02d' % _day] = 'city-solo' if _day < 50 else 'city-spaced'
_MUSIC['finale'] = 'motif-warm'
_MUSIC['menu'] = 'motif-warm'
from .campaign_life import day as _campaign_day
for _day in range(1, 61):
    _prefix = 'farm' if _day <= 20 else 'village' if _day <= 40 else 'city'
    _MUSIC['%s_%02d' % (_prefix, _day)] = _campaign_day(_day).music
_scene_kind = None
_environment_sounds = {}
_environment_normal = None
_environment_uniform = False
_environment_gain = 1.0

def environment_asset(kind):
    if kind.startswith('farm_'):
        day = int(kind[-2:])
        return 'farm-rain' if day == 4 else 'farm-air-evening' if day == 9 else 'farm-air'
    if kind.startswith('village_'):
        day = int(kind[-2:])
        return 'farm-rain' if day == 37 else 'village-market' if day in (28, 40) else 'village-air'
    if kind.startswith('city_'):
        day = int(kind[-2:])
        return 'city-saturday' if day in (45, 49, 59, 60) else 'city-still' if day == 57 else 'city-air'
    if kind == 'finale':
        return 'city-air'
    return None
_campaign_previous = None

def scene_step(index, elapsed):
    global _campaign_previous
    from . import campaign_life
    level = index + 1
    if _scene_kind not in ('farm_%02d' % level, 'village_%02d' % level, 'city_%02d' % level):
        return
    previous = _campaign_previous
    _campaign_previous = (index, elapsed)
    if not _enabled or _pg is None:
        return
    d = campaign_life.day(level)
    try:
        _pg.mixer.music.set_volume(_vol * (0.6 - 0.12 * d.perspective))
        _pg.mixer.Channel(0).set_volume(_vol * 0.55)
        if previous is None or previous[0] != index or elapsed < previous[1]:
            return
        for (at, name) in campaign_life.schedule(level):
            if previous[1] < at <= elapsed:
                channel = {'door': 2, 'cup': 3, 'wheel': 4}[name]
                (hz, duration, kind) = {'door': (392, 0.38, 'doorbell'), 'cup': (640, 0.11, 'porcelain'), 'wheel': (68, 1.35, 'cartwheel')}[name]
                snd = _tone(hz, duration, 0.22, kind)
                if snd is not None:
                    base = {'door': 0.16, 'cup': 0.065, 'wheel': 0.09}[name]
                    gain = base + (0.18 - base) * d.perspective
                    c = _pg.mixer.Channel(channel)
                    position = {'door': 0.9, 'cup': 0.65, 'wheel': -0.85}[name] * (1 - d.perspective)
                    gains = (gain * (1 - max(0, position) * 0.7), gain * (1 - max(0, -position) * 0.7))
                    _source_channel_gains[channel] = gains
                    snd.set_volume(1)
                    c.set_volume(*gains)
                    c.set_volume(_vol)
                    c.play(snd)
    except Exception:
        pass
_music_gen = 0
_music_cancel = None

def music_start(kind, _gap_override=None):
    global _music_cancel, _scene_kind, _environment_normal, _environment_uniform, _environment_gain, _campaign_previous
    with _mix_lock:
        music_stop()
        _scene_kind = kind
        _campaign_previous = None
        _source_channel_gains.clear()
        _environment_gain = 1.0
        _environment_uniform = False
        _environment_sounds.clear()
        _environment_normal = environment_asset(kind)
    gen = _music_gen
    if not _enabled or kind not in _MUSIC:
        return
    cancel = threading.Event()
    _music_cancel = cancel

    def run():
        if cancel.wait(0.36):
            return
        import os
        arrangement = _MUSIC[kind]
        if kind.startswith(('farm_', 'village_', 'city_')):
            from .campaign_life import day
            arrangement = day(int(kind[-2:])).music
        path = os.path.join(os.path.dirname(__file__), 'assets', 'audio', arrangement + '.ogg')
        with _mix_lock:
            if gen != _music_gen or _stop.is_set() or (not _enabled):
                return
            try:
                _pg.mixer.set_num_channels(max(8, _pg.mixer.get_num_channels()))
                _pg.mixer.set_reserved(5)
                env_name = environment_asset(kind)
                if env_name:
                    env_path = os.path.join(os.path.dirname(__file__), 'assets', 'audio', env_name + '.ogg')
                    env = _pg.mixer.Sound(env_path)
                    _environment_sounds[env_name] = env
                    _pg.mixer.Channel(0).set_volume(_vol * 0.55)
                    _pg.mixer.Channel(0).play(env, loops=-1, fade_ms=1200)
                if kind in ('village_23', 'village_27', 'village_30'):
                    whistle = _pg.mixer.Sound(os.path.join(os.path.dirname(__file__), 'assets', 'audio', 'village-whistle.ogg'))
                    _pg.mixer.Channel(1).set_volume(_vol * 0.6)
                    _pg.mixer.Channel(1).play(whistle, loops=-1, fade_ms=1200)
                _pg.mixer.music.load(path)
                _pg.mixer.music.set_volume(_vol * 0.6)
                _pg.mixer.music.play(0 if kind == 'finale' else -1, fade_ms=1200)
                for spec in ((392, 0.38, 0.22, 'doorbell'), (640, 0.11, 0.22, 'porcelain'), (68, 1.35, 0.22, 'cartwheel')):
                    _tone(*spec)
            except Exception:
                return
    th = threading.Thread(target=run, daemon=True)
    _threads[:] = [worker for worker in _threads if worker.is_alive()]
    _threads.append(th)
    th.start()

def music_stop():
    global _music_gen
    _music_gen += 1
    if _music_cancel is not None:
        _music_cancel.set()
    try:
        if _pg is not None:
            _pg.mixer.music.fadeout(350)
            _pg.mixer.Channel(0).fadeout(350)
            _pg.mixer.Channel(1).fadeout(350)
            for channel in (2, 3, 4):
                _pg.mixer.Channel(channel).fadeout(350)
    except Exception:
        pass

def rail_step():
    if _enabled:
        _play(_tone(67, 0.1, 0.19, 'bucket_iron'))

def pawl_seat():
    if _enabled:
        _play(_tone(96, 0.065, 0.13, 'bucket_iron'))
