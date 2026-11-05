# Pegfall

An original peg-bouncing arcade game. Aim, fire, and watch the ball
carom through a night sky of glowing pegs. Clear every orange peg to
win the board; catch the ball in the roaming bucket for a free shot;
hit the last orange and ride the slow-motion fever into the bonus wells.

Pegfall is its own game: original code, levels, art direction and sound.
It shares only a genre with other peg-bouncing games.

## Download

Use Releases for the Ubuntu game, complete project source, third-party source
companion and checksums. The project source includes the full build recipe,
font and notices. GitHub's automatic source archives contain this download
page only; choose the named project-source ZIP instead.

## Play it (no installation, no Python needed)

Download the Linux archive from this repository's Releases page, then:

    tar xzf pegfall-*-linux.tar.gz
    cd pegfall-*
    ./pegfall

That is the whole setup: one self-contained binary. Progress saves itself
under your user data directory and is there next time you play.

The game itself is original (LICENSE). The frozen binary also bundles
its runtime (Python, pygame-ce, SDL2, codecs, a font) - every component
with its license is listed in THIRD_PARTY/THIRD_PARTY_NOTICES.md, with
corresponding-source directions in THIRD_PARTY/SOURCES.md.

## Features

- 25 handcrafted boards, from a gentle sunrise arc to the Zenith finale,
  ending in a full campaign finale
- Choose your companion before every board: Sprocket (guided aim),
  Comet (ploughs through pegs), Gemini (two balls), Nova (cluster blasts),
  or Rotator to cycle all four powers - green pegs grant its power
- Real physics on a fixed 120 Hz timestep: identical bounces on any display
  refresh rate, gravity, wall caroms, dead-centre rescue nudges
- Four peg powers: **guide** (predicted path), **comet** (plough through pegs),
  **multiball**, **burst** (first touch detonates a peg cluster)
- A purple peg worth 5x a blue one - it moves after every shot
- Golden bumpers that kick the ball back fast: bank shots off them to
  reach pegs a straight fall cannot
- Style bonuses: long shots pay extra; chained hits build score multipliers
- Score multiplier ladder (x1 to x10) and a slow-motion fever finish with 50k bonus wells
- Free balls via the moving bucket; per-board best scores, 3-star ratings and unlock progress
- Original game art and sound are generated in code. The interface uses the
  bundled Liberation Sans Bold font under SIL OFL 1.1; its notice is included.
- Headless self-test and QA frame captures for CI

## Run from source

```
pip install -r requirements.txt
python -m pegfall
```

## Controls

- Fully playable keyboard-only: menus = arrow keys (Left/Right hop columns) + Enter, Esc back
- Mouse: aim, click to fire
- Arrow keys / A-D: aim; hold Shift for fine aim
- Space: fire
- H: help screen (from the menu)
- Esc: pause / back; V: mute on/off (remembered)
- R: restart the board (from pause or the win/lose screen), Enter: next board (after a clear), M: menu

## Development

```
python -m pegfall --selftest                 # headless smoke test (exit 0/1)
python -m unittest discover -s tests         # full test suite
python -m pegfall --shot frame.png --level 3 --ticks 160   # headless frame capture
```

## Build a standalone binary (Ubuntu)

```
pip install -r requirements.txt pyinstaller==6.22.3
pyinstaller pegfall.spec
mkdir -p package/pegfall-0.16.0
cp dist/pegfall README.md LICENSE package/pegfall-0.16.0/
cp -R THIRD_PARTY package/pegfall-0.16.0/
tar -czf pegfall-0.16.0-linux.tar.gz -C package pegfall-0.16.0
tar -xzf pegfall-0.16.0-linux.tar.gz
cd pegfall-0.16.0 && ./pegfall
```

Progress (unlocks, best scores, stars) lives in
`$XDG_DATA_HOME/pegfall/progress.json` (default `~/.local/share/pegfall/`),
so it survives deleting or replacing the game itself. Saves from pre-0.3
locations (beside the executable, `~/.pegfall/`) are migrated on first run.

## Licence

Pegfall game code, levels, original art and audio are MIT - see LICENSE.
Liberation Sans Bold 2.1.5 is a third-party font under SIL OFL 1.1; see
pegfall/assets/fonts/OFL-1.1.txt and THIRD_PARTY/THIRD_PARTY_NOTICES.md.
The standalone binary bundles additional runtime components under their own
licenses. Their notices and corresponding-source directions are in THIRD_PARTY/.

## Verification limits

Keyboard menus, aiming, firing, pause, scoring, board clear, progression,
loss and restart were checked on the Ubuntu binary with scripted keyboard
input. This is not a human playtest or an audible-audio check. Full campaigns
and every hardware configuration have not been tested.
