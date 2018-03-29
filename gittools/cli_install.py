#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import subprocess
import click
import stat
import os
import platform
import pathlib
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


def create_script(cmd, dst, env_name, env_path, template):

    script = pkg_resources.resource_string('gittools','template_scripts/{}'.format(template)).decode('utf-8')
    _, ext = os.path.splitext(template)

    script = script.format(command=cmd, env_name=env_name, env_path=env_path)

    dst = pathlib.Path(dst).joinpath(cmd).with_suffix(ext)

    with open(dst,'w+') as fp:
        fp.write(script)

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

    if platform.platform() == 'linux':
        dst = create_script(cmd, dst, env_name=env, env_path=env_dir, template='encaps_cmd_template_bash.sh')

        st = os.stat(dst)
        os.chmod(dst, st.st_mode | stat.S_IEXEC)

        click.echo('UNIX script successfully created! (in {})'.format(dst))

    elif platform.platform().lower().startswith('windows'):

        dst = create_script(cmd, dst, env_name=env, env_path=env_dir, template='encaps_cmd_template_win.bat')

        click.echo('WINDOWS script successfully created! (in {})'.format(dst))

    click.echo("now you can use '{}' in your console without activating the environment...".format(cmd))


@install.command()
@click.option('--dst',type=click.Path(exists=True), help='optional specification of the target directory')
@click.option('--env',type=str, help="optional specification of the conda environment")
def commithook(dst=None, env=None):
    """ installs the git commit hook for automatically update the requirements files """

    if platform.platform() == 'linux':
        dst = create_script(cmd, dst, env_name=env, env_path=env_dir, template='encaps_cmd_template_bash.sh')

        st = os.stat(dst)
        os.chmod(dst, st.st_mode | stat.S_IEXEC)

        click.echo('UNIX script successfully created! (in {})'.format(dst))

    elif platform.platform().lower().startswith('windows'):

        dst = create_script(cmd, dst, env_name=env, env_path=env_dir, template='encaps_cmd_template_win.bat')

        click.echo('WINDOWS script successfully created! (in {})'.format(dst))

    click.echo("now you can use '{}' in your console without activating the environment...".format(cmd))