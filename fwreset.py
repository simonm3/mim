#!/usr/bin/env python

# this resets all iptables settings

from tools import su
from logs import log

su("sysctl net.ipv4.ip_forward=0 >/dev/null")

# reset defaults for filter, nat and mangle
su("iptables -P INPUT ACCEPT")
su("iptables -P FORWARD ACCEPT")
su("iptables -P OUTPUT ACCEPT")
su("iptables -t nat -P PREROUTING ACCEPT")
su("iptables -t nat -P POSTROUTING ACCEPT")
su("iptables -t nat -P OUTPUT ACCEPT")
su("iptables -t mangle -P PREROUTING ACCEPT")
su("iptables -t mangle -P OUTPUT ACCEPT")

# flush rules
su("iptables -F")
su("iptables -t nat -F")
su("iptables -t mangle -F")

# erase chains
su("iptables -X")
su("iptables -t nat -X")
su("iptables -t mangle -X")

# set new rules
su("iptables -A INPUT -i lo -j ACCEPT")

log.info("iptables has been reset")