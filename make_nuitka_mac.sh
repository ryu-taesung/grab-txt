#!/bin/sh
python3 -c 'import get_git_version_tag; get_git_version_tag.write_git_version_tag()'
python3 -m nuitka --macos-create-app-bundle --standalone --onefile --enable-plugin=tk-inter --include-package=socket --include-data-files=version.txt=. --include-data-files=icons/smiley-glass.png=icons/smiley-glass.png --macos-app-icon=icons/smiley-glass.png grab-txt.py
