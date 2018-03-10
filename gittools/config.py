#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 06.03.2018
# author:  TOS

import logging
import pathlib
import shutil
import yaml

log = logging.getLogger(__name__)

config_file = pathlib.Path.home().joinpath('.gittools')


def assert_cfg():

    if not config_file.exists():
        template = pathlib.Path(__file__).parent.joinpath('.gittools_template.yaml')
        shutil.copy2(src=template, dst=config_file)

def load_cfg():

    if config_file.exists() and config_file.is_file():
        with open(config_file, 'r') as fp:
            config = yaml.load(fp)
        if config is None:
            config = {}
    else:
        config = {}
    if len(config) == 0:
        print("gittool config is empty ({})!".format(config_file))
    return config

# create the config file from template if not yet existing
assert_cfg()

# load the configuration
cfg = load_cfg()

def get_cfg():
    global cfg
    return cfg

def set_cfg(config):
    global cfg
    cfg = config.copy()
