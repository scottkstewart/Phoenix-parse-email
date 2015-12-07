from phoenixChecker import *
import time
import shelve
import sys
import os
accounts = shelve.open(os.path.realpath(__file__)[:-6] + 'accounts', writeback=True)
stuff = shelve.open(os.path.realpath(__file__)[:-6] + 'stuff')
sys.setrecursionlimit(10000)

bots = []
count = 0
for str in list(accounts.keys()):
    bots.append(accounts[str])
    count += 1

while True:
    for b in bots:
        b.check()
    
    accounts.sync()

    time.sleep(stuff['interval'])
