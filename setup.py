#!/usr/bin/python

""" simple setup.py with common defaults
should be usable without editing for all typical projects

Optional configuration files (if missing then assumed blank):
    requirements.txt => installs all dependencies
    README.*         => long_description
    LICENSE.txt      => first line is license
    version.py       => contains __version__
    .gitignore       => install is same files as git monitorsS

To publish:
    setup.py sdist (creates tarball of source for uploading to github)
    git commit -a -m <message>
    setup.py register (sends metadata to pypi)


To install:
    pip install <name>
"""
from tools.logs import log
from setuptools import setup, find_packages
from subprocess import check_output
import os
try:
    from version import __version__
except:
    __version__ = ""
here = os.path.abspath(os.path.dirname(__file__))
os.chdir(here)

def main():
    setupdict = defaultSetup()

    ###### add bespoke configuration here #######


    #################################################

    # log the configuration
    output=""
    for k,v in setupdict.items():
        if k == "long_description":
            v=v[:25]
        output+="{k}={v}\n".format(**locals())
    log.info(output)

    setup(**setupdict)

def defaultSetup():
    github_user = 'simoneva'
    version = __version__
    name = here.split("/")[-1]

    setupdict=dict(
        setup_requires = ["setuptools_git >= 0.3"],
        author       = 'simon',
        author_email = 'simonm3@gmail.com',
        name         = name,
        version      = version,
        description  = name,
        long_description = long_description(),
        license = license(),
        url =  'https://pypi.python.org/pypi/{name}/{version}'.format(**locals()),
        download_url = 'https://github.com/{github_user}/{name}/dist/{name}-{version}.tar.gz'
                                .format(**locals()),
        install_requires = install_requires(),
        include_package_data=True)
    return setupdict

def install_requires():
    """ set install_requires = requirements.txt """
    with open("requirements.txt", "r") as f:
        try:
            reqs = f.read().splitlines()
            return [r.split("#")[0].strip() for r in reqs]
        except:
        	return []

def long_description():
    """ set long description = first README.* """
    try:
        readme = [f for f in os.listdir(here) if f.startswith("README")][0]
        with open(readme, "r") as f:
    	    return f.read()
    except:
     	return ""

def license():
    """ first line of LICENSE.txt """
    try:
        with open("LICENSE.txt") as f:
            return f.readline().strip()
    except:
        return ""

main()
################### notes on potential changes #################
""" 
default using setuptools_git is to include the same files as monitored by github_user
and ignore the .gitignore

if want to specify files separate to git then....

        data_files = ['data/*.*', 'requirements.txt'],
        packages     = find_packages(exclude = ['contrib*', 'tests*', 'docs*']),
        scripts = [f for f in os.listdir(here) if os.path.isfile(f)
                   and f.endswith(".py") and f != "setup.py"
                   and f in check_output(["git", "ls-files"])],
Note data_files MUST include requirements.txt for setup to work
Note scripts probably would want to only include files in gitfiles
"""