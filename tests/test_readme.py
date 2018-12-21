#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 06.03.2018
# author:  TOS

import contextlib
import pathlib
import shutil

import pytest

import gittools.readme as rm


@contextlib.contextmanager
def change_readme_file(newname):
    old = rm.readme_filename
    rm.readme_filename = newname
    yield
    rm.readme_filename = old


@contextlib.contextmanager
def change_changelog_file(newname):
    old = rm.changelog_filename
    rm.changelog_filename = newname
    yield
    rm.changelog_filename = old


@pytest.fixture(scope='function')
def readmedir(tmpdir, request):
    tmpdir = pathlib.Path(tmpdir)

    here = pathlib.Path(request.module.__file__).parent
    rdme = here.joinpath('README.md')
    shutil.copy2(rdme, tmpdir)
    rdme = here.joinpath('DA_README.md')
    shutil.copy2(rdme, tmpdir)
    rdme = here.joinpath('CHANGELOG.md')
    shutil.copy2(rdme, tmpdir)
    return tmpdir


@pytest.fixture(scope='function')
def readmedir_nochangelog(tmpdir, request):
    tmpdir = pathlib.Path(tmpdir)

    here = pathlib.Path(request.module.__file__).parent
    rdme = here.joinpath('README.md')
    shutil.copy2(rdme, tmpdir)
    rdme = here.joinpath('DA_README.md')
    shutil.copy2(rdme, tmpdir)

    return tmpdir


def test_description(readmedir):
    # print(rm.description('..'))
    assert rm.description(
        readmedir) == "A collection of tools to connect to predefined git remote servers and create remote repos, define them as remotes, install local hooks, etc."
    with change_readme_file('DA_README.md'):
        assert rm.description(
            readmedir) == "A collection of tools to connect to predefined git remote servers and create remote repos, define them as remotes, install local hooks, etc."


def test_name(readmedir):
    assert rm.project_name(readmedir) == 'Git Tools'
    assert rm.package_name(readmedir) == 'gittools'
    with change_readme_file('DA_README.md'):
        assert rm.project_name(readmedir) == 'Git Tools'
        assert rm.package_name(readmedir) == 'gittools'


def test_changelog_readme(readmedir_nochangelog):
    print(rm.changelog(readmedir_nochangelog))
    assert rm.changelog(readmedir_nochangelog) == """##### 0.0.1
* initial version"""

    assert str(rm.versions(readmedir_nochangelog)) == "['v0.0.1']"
    with change_readme_file('DA_README.md'):
        assert str(rm.versions(readmedir_nochangelog)) == "[]"
        assert rm.changelog(readmedir_nochangelog) == ""


def test_changelog(readmedir):
    print(rm.changelog(readmedir))
    assert rm.changelog(readmedir) == """##### 0.0.1
* initial version"""

    assert str(rm.versions(readmedir)) == "['v0.0.1']"
    with change_readme_file('DA_README.md'):
        assert str(rm.versions(readmedir)) == "['v0.0.1']"

    with change_changelog_file("DA_README.md"):
        assert str(rm.versions(readmedir)) == "[]"
        assert rm.changelog(readmedir) == ""

    with change_changelog_file("README.md"):
        assert rm.changelog(readmedir) == """##### 0.0.1
* initial version"""

        assert str(rm.versions(readmedir)) == "['v0.0.1']"


def test_setgiturl(readmedir):
    rm.set_placeholder('<git-url>', 'http://gitserver:8080', path=readmedir)
    with open(readmedir.joinpath('README.md'), 'r') as fp:
        txt = fp.read()
    assert txt.find('http://gitserver:8080') > 0
    assert txt.find('<git-url>') < 0


def test_addversion_readme(readmedir_nochangelog):
    with change_changelog_file("README.md"):
        assert rm.changelog(readmedir_nochangelog) == """##### 0.0.1
* initial version"""

        rm.add_changelog_version("v1.1.1", ['fixed bug1', 'fixed bug2'], path=readmedir_nochangelog)

        assert rm.changelog(readmedir_nochangelog) == """##### v1.1.1
* fixed bug1
* fixed bug2

##### 0.0.1
* initial version"""


def test_addversion(readmedir):
    assert rm.changelog(readmedir) == """##### 0.0.1
* initial version"""

    rm.add_changelog_version("v1.1.1", ['fixed bug1', 'fixed bug2'], path=readmedir)

    assert rm.changelog(readmedir) == """##### v1.1.1
* fixed bug1
* fixed bug2

##### 0.0.1
* initial version"""
