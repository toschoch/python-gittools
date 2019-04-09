#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import subprocess

import click
import pathlib

from .cli_install import install
from .cli_remote import remote, git_commit_only, git_exception
from .readme import add_changelog_version, changelog_filename as changelog, readme_filename as readme, versions


def get_tags():
    """ returns the tags of the git repository in the current directory. """
    try:
        tags = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0', '@^'], stderr=subprocess.STDOUT)
        tags = tags.decode('utf-8').splitlines()
    except subprocess.CalledProcessError as err:
        reason = err.output.decode('utf-8')
        if reason == "fatal: No names found, cannot describe anything.":
            tags = []
        else:
            raise ValueError(reason)
    except FileNotFoundError:
        raise git_exception

    return tags


@click.group()
def gittool():
    """ CLI tool to setup git remote repositories. """


@gittool.command()
def version():
    """ returns the version of gittool """
    import pkg_resources
    ver = pkg_resources.get_distribution('gittools').version
    click.echo(ver)


@gittool.command()
def init():
    """ initialize local git repo and creates an initial version. """

    if subprocess.call(['git', 'init']) != 0:
        raise git_exception
    subprocess.call(['git', 'add', '.gitignore'])
    subprocess.call(['git', 'commit', '-m', '"initial commit"'])

    # get tags
    readme_tags = versions()

    if len(readme_tags) > 0:
        # create a tag with the last version defined in readme
        subprocess.call(['git', 'tag', readme_tags[0]])


@gittool.command()
@click.argument('tagname', type=str)
@click.option('-m', '--message', help='optional message for annotated tags')
def tag(tagname, message):
    """ creates the tag TAGNAME and updates the version changelog in readme. """
    # get all tags
    tags = get_tags()
    lasttag = tags[0]

    # commit messages
    msgs = subprocess.check_output(['git', 'log', '--oneline', '{}..@'.format(lasttag)]).decode('utf-8').splitlines()
    msgs = [' '.join(m.split(' ')[1:]) for m in msgs]

    # insert into readme
    files = [fn for fn in [changelog, readme] if pathlib.Path(fn).exists()]
    with git_commit_only(" ".join(files), 'update {} for tag {}'.format(changelog, tagname)):
        add_changelog_version(tagname.lstrip('v'), points=msgs)

    # create the tag
    if message is None:
        subprocess.call(['git', 'tag', tagname])
    else:
        subprocess.call(['git', 'tag', tagname, '-m', '{}'.format("\n".join(message))])


# try to add command group
gittool.add_command(install)
gittool.add_command(remote)
