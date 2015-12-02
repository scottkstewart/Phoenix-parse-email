from phoenixChecker import *
import time
import shelve
import sys
accounts = shelve.open('accounts', writeback=True)
stuff = shelve.open('stuff')
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
