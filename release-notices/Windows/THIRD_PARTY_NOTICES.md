# Windows release third-party notices

This document describes the actual Windows executable, not the Linux
runtime. Game code/art/audio: MIT, Copyright (c) 2026 BaptistSec (LICENSE).
Runtime: Python 3.10.11, pygame-ce 2.5.8, SDL 2.32.10, bundled by
PyInstaller 6.22.3. Full licence texts are under licenses/.

## Copyleft components and replacement

- pygame-ce 2.5.8, pygame-ce contributors: LGPL-2.1-or-later.
  Full exact source is in the Windows dependency-source companion.
  https://github.com/pygame-community/pygame-ce/tree/2.5.8
- PyInstaller 6.22.3, PyInstaller Development Team: GPL-2.0 with
  bootloader exception (the bundled game is not thereby GPL).
  Exact source including bootloader is in the same companion.

Game source is provided as Pegfall-0.20.0-source.zip.
Rebuild with Windows Python and chosen replacement libraries as SOURCES.md
explains. No restriction on modifying/replacing LGPL components is imposed.

## Windows libraries

| Component | Payload | Licence/notice |
|---|---|---|
| Python 3.10.11, Python Software Foundation and contributors | python310.dll, extension modules and standard library | Python-3.10.11-Windows-LICENSE.txt, includes third-party and Microsoft distributable-code terms |
| Microsoft Visual C runtime, Microsoft Corporation | VCRUNTIME140.dll, VCRUNTIME140_1.dll | Microsoft distributable-code terms in Python-3.10.11-Windows-LICENSE.txt apply to those components only |
| SDL2 2.32.10, Sam Lantinga/SDL contributors | SDL2.dll | SDL2-LICENSE.txt (zlib) |
| SDL2_image 2.8.12 and contributors | SDL2_image.dll | SDL2-LICENSE.txt (zlib); dependency texts below |
| SDL2_mixer 2.8.2 and contributors | SDL2_mixer.dll | SDL2-LICENSE.txt (zlib); dependency texts below |
| SDL2_ttf 2.24.0 and contributors | SDL2_ttf.dll | SDL2-LICENSE.txt (zlib); FreeType/HarfBuzz notices below |
| FreeType, David Turner, Robert Wilhelm, Werner Lemberg and contributors | freetype.dll plus SDL_ttf's upstream distribution | FTL.txt, copyright and attribution retained; standalone DLL matches pygame's legacy prebuilt with 2.11.1 header |
| HarfBuzz authors | upstream SDL2_ttf text-shaping dependency | HarfBuzz-COPYING.txt (MIT-style) |
| libjpeg-turbo authors | libjpeg-62.dll | LICENSE.libjpegturbo.md (IJG/BSD/zlib terms within) |
| PNG Development Group | libpng16-16.dll, embedded version 1.6.58 | libpng-LICENSE.txt |
| Sam Leffler/Silicon Graphics and libtiff contributors | libtiff-5.dll | LICENSE.tiff.txt |
| Google and WebP contributors | libwebp-7.dll, libwebpdemux-2.dll | LICENSE.webp.txt (BSD) |
| Xiph.Org contributors | libogg-0.dll | LICENSE.ogg-vorbis.txt (BSD) |
| Opus contributors | libopus-0.dll, libopusfile-0.dll | LICENSE.opus.txt, LICENSE.opusfile.txt (BSD) |
| David Bryant/Conifer Software | libwavpack-1.dll | LICENSE.wavpack.txt (BSD) |
| Claudio Matsuoka, Hipolito Carraro Jr and contributors | libxmp.dll, 4.6.3 | LICENSE.xmp.txt (MIT, not the Linux version) |
| Ross Bencina, Phil Burk, Roger B. Dannenberg | portmidi.dll | PortMidi-LICENSE.txt (MIT) |
| OpenSSL Project and contributors | libcrypto-1_1.dll | Python-3.10.11-Windows-LICENSE.txt: bundled OpenSSL 1.1 terms; OpenSSL-3-LICENSE.txt is retained as an extra upstream notice, not substituted for this component |

COMPONENT-HASHES.json lists the bundled component hashes. Python310 and its Windows runtime come from the official Python 3.10.11 embeddable archive; its full license text is retained. Linux-only FluidSynth/mpg123/libsndfile and .so notices are not substituted for Windows. Additional license texts from the SDL distributions are retained, including optional components not necessarily bundled.

## Font

Liberation Sans Bold 2.1.5, Liberation Fonts contributors, SIL OFL 1.1:
licenses/OFL-1.1.txt. Font SHA256:
ba0e0dc3f7aca5b0afbc31e800531ee43be3aa79ae35b2ef1f6470a9547765c4
https://github.com/liberationfonts/liberation-fonts
The bundled pygame FreeSans is excluded; the game uses Liberation by path.

Original upstream notices are also retained under licenses/pygame-upstream/. The actual Liberation font copyright accompanies the OFL text in licenses/Liberation-fonts-copyright.txt. On Ubuntu, system-library copyright files are under licenses/system-copyrights/. Extra upstream notices do not mean every optional codec is bundled.
