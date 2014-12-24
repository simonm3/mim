#!/usr/bin/env python

"""
simple setup.py with common defaults

assumptions:
    the project uses git and github
    scripts are in scripts folder

Configuration files (if missing then assumed blank):
    requirements.txt => list of dependencies to be installed
    README.*         => first found is long_description
    LICENSE.txt      => license
    version.py       => contains __version__
    .gitignore       => files to exclude from git and installation
No other configuration files are needed

To publish to pypi and github:
    set __version__ in version.py
    git commit -a -m "message" push
    setup.py register sdist upload => register metadata; tar source; upload to pypi

Note do not use setup.py install or pip install
"""
from tools.logs import log
from setuptools import setup, find_packages
from subprocess import check_output
import os
import glob

try:
    from version import __version__
except:
    __version__ = ""
here = os.path.abspath(os.path.dirname(__file__))
os.chdir(here)

def main():
    setupdict = defaultSetup()

    ###### add bespoke configuration here #######

    setupdict["classifiers"]= [ \
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python']

    ################################################

    # remove any scripts not managed by git
    try:
        gitfiles = check_output(["git", "ls-files"])
        setupdict["scripts"] = [s for s in setupdict["scripts"] if s in gitfiles]
    except:
        # install machine may not have git installed
        pass
    
    # log the configuration
    output=""
    for k,v in setupdict.items():
        if k == "long_description":
            v=v[:25]
        output+="{k}={v}\n".format(**locals())
    log.info(output)

    setup(**setupdict)

def defaultSetup():
    name = here.split("/")[-1]

    setupdict=dict(
        # setuptools_git ensures .tar.gz includes all git tracked files
        setup_requires = ["setuptools_git >= 0.3"], 
        author       = 'simon',
        author_email = 'simonm3@gmail.com',
        name         = name,
        version      = __version__,
        description  = name,
        long_description = long_description(),
        url =  'https://github.com/simonm3/{name}'.format(**locals()),
        install_requires = install_requires()
        include_package_data = True

        # REQUIRED IF PIP INSTALL EVER USED
        ###### pip install ignores tar.gz files unless specified below
        #data_files = [('data', [f for f in glob.glob(os.path.join(here, 'data/*'))]),
        #              ('', ['requirements.txt'])                    ],
        packages     = find_packages(),
        scripts = [f for f in glob.glob(os.path.join(here, 'scripts/*') if os.path.isfile(f)]
        )
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

main()