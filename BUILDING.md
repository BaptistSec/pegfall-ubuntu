# Build Pegfall

Use Python 3.10 x86-64 on the target operating system. Install the packages in requirements-build.txt in a virtual environment, then run:

    python -m PyInstaller --clean --noconfirm pegfall.spec

The executable is written to dist/. The build includes the game assets and Liberation Sans font. Keep LICENSE and the platform notices from release-notices/ with any binary distribution. Exact component sources accompany the download. Components covered by the LGPL may be modified or replaced when rebuilding.
