#!/usr/bin/env python

"""
simple setup.py with common defaults

Configuration (all optional):
    root folder name => name and description
    requirements.txt => list of dependencies to be installed
    README.*         => first found is long_description
    LICENSE.txt      => license
    version.py       => contains __version__
    .gitignore       => files to exclude from git and installation
    everything in the bin folder is treated as a script
    setup.cfg        => [metadata] section. adds further data and overrides the above
                        [setup] section. autoinc = 0,1,2 increments major/minor/micro version

To publish to pypi and github:
    git commit -a -m "message" push
    setup.py register sdist upload => register metadata; tar source; upload to pypi
"""
import ConfigParser
from tools.logs import log
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
    setupdict = defaultSetup()
    if sys.argv[1] == "sdist":
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
        scripts = scripts(),
        data_files = [('', data_files())]
    )
    return setupdict

def cfgSetup():
    """ process setup.cfg and return dict """
    
    # get setup.cfg
    c = ConfigParser.ConfigParser(allow_no_value=True)
    try:
        c.readfp(open("setup.cfg"))
    except:
        return dict()
    
    # get metadata section
    try:
        cfg = dict(c.items("metadata"))
        cfg["classifiers"] = cfg["classifiers"].splitlines()
    except:
        cfg = dict()
    
    # autoincrement version
    try:
        inc = int(c.get("setup", "autoinc"))
        v = pkg_resources.parse_version(__version__)
        vints = map(int, v[:3])
        vints[inc] += 1
        cfg["version"] = ".".join(map(str,vints))
        with open("version.py", "w") as f:
            f.write("__version__='%s'"%cfg["version"])
    except:
        pass

    return cfg

def logsetup(setupdict):
    """ log the setupdict """
    output=""
    for k,v in setupdict.items():
        if k == "long_description":
            v=v.splitlines()[0]
        output+="{k}={v}\n".format(**locals())
    log.info(output)

def scripts():
    """ get files from scripts folder and remove any not managed by git """
    files = ["scripts/"+f for f in os.listdir('bin') if os.path.isfile(f)]
    if sys.argv[1] == "sdist":
        gitfiles = check_output(["git", "ls-files"]).splitlines()
        # must remove else any scripts specified are included even if not managed by git
        files = [script for script in files if script in gitfiles]
    return files

def data_files():
    """ get files from root folder and remove any not managed by git """
    files = [f for f in os.listdir(here) if os.path.isfile(f)]
    if sys.argv[1] == "sdist":
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