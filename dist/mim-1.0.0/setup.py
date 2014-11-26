#!/usr/bin/python

""" simple setup.py with common defaults

Optional configuration files (if missing then assumed blank):
    requirements.txt => install_requires
    README.*         => long_description
    LICENSE.txt      => first line is license
    .py in root      => scripts
    version.py       => contains __version__
    data/*.*         => data files

To publish:
    setup.py register (sends metadata to pypi)
    setup.py sdist (creates tarball of source for uploading to github)

To install:
    pip install <name>
"""
from tools.logs import log
from setuptools import setup, find_packages
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

    setupdict["scripts"].extend(["fwreset", "proxy1"])

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
        data_files = ['data/*.*', 'requirements.txt'],
        packages     = find_packages(exclude = ['contrib*', 'tests*', 'docs*']),
        scripts = [f for f in os.listdir(here) if os.path.isfile(f)
                        and f.endswith(".py") and f != "setup.py"],
        install_requires = install_requires())
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

    dataFiles[name].extend([f for f in os.listdir(here) \
                            if os.path.isfile(f) and f.find(".") < 0])
main()