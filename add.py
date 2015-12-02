from phoenixChecker import *
import getpass
import shelve
import sys

username = input("Username: ")
password = getpass.getpass("Password: ")
email = input("Email: ")

bot = phoenixChecker(username, password, email)

sys.setrecursionlimit(10000)
d = shelve.open('accounts')
d[username] = bot
