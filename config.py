#!/usr/bin/env python3

from pathlib import Path
import argparse
import os
import shutil


# todo make install by symlinks, not copying config files
parser = argparse.ArgumentParser()
parser.add_argument('action',
                    choices=['grub', 'install'],
                    help='grub config files from $HOME or install them there')

script_action = parser.parse_args().action

files = [
    # configs
    '.config/i3/config',
    '.config/polybar/config',
    '.zshrc',
    # other stuff
    '.config/polybar/launch.sh'
]

home_path = Path.home()
dotfile_repo_path = Path(__file__).absolute().parent

# todo refactoring: move to policy-based paradigm
if script_action == 'grub':
    source_dir_path = home_path
    destination_dir_path = dotfile_repo_path
else:
    source_dir_path = dotfile_repo_path
    destination_dir_path = home_path

for file in files:
    source_file_path = source_dir_path / file
    destination_file_path = destination_dir_path / file

    source_file = str(source_file_path)
    destination_file = str(destination_file_path)

    destination_dir = str(destination_dir_path)

    if not source_file_path.exists():
        raise FileNotFoundError(source_file)

    # todo add a cool colored logger
    print('from', source_file, 'to', destination_file)

    os.makedirs(destination_dir, exist_ok=True)

    if destination_file_path.exists():
        os.remove(destination_file)

    shutil.copy(source_file, destination_file)
