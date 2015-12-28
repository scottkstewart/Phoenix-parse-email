import shelve
import os

#accept string for type of interval input
checkType = input("Update interval type ((s)econd, (m)inute, (h)our, (d)ay), default minute: ")

#interpret timeframe and accept interval time
if checkType == 's' or checkType == 'S':
    timeInt = int(input("How many seconds? "))
elif checkType == 'h' or checkType == 'H':
    timeInt = 60*60*int(input("How many hours? "))
elif checkType == 'd' or checkType == 'D':
    timeInt = 60*60*24*int(input("how many days? "))
else:
    timeInt = 60 * int(input("How many minutes? "))

#shelve interval for long-term storage
stuff = shelve.open(os.path.realpath(__file__)[:-14] + 'stuff', writeback=True)
stuff['interval'] = timeInt

stuff.close()
