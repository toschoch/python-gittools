#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import click
import stat
import os
import subprocess
import pathlib

here = pathlib.Path(__file__).parent

@click.group()
def install():
    """ install things as encapsulated python scripts or git hooks """

@install.command()
@click.argument('cmd')
@click.argument('dst',type=click.Path(exists=True))
@click.option('--env',type=str, help="name of the capsulating conda environment")
def script(cmd, dst, env=None):
    """ installs the command CMD (assumes a python console script) encapsulated into DST """

    with open(r'/home/tobi/PycharmProjects/python-gittools/gittools/console_scripts/encaps_cmd_template.sh','r') as fp:
        bash_script = fp.read()

    # set env and command
    if env is None:
        env = cmd
    bash_script = bash_script.format(command=cmd, env=env)

    dst = pathlib.Path(dst).joinpath(cmd)

    with open(dst,'w+') as fp:
        fp.write(bash_script)

    st = os.stat(dst)
    os.chmod(dst, st.st_mode | stat.S_IEXEC)

    print('script successfully created ({})!'.format(dst))