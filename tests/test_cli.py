#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 08.03.2018
# author:  TOS
import gittools.cli as cli
import gittools.cli_remote as cli_remote
import gittools.readme as rm
from gittools import config
from unittest.mock import MagicMock, call
import pathlib
from test_readme import readmedir, readmedir_nochangelog, change_changelog_file, change_readme_file

here = pathlib.Path(__file__).parent

from click.testing import CliRunner

def test_remote_list():

    config.set_cfg({'reposervers':{'myserver':{'type':'Github','url':'www.github.com'}}})
    runner = CliRunner()
    result = runner.invoke(cli_remote.list)
    assert result.exit_code == 0
    assert result.output == 'following remote repository servers are configured:\nmyserver	www.github.com\n'


def test_package_name():
    assert cli_remote.package_name(here)=='tests'


def test_get_git_tags():
    import subprocess
    mocked_call = MagicMock()
    mocked_checked_output = MagicMock()
    subprocess.call = mocked_call
    subprocess.check_output = mocked_checked_output

    cli.get_tags()

    mocked_checked_output.assert_called_with(['git', 'describe', '--tags', '--abbrev=0', '@^'], stderr=subprocess.STDOUT)


def test_init():


    import subprocess
    subprocess.call = MagicMock(return_value=-1)
    subprocess.check_output = MagicMock(side_effect=FileNotFoundError)
    subprocess.check_call = MagicMock(side_effect=FileNotFoundError)

    import os
    os.chdir(here)

    config.set_cfg({'reposervers': {'myserver': {'type': 'Github', 'url': 'www.github.com'}}})
    runner = CliRunner()
    result = runner.invoke(cli.init)
    assert result.exit_code != 0
    assert str(result.exception) == "gittools need Git to be installed on your machine! Install Git first..."

    subprocess.call = MagicMock(return_value=0)
    result = runner.invoke(cli.init)
    assert result.exit_code == 0
    subprocess.call.assert_has_calls([call(['git', 'init']),
                                      call(['git', 'add', '.gitignore']),
                                      call(['git', 'commit', '-m', '"initial commit"']),
                                      call(['git', 'tag', 'v0.0.1'])])

def test_tag(readmedir):
    import subprocess
    subprocess.call = MagicMock(return_value=-1)
    subprocess.check_output = MagicMock(side_effect=FileNotFoundError)
    subprocess.check_call = MagicMock(side_effect=FileNotFoundError)

    import os
    os.chdir(here)

    config.set_cfg({'reposervers': {'myserver': {'type': 'Github', 'url': 'www.github.com'}}})
    runner = CliRunner()
    result = runner.invoke(cli.tag,args=['v0.0.8'])
    assert result.exit_code != 0
    assert str(result.exception) == "gittools need Git to be installed on your machine! Install Git first..."

    subprocess.call = MagicMock(return_value=0)
    subprocess.check_output = MagicMock(side_effect=['v0.0.4\n'.encode('utf-8'),
                                                     """4d70c5c last test
b50367c very last
dc2e120 last test
""".encode('utf-8')])
    with change_changelog_file(readmedir.joinpath('CHANGELOG.md')):
        result = runner.invoke(cli.tag, ['v0.0.7'])
    assert result.exit_code == 0
    subprocess.call.assert_called_with(['git', 'tag', 'v0.0.7'])

    assert rm.changelog(readmedir) == """##### 0.0.7
* last test
* very last
* last test

##### 0.0.1
* initial version"""

def test_tag_readme(readmedir_nochangelog):
    import subprocess
    subprocess.call = MagicMock(return_value=-1)
    subprocess.check_output = MagicMock(side_effect=FileNotFoundError)
    subprocess.check_call = MagicMock(side_effect=FileNotFoundError)

    import os
    os.chdir(here)

    config.set_cfg({'reposervers': {'myserver': {'type': 'Github', 'url': 'www.github.com'}}})
    runner = CliRunner()
    result = runner.invoke(cli.tag,args=['v0.0.8'])
    assert result.exit_code != 0
    assert str(result.exception) == "gittools need Git to be installed on your machine! Install Git first..."

    subprocess.call = MagicMock(return_value=0)
    subprocess.check_output = MagicMock(side_effect=['v0.0.4\n'.encode('utf-8'),
                                                     """4d70c5c last test
b50367c very last
dc2e120 last test
""".encode('utf-8')])
    with change_changelog_file("notexisting.md"):
        with change_readme_file(readmedir_nochangelog.joinpath('README.md')):
            result = runner.invoke(cli.tag, ['v0.0.7'])
    assert result.exit_code == 0
    subprocess.call.assert_called_with(['git', 'tag', 'v0.0.7'])

    assert rm.changelog(readmedir_nochangelog) == """##### 0.0.7
* last test
* very last
* last test

##### 0.0.1
* initial version"""