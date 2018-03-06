#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 06.03.2018
# author:  TOS

import gittools.readme as rm
import pathlib
import shutil
import pytest

here = pathlib.Path(__file__).parent

@pytest.fixture(scope='function')
def readmedir(tmpdir):
    tmpdir = pathlib.Path(tmpdir)

    rdme = here.joinpath('README.md')
    shutil.copy2(rdme, tmpdir)
    return tmpdir

def test_description():
    # print(rm.description('..'))
    assert rm.description(here) == "A collection of tools to connect to predefined git remote servers and create remote repos, define them as remotes, install local hooks, etc."

def test_name():
    assert rm.project_name(here) == 'Git Tools'
    assert rm.package_name(here) == 'python-gittools'

def test_changelog():
    print(rm.changelog(here))
    assert rm.changelog(here) == """##### 0.0.1
* initial version"""

def test_setgiturl(readmedir):
    rm.set_placeholder('<git-url>','http://gitserver:8080',path=readmedir)
    with open(readmedir.joinpath('README.md'),'r') as fp:
        txt =fp.read()
    assert txt.find('http://gitserver:8080')>0
    assert txt.find('<git-url>')<0


def test_addversion(readmedir):

    # print(rm.changelog(readmedir))
    assert rm.changelog(readmedir) == """##### 0.0.1
* initial version"""

    rm.add_changelog_version("v1.1.1",['fixed bug1', 'fixed bug2'],path=readmedir)

    assert rm.changelog(readmedir) == """##### v1.1.1
* fixed bug1
* fixed bug2

##### 0.0.1
* initial version"""