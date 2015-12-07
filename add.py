from phoenixChecker import *
import getpass
import shelve
import sys
import os

username = input("Username: ")
password = getpass.getpass("Password: ")
email = input("Email: ")

bot = phoenixChecker(username, password, email)

sys.setrecursionlimit(10000)
d = shelve.open(os.path.realpath(__file__)[:-6] + 'accounts')
d[username] = bot
