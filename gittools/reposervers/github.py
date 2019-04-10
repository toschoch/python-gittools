#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 09.04.2019
# author:  TOS

import logging
import urllib
import github

from .reposerver import RepoServer

log = logging.getLogger(__name__)


class Github(RepoServer):

    def __init__(self, name, url="https://github.com/", **kwargs):
        RepoServer.__init__(self)
        self.name = name
        self.url = urllib.parse.urlparse(url)

        self.login_info = {}
        self.repo_info = {}

        self.ssh = kwargs.get('ssh', False)
        self.repo_info.update(kwargs.get('newrepo', {}))
        self.login_info.update(kwargs.get('login', {}))

        # First create a Github instance:
        if not 'Token' in self.login_info:
            self.username = self.login_info['Username']
            self.password = self.login_info['Password']

            # using username and password
            self.api = github.Github(self.username, self.password)
        else:
            self.token = self.login_info['Token']

            self.api = github.Github(self.token)

        self.user = self.api.get_user()

    def create_repository(self, name, description, **info):
        repo = self.user.create_repo(name=name, description=description, **info)
        if self.ssh:
            return self.Repo(repo.name, repo.id, repo.ssh_url)
        else:
            return self.Repo(repo.name, repo.id, repo.clone_url)

    def delete_repository(self, name):
        repo = self.user.get_repo(name)
        repo.delete()

    def get_repository(self, name):
        repo = self.user.get_repo(name)
        if self.ssh:
            return self.Repo(repo.name, repo.id, repo.ssh_url)
        else:
            return self.Repo(repo.name, repo.id, repo.clone_url)

    def repository_exists(self, name):
        try:
            self.user.get_repo(name)
            return True
        except:
            return False