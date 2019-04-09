#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import logging
import importlib

from ..config import get_cfg

log = logging.getLogger(__name__)


def repository_servers_cfg():
    return get_cfg()['reposervers'].copy()


class RepoServer(object):
    class Repo(object):

        def __init__(self, name, id, giturl):
            self.id = id
            self.name = name
            self.giturl = giturl

    def __init__(self, **kwargs):
        self.username = None
        self.password = None
        self.name = None
        raise NotImplementedError()

    def create_repository(self, name, description, **info):
        raise NotImplementedError()

    def delete_repository(self, name):
        raise NotImplementedError()

    def get_repository(self, name) -> Repo:
        raise NotImplementedError()

    def repository_exists(self, name):
        raise NotImplementedError()


def get_repo_server(name) -> RepoServer:
    cfg = repository_servers_cfg()

    srv_cfg = cfg[name].copy()
    srv_cfg['name'] = name
    repo_type = srv_cfg.pop('type')
    m = importlib.import_module(repo_type.lower())
    srv_type = getattr(m, repo_type)

    srv = srv_type(**srv_cfg)
    return srv
