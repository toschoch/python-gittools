#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import logging
import six
import bs4
import requests
import gogs_client
import urllib.parse
from .config import cfg


log = logging.getLogger(__name__)


def repository_servers_cfg():
    return cfg['reposervers'].copy()

def get_repo_server(name):
    cfg = repository_servers_cfg()

    srv_cfg = cfg[name].copy()
    srv_cfg['name'] = name
    srv_type = globals().get(srv_cfg.pop('type'))

    srv = srv_type(**srv_cfg)
    return srv

class Repo(object):

    def __init__(self, name, id, giturl):

        self.id = id
        self.name = name
        self.giturl = giturl


class Gogs(object):

    def __init__(self, name, url, **kwargs):

        self.name = name
        self.url = urllib.parse.urlparse(url)

        self.login_info = {}
        self.repo_info = {}

        self.ssh = kwargs.get('ssh', False)
        self.repo_info.update(kwargs.get('newrepo', {}))
        self.login_info.update(kwargs.get('login', {}))

        self.username = self.login_info['Username']
        self.password = self.login_info['Password']

        self.token = gogs_client.Token("gittools")

        self.api = gogs_client.GogsApi(self.url.geturl())
        self.auth = gogs_client.UsernamePassword(self.username, self.password)

    def create_repository(self, name, description, **info):
        repo_info = self.repo_info.copy()
        repo_info.update(info)
        if not self.api.repo_exists(self.auth, self.username, name):
            repo = self.api.create_repo(self.auth, name=name, description=description, **repo_info)
        else:
            repo = self.api.get_repo(self.auth, self.username, name)
        if self.ssh:
            return Repo(repo.name, repo.id, repo.urls.ssh_url)
        else:
            return Repo(repo.name, repo.id, repo.urls.clone_url)

    def delete_repository(self, name):
        self.api.delete_repo(self.auth, self.username, name)


class Bonobo(object):

    def __init__(self, name, url, **kwargs):
        self.name = name
        self.url = urllib.parse.urlparse(url)

        self.login_info = {}
        self.repo_info = {}

        self.repo_info.update(kwargs.get('newrepo',{}))
        self.login_info.update(kwargs.get('login',{}))

        self.username = self.login_info['Username']
        self.password = self.login_info['Password']

    def create_repository(self, name, description, **info):

        repo_info = self.repo_info.copy()

        repo_info['Name'] = name
        repo_info['Description'] = description
        repo_info.update(info)
        adminlist = repo_info.pop('Administrators')
        repo_info['PostedSelectedAdministrators'] = []

        assert len(adminlist)>0

        # create the git repo with push requests
        log.info("create GIT repository on {}...".format(self.name))

        with requests.Session() as s:
            login_info = self.login_info.copy()

            # get request token
            r = s.get("{}/Repository/Create".format(self.url.geturl()), data=login_info)

            bs = bs4.BeautifulSoup(r.content, "html.parser")
            for tag in bs.find_all("input", type="hidden"):
                if tag.attrs['name'] == '__RequestVerificationToken':
                    login_info[tag.attrs['name']] = tag.attrs['value']
                    break

            # log in
            r = s.post("{}/Home/LogOn".format(self.url.geturl()), data=login_info)

            r = s.get("{}/Repository/Create".format(self.url.geturl()))

            bs = bs4.BeautifulSoup(r.content, "html.parser")
            for tag in bs.find_all("input", type="hidden"):
                if tag.attrs['name'] == '__RequestVerificationToken':
                    repo_info[tag.attrs['name']] = tag.attrs['value']
                    break

            # add the login user as administrator
            for tag in bs.find_all("input", type="checkbox"):
                if tag.attrs['name'] == 'PostedSelectedUsers':
                    for lbl in tag.next:
                        if lbl in adminlist:
                            repo_info['PostedSelectedAdministrators'].append(tag.attrs['value'])

            # create the repo
            r = s.post("{}/Repository/Create".format(self.url.geturl()), data=repo_info)
            if r.text.find('Repository was created successfully.') < 0:
                raise ValueError('could not create repository!')

            # get hash of repo
            bs = bs4.BeautifulSoup(r.content, "html.parser")
            tag = bs.find("div", {"class": "summary-success"})
            repo_detail_link = tag.find('a').attrs['href']

            r = s.get("{}{}".format(self.url.geturl(),repo_detail_link))

            # get the personal git url
            bs = bs4.BeautifulSoup(r.content, "html.parser")
            tag = bs.find("span", {'class': "personal-url-text"})

            log.info("successfully created repository!")

        return Repo(repo_info['Name'], repo_detail_link.split('/')[-1], tag.text)

