#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import click
import pathlib
import subprocess
import os
from contextlib import contextmanager

from .reposerver import get_repo_server, repository_servers_cfg
from .readme import set_placeholder, filename as readme, description
from .reposerver import RepoServer

git_exception = EnvironmentError('gittools need Git to be installed on your machine! Install Git first...')

@contextmanager
def git_commit_only(pattern, message):
    """ commit only the files according to pattern, stashes the stage. """
    null = open(os.devnull, 'w')
    if subprocess.call(['git', 'stash'], stdout=null) != 0:
        raise git_exception
    yield
    subprocess.call(['git', 'add', pattern], stdout=null)
    subprocess.call(['git', 'commit', '-m', message], stdout=null)
    subprocess.call(['git', 'stash','pop'], stdout=null)
    null.close()


def package_name(path='.'):
    """ tries to guess the package name on the readme if any, or the directory name. """
    # title = rm_name(path)
    p = pathlib.Path(path).absolute()
    dir_name = p.name
    return dir_name
    # subidr = p.joinpath(title)
    #
    # if dir_name.endswith(title) and subidr.exists() and subidr.is_dir():
    #     # then its most likely a python package
    #     return dir_name


def track(remote):
    """ sets the current branch to track the same branch on the remote. """
    try:
        branch = subprocess.check_output(['git', 'branch']).decode('utf-8').lstrip('* ').rstrip('\n ')
    except FileNotFoundError:
        raise git_exception
    subprocess.check_output(['git','branch','-u','{}/{}'.format(remote, branch)])

def update_readme(url):
    # update readme
    with git_commit_only(readme, "update readme"):
        set_placeholder("<git-url>", url)


@click.pass_context
def add(ctx, remote, url, main_remote=True):
    """ add remote repository to git remotes """
    try:
        if subprocess.call(['git', 'remote', 'add', remote, url]) != 0:
            click.echo("Git repository not yet initialized. Initialize...")
            from .cli import init
            ctx.invoke(init)

    except FileNotFoundError:
        raise git_exception

    # set git urls in usage section of readme
    if main_remote:
        update_readme(url)

def push(srv: RepoServer, main_remote=True):
    """ pushes to the repository server """

    #TODO: find a solution to call and pass username and pw
    click.echo("if prompted, use user: {}, pw: {}".format(srv.username,srv.password))
    if main_remote:
        if subprocess.call(['git', 'push', '--set-upstream', srv.name, "master"]) != 0:
            raise git_exception
        subprocess.call(['git', 'push', '--tags', srv.name])
    else:
        if subprocess.call(['git', 'push', srv.name, "master"]) != 0:
            raise git_exception
        subprocess.call(['git', 'push', '--tags', srv.name])

@click.group()
def remote():
    """ create and setup remote repositories """

@remote.command()
def list():
    """ list the configured remote repository servers. """
    remotes = repository_servers_cfg()
    if len(remotes) > 0:
        click.echo("following remote repository servers are configured:")
    for name, cfg in remotes.items():
        click.echo("{}\t{}".format(name, cfg.get('url','...')))

@remote.command()
@click.argument('remote')
def default(remote):
    """ sets the remote server REMOTE as default remote and updates the readme. """

    srv = get_repo_server(remote)
    repo = srv.get_repository(package_name())

    update_readme(repo.giturl)
    track(remote)


@remote.command()
@click.argument('remote')
@click.option('--setup/--no-setup', default=True, help="setup as remote repository after creation")
@click.option('--default/--no-default', default=True, help="define as default remote repository, if setup")
def create(remote, setup, default):
    """ creates a remote git repository on the selected repository server REMOTE. """
    srv = get_repo_server(remote)
    repo = srv.create_repository(package_name(), description())

    if setup:
        # add
        add(srv.name, repo.giturl, default)
        # push to server
        push(srv, default)


@remote.command()
@click.argument('remote')
@click.option('--default/--no-default', default=True, help="define as default remote repository")
def setup(remote, default):
    """ setup the remote repository on the server as git remote. """
    srv = get_repo_server(remote)
    repo = srv.get_repository(package_name())

    # add as remote repo
    add(srv.name, repo.giturl, default)

    # push to server
    push(srv, default)