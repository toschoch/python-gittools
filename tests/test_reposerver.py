import requests, bs4
import contextlib
import gittools.config as config
import gittools.reposerver
import pathlib
import pytest
from unittest.mock import MagicMock, Mock


@contextlib.contextmanager
def change_config(newname):
    old = config.config_file
    config.config_file = pathlib.Path(newname)
    config.assert_cfg()
    config.cfg = config.load_cfg()
    yield
    config.config_file = old


def test_reposerver_cfg(tmpdir):

    tmp_cfg_file = tmpdir.join('.gittools')

    assert not tmp_cfg_file.exists()
    with change_config(tmp_cfg_file):
        cfg = gittools.reposerver.repository_servers_cfg()
        assert tmp_cfg_file.exists()

    for name in ['bonobo','github','gogs']:
        assert 'url' in cfg[name]
        if name == 'bonobo':
            assert cfg[name]['url'] == '<url>'
        assert cfg[name]['login']['Username'] == '<username>'
        assert cfg[name]['login']['Password'] == '<password>'

# Sample Test passing with nose and pytest
def test_bonobo_create(request):

    here = pathlib.Path(request.module.__file__).parent
    htmls = here.joinpath('test_htmls')

    srv_cfg = {
        'name': 'Bonobo',
        'url': 'http://scmserver:8080',
        'login': {
            'Username': '<user>',
            'Password': '<'
        }
    }


    session = MagicMock()

    files = ['bonobo_login1.html','bonobo_repo_create1.html','bonobo_repo_create3.html']
    gets = []
    for fn in files:
        with open(htmls.joinpath(fn),'rb') as fp:
            r = Mock()
            r.content = fp.read()
            gets.append(r)

    files = ['bonobo_login2.html','bonobo_repo_create2.html']
    posts = []
    for fn in files:
        with open(htmls.joinpath(fn), 'rb') as fp:
            r = Mock()
            r.content = fp.read()
            r.text = 'Repository was created successfully.'
            posts.append(r)

    session.get = Mock(side_effect=gets)
    session.post = Mock(side_effect=posts)

    session_ctx = MagicMock()
    session_ctx.__enter__  = Mock(return_value=session)
    session_ctx_factory = Mock(return_value=session_ctx)

    import requests
    requests.Session = session_ctx_factory

    srv = gittools.reposerver.Bonobo(**srv_cfg)

    with pytest.raises(KeyError):
        srv.create_repository('testrepo4','this is a test repo')


    with pytest.raises(AssertionError):
        srv.create_repository('testrepo4','this is a test repo', Administrators=[])

    repo = srv.create_repository('testrepo4','this is a test repo', Administrators=['Tobias Schoch'])

    assert repo != None


# def test_gogs():
#
#     srv_cfg = {'type': 'Gogs', 'url': 'https://try.gogs.io/', 'newrepo': {'private': False}, 'login': {
#         'Username': '<username>',
#         'Password': '<password>'}, 'name': 'gogs'}
#     srv_type = gittools.reposerver.Gogs(**srv_cfg)
#
#     srv = srv_type(**srv_cfg)
#
#     print(srv.ssh)
#
#     if not srv.api.repo_exists(srv.auth, srv.username, "testrepo"):
#         repo = srv.create_repository('testrepo', 'this is a test repo')
#     else:
#         repo = srv.api.get_repo(srv.auth, srv.username, 'testrepo')
#     print(repo.giturl)
#
#     srv.delete_repository('testrepo')
#
#
# def test_github():
#
#     cfg = gittools.reposerver.repository_servers_cfg()
#
#     srv_cfg = cfg['github'].copy()
#     srv_cfg['name'] = 'github'
#     srv_type = getattr(gittools.reposerver, srv_cfg.pop('type'))
#
#     srv = srv_type(**srv_cfg)
#
#     print(srv.ssh)
#
#     if not srv.repository_exists('testrepo'):
#         repo = srv.create_repository('testrepo', 'this is a test repo')
#     else:
#         repo = srv.get_repository('testrepo')
#     print(repo.giturl)
#
#     srv.delete_repository('testrepo')