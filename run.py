from phoenixChecker import *
import time
import shelve
accounts = shelve.open('accounts', writeback=True)
stuff = shelve.open('stuff')

bots = []
count = 0
for str in accounts.keys():
    bots.append(accounts[str])
    bots[count].update()
    bots[count].printGrades()
    
    count += 1

while True:
    time.sleep(stuff['interval'])
    for b in bots:
        b.check()

    d.sync()
