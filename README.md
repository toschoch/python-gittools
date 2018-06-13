Git Tools
===============================
author: Tobias Schoch

Overview
--------

A collection of tools to connect to predefined git remote servers and create remote repos, define them as remotes, install local hooks, etc.


Change-Log
----------
##### 0.1.0
* Merge branch 'master' of https://github.com/toschoch/python-gittools
* add branch name into push command
* change gogs authentification
* try to use context for invokint gittool init
* fixed missing commands in drone.yml
* fix syntax error in drone.yml
* on success
* Merge branch 'master' of ssh://dietzi.ddns.net:4022/Tobi/python-gittools
* fixed remote creation if Git repo not yet initialized
* improved error message for Bonobo Git Server
* fixed missing import bug in remote create
* added staging to pipeline
* add staging devpi upload
* Merge branch 'master' of ssh://nas:4022/Tobi/python-gittools
* Devpi publish on drone

##### 0.0.6
* added command for install git hook (windows)
* fixed missing template file
* Merge branch 'master' of ssh://dietzi.ddns.net:4022/Tobi/python-gittools
* some not yet working draft of install hooks
* fixed install script command under UNIX

##### 0.0.5
* added version command
* added install script command for windows and unix
* rearranged commands into a remote group
* added cli tests
* fixed compatibility for data-science projects
##### 0.0.4
* add github support
* add default command
* improved help
* add create command
* initialize local git repo and tag according to versions in readme

##### 0.0.3
* fixed small bugs
* git url set in usage section of readme
* added Gogs support
* add list command

##### 0.0.2
* fixed tests, reads info for remote repo from README.md
* add tag command
* working cli for init and create remote on Bonobo Server

##### 0.0.1
* initial version


Installation / Usage
--------------------

To install use pip:

```
pip install <git-url>
```


Or clone the repo:

```
git clone <git-url>
python setup.py install
```

Example
-------

```
gittool version
```

install a script from the current active conda environment

```
gittool install script <script>
```

Contributing
------------

TBD