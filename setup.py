from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

def read(fname):
    with open(path.join(here,fname)) as fp:
        content = fp.read()
    return content

# Get the long description from the README file
long_description = read('README.md')

all_reqs = read('requirements.txt').splitlines()

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip() for x in all_reqs if x.startswith('git+')]

setup(
    name='gittools',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=['setuptools-git-version','pytest-runner'],
    description='description [A python package that can be installed with pip.]: A collection of tools to connect to predefined git remote servers and create remote repos, define them as remotes, install local hooks, etc.',
    long_description=long_description,
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    entry_points={'console_scripts': [
        'gittool = gittools.cli:gittool'
    ]},
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Tobias Schoch',
    install_requires=install_requires,
    tests_require=['pytest'],
    dependency_links=dependency_links,
    author_email='tobias.schoch@helbling.ch'
)
