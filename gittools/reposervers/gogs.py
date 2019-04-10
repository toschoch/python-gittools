#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 09.04.2019
# author:  TOS

import urllib
import logging

from .reposerver import RepoServer

log = logging.getLogger(__name__)

class Gogs(RepoServer):

    def __init__(self, name, url, **kwargs):
        RepoServer.__init__(self)

        import gogs_client

        self.name = name
        self.url = urllib.parse.urlparse(url)

        self.login_info = {}
        self.repo_info = {}

        self.ssh = kwargs.get('ssh', False)
        self.repo_info.update(kwargs.get('newrepo', {}))
        self.login_info.update(kwargs.get('login', {}))

        self.api = gogs_client.GogsApi(self.url.geturl())

        if not 'Token' in self.login_info:
            self.username = self.login_info['Username']
            self.password = self.login_info['Password']

            self.auth = gogs_client.UsernamePassword(self.username, self.password)
            tokens = self.api.get_tokens(self.auth, "gittools")
            if len(tokens) > 0:
                self.token = tokens[0]
            else:
                self.token = self.api.create_token(self.auth, "gittools")
        else:
            self.token = gogs_client.Token(self.login_info['Token'], "gittools")


    def create_repository(self, name, description, **info):
        repo_info = self.repo_info.copy()
        repo_info.update(info)
        if not self.api.repo_exists(self.token, self.username, name):
            repo = self.api.create_repo(self.token, name=name, description=description, **repo_info)
        else:
            repo = self.api.get_repo(self.token, self.username, name)
        if self.ssh:
            return self.Repo(repo.name, repo.id, repo.urls.ssh_url)
        else:
            return self.Repo(repo.name, repo.id, repo.urls.clone_url)

    def repository_exists(self, name):
        return self.api.repo_exists(self.token, self.username, name)

    def get_repository(self, name):
        repo = self.api.get_repo(self.token, self.username, name)
        if self.ssh:
            return self.Repo(repo.name, repo.id, repo.urls.ssh_url)
        else:
            return self.Repo(repo.name, repo.id, repo.urls.clone_url)

    def delete_repository(self, name):
        self.api.delete_repo(self.token, self.username, name)