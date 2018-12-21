#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 06.03.2018
# author:  TOS

import fileinput
import logging
import pathlib
import re

log = logging.getLogger(__name__)

readme_filename = 'README.md'
changelog_filename = 'CHANGELOG.md'


def getlines(path='.'):
    path = pathlib.Path(path)
    if path.exists() and path.is_file():
        readmefile = path
    else:
        readmefile = pathlib.Path(path).joinpath(readme_filename)

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


def versions(path='.'):
    vs = [l.strip('# ') for l in changelog(path).splitlines() if l.strip().startswith('#')]
    vs = list(map(lambda v: "v{}".format(v) if not v.startswith('v') else v, vs))
    return vs


def package_name(path='.'):
    return project_name(path).lower().replace(' ', '')


def description(path='.'):
    lines = getlines(path)

    descr = []
    for i, line in enumerate(lines):
        if line.strip().startswith('---'):
            for j, line in enumerate(lines[i + 1:]):
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
        j = i + 1

        if line.strip().lstrip("#").replace('-', '').lower() == 'changelog':
            if line.strip().startswith('# '): continue  # level 0 header changelog in separate file
            for j, line in enumerate(lines[i + 2:]):
                if line.strip().startswith('####'): continue  # version entry e.g. ####(#) 0.0.3
                if line.strip().startswith('#'):  # next section
                    j = j + 1
                    break
                if line.strip().startswith('---'):  # next section
                    break
                if line.strip().startswith('['):
                    j = j + 1
                    break
            break

        # for changelog in separate file file with versions
        if line.strip().lstrip("#").replace('-', '').replace(' ', '').lower() == 'versions':
            for j, line in enumerate(lines[i + 1:]):
                if line.strip().startswith('####'): continue  # version entry e.g. ####(#) 0.0.3
                if line.strip().startswith('#'):  # next section
                    j = j + 1
                    break
                if line.strip().startswith('---'):  # next section
                    break
                if line.strip().startswith('['):
                    j = j + 1
                    break
            i = i - 1
            break

    return i + 2, i + 1 + j


def _get_changelog_file(path):
    changelog_file = pathlib.Path(path).joinpath(changelog_filename)
    if changelog_file.exists() and changelog_file.is_file():
        return changelog_file
    return pathlib.Path(path).joinpath(readme_filename)


def _get_changelog_lines(path):
    changelog_file = _get_changelog_file(path)
    return getlines(changelog_file)


def changelog(path='.'):
    lines = _get_changelog_lines(path)
    i, j = _changelog_indices(lines)
    changlog = lines[i:j]
    changlog = ''.join(changlog).strip(' \n')
    return changlog


def add_changelog_version(version, points=[], path='.'):
    changelogfile = _get_changelog_file(path)
    lines = getlines(changelogfile)
    I, J = _changelog_indices(lines)

    # text to include
    text = "##### {}".format(version)
    for p in points:
        text += "\n* {}".format(p)
    text += "\n\n"

    # change file
    i = 0
    for line in fileinput.FileInput(str(changelogfile), inplace=1):
        if i == I:
            line = "{}{}".format(text, line)
        i += 1
        print(line, end='')


def set_placeholder(pattern, replace, path='.'):
    readmefile = pathlib.Path(path).joinpath(readme_filename)

    pattern = re.compile(pattern)
    for line in fileinput.FileInput(str(readmefile), inplace=1):
        if re.search(pattern, line):
            line = re.sub(pattern, replace, line)
        print(line, end='')
