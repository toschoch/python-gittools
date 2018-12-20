#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import subprocess
import click
import stat
import os
import sys
import platform
import pathlib
import shutil
import re
import pkg_resources

from .config import get_cfg

here = pathlib.Path(__file__).parent

conda_exception = EnvironmentError('gittools need conda to be installed on your machine! Install conda first...')

def conda_envs():
    environments = {}
    try:
        envs = subprocess.check_output(['conda','env','list']).decode('utf-8').splitlines()[2:]
        for env in envs:
            if env.strip() == '': continue
            if env.find("*")>0:
                name, _, env_dir = re.split(r'[\s]+',env)
                active = name
            else:
                name, env_dir = re.split(r'[\s]+',env)
            environments[name.strip()] = pathlib.Path(env_dir.strip())
        return environments, active

    except FileNotFoundError:
        raise conda_exception

def active_conda_env():
    envs, active = conda_envs()
    return active, envs[active]


def create_script(cmd, dst, env_name, env_path, template, suffix=True):

    script = pkg_resources.resource_string('gittools','template_scripts/{}'.format(template)).decode('utf-8')
    _, ext = os.path.splitext(template)

    script = script.format(command=cmd, env_name=env_name, env_path=env_path)

    dst = pathlib.Path(dst).joinpath(cmd)
    if suffix:
        dst = dst.with_suffix(ext)

    with open(dst,'w+') as fp:
        fp.write(script)

    return dst

def create_hook(dst, env_name, env_path, template, suffix, script_suffix):
    hook = pkg_resources.resource_filename('gittools','git_hooks/{}_{}'.format(template, suffix))
    script = pkg_resources.resource_string('gittools','git_hooks/{}_{}.{}'.format(template, suffix, script_suffix)).decode('utf-8')

    script = script.format(env_name=env_name, env_path=env_path)

    # copy modified script
    dst_dir = pathlib.Path(dst)
    dst = dst_dir.joinpath('{}.{}'.format(template, script_suffix))
    with open(dst,'w+') as fp:
        fp.write(script)

    # copy corresponding hook
    dst = dst_dir.joinpath(template)
    shutil.copy(hook, dst)

    return dst


@click.group()
def install():
    """ install things as encapsulated python scripts or git hooks """

@install.command()
@click.argument('cmd')
@click.option('--dst',type=click.Path(exists=True), help='optional specification of the target directory')
@click.option('--env',type=str, help="optional specification of the conda environment")
def script(cmd, dst=None, env=None):
    """ installs the command CMD (assumes a conda console script) encapsulated in its environment"""

    if env is None:
        env, env_dir = active_conda_env()
    else:
        env_dir = conda_envs()[env]

    if dst is None:
        cfg = get_cfg()
        try:
            dst = pathlib.Path(cfg['scripts']['directory']).expanduser()
        except KeyError as e:
            raise click.UsageError("configuration has no {} section! Specify with --dst option".format(str(e)))

    if platform.system().lower() == 'linux':
        dst = create_script(cmd, dst, env_name=env, env_path=env_dir, template='encaps_cmd_template_bash.sh', suffix=False)

        st = os.stat(dst)
        os.chmod(dst, st.st_mode | stat.S_IEXEC)

        click.echo('UNIX script successfully created! (in {})'.format(dst))

    elif platform.system().lower() == 'windows':

        dst = create_script(cmd, dst, env_name=env, env_path=env_dir, template='encaps_cmd_template_win.bat')

        click.echo('WINDOWS script successfully created! (in {})'.format(dst))

    click.echo("now you can use '{}' in your console without activating the environment...".format(cmd))


@install.command()
@click.option('--dst',type=click.Path(exists=True), help='optional specification of the target directory')
@click.option('--env',type=str, help="optional specification of the conda environment")
def hook(dst=None, env=None):
    """ installs the git commit hook for automatically update the requirements files """

    if dst is None:
        dst = pathlib.Path()

    git_dir = dst.joinpath('.git')
    if not git_dir.exists():
        raise EnvironmentError('This directory is not a Git repository!')
    git_dir = git_dir.joinpath('hooks')
    # assure there is a git hooks dir
    git_dir.mkdir(exist_ok=True)

    if env is None:
        env, env_dir = active_conda_env()
    else:
        env_dir = conda_envs()[env]

    if platform.platform() == 'linux':

        raise NotImplementedError("Not yet implemented for UNIX systems!") 
        # dst = create_script(cmd, dst, env_name=env, env_path=env_dir, template='encaps_cmd_template_bash.sh')
        #
        # st = os.stat(dst)
        # os.chmod(dst, st.st_mode | stat.S_IEXEC)
        #
        # click.echo('UNIX script successfully created! (in {})'.format(dst))

    elif platform.platform().lower().startswith('windows'):

        dst = create_hook(git_dir, env_name=env, env_path=env_dir, template='pre-commit', suffix='win', script_suffix='cmd')

        click.echo("WINDOWS git hooks successfully installed for environment '{}'!".format(env))

    click.echo("now before every commit the requirements files are updated with '{}' package status...".format(env))