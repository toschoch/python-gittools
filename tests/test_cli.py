#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 08.03.2018
# author:  TOS
import gittools.cli as cli
import pathlib

here = pathlib.Path(__file__).parent

def test_package_name():
    assert cli.package_name(here)=='tests'