#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import click
import subprocess
from .readme import description, package_name, add_changelog_version, filename as readme, set_placeholder, versions
from .reposerver import get_repo_server, repository_servers_cfg, RepoServer


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


def git_commit_only(pattern, message):
    """ commit only the files according to pattern, stashes the stage. """
    subprocess.call(['git', 'stash'])
    subprocess.call(['git', 'add', pattern])
    subprocess.call(['git', 'commit', '-m', message])
    subprocess.call(['git', 'stash','pop'])


def add(srv : RepoServer, repo : RepoServer.Repo, main_remote=True):
    """ add remote repository to git remotes """
    subprocess.call(['git', 'remote', 'add', srv.name, repo.giturl])

    # set git urls in usage section of readme
    if main_remote:
        # update readme
        set_placeholder("<git-url>",repo.giturl)
        # add
        git_commit_only(readme, "update readme")

def push(srv: RepoServer, main_remote=True):
    """ pushes to the repository server """

    #TODO: find a solution to call and pass username and pw
    click.echo("if prompted, use user: {}, pw: {}".format(srv.username,srv.password))
    if main_remote:
        subprocess.call(['git', 'push', '--tags', '--set-upstream', srv.name])
    else:
        subprocess.call(['git', 'push', '--tags', srv.name])

@click.group()
def gittool():
    """ CLI tool to setup git remote repositories. """

@gittool.command()
def list():
    """ list the configured remote repository servers. """
    remotes = repository_servers_cfg().items()
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
@click.argument('remote', help='remote repository server name. [{}]'.format(', '.join(repository_servers_cfg().keys())))
@click.option('--setup/--no-setup', default=True, help="setup as remote repository after creation")
@click.option('--default/--no-default', default=True, help="define as default remote repository, if setup")
def create(remote, setup, default):
    """ creates a remote git repository on the selected repository server. """
    srv = get_repo_server(remote)
    repo = srv.create_repository(package_name(), description())

    if setup:
        add(srv, repo, default)


@gittool.command()
@click.argument('remote', help='remote repository server name. [{}]'.format(', '.join(repository_servers_cfg().keys())))
@click.option('--default/--no-default', default=True, help="define as default remote repository")
def setup(remote, default):
    """ setup the remote repository on the server as git remote. """
    srv = get_repo_server(remote)
    repo = srv.get_repository(package_name())

    # add as remote repo
    add(srv, repo, default)


@gittool.command()
@click.argument('tagname', type=str, help='name of the version to be created')
@click.option('-m', '--message',  multiple=True, help='optional message for annotated tags')
def tag(tagname, message):
    """ updates the version changelog in readme and creates the tag. """
    # get all tags
    tags = get_tags()
    lasttag = tags[0]

    # commit messages
    msgs = subprocess.check_output(['git','log','--oneline','{}..@'.format(lasttag)]).decode('utf-8').splitlines()
    msgs = [' '.join(m.split(' ')[1:]) for m in msgs]

    # insert into readme
    add_changelog_version(tagname.lstrip('v'), points=msgs)

    # add readme, and commit
    git_commit_only(readme, 'update {} for tag {}'.format(readme, tagname))

    # create the tag
    if message == "":
        subprocess.call(['git', 'tag', tagname])
    else:
        subprocess.call(['git', 'tag', tagname, '-m', '{}'.format("\n".join(message))])