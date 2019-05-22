#!/usr/bin/python3
import queue
import urllib3
import threading
import urllib.request


threads = 10
target_url = "http://testphp.vulnweb.com/"
wordlist = "/root/WordList/all.txt"
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"


def build_wordlist(wordlist):
    with open(wordlist, 'rb') as fd:
        raw_words = fd.readlines()
        fd.close()

    found_resume = False
    words = queue.Queue()

    for word in raw_words:
        word = word.rstrip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resume wordlist from: {}".format(resume))
        else:
            words.put(word)

    return words


def dir_brute(word_queue, extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []

        # check there is a file extension; else it's a director path we are bruting
        if ".".encode('ascii') not in attempt:
            attempt_list.append("{}".format(attempt))
        else:
            attempt_list.append("{}".format(attempt))

        # brute-force extensions
        if extensions:
            for extension in extensions:
                attempt_list.append("{}{}".format(attempt, extension))

        # iterate over out list of attempts
        for brute in attempt_list:
            url = "{}{}".format(target_url, urllib.request.quote(brute))
            try:
                headers = {}
                headers["User-Agent"] = user_agent
                r = urllib.request.Request(url, headers=headers)

                response = urllib.request.urlopen(r)
                if len(response.read().decode('utf-8')):
                    print("[{}] => ".format(response.code, url))
            except urllib.request.URLError as e:
                if hasattr(e, 'code') and e.code != 404:
                    print("[!!] {}".format(e.code, url))
                pass


word_queue = build_wordlist(wordlist)
extensions = [".php", ".bak", "orig", "inc"]

for i in range(threads):
    t = threading.Thread(target=dir_brute, args=(word_queue, extensions,))
    t.start()
