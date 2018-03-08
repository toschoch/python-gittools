#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import click
import subprocess
import os
import pathlib
from contextlib import contextmanager
from .readme import description, package_name as rm_name, add_changelog_version, filename as readme, set_placeholder, versions
from .reposerver import get_repo_server, repository_servers_cfg, RepoServer

def package_name(path='.'):
    """ tries to guess the package name on the readme if any, or the directory name. """
    # title = rm_name(path)
    p = pathlib.Path(path)
    dir_name = p.parent.name
    return dir_name
    # subidr = p.joinpath(title)
    #
    # if dir_name.endswith(title) and subidr.exists() and subidr.is_dir():
    #     # then its most likely a python package
    #     return dir_name



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

@contextmanager
def git_commit_only(pattern, message):
    """ commit only the files according to pattern, stashes the stage. """
    null = open(os.devnull, 'w')
    subprocess.call(['git', 'stash'], stdout=null)
    yield
    subprocess.call(['git', 'add', pattern], stdout=null)
    subprocess.call(['git', 'commit', '-m', message], stdout=null)
    subprocess.call(['git', 'stash','pop'], stdout=null)
    null.close()

def update_readme(url):
    # update readme
    with git_commit_only(readme, "update readme"):
        set_placeholder("<git-url>", url)

def add(remote, url, main_remote=True):
    """ add remote repository to git remotes """
    subprocess.call(['git', 'remote', 'add', remote, url])

    # set git urls in usage section of readme
    if main_remote:
        update_readme(url)

def track(remote):
    """ sets the current branch to track the same branch on the remote. """
    branch = subprocess.check_output(['git', 'branch']).decode('utf-8').lstrip('* ').rstrip('\n ')
    subprocess.check_output(['git','branch','-u','{}/{}'.format(remote, branch)])

def push(srv: RepoServer, main_remote=True):
    """ pushes to the repository server """

    #TODO: find a solution to call and pass username and pw
    click.echo("if prompted, use user: {}, pw: {}".format(srv.username,srv.password))
    if main_remote:
        subprocess.call(['git', 'push', '--set-upstream', srv.name])
        subprocess.call(['git', 'push', '--tags', srv.name])
    else:
        subprocess.call(['git', 'push', srv.name])
        subprocess.call(['git', 'push', '--tags', srv.name])

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
@click.argument('remote')
def default(remote):
    """ sets the remote server REMOTE as default remote and updates the readme. """

    srv = get_repo_server(remote)
    repo = srv.get_repository(package_name())

    update_readme(repo.giturl)
    track(remote)


@gittool.command()
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


@gittool.command()
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