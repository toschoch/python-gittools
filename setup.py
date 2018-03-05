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

changelog = read('README.md').splitlines()
for i,line in enumerate(changelog):
    if line.startswith('Change-Log'):
        line = changelog[i+1]
        j = 1
        while line.strip()=='' or line.startswith('---'):
            j += 1
            line = changelog[j]
        version = line.strip('# ')
        break


# get the dependencies and installs
all_reqs = []
for line in read('conda_reqs.txt').splitlines():
    if line.startswith('#'): continue # except only comments
    if line.strip().endswith('conda'): continue # except lines marked as only conda
    line = line.split('#')[0] # except comments
    line = "==".join(line.split('=')[:2]) # except conda second version spec
    all_reqs.append(line)

all_reqs += read('requirements.txt').splitlines()

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip() for x in all_reqs if x.startswith('git+')]

setup(
    name='python-gittools',
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
        'gittools = gittools.cli:gittools'
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
