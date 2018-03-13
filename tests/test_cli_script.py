#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 13.03.2018
# author:  TOS

import gittools.cli as cli
import gittools.cli_install as cli_install
from gittools import config
from unittest.mock import MagicMock, call
import pathlib

here = pathlib.Path(__file__).parent

from click.testing import CliRunner


def test_install_script(tmpdir):

    import subprocess
    call_no_mock = subprocess.check_output

    subprocess.check_output = MagicMock(side_effect=FileNotFoundError)
    subprocess.check_call = MagicMock(side_effect=FileNotFoundError)

    config.set_cfg({'reposervers':{'myserver':{'type':'Github','url':'www.github.com'}}})
    runner = CliRunner()
    result = runner.invoke(cli_install.script, args=['python'])
    assert result.exit_code == -1
    assert str(result.exception) == "gittools need conda to be installed on your machine! Install conda first..."

    subprocess.check_output = MagicMock(side_effect=[r"""# conda environments:
#
meat                     D:\Users\TOS\conda\meat
rfl                   *  D:\Users\TOS\conda\rfl
root                     C:\ProgramData\Miniconda2

""".encode('utf-8')])

    config.set_cfg({'reposervers': {'myserver': {'type': 'Github', 'url': 'www.github.com'}}})
    runner = CliRunner()
    result = runner.invoke(cli_install.script, args=['python'])
    assert result.exit_code==2
    assert str(result.output) == """Usage: script [OPTIONS] CMD

Error: configuration has no 'scripts' section! Specify with --dst option
"""
    subprocess.check_output = MagicMock(side_effect=[r"""# conda environments:
#
meat                     D:\Users\TOS\conda\meat
rfl                      D:\Users\TOS\conda\rfl
root                  *  C:\ProgramData\Miniconda2

""".encode('utf-8')])

    config.set_cfg({'reposervers': {'myserver': {'type': 'Github', 'url': 'www.github.com'}},
                    'scripts': {'directory': tmpdir}})
    runner = CliRunner()
    result = runner.invoke(cli_install.script, args=['pip'])
    assert result.exit_code == 0
    assert result.output.splitlines()[-1] == "now you can use 'pip' in your console without activating the environment..."

    script_path = pathlib.Path(tmpdir).joinpath('pip.bat')
    assert script_path.exists()

