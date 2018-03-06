#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import click
import subprocess
from .readme import description, package_name, add_changelog_version, filename
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
def setup(repo):

    git_user = subprocess.check_output(['git', 'config', '--get', 'user.name']).decode('utf-8').strip('\n')

    srv = get_repo_server(repo)
    remote_repo = srv.create_repository(package_name(), description(), Administrators=[git_user])

    giturl = remote_repo.giturl.split('@')
    giturl[0] = '{}:{}'.format(giturl[0],remote_repo.password)
    giturl = '@'.join(giturl)

    subprocess.call(['git', 'remote', 'add', repo, giturl])

    # make initial commit and push (set upstream)
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