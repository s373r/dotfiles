#!/usr/bin/env python3

from pathlib import Path
from termcolor import cprint, colored
import os
import sys
import argparse
import shutil
import traceback
import subprocess
import platform
import functools


def print_error(message):
    cprint(message, 'red')


def check_root_right():
    if os.geteuid() != 0:
        raise Exception('You must be root to permit this action!')


def _change_privileges(root):
    gid = 0 if root else int(os.getenv('SUDO_GID'))
    uid = 0 if root else int(os.getenv('SUDO_UID'))

    if not root and uid == 0:
        raise Exception('Rights weren\'t changed!')

    os.setresgid(gid, gid, -1)
    os.setresuid(uid, uid, -1)


# todo make RejectReason class
def ubuntu_more_than_17_04():
    (distro, version, _) = platform.linux_distribution()
    return (distro == 'Ubuntu' and float(version) < 17.04,
            'the workaround is needed only for Ubuntu more than 17.04')


class RootRights:
    def __enter__(self):
        _change_privileges(root=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        _change_privileges(root=False)


class PrintStep:
    def __init__(self, message, bold=True):
        self._message = message
        self._attrs = ['bold'] if bold else []

    def __enter__(self):
        print(self.get_message('white'))

    def __exit__(self, exc_type, exc_val, exc_tb):
        ok = sys.exc_info()[0] is None
        print(self.get_message('green' if ok else 'red',
                               'ok' if ok else 'fail'))

    def get_message(self, color, postfix_text=''):
        if postfix_text:
            postfix_text = '... {}'.format(postfix_text)
        return colored('* {}{}'.format(self._message, postfix_text),
                       color, attrs=self._attrs)


class InstallationStep:
    def __init__(self, skip_if=None):
        self._skip = False
        self._reason = ''
        if skip_if is not None:
            (self._skip, self._reason) = skip_if()

    def __call__(self, original_func):
        decorator_self = self

        def skipped_function(*args, **kwargs):
            # todo refactor duplicates
            skip_message = '* Installing "{}"... skipped "{}"'.format(
                original_func.__name__, decorator_self._reason)
            cprint(skip_message, 'yellow', attrs=['bold'])

        def installation_function(*args, **kwargs):
            with PrintStep('Installing "{}"'.format(original_func.__name__)):
                original_func(*args, **kwargs)

        return skipped_function if self._skip else installation_function


def install_step(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with PrintStep('Installing "{}"'.format(f.__name__)):
            return f(*args, **kwargs)

    return wrapper


# todo migrate to class like a InstallationStep
def require_packages(packages):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            self.installer_manager.install_packages(packages)
            return f(self, *args, **kwargs)

        return wrapper

    return decorator


def copy_config_files(source_dir_path, destination_dir_path):
    for file in files:
        source_file_path = source_dir_path / file
        destination_file_path = destination_dir_path / file

        source_file = str(source_file_path)
        destination_file = str(destination_file_path)

        if not source_file_path.exists():
            raise FileNotFoundError(source_file)

        # todo add a cool colored logger
        print('from', source_file, 'to', destination_file)

        destination_file_path.parent.mkdir(parents=True, exist_ok=True)

        if destination_file_path.exists():
            os.remove(destination_file)

        shutil.copy(source_file, destination_file)


class ProgramManager:
    @staticmethod
    def run(command, output_expected_string=None, print_output=True,
            root=False):

        # todo refactor duplicates
        if root:
            with RootRights():
                process = subprocess.Popen(command, shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           universal_newlines=True)
        else:
            process = subprocess.Popen(command, shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True)
        output = ''
        while True:
            line = process.stdout.readline()
            if print_output:
                print(line, end='', flush=True)
            output += line

            return_code = process.poll()
            if return_code is not None:
                break

        if return_code != 0:
            raise Exception('Non-zero return code for "{}"'.format(command))

        if output_expected_string and output_expected_string not in output:
            raise Exception('"{}" was not found in the output'
                            .format(output_expected_string))


class InitManager:
    def __init__(self, dotfile_repo_path):
        cprint('''
           .                                           
          ;WL                      L        j.         
         f#E#K:    :;;;;;;;;;;;;;. #K:      EW,        
       .E#f :K#t    jWWWWWWWW###L  :K#t     E##j       
      iWW;    L#G.          ,W#f     L#G.   E###D.     
     L##Lffi   t#W,        ,##f       t#W,  E#jG#W;    
    tLLG##L .jffD##f      i##j     .jffD##f E#t t##f   
      ,W#i .fLLLD##L     i##t     .fLLLD##L E#t  :K#E: 
     j#E.      ;W#i     t##t          ;W#i  E#KDDDD###i
   .D#j       j#E.     t##i          j#E.   E#f,t#Wi,,,
  ,WK,      .D#f      j##;         .D#f     E#t  ;#W:  
  EG.       KW,      :##,          KW,      DWi   ,KK: 
  ,         G.       ,W,           G.                  
                     ::                                
        ''', 'red')
        check_root_right()
        _change_privileges(root=False)

        self.installer_manager = InstallerManager()
        self.git_manager = GitManager(dotfile_repo_path)

    @InstallationStep()
    @require_packages(['git', 'zsh'])
    def ohmyzsh_install(self):
        oh_my_zsh_install_command = 'sh -c "$(wget https://' \
                                    'raw.githubusercontent.com/robbyrussell/' \
                                    'oh-my-zsh/master/tools/install.sh -O -)"'
        ProgramManager.run(oh_my_zsh_install_command,
                           output_expected_string='is now installed')
        # todo decorator
        git_repo_urls = [
            'https://github.com/zsh-users/zsh-completions',
            'https://github.com/zdharma/history-search-multi-word',
            'https://github.com/zdharma/fast-syntax-highlighting'
        ]

        for git_repo_url in git_repo_urls:
            self.git_manager.clone(git_repo_url,
                                   Path('~/.oh-my-zsh/custom/plugins/'))

    @InstallationStep()
    @require_packages(['i3'])
    def i3_install(self):
        pass

    @InstallationStep()
    @require_packages(['compton'])
    def compton_install(self):
        pass

    @InstallationStep()
    @require_packages(['ninja-build',
                       # https://github.com/jaagr/polybar/wiki/Compiling#apt-get
                       'cmake',
                       'cmake-data',
                       'libcairo2-dev',
                       'libxcb1-dev',
                       'libxcb-ewmh-dev',
                       'libxcb-icccm4-dev',
                       'libxcb-image0-dev',
                       'libxcb-randr0-dev',
                       'libxcb-util0-dev',
                       'libxcb-xkb-dev',
                       'pkg-config',
                       'python-xcbgen',
                       'xcb-proto',
                       'libxcb-xrm-dev',
                       'i3-wm',
                       'libasound2-dev',
                       'libmpdclient-dev',
                       'libiw-dev',
                       'libcurl4-openssl-dev'])
    def polybar_install(self):
        repo_path = self.git_manager.clone('https://github.com/jaagr/polybar',
                                           recursive=True)
        build_dir_path = repo_path / 'build'
        build_dir_path.mkdir()

        cmake_generate_command = 'cmake -G Ninja -B{} -H{}'.format(
            build_dir_path, build_dir_path.parent)
        cmake_build_command = 'cmake --build {}'.format(build_dir_path)
        ninja_install_command = 'ninja -C{} install'.format(build_dir_path)

        ProgramManager.run(cmake_generate_command)
        ProgramManager.run(cmake_build_command)
        ProgramManager.run(ninja_install_command, root=True)

    @InstallationStep(skip_if=ubuntu_more_than_17_04)
    def polybar_ubuntu_17_workaround(self):
        # https://github.com/jaagr/polybar/wiki/Compiling#version-mismatch-between-xcb-proto-and-libxcb-randr0-dev
        custom_xcb_proto_path = self.git_manager._3rdParty_path / 'custom-xcb-proto'
        custom_xcb_proto_path.mkdir()

        build_script = '''
            cd {}
            wget https://launchpad.net/ubuntu/+archive/primary/+files/xcb-proto_1.11.orig.tar.gz
            wget https://launchpad.net/ubuntu/+archive/primary/+files/xcb-proto_1.11-1.diff.gz
            tar -xzvf xcb-proto_1.11.orig.tar.gz
            gzip -d xcb-proto_1.11-1.diff.gz
            cd xcb-proto-1.11
            patch -p1 <../xcb-proto_1.11-1.diff
            ./configure
            make -j4
        '''.format(custom_xcb_proto_path)

        ProgramManager.run(build_script)
        ProgramManager.run('make -C{} install'.format(
            custom_xcb_proto_path / 'xcb-proto-1.11'), root=True)


class InstallerManager:
    def __init__(self):
        with PrintStep('Update list of available packages'):
            ProgramManager.run('apt update', root=True)

    def install_packages(self, packages):
        package_names = ' '.join(packages).strip()
        with PrintStep('Installing "{}"'.format(package_names), False):
            ProgramManager.run('apt install -y {}'.format(package_names),
                               root=True)


class GitManager:
    def __init__(self, dotfile_repo_path):
        _3rdParty_path = dotfile_repo_path / '3rdParty'
        if _3rdParty_path.exists():
            shutil.rmtree(str(_3rdParty_path))
        _3rdParty_path.mkdir(exist_ok=True)

        self._3rdParty_path = _3rdParty_path

    def clone(self, git_repo_url, destination_dir_path=None, recursive=False):
        if destination_dir_path is None:
            destination_dir_path = self._3rdParty_path

        git_repo_name = git_repo_url.split('/')[-1]
        destination_dir_path = destination_dir_path / git_repo_name
        destination_dir = str(destination_dir_path)

        if destination_dir_path.exists():
            shutil.rmtree(destination_dir)

        # print_regular('Cloning "{}" to "{}"'.format(
        #     git_repo_url, destination_dir))
        clone_command = 'git clone {} --depth 1 {} {}'.format(
            '--recursive' if recursive else '', git_repo_url, destination_dir)

        # todo check result
        ProgramManager.run(clone_command)

        return destination_dir_path


def init(dotfile_repo_path):
    try:
        init_manager = InitManager(dotfile_repo_path)
        init_manager.ohmyzsh_install()
        init_manager.i3_install()
        init_manager.compton_install()
        init_manager.polybar_install()
        init_manager.polybar_ubuntu_17_workaround()
    except Exception as e:
        print_error('Error upon installation!')
        # todo provide argument to enable printing traceback
        traceback.print_exc()
        print_error(str(e))
        print_error('Installation is stopped! Exiting...')
        exit(1)


if __name__ == '__main__':
    # todo make install by symlinks, not copying config files
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices=['grub', 'install', 'init'],
                        # todo change help
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
        copy_config_files(home_path, dotfile_repo_path)
    elif script_action == 'install':
        copy_config_files(dotfile_repo_path, home_path)
    else:
        init(dotfile_repo_path)
