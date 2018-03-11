#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import click
import subprocess
from .readme import add_changelog_version, filename as readme, versions
from .reposerver import repository_servers_cfg
from .cli_install import install
from .cli_remote import remote, git_commit_only


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
    return tags


@click.group()
def gittool():
    """ CLI tool to setup git remote repositories. """


@gittool.command()
def list():
    """ list the configured remote repository servers. """
    remotes = repository_servers_cfg()
    if len(remotes) > 0:
        click.echo("following remote repository servers are configured:")
    for name, cfg in remotes.items():
        click.echo("{}\t{}".format(name, cfg.get('url','...')))

@gittool.command()
def init():
    """ initialize local git repo and creates an initial version. """

    subprocess.call(['git', 'init'])
    subprocess.call(['git', 'add', '.gitignore'])
    subprocess.call(['git','commit', '-m','"initial commit"'])

    # get tags
    readme_tags = versions()

    if len(readme_tags) > 0:
        # create a tag with the last version defined in readme
        subprocess.call(['git','tag',readme_tags[0]])


@gittool.command()
@click.argument('tagname', type=str)
@click.option('-m', '--message',  multiple=True, help='optional message for annotated tags')
def tag(tagname, message):
    """ creates the tag TAGNAME and updates the version changelog in readme. """
    # get all tags
    tags = get_tags()
    lasttag = tags[0]

    # commit messages
    msgs = subprocess.check_output(['git','log','--oneline','{}..@'.format(lasttag)]).decode('utf-8').splitlines()
    msgs = [' '.join(m.split(' ')[1:]) for m in msgs]

    # insert into readme
    with git_commit_only(readme, 'update {} for tag {}'.format(readme, tagname)):
        add_changelog_version(tagname.lstrip('v'), points=msgs)

    # create the tag
    if message == "":
        subprocess.call(['git', 'tag', tagname])
    else:
        subprocess.call(['git', 'tag', tagname, '-m', '{}'.format("\n".join(message))])

# try to add command group
gittool.add_command(install)
gittool.add_command(remote)