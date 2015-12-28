from phoenixChecker import *
import time
import shelve
import sys
import os
#open shelved accounts and data
accounts = shelve.open(os.path.realpath(__file__)[:-6] + 'accounts', writeback=True)
stuff = shelve.open(os.path.realpath(__file__)[:-6] + 'stuff')
sys.setrecursionlimit(10000)

#instantiate list of all phoenix checkers
bots = []
for str in list(accounts.keys()):
    bots.append(accounts[str])

#checks each account, syncs with shelve, and waits for specified interval
while True:
    for b in bots:
        b.check()
    
    accounts.sync()

    time.sleep(stuff['interval'])
