#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 09.04.2019
# author:  TOS

import logging
import urllib
from .reposerver import RepoServer

log = logging.getLogger(__name__)

class Gitlab(RepoServer):

    def __init__(self, name, url, **kwargs):

        import gitlab

        self.name = name
        self.url = urllib.parse.urlparse(url)

        self.login_info = {}
        self.repo_info = {}

        self.ssh = kwargs.get('ssh', False)
        self.repo_info.update(kwargs.get('newrepo', {}))
        self.login_info.update(kwargs.get('login', {}))

        self.token = self.login_info['Token']

        self.api = gitlab.Gitlab(self.url.geturl(), private_token=self.token)
        self.username = self.login_info['Username']

        self.group = None
        all_groups = self.api.groups.list(all=True, as_list=False)
        for group in all_groups:
            if group.name == self.repo_info['group']:
                self.group = group
                self.group_id = group.id
                break
        assert self.group is not None

        self.project_ids = {}


    def create_repository(self, name, description, **info):
        repo_info = self.repo_info.copy()
        repo_info.update(info)
        if not self.repository_exists(name):
            repo_info['name'] = name
            repo_info['description'] = description
            repo_info['namespace_id'] = self.group_id
            repo = self.api.projects.create(repo_info)
        else:
            repo = self.api.projects.get('{}/{}'.format(self.group.path, name))

        if self.ssh:
            return self.Repo(repo.name, repo.id, repo.ssh_url_to_repo)
        else:
            return self.Repo(repo.name, repo.id, repo.http_url_to_repo)

    def repository_exists(self, name):
        import gitlab
        try:
            if name not in self.project_ids:
                project = self.api.projects.get('{}/{}'.format(self.group.path, name))
                self.project_ids[project.name] = project.id
            else:
                project = self.api.projects.get(self.project_ids[name])
            return True
        except gitlab.exceptions.GitlabGetError:
            return False

    def get_repository(self, name):
        if name not in self.project_ids:
            repo = self.api.projects.get('{}/{}'.format(self.group.path, name))
            self.project_ids[repo.name] = repo.id
        else:
            repo = self.api.projects.get(self.project_ids[name])
        if self.ssh:
            return self.Repo(repo.name, repo.id, repo.ssh_url_to_repo)
        else:
            return self.Repo(repo.name, repo.id, repo.http_url_to_repo)

    def delete_repository(self, name):
        if name not in self.project_ids:
            repo = self.api.projects.get('{}/{}'.format(self.group.path, name))
            self.project_ids[repo.name] = repo.id
        else:
            repo = self.api.projects.get(self.project_ids[name])
        repo.delete()