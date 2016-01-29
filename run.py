from phoenixChecker import *
import time
import shelve
import sys
import os
import urllib.request
import select

#open shelved accounts and data
accounts = shelve.open(os.path.realpath(__file__)[:-6] + 'accounts', writeback=True)
stuff = shelve.open(os.path.realpath(__file__)[:-6] + 'stuff')
sys.setrecursionlimit(10000)

#instantiate list of all phoenix checkers
bots = []
for key in list(accounts.keys()):
    bots.append(accounts[key])

#checks each account, syncs with shelve, and waits for specified interval
while True:
    # get sleep/autotry intervals
    sleepInterval = stuff['interval']
    autotryInterval = stuff['autotry']
    
    #check until the program exits or connects
    while True:
        try: #will exit loop and check if the script connects to phoenix without error (times out after a minute)
            r = urllib.request.urlopen('http://portal.lcps.org/',timeout=60)
            break
        except urllib.request.URLError:
            #format interval between autotries to be human readable
            if autotryInterval <= 60:
                autotryTime = str(autotryInterval) + ' seconds'
            elif autotryInterval <= 3600:
                autotryTime = str(autotryInterval/60) + ' minutes'
            else:
                autotryTime = str(autotryInterval/3600) + ' hours'
            
            #print and read input for time specified by autotry interval
            print('Phoenix not loaded within 60 seconds. Retry? (Y/n). Will autotry in ' + autotryTime + '.')
            i, o, e = select.select([sys.stdin], [], [], autotryInterval)
            

            if i:#if there is an input, continue in loop if 'y', exit otherwise
                if sys.stdin.readline().strip()[0] == 'y':
                    print('Retrying...')
                else:
                    print('Exiting')
                    sys.exit(0)
            else:#if the program continues without input, autotry (interval is over)
                print('Autotrying...')

    # iterate through list of bots, checking each
    for b in bots:
        b.check()
    
    # sync accounts database with checked bots
    accounts.sync()
    
    #sleep for specified time
    time.sleep(sleepInterval)
