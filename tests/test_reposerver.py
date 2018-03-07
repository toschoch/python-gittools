import gittools.reposerver
import requests, bs4

# Sample Test passing with nose and pytest
def test_bonobo_create():

    cfg = gittools.reposerver.repository_servers_cfg()

    srv_cfg = cfg['aarau'].copy()
    srv_cfg['name'] = 'aarau'
    srv_type = getattr(gittools.reposerver,srv_cfg.pop('type'))

    srv = srv_type(**srv_cfg)
    # repo = srv.create_repository('testrepo3','this is a test repo')

def test_config():

    srv = gittools.reposerver.get_repo_server('aarau')
    # print(srv)
    assert str(srv).startswith('<gittools.reposerver.Bonobo object at')


def test_bonobo_requests():

    payload = {
        'Username': 'tos',
        'Password': 'GitAarau18'
    }

    # Use 'with' to ensure the session context is closed after use.
    with requests.Session() as s:

        r = s.get('http://scmserver:8080/Repository/Create')
        # print(r.text)

        bs = (bs4.BeautifulSoup(r.content, "html.parser"))
        for tag in bs.find_all("input", type="hidden"):
            if tag.attrs['name'] == '__RequestVerificationToken':
                payload[tag.attrs['name']] = tag.attrs['value']
                break

        p = s.post('http://scmserver:8080/Home/LogOn', data=payload)
        # print the html returned or something more intelligent to see if it's a successful login page.
        assert (p.text.find('500 Server Error')<0)


def test_gogs():


    cfg = gittools.reposerver.repository_servers_cfg()

    srv_cfg = cfg['nas'].copy()
    srv_cfg['name'] = 'nas'
    srv_type = getattr(gittools.reposerver, srv_cfg.pop('type'))

    srv = srv_type(**srv_cfg)

    print(srv.ssh)

    if not srv.api.repo_exists(srv.auth, srv.username, "testrepo"):
        repo = srv.create_repository('testrepo', 'this is a test repo')
    else:
        repo = srv.api.get_repo(srv.auth, srv.username, 'testrepo')
    print(repo.giturl)

    srv.delete_repository('testrepo')


def test_github():

    cfg = gittools.reposerver.repository_servers_cfg()

    srv_cfg = cfg['github'].copy()
    srv_cfg['name'] = 'github'
    srv_type = getattr(gittools.reposerver, srv_cfg.pop('type'))

    srv = srv_type(**srv_cfg)

    print(srv.ssh)

    if not srv.repository_exists('testrepo'):
        repo = srv.create_repository('testrepo', 'this is a test repo')
    else:
        repo = srv.get_repository('testrepo')
    print(repo.giturl)

    srv.delete_repository('testrepo')