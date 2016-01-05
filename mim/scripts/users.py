#!/usr/bin/env python

# shows users

import logging as log
from mim.bash import route, nmap, nbtscan, ifconfig
import socket

def hostsort(host):
    """ returns ip as binary for sorting """
    if not host.ip:
        return None
    else:
        return socket.inet_aton(host.ip)

def getUsers():
    """ prints list of ip, MAC, hardware, netbios """

    log.info("listing users")
    
    # get data
    router = route().ifaces[0]
    subnet =  router.ip +  "/24"
    nmap1 = nmap("-sn -n %s" % subnet)
    nbtscan1 = nbtscan(subnet)
    ifconfig1 = ifconfig()
    
    #use nmap as base
    hosts = nmap1.hosts
    
    # add current machine
    thispc = next((iface for iface in ifconfig1.ifaces \
                    if iface.name == "wlan0"), None)
    if not thispc:
        thispc = next((iface for iface in ifconfig1.ifaces \
                    if iface.name == "eth0"), None)
    for host in hosts:
        if host.ip == thispc.ip: 
            host.ip = thispc.ip
            host.mac = thispc.mac
            break
    
    # format nbtscan as dict of ip=>netbios
    nbt = dict()
    for host in nbtscan1.hosts:
        nbt[host.ip] = host.netbios 

   # add netbios
    for host in hosts:
        if host.ip == router.ip:
            host.netbios = "** router **"
        elif host.ip == thispc.ip:
            host.netbios = "** this pc **"
        else:
            host.netbios = nbt.get(host.ip, "")
    
    # print formatted
    try:
        nmap1.hosts = sorted(nmap1.hosts, key=hostsort)
    except Exception as e:
        log.error("Problem sorting ip addresses\n%s"%e)
    format1 = '{0:<15} {1:<17} {2:<15} {3:<15}'
    print(format1.format("ip", "mac", "hardware", "netbios"))
    print(format1.format("==", "===", "========", "======="))
    for host in nmap1.hosts:
        print(format1.format(host.ip, host.mac or "", 
                             host.hw or "", host.netbios or ""))

log.getLogger().setLevel(log.INFO)
getUsers()