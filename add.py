from phoenixChecker import *
import getpass
import shelve
import sys
import os

#accept user input
username = input("Username: ")
password = getpass.getpass("Password: ")
email = input("Email: ")

#instantiate bot
bot = phoenixChecker(username, password, email)

#set high recursion limit, shelve bot for long term storage
sys.setrecursionlimit(10000)
d = shelve.open(os.path.realpath(__file__)[:-6] + 'accounts')
d[username] = bot
