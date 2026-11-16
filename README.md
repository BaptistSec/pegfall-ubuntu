# PEGFALL 0.20.0

A sixty-board peg-bouncing arcade campaign following The Brass Lantern from a country lane to a city attraction. Clear every orange peg, earn stars and unlock the next board. Green pegs grant companion powers; bucket catches return a ball. The campaign's wordless scenes follow the people around the attraction across the years.

## Play

Extract the whole archive to a new folder. On Ubuntu x86-64, run `./pegfall`. On Windows x64, open `pegfall.exe`. No Python installation is needed. Do not run inside the ZIP or merge folders from older versions. The Windows application is unsigned and may show the usual Windows warning.

## Controls

- Mouse or Left/Right / A-D: aim. Hold Shift for fine keyboard aim.
- Space or left click: fire. A first press during the brief board intro dismisses it without firing.
- Esc: pause/resume. R from pause/results: restart. M: menu.
- Enter after a clear: next board. R: replay. M: menu.
- Menus: arrows and Enter, or mouse. PageUp/PageDown changes board page. H: help.
- V: mute. Minus/equal: master volume. F11: fullscreen/windowed.
- T from menu: story scenes on/off. O: replay story scenes.

## Progress and saves

Your first game starts at board 1 and unlocks boards through earned clears. Clear every orange before running out of balls. One star is enough to progress. Replays never lower recorded bests. All 60 clears lead to the ending.

For compatibility, this version keeps the `pegfall-rc1` save location. Back up your progress before replacing an earlier version:
- Ubuntu: `$XDG_DATA_HOME/pegfall-rc1/progress.json`, or `~/.local/share/pegfall-rc1/progress.json`.
- Windows: `%LOCALAPPDATA%\pegfall-rc1\progress.json`, with APPDATA fallback.

Earlier stable releases use a separate save location. Progress is saved after completed clears and option changes, not mid-shot. If a save warning appears, press S to retry. Pending unsaved records do not survive quitting. Do not edit progress while the game is open.

## Source and licences

Game code, art and audio: MIT, Copyright(c)2026 BaptistSec. See LICENSE. Included runtime components and font have their own licences and copyrights in THIRD_PARTY. Corresponding source and rebuild instructions are in Pegfall-0.20.0-source.zip, with exact dependency sources in Pegfall-0.20.0-dependency-sources.tar.gz, alongside this release.

