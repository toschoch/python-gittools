#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 05.03.2018
# author:  TOS

import logging
import six
import bs4
import requests
import subprocess
import os
import pathlib
import yaml
import urllib.parse
import shutil
import json

log = logging.getLogger(__name__)

config_file = pathlib.Path.home().joinpath('.gittools')


def assert_cfg():

    if not config_file.exists():
        template = pathlib.Path(__file__).parent.joinpath('.gittools_template.yaml')
        shutil.copy2(src=template, dst=config_file)

# create the config file from template if not yet existing
assert_cfg()

def configured_repository_servers():
    if config_file.exists() and config_file.is_file():
        with open(config_file, 'r') as fp:
            config = yaml.load(fp)
    else:
        config = {}
    return config

def get_repo_server(name):
    cfg = configured_repository_servers()

    srv_cfg = cfg['reposervers'][name]
    srv_cfg['name'] = name
    srv_type = globals().get(srv_cfg.pop('type'))

    srv = srv_type(**cfg['reposervers'][name])
    return srv

class Bonobo(object):

    class Repo(object):
        hash = None
        name = None
        giturl = None
        user = None
        password = None

    repo_info = {
        "Group": "PythonPackages"
    }

    login_info = {}

    def __init__(self, name, url, **kwargs):
        self.name = name
        self.url = urllib.parse.urlparse(url)
        self.repo_info.update(kwargs.get('newrepo',{}))
        self.login_info.update(kwargs.get('login',{}))

    def create_repository(self, name, description, **repo_info):

        repo_info['Name'] = name
        repo_info['Description'] = description
        repo_info.update(self.repo_info)
        adminlist = repo_info.pop('Administrators')
        repo_info['PostedSelectedAdministrators'] = []

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

            repo = self.Repo()
            repo.hash = repo_detail_link.split('/')[-1]
            repo.name = repo_info['Name']
            repo.giturl = tag.text
            repo.user = login_info['Username']
            repo.password = login_info['Password']

            log.info("successfully created repository!")

        return repo
