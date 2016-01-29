import shelve
import os

def formatInput(checkType):
    #interpret timeframe and accept interval time
    if checkType == 's' or checkType == 'S':
        return int(input("How many seconds? "))
    elif checkType == 'h' or checkType == 'H':
        return 60*60*int(input("How many hours? "))
    elif checkType == 'd' or checkType == 'D':
        return 60*60*24*int(input("how many days? "))
    else:
        return 60 * int(input("How many minutes? "))

#shelve intervals for long-term storage
stuff = shelve.open(os.path.realpath(__file__)[:-14] + 'stuff', writeback=True)

stuff['interval'] = formatInput(input("Update interval type ((s)econd, (m)inute, (h)our, (d)ay), default minute: "))
stuff['autotry'] = formatInput(input("Update autotry type ((s)econd, (m)inute, (h)our, (d)ay), default minute: "))

stuff.close()
