#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import click
import sys
import subprocess
from .readme import description, package_name, add_changelog_version, filename, set_placeholder
from .reposerver import get_repo_server, repository_servers_cfg


@click.group()
def gittool():
    """ CLI tool to setup git remote repositories. """

@gittool.command()
def list():
    for name, cfg in repository_servers_cfg().items():
        print("{}\t{}".format(name, cfg.get('url','...')))

@gittool.command()
@click.option('--tag/--no-tag', default=True)
def init(tag):
    subprocess.call(['git', 'init'])
    subprocess.call(['git', 'add', '.gitignore'])
    subprocess.call(['git','commit', '-m','"initial commit"'])
    if tag:
        subprocess.call(['git','tag','v0.0.1'])


@gittool.command()
@click.argument('repo', type=click.Choice(repository_servers_cfg().keys()))
@click.option('--usage/--no-usage', default=False)
def setup(repo, usage):

    srv = get_repo_server(repo)
    remote_repo = srv.create_repository(package_name(), description())

    # add the remote
    subprocess.call(['git', 'remote', 'add', repo, remote_repo.giturl])

    # set git urls in usage section of readme
    if usage:
        set_placeholder("<git-url>",remote_repo.giturl)

    #TODO: find a solution to call and pass username and pw
    print("if prompted, use user: {}, pw: {}".format(srv.username,srv.password))
    subprocess.call(['git', 'push', '--set-upstream', repo])


@gittool.command()
@click.argument('tagname', type=str)
@click.option('-m', '--message',  multiple=True)
def tag(tagname, message):

    # get all tags
    tags = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0', '@^']).decode('utf-8').splitlines()
    lasttag = tags[0]

    # commit messages
    msgs = subprocess.check_output(['git','log','--oneline','{}..@'.format(lasttag)]).decode('utf-8').splitlines()
    msgs = list(map(lambda msg: ' '.join(msg.split(' ')[1:]), msgs))

    # insert into readme
    add_changelog_version(tagname.lstrip('v'), points=msgs)

    # add readme, and commit
    subprocess.call(['git', 'add', filename])
    subprocess.call(['git', 'commit','-m', 'update {} for tag {}'.format(filename, tagname)])

    # create the tag
    if message == "":
        subprocess.call(['git', 'tag', tagname])
    else:
        subprocess.call(['git', 'tag', tagname, '-m', '{}'.format("\n".join(message))])