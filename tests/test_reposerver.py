import gittools.reposerver
import pathlib
import requests, bs4

# Sample Test passing with nose and pytest
def test_bonobo_create():

    # template = pathlib.Path(gittools.__path__[0]).joinpath('.gittools_template.yaml')
    #
    # gittools.reposerver.config_file = template


    cfg = gittools.reposerver.configured_repository_servers()

    srv_cfg = cfg['reposervers']['aarau']
    srv_cfg['name'] = 'aarau'
    srv_type = getattr(gittools.reposerver,srv_cfg.pop('type'))

    srv = srv_type(**cfg['reposervers']['aarau'])
    repo = srv.create_repository('testrepo3','this is a test repo')

def test_config():

    srv = gittools.reposerver.get_repo_server('aarau')
    print(srv)


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