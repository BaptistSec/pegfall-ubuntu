# Third-party components in the bundled Pegfall binary (Linux)

Pegfall's game code, levels, art and audio are original (see LICENSE).
The bundled Linux binary additionally bundles the runtime below, produced
by PyInstaller 6.22.3 from Python 3.10.12 + pygame-ce 2.5.8. Bundled
shared-library versions are the exact upstream versions pinned by the
pygame-ce 2.5.8 manylinux wheel build
(buildconfig/manylinux-build/docker_base/ at pygame-ce tag 2.5.8);
SONAMEs are listed for cross-checking against the payload. Full license
texts are in ./licenses/.

## LGPL-2.1 components (corresponding source: see SOURCES.md)

| Component | Bundled as | License | Copyright / upstream |
|---|---|---|---|
| pygame-ce 2.5.8 | Python package | LGPL-2.1-or-later | pygame-ce community, https://github.com/pygame-community/pygame-ce |
| FluidSynth 2.5.7 | libfluidsynth.so.3.5.6 | LGPL-2.1-or-later | FluidSynth developers, https://www.fluidsynth.org |
| mpg123 1.33.7 | libmpg123.so.0.49.4 | LGPL-2.1 | mpg123 project, https://www.mpg123.de |
| libsndfile 1.2.2 | libsndfile.so.1.0.37 | LGPL-2.1-or-later | Erik de Castro Lopo, https://libsndfile.github.io |
| libxmp 4.7.2 | libxmp.so.4.7.2 | LGPL-2.1-or-later | libxmp project, https://xmp.sourceforge.net |

Under LGPL-2.1 you may replace these libraries: Pegfall is also
distributed as full source (Pegfall-0.20.0-source.zip) with the build
recipe (requirements-build.txt + BUILDING.md + pegfall.spec), and the exact upstream sources
ship in the companion archive (Pegfall-0.20.0-dependency-sources.tar.gz), so you can
rebuild with your own library builds. See SOURCES.md.

SDL2 uses host audio backends (ALSA, PulseAudio, PipeWire) via dlopen
at runtime when present; those host libraries are NOT bundled in this
binary. PortMidi is likewise not bundled (pygame.midi is not bundled in).

## Permissive components

| Component | License | Copyright / upstream |
|---|---|---|
| Python 3.10.12 runtime (libpython3.10) | PSF-2.0 (licenses/PSF-Python-3.10.txt) | Python Software Foundation |
| SDL2 2.32.10, SDL2_image 2.8.12, SDL2_mixer 2.8.2, SDL2_ttf 2.24.0 | zlib (licenses/SDL2-LICENSE.txt) | Sam Lantinga / SDL contributors |
| OpenSSL 3 (libcrypto) | Apache-2.0 | OpenSSL Project |
| FreeType 2.14.3 (libfreetype.so.6.20.6) | FreeType License (licenses/FTL.txt) | David Turner, Robert Wilhelm, Werner Lemberg |
| HarfBuzz 14.3.0 (libharfbuzz) | MIT (old-style) | HarfBuzz authors |
| Brotli (libbrotlicommon/dec) | MIT | Google |
| libjpeg-turbo (libjpeg.so.62) | IJG + BSD-3-clause | libjpeg-turbo project |
| libpng (libpng16) | libpng/zlib-style | PNG Development Group |
| libtiff (libtiff.so.6) | MIT-like | Sam Leffler / Silicon Graphics |
| FLAC (libFLAC.so.14) | BSD-3-clause | Xiph.Org Foundation |
| libogg, libvorbis(enc/file) | BSD-3-clause | Xiph.Org Foundation |
| libopus, libopusfile | BSD-3-clause | Xiph.Org / Opus authors |
| WavPack (libwavpack.so.1) | BSD-3-clause | David Bryant |
| libwebp, libwebpdemux, libsharpyuv | BSD-3-clause | Google |
| Expat (libexpat.so.1) | MIT | Thai Open Source Software Center / Expat team |
| libmpdec | BSD-2-clause | Stefan Krah |
| liblzma (xz) | public domain | Lasse Collin / Tukaani project |
| bzip2 (libbz2.so.1.0) | bzip2 license (BSD-style) | Julian Seward |
| zlib (libz.so.1) | zlib | Jean-loup Gailly, Mark Adler |
| libgcc_s, libstdc++ | GPL-3.0 (licenses/GPL-3.0.txt) + GCC Runtime Library Exception 3.1 (licenses/GCC-Runtime-Exception-3.1.txt) | Free Software Foundation |
| PyInstaller bootloader | GPL-2.0 with special exception (bundled applications are not covered) | PyInstaller Development Team |

The short permissive licenses above (MIT / BSD / IJG / bzip2 / libpng /
zlib) require retention of their copyright notices, which this file
preserves; full original copyright and licence texts are retained in licenses/upstream-copyrights.

## Font

| Component | License | Source |
|---|---|---|
| Liberation Sans Bold 2.1.5, shipped as pegfall/assets/fonts/LiberationSans-Bold.ttf (sha256 ba0e0dc3f7aca5b0afbc31e800531ee43be3aa79ae35b2ef1f6470a9547765c4) | SIL Open Font License 1.1 (licenses/OFL-1.1.txt) | liberationfonts/liberation-fonts release 2.1.5, https://github.com/liberationfonts/liberation-fonts |

The UI loads this font by explicit path on every render use
(pegfall/render.py _font_path). pygame-ce's bundled FreeSans Bold
(GNU FreeFont r0.4, embedding-exception status not established) is
excluded from the bundled payload by pegfall.spec and is not shipped.

Original upstream notices are also retained under licenses/pygame-upstream/. The actual Liberation font copyright accompanies the OFL text in licenses/Liberation-fonts-copyright.txt. On Ubuntu, system-library copyright files are under licenses/system-copyrights/. Extra upstream notices do not mean every optional codec is bundled.
