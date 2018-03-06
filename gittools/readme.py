#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 06.03.2018
# author:  TOS

import logging
import pathlib
import fileinput
import re

log = logging.getLogger(__name__)

filename = 'README.md'

def getlines(path='.'):

    readmefile = pathlib.Path(path).joinpath(filename)
    if not readmefile.exists() or not readmefile.is_file():
        raise FileNotFoundError("'{}' not found!".format(readmefile))

    with open(readmefile, 'r') as fp:
        lines = fp.readlines()

    return lines


def project_name(path='.'):
    lines = getlines(path)

    name = []
    for i, line in enumerate(lines):
        if line.startswith('==='):
            break
        name.append(line)
    name = '\n'.join(name).strip(' \n')

    return name


def package_name(path='.'):
    return "python-{}".format(project_name(path).lower().replace(' ', ''))


def description(path='.'):
    lines = getlines(path)

    descr = []
    for i, line in enumerate(lines):
        if line.strip().startswith('---'):
            for j, line in enumerate(lines[i+1:]):
                descr.append(line)
                if line.strip().startswith('---'):
                    # drop the following title
                    descr.pop()
                    descr.pop()
                    break
            break
    descr = ''.join(descr).strip(' \n')
    return descr

def _changelog_indices(lines):
    for i, line in enumerate(lines):
        if line.strip().replace('-','').lower()=='changelog':
            for j, line in enumerate(lines[i+2:]):
                if line.strip().startswith('---'):
                    break
            break
    return i+2,i+1+j

def changelog(path='.'):

    lines = getlines(path)
    i, j = _changelog_indices(lines)
    changlog = lines[i:j]
    changlog = ''.join(changlog).strip(' \n')
    return changlog


def add_changelog_version(version, points=[], path='.'):

    readmefile = pathlib.Path(path).joinpath(filename)
    lines = getlines(path)
    I, J = _changelog_indices(lines)

    # text to include
    text = "##### {}".format(version)
    for p in points:
        text += "\n* {}".format(p)
    text += "\n\n"

    # change file
    i = 0
    for line in fileinput.FileInput(str(readmefile), inplace=1):
        if i == I:
            line = "{}{}".format(text, line)
        i += 1
        print(line,end='')

def set_placeholder(pattern, replace, path='.'):

    readmefile = pathlib.Path(path).joinpath(filename)

    pattern = re.compile(pattern)
    for line in fileinput.FileInput(str(readmefile), inplace=1):
        if re.search(pattern, line):
            line = re.sub(pattern, replace, line)
        print(line,end='')