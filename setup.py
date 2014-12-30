#!/usr/bin/env python

"""
simple setup.py with common defaults

Configuration files (all optional):
    requirements.txt => list of dependencies to be installed
    README.*         => first found is long_description
    LICENSE.txt      => license
    version.py       => contains __version__
    .gitignore       => files to exclude from git and installation
    everything in the scripts folder is treated as a script
    setup.cfg        => metadata section for setup. adds further data and overrides the above

To publish to pypi and github:
    set __version__ in version.py
    git commit -a -m "message" push
    setup.py register sdist upload => register metadata; tar source; upload to pypi
"""
import ConfigParser
from tools.logs import log
from setuptools import setup, find_packages
from subprocess import check_output
import os
import sys

try:
    from version import __version__
except:
    __version__ = ""
here = os.path.abspath(os.path.dirname(__file__))
os.chdir(here)

def main():
    log.info("***** running setup.py with args=%s *****"%sys.argv)

    setupdict = defaultSetup()
    setupdict.update(cfgSetup())
    logsetup(setupdict)    
    setup(**setupdict)

def defaultSetup():
    """ returns default dict """
    name = here.split("/")[-1]
    setupdict=dict(
    	# basic settings to create sdist tar with files under version control
        name = name,
        description = name,
        setup_requires = ["setuptools_git >= 0.3"],
        version      = __version__,
        long_description = long_description(),
        install_requires = install_requires(),
        dependency_links = dependency_links(),
        
        # additional settings for pip install
        packages     = find_packages(),
        include_package_data = True,
        scripts = scripts()
    )
    return setupdict

def cfgSetup():
    """ returns setup.cfg dict """
    c = ConfigParser.ConfigParser(allow_no_value=True)
    try:
        c.readfp(open("setup.cfg"))
        return dict(c.items("metadata"))
    except:
        return dict()

def logsetup(setupdict):
    """ log the setupdict """
    output=""
    for k,v in setupdict.items():
        if k == "long_description":
            v=v.splitlines()[0]
        output+="{k}={v}\n".format(**locals())
    log.info(output)

def scripts():
    """ get files from scripts folder and remove any scripts not managed by git """
    s = ["scripts/"+f for f in os.listdir('scripts')]
    if sys.argv[1] == "sdist":
        gitfiles = check_output(["git", "ls-files"]).splitlines()
        # must remove else any scripts specified are included even if not managed by git
        #s = [script for script in s if script in gitfiles]
    return s

def install_requires():
    """ use requirements.txt """
    try:
        with open("requirements.txt", "r") as f:
            reqs = [req.split("#")[0].strip() for req in f.read().splitlines()]
            install_requires = [req for req in reqs if not req.startswith("http")]
            return install_requires
    except IOError:
        return []
    except:
        log.exception("problem parsing install_requires")
        sys.exit()

def dependency_links():
    """ use requirements.txt """
    try:
        with open("requirements.txt", "r") as f:
            reqs = [req.split("#")[0].strip() for req in f.read().splitlines()]
            dependency_links = [req for req in reqs if req.startswith("http")]
            return dependency_links
    except IOError:
        return []
    except:
        log.exception("problem parsing dependency_links")
        sys.exit()

def long_description():
    """ set long description = first README.* """
    try:
        readme = [f for f in os.listdir(here) if f.startswith("README")][0]
        with open(readme, "r") as f:
    	    return f.read()
    except:
     	return ""

main()