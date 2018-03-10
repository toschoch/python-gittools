#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 08.03.2018
# author:  TOS
import gittools.cli as cli
from gittools import config
import pathlib

from click.testing import CliRunner

def test_list():

    config.set_cfg({'reposervers':{'myserver':{'type':'Github','url':'www.github.com'}}})
    runner = CliRunner()
    result = runner.invoke(cli.list)
    assert result.exit_code == 0
    assert result.output == 'following remote repository servers are configured:\nmyserver	www.github.com\n'

here = pathlib.Path(__file__).parent

def test_package_name():
    assert cli.package_name(here)=='tests'