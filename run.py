from phoenixChecker import *
import time
import getpass

username = input("Username: ")
password = getpass.getpass("Password: ")
email = input("Email: ")

bot = phoenixChecker(username, password, email)

checkType = input("Update interval type ((s)econd, (m)inute, (h)our, (d)ay), default minute: ")

if checkType == 's' or checkType == 'S':
    timeInt = int(input("How many seconds? "))
elif checkType == 'h' or checkType == 'H':
    timeInt = 60*60*int(input("How many hours? "))
elif checkType == 'd' or checkType == 'D':
    timeInt = 60*60*24*int(input("how many days? "))
else:
    timeInt = 60 * int(input("How many minutes? "))

bot.printGrades()
while True:
    time.sleep(timeInt)
    bot.check()
