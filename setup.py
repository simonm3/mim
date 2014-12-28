#!/usr/bin/env python

"""
simple setup.py with common defaults

Configuration (all optional):
    requirements.txt => list of dependencies to be installed
    README.*         => first found is long_description
    LICENSE.txt      => license
    version.py       => contains __version__
    .gitignore       => files to exclude from git and installation
    everything in the scripts folder is treated as a script

No other configuration files are needed

To publish to pypi and github:
    set __version__ in version.py
    git commit -a -m "message" push
    setup.py register sdist upload => register metadata; tar source; upload to pypi
"""
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
    log.info("***** running setup.py with args=%s"%sys.argv)
    setupdict = defaultSetup()

    ###### add application specific configuration here #######

    setupdict["classifiers"]= [ \
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python']

    ################################################
    logsetup(setupdict)    
    setup(**setupdict)

def defaultSetup():
    name = here.split("/")[-1]

    install_requires, dependency_links = getRequirements()

    setupdict=dict(
    	# basic settings to create sdist tar with files under version control
        setup_requires = ["setuptools_git >= 0.3"],
        author       = 'simon',
        author_email = 'simonm3@gmail.com',
        name         = name,
        version      = __version__,
        description  = name,
        long_description = long_description(),
        url =  'https://github.com/simonm3/{name}'.format(name=name),
        install_requires = install_requires,
        dependency_links = dependency_links,
        
        # additional settings for pip install
        packages     = find_packages(),
        include_package_data = True,
        scripts = scripts()
    )

    return setupdict

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
    try:
        gitfiles = check_output(["git", "ls-files"]).splitlines()
        s = [script for script in s if script in gitfiles]
    except:
        # client may not have git installed
        pass
    return s

def getRequirements():
    """ use requirements.txt """
    with open("requirements.txt", "r") as f:
        try:
            reqs = [req.split("#")[0].strip() for req in f.read().splitlines()]
            dependency_links = [req for req in reqs if req.startswith("http")]
            install_requires = [req for req in reqs if not req.startswith("http")]
            return install_requires, dependency_links
        except:
            log.exception("problem parsing requirements")
            sys.exit()
    return []

def long_description():
    """ set long description = first README.* """
    try:
        readme = [f for f in os.listdir(here) if f.startswith("README")][0]
        with open(readme, "r") as f:
    	    return f.read()
    except:
     	return ""

main()