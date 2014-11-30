#!/usr/bin/env python

"""
simple setup.py with common defaults

assumptions:
    the project uses git and github.

Configuration files (if missing then assumed blank):
    requirements.txt => list of dependencies to be installed
    README.*         => first found is long_description
    version.py       => contains __version__
    .gitignore       => files to exclude from git and installation
No other configuration files are needed

To publish to pypi:
    set __version__ in version.py
    git commit -a -m "message" push
    setup.py register sdist upload => register metadata; tar source; upload to pypi

To install:
    pip install <name>
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
          'Programming Language :: Python'
        ]

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
    name = here.split("/")[-1]
    datafiles = [f for f in glob.glob(os.path.join(here, 'data/*'))]

    setupdict=dict(
        # setuptools_git makes install use git tracked files as a base
        setup_requires = ["setuptools_git >= 0.3"], 
        author       = 'simon',
        author_email = 'simonm3@gmail.com',
        name         = name,
        version      = __version__,
        description  = name,
        long_description = long_description(),
        url =  'https://github.com/simonm3/{name}'.format(**locals()),
        install_requires = install_requires(),

        data_files = [('data', datafiles),
                      ('', ['requirements.txt'])
                    ],
        packages     = find_packages(exclude = ['contrib*', 'tests*', 'docs*']),
        include_package_data=True,
        scripts = [f for f in os.listdir(here) if os.path.isfile(f)
                   and f.endswith(".py") and f not in ("setup.py")]
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
################### notes on potential changes #################
""" 
setuptools_git sets distribution to include the same files as tracked by git

for binary distributions OR if you want to use different distribution from git files....
        data_files = ['data/*.*', 'requirements.txt'],
        packages     = find_packages(exclude = ['contrib*', 'tests*', 'docs*']),
        scripts = [f for f in os.listdir(here) if os.path.isfile(f)
                   and f.endswith(".py") and f != "setup.py"
                   and f in check_output(["git", "ls-files"])],
        include_package_data=True
Note:
    data_files MUST include requirements.txt for setup to work
    scripts probably want to exclude files not git tracked as above
    binary distribution requires other changes too e.g to pythonpath, path
"""