from phoenixChecker import *
import time
import shelve
accounts = shelve.open('accounts', writeback=True)
stuff = shelve.open('stuff')

bots = []
count = 0
for str in list(accounts.keys()):
    bots.append(accounts[str])
    count += 1

while True:
    for b in bots:
        b.check()
    
    time.sleep(stuff['interval'])

    d.sync()
