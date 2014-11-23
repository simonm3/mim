#!/usr/bin/python

""" simple setup.py with common defaults

To publish:
    setup.py register (sends metadata to pypi)
    setup.py sdist (creates tarball of source for uploading to github)
    setup.py bdist_wininst (windows installer)

To install:
    pip install <name>
"""
from tools.logs import log
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

# set info from config file
version=author=author_email=github_user = ""
try:
    from config import version, author, author_email, github_user
except:
    pass

# set name = root folder
name = here.split("/")[-1]

# set install_requires = requirements.txt
req = os.path.join(here, "requirements.txt")
with open(req, "r") as f:
    try:
        reqs = f.read().splitlines()
    	reqs = [r.split("#")[0].rstrip() for r in reqs]
    except:
    	reqs = []

# set long description = first README.*
try:
    readme = [f for f in os.listdir(here) if f.split(".")[0] == "README"][0]
    with open(os.path.join(here, readme)) as f:
	    long_description = f.read()
except:
 	long_description = ""

# set scripts = .py files in project folder
scripts = [f for f in os.listdir(here) if f.endswith(".py") and f not in "setup.py"]

setupdict=dict(
    name = name,
    version = version,
    description = name,
    long_description = long_description,
    url =  'https://pypi.python.org/pypi/%s/%s'%(name, version),
    download_url='https://github.com/{github_user}/{name}/dist/{name}-{version}.tar.gz'
                            .format(**locals()),
    author = author,
    author_email = author_email,
    packages = find_packages(exclude = ['contrib*', 'tests*']),
    scripts = scripts,
    install_requires = reqs)

# log the configuration
output=""
for k,v in setupdict.items():
    if k == "long_description":
        v=v[:25]
    output+="%s = %s\n"%(k,v)
log.info(output)

setup(**setupdict)