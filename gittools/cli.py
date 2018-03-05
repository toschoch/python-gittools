#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import click
import subprocess
from .reposerver import configured_repository_servers, get_repo_server





@click.group()
def gittools():
    """ this script sets up the git remote r """

@gittools.command()
def init():
    subprocess.call(['git', 'init'])
    subprocess.call(['git', 'add', '.gitignore'])
    subprocess.call(['git','commit', '-m','"initial commit"'])
    subprocess.call(['git','tag','v0.0.1'])


@gittools.command()
@click.argument('repo')
def setup(repo):
    srv = get_repo_server(repo)
    remote_repo = srv.create_repository('testrepo3', 'this is a test repo')

    giturl = remote_repo.giturl.split('@')
    giturl[0] = '{}:{}'.format(giturl[0],remote_repo.password)
    giturl = '@'.join(giturl)

    subprocess.call(['git', 'remote', 'add', 'origin', giturl])

    # make initial commit and push (set upstream)
    subprocess.call(['git', 'push', '--set-upstream', 'origin'])