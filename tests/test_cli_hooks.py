#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 13.03.2018
# author:  TOS

import gittools.cli_install as cli_install
from gittools import config
from unittest.mock import MagicMock
import pathlib
import shutil
import pytest
import contextlib
import os

@contextlib.contextmanager
def change_cwd(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(cwd)

@pytest.fixture(scope='function')
def gitdir(tmpdir, request):
    tmpdir = pathlib.Path(tmpdir)

    here = pathlib.Path(request.module.__file__).parent
    gitrepo = here.joinpath('test_git_repo/')
    shutil.copytree(gitrepo, tmpdir.joinpath('.git'))
    return tmpdir

from click.testing import CliRunner


def test_install_hook(gitdir):

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
rfl                      D:\Users\TOS\conda\rfl
root                  *  C:\ProgramData\Miniconda2

""".encode('utf-8')])

    config.set_cfg({'reposervers': {'myserver': {'type': 'Github', 'url': 'www.github.com'}}})
    runner = CliRunner()
    with change_cwd(gitdir):
        result = runner.invoke(cli_install.hook)
    assert result.exit_code == 0
    assert result.output == "WINDOWS git hooks successfully installed for environment 'root'!\nnow before every commit the requirements files are updated with 'root' package status...\n"
    commit_hook = gitdir.joinpath('.git/hooks/pre-commit')
    assert commit_hook.exists() and commit_hook.is_file()
    commit_hook_win = gitdir.joinpath('.git/hooks/pre-commit.cmd')
    commit_hook_sh = gitdir.joinpath('.git/hooks/pre-commit.sh')
    assert (commit_hook_win.exists() and commit_hook_win.is_file()) or \
           (commit_hook_sh.exists() and commit_hook_sh.is_file())
