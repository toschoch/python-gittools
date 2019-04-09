#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 09.04.2019
# author:  TOS

import logging
import urllib
import bs4
import requests

from .reposerver import RepoServer

log = logging.getLogger(__name__)

class Bonobo(RepoServer):

    def __init__(self, name, url, **kwargs):
        self.name = name
        self.url = urllib.parse.urlparse(url)

        self.login_info = {}
        self.repo_info = {}

        self.repo_info.update(kwargs.get('newrepo', {}))
        self.login_info.update(kwargs.get('login', {}))

        self.username = self.login_info['Username']
        self.password = self.login_info['Password']

    def create_repository(self, name, description, **info):

        repo_info = self.repo_info.copy()

        repo_info['Name'] = name
        repo_info['Description'] = description
        repo_info.update(info)
        adminlist = repo_info.pop('Administrators')
        repo_info['PostedSelectedAdministrators'] = []

        assert len(adminlist) > 0

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

            r = s.get("{}{}".format(self.url.geturl(), repo_detail_link))

            # get the personal git url
            bs = bs4.BeautifulSoup(r.content, "html.parser")
            tag = bs.find("span", {'class': "personal-url-text"})

            log.info("successfully created repository!")

        return self.Repo(repo_info['Name'], repo_detail_link.split('/')[-1], tag.text)

    def get_repository(self, name):
        raise NotImplementedError("Bonobo Server currently not supports the repository lookup.")