#!/usr/bin/env python

"""
This file provides a standard setup.py for use with any python/git source distribution.
The defaults can be overridden using setup.cfg

Defaults:
    name             = root folder name
    description      = root folder name
    install_requires = requirements.txt
    dependency_links = requirements.txt lines starting http
    long_description = first README.*
    license          = first line of LICENSE.txt
    version          = root/version.py with a line such as __version__ = "9.9.9"
    included files   = everything managed by git (see git ls-files)
    excluded files   = .gitignore
    scripts          = files in bin folder

Example of setup.cfg to override defaults:
    [metadata]
        name=myproject # overrides default setting
        author=simon   # adds new setting
    [setup]
        autoinc = 0,1,2 # increments major/minor/micro version when you call setup.py sdist

To submit to pypi for first time
    setup.py register sdist upload

To submit to pypi 2nd time
    setup.py sdist upload

To upload to github after setup run (setup.py stages changes but does not commit)
    git commit -am <message> push

To install:
    pip install <name>
"""
import ConfigParser
from mim.tools.logs import log
from setuptools import setup, find_packages
import pkg_resources
from subprocess import check_output
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
os.chdir(here)

try:
    from version import __version__
except:
    __version__ = "0.0.0"
    with open("version.py", "w") as f:
        f.write("__version__='%s'"%__version__)

def main():
    log.info("***** running setup.py with args=%s *****"%sys.argv)
    
    # get setup.cfg
    c = ConfigParser.ConfigParser(allow_no_value=True)
    try:
        c.readfp(open("setup.cfg"))
    except:
        log.warning("setup.cfg not found")
        c = None

    if "sdist" in sys.argv:
        updateversion(c)
        # update git with new and deleted files to ensure correct files included
        try:
            check_output(["git", "add", "-A"])
        except:
            log.exception("Error updating git files")
            sys.exit()
        
    setupdict = defaultSetup()
   
    setupdict.update(cfgSetup(c))
    
    logsetup(setupdict)    
    setup(**setupdict)

def updateversion(c):
    global __version__

    # setup.cfg
    try:
        __version__ = c.get("metadata", "version")
        with open("version.py", "w") as f:
            f.write("__version__='%s'"%__version__)
        return
    except ConfigParser.NoOptionError:
        pass
    
    # autoincrement
    try:
        inc = int(c.get("setup", "autoinc"))
        v = pkg_resources.parse_version(__version__)
        vints = map(int, v[:3])
        vints[inc] += 1
        for vint in vints[inc+1:]:
            vint = 0
        __version__ = ".".join(map(str,vints))
        with open("version.py", "w") as f:
            f.write("__version__='%s'"%__version__)
        return
    except ConfigParser.NoOptionError:
        pass

def defaultSetup():
    """ returns default dict """
    name = here.split("/")[-1]
    setupdict=dict(
    	# basic settings to create sdist tar with files under version control
        name = name,
        description = name,
        setup_requires = ["setuptools_git >= 0.3"],
        version      = __version__,
        license = license(),
        long_description = long_description(),
        install_requires = install_requires(),
        dependency_links = dependency_links(),
        
        # additional settings for pip install
        packages     = find_packages(),
        include_package_data = True,
        scripts = scripts(),
        data_files = [('', data_files())]
    )
    return setupdict

def cfgSetup(c):
    """ process setup.cfg and return dict """

    # get metadata section
    try:
        cfg = dict(c.items("metadata"))
        cfg.update({k:v.splitlines() for k,v in cfg.items() if v.find("\n") >=0})
    except:
        cfg = dict()
    
    return cfg

def logsetup(setupdict):
    """ log the setupdict """
    output=""
    for k,v in setupdict.items():
        if k == "long_description":
            v=v.splitlines()[0]
        output+="{k}={v}\n".format(**locals())
    log.info(output)

def license():
    try:
        with open("LICENSE.txt","r") as f:
            return f.readline().strip()
    except:
        return ""

def scripts():
    """ get files from scripts folder and remove any not managed by git """
    files = ["bin/"+f for f in os.listdir('bin') if os.path.isfile("bin/"+f)]
    if "sdist" in sys.argv:
        gitfiles = check_output(["git", "ls-files"]).splitlines()
        # must remove else any scripts specified are included even if not managed by git
        files = [script for script in files if script in gitfiles]
    return files

def data_files():
    """ get files from root folder and remove any not managed by git """
    files = [f for f in os.listdir(here) if os.path.isfile(f)]
    if "sdist" in sys.argv:
        gitfiles = check_output(["git", "ls-files"]).splitlines()
        # must remove else any scripts specified are included even if not managed by git
        files = [f for f in files if f in gitfiles]
    return files

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