#!/usr/bin/env python3
import imp
import errno
import getpass
import sys
import shelve
import os
import time
import datetime
import urllib.request
import select
import signal
import dbm.gnu
import curses
from ppe import (PhoenixClass, PhoenixChecker)
from daemonize import Daemonize

def log(messageList):# add single message to log
    # get log
    logfile = open('/etc/ppe/runlog', 'r')
    log = logfile.readlines()
    logfile.close()

    # truncate if necessary
    if len(log) + len(messageList) > 1000:
        log = log[(-1000+len(messageList)):]
    
    # write to file (ternary to avoid newlining letters of a single string)
    logfile = open('/etc/ppe/runlog', 'w')
    logfile.write(''.join(log) + "\n".join(messageList) + '\n' if hasattr(messageList,'__iter__') and not isinstance(messageList,str) else messageList + "\n")
    logfile.close()

def add(nocontinue=False):# add user to list of bots
    # open accounts database, set high recursion limit
    data = shelve.open('/etc/ppe/data')
    try:
        accounts = data['accounts']
    except KeyError:
        accounts = data['accounts'] = dict()
    data.close()

    sys.setrecursionlimit(10000)

    additions = []
    cont = 'y'
    while cont.lower() == 'y':# continue to ask additions until user doesn't say 'y'
        # accept user input
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        email = input("Email: ")

        # instantiate bot and shelve (prompt on overwrite)
        if not (username in accounts.keys()) or input("Account {} already exists. Overwrite? (y/n): ".format(username)).lower() == 'y':
            try:
                bot = PhoenixChecker(username, password, email)
                accounts[username] = bot
                additions.append('[{}] {} added to database.'.format(str(datetime.datetime.now()), username))
            finally:
                pass
            #except IndexError:
            #    print("Bot not valid (no grades found).")
            #    additions.append('[{}] {} attempted to add; bot was found invalid.'.format(str(datetime.datetime.now()), username))

        if nocontinue:# if nocontinue is specified, stop after one iteration
            cont = 'n'
        else:# ask for user input to continue or stop
            cont = input("Add another? (y/n): ")
    
    data = shelve.open('/etc/ppe/data')
    data['accounts'] = accounts
    log(additions)
    data.close()


def formatInput(checkType):# format input for set
    #interpret timeframe and accept interval time
    if checkType.lower() == 's':
        return int(input("How many seconds? "))
    elif checkType.lower() == 'h':
        return 60*60*int(input("How many hours? "))
    elif checkType.lower() == 'd':
        return 60*60*24*int(input("How many days? "))
    else:
        return 60 * int(input("How many minutes? "))

def setStuff(interval=True, autotry=True):# set intervals between events
    data = shelve.open('/etc/ppe/data')

    if interval:# if -i is specified or no operation specified prompt for interval
        data['interval'] = formatInput(input("Update interval type ((s)econd, (m)inute, (h)our, (d)ay), default minute: "))
    if autotry:# if -t is specified or no operation specified prompt for autotry
        data['autotry'] = formatInput(input("Update autotry type ((s)econd, (m)inute, (h)our, (d)ay), default minute: "))

    data.close()

def run(botlist=[], quiet=False, verbose=False, email=True, quarter=0):# start the bots
    # open shelved data set recursion limit
    sys.setrecursionlimit(10000)

    # instantiate list of all used phoenix checkers and shelve list of keys running
    data = shelve.open('/etc/ppe/data')
    if len(botlist) == 0:# if list of bots is empty check all in accounts database
        bots = list(data['accounts'].values())
        data['botlist'] = list(data['accounts'].keys())
    else:# otherwise iterate through all bots in list
        data['botlist'] = botlist
        bots = [data[accounts][key] for key in botlist]
    data.close()

    # checks each account, syncs with shelve, and waits for specified interval
    while True:
        # open accounts
        data = shelve.open('/etc/ppe/data', writeback=True)
        
        # get sleep/autotry intervals
        sleepInterval = data['interval']
        autotryInterval = data['autotry']
        
        changes = [] 
        # check until the program exits or connects
        while True:
            try: # will exit loop and check if the script connects to phoenix without error (times out after a minute)
                r = urllib.request.urlopen('http://portal.lcps.org/',timeout=60)
                break
            except urllib.request.URLError:
                # format interval between autotries to be human readable
                if autotryInterval <= 60:
                    autotryTime = str(autotryInterval) + ' seconds'
                elif autotryInterval <= 3600:
                    autotryTime = str(autotryInterval/60) + ' minutes'
                else:
                    autotryTime = str(autotryInterval/3600) + ' hours'
                
                # if quiet, simply retry after interval andlog
                if quiet:
                    time.sleep(autotryInterval)
                    changes.append('[{}] Phoenix not loaded, script automatically retrieved after {}s as daemon.'.format(str(datetime.datetime.now()), autotryTime))
                else:# if not quiet, read input, autotrying on interval    
                    # print and read input for time specified by autotry interval
                    print('Phoenix not loaded within 60 seconds. Retry? (Y/n). Will autotry in ' + autotryTime + '.')
                    i, o, e = select.select([sys.stdin], [], [], autotryInterval)

                    if i:# if there is an input, continue in loop if 'y', exit otherwise
                        if sys.stdin.readline().strip()[0] == 'y':
                            print('Retrying...')
                            changes.append('[' + str(datetime.datetime.now()) + ']  Phoenix not loaded, script manually retried.')
                        else:
                            print('Exiting')
                            changes.append('[' + str(datetime.datetime.now()) + ']  Phoenix not loaded, script manually exited.')
                            log(changes)
                            sys.exit(0)
                    else:# if the program continues without input, autotry (interval is over)
                        print('Autotrying...')
                        changes.append('[{}] Phoenix not loaded, script automatically retried after {}s.'.format(str(datetime.datetime.now()), autotryTime))

        # iterate through list of bots, checking each, specifying bool echo as !quiet
        for b in bots:
            # if quarter signifies all, check all quarters, otherwise check the specified quarter
            if quarter == -1:
                if not email:
                    b.updatePage()
                    b.urlUpdate()
                for i in range(1, 5):
                    try:# try block fixes occasional anomalous list error
                        if email:
                            b.check(not quiet, verbose, i)
                        else:
                            b.update(i)
                        changes.append('[{}] {} checked for quarter {}.'.format(str(datetime.datetime.now()), b.getUsername(), str(i)))
                    except IndexError:
                        print("Index error, skipping...")
                        changes.append('[{}] List index while checking {} for quarter {}.'.format(str(datetime.datetime.now()), b.getUsername(), str(i)))
            else:
                try:
                    if email:
                        b.check(not quiet, verbose, quarter)
                    else:
                        b.updatePage()
                        b.urlUpdate()
                        b.update(quarter)
                    changes.append('[{}] {} checked for quarter {}.'.format(str(datetime.datetime.now()), b.getUsername(), str(quarter)))
                except IndexError:
                    print("Index error, skipping...")
                    changes.append('[{}] List index while checking {} for quarter {}.'.format(str(datetime.datetime.now()), b.getUsername(), str(quarter)))
            data['accounts'][b.getUsername()] = b

        # write changes to log file
        log(changes)

        # sync database (botlist), shelve time for scheduled change
        data['schedule'] = time.time() + sleepInterval
        data.close()
        
        #sleep for specified time
        time.sleep(sleepInterval)

# return populated list of all bots in list (or all in database if list is empty), data is shelve object
def getBots(botlist=[], data=None):
    # open database if not already supplied
    if data is None:
        data = shelve.open('/etc/ppe/data')
    
    if len(botlist) == 0:
        return [data['accounts'][key] for key in data['accounts'].keys()]
    else:
        return [data['accounts'][key] for key in botlist]

def output(botlist=[], quiet=False, verbose=False, quarter=0):
    # open shelved data, set recursion limit
    data = shelve.open('/etc/ppe/data')
    sys.setrecursionlimit(10000)

    if quiet:# if quiet, list all keys and exit
        for key in list(data['accounts'].keys()):
            print(key)
        return

    bots = getBots(botlist, data)

    # print grades for each bot
    for bot in bots:
        # if all quarters is specified, print all 4 quarters, otherwise print specified quarter
        if quarter == -1:
            for i in range(1, 5):
                # pass verbosity of output
                bot.printGrades(i, verbose)
        else:
            bot.printGrades(quarter, verbose)

    data.close()

def remove(botlist):
    if len(botlist) == 0:# if no keys specified, exit
        print("No keys entered. Specify accounts to delete and run again.")
        return

    # open shelved data, set recursion limit
    data = shelve.open('/etc/ppe/data', writeback=True)
    sys.setrecursionlimit(10000)

    # iterate through keys, removing if the account exists
    for key in botlist:
        if key in data['accounts']:
            del data['accounts'][key]
        else:
            print("Can't delete " + key + "; account not in database.")

    # sync and close database
    data.close()

def check(botlist=[], quiet=False, quarter=0):
    # open shelved data, set recursion limit
    data = shelve.open('/etc/ppe/data')
    sys.setrecursionlimit(10000)

    bots = getBots(botlist, data)
   
    # close database
    data.close()

    # iterate through bots, checking each (includes email) if specified, updating each otherwise
    if quiet:
        for bot in bots:# update doesn't include echo or email
            # update all urls for page
            bot.updatePage()
            bot.urlUpdate()
            # if all quarters are specified, update 1-4, otherwise update specified
            if quarter == -1:
                for i in range(1, 5):
                    bot.update(i)
            else:
                bot.update(quarter)
    else:
        for bot in bots:# check but don't echo
            if quarter == -1:
                for i in range(1, 5):
                    bot.check(quarter=i)
            else:
                bot.check(quarter=quarter)
    
    # open database
    data = shelve.open('/etc/ppe/data', writeback=True)
    
    # add back checked bots
    for bot in bots:
        data['accounts'][bot.getUsername()] = bot

    # close database
    data.close()

def status(quiet=False):# print information on status of programd 
    try:# try to open database
        data = shelve.open('/etc/ppe/data')
    except dbm.gnu.error:# if error is raised, the check is currently executed
        return "Executing" if quiet else ["PPE Currently Executing (try again in a little while)."]

    out = []
    try:# try to open pid file
        pid = int(open('/etc/ppe/pid').read())
    except FileNotFoundError:
        if quiet:
            return 'Not running'
        out.append("Daemon: not currently running.")
        running = False
    else:
        if quiet:
            return 'Running'
        out.append("Daemon: running (PID=" + str(pid) + ")")
        running = True
    
        # find time until check
        scheduledTime = data['schedule']
        timeUntilRun = int(scheduledTime - time.time())

        formTime = ""
        # get string for formatted time
        if(timeUntilRun > 60*60*24):
            formTime += " " + str(timeUntilRun//(3600*24)) + " days"
            timeUntilRun %= (3600*24)
        if(timeUntilRun > 60*60):
            formTime += " " + str(timeUntilRun//3600) + " hours"
            timeUntilRun %= 3600
        if(timeUntilRun > 60):
            formTime += " " + str(timeUntilRun//60) + " minutes"
            timeUntilRun %= 60
        formTime += " " + str(timeUntilRun) + " seconds"

        out.append("Next scheduled check in" + formTime + ".")

    # log bots in the following format: (R if running) key
    out.append("The following bots are logged (R = running):")
    out.extend(('{}{}'.format('{}\t'.format('(R)' if key in data['botlist'] else '') if running else '', key) for key in data['accounts'].keys())) 

    # close databases
    data.close()

    # return list of strings
    return out

def monitor(stdscr):
    # initialize screen using default colors, no cursor
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.use_default_colors()
    curses.curs_set(0)
    # set getch to wait one second (effectively setting refresh rate of monitor)
    curses.halfdelay(10)

    # initialize data as empty before updating
    stat = ['','','']
    size = [0,0]
    char = curses.ERR
    while char == curses.ERR:# loop until character is typed (no character after 1s == curses.ERR)
        # get status and screen size
        oldStat = stat
        stat = status()
        
        oldsize = size
        size = stdscr.getmaxyx()

        if len(oldStat) != len(stat) or (len(oldStat) > 2 and (oldStat[2:] != stat[2:] or len(oldStat[1]) > len(stat[1]))) or oldsize != size:# if any changes occur that shrinks the size in any dimension, clear the screen to keep clean output
            stdscr.clear()
        
        # output all lines centered on y axis
        curRow = int(size[0]/2-len(stat)/2)
        for line in stat:
            if line[0]=='\t' or line[0]=='(':# if it's a bot list, let it be flush on left
                stdscr.addstr(curRow, int(size[1]/2-22), line)
            else:# otherwise center it on x axis
                stdscr.addstr(curRow, int(size[1]/2-len(line)/2), line)
            curRow += 1
        
        # update screen
        stdscr.refresh()
        
        # get character (if character is typed this will end the loop)
        char = stdscr.getch()


def daemon_start(botlist=[], email=True, quarter=0):# start daemon w/PID /etc/ppe/pid
    try:# try to open pid file
        pid = int(open('/etc/ppe/pid').read())
    except FileNotFoundError:# if the file doesn't exist, start daemon
        # define action for daemon as run w/specified botlist, quiet, quarter
        daemonAction = lambda: run(botlist, quiet=True, email=email, quarter=quarter)
        
        # fork process to daemon
        daemon = Daemonize(app="phoenix-parse-email", pid=('/etc/ppe/pid'), action=daemonAction)
        print("Forking to daemon (PID File at /etc/ppe/pid)...")
        log('['+str(datetime.datetime.now())+'] Daemon started.')
        daemon.start()
    else:# if the file does exist already, print message and don't fork
        print("PID already exists (" + str(pid) + "). Try 'phoenix kill'")

def daemon_exit(sig=0, quiet=False):# kill daemon w/PID /etc/ppe/pid
    try:# try to open pid file
        pid = int(open('/etc/ppe/pid').read())
        os.kill(pid, sig)
    except FileNotFoundError:# if not found, send a message
        if not quiet:
            print("PID not found (PPE is not currently running).")
    except OSError as err:
        if err.errno == errno.ESRCH:
            os.remove('/etc/ppe/pid')
        else:
            raise
    else:# if the file exists, send sigterm to kill it
        if not quiet:
            print("Killed PPE (PID=" + str(pid) + ").")
        log('['+str(datetime.datetime.now())+'] Daemon killed.')

def get_botlist(args):# iterate through arguments to give a list of the keys following a command
    for ind, key in enumerate(args):
        if not key.isnumeric():
            return args[0:ind]
    
    return args

# set menu for help/usage instructions
HELPMENU = """phoenix [options] {command [modifiers] command [modifiers] ...}

OPTIONS:
-h, --help: print usage and exit
-Q n: applies commands to quarter n (1-4), default current, n = all for every Q
-v, --verbose: includes assigmnents while printing grades

COMMANDS:
add [-n, --no-continue]: add/change users (-n or --no-continue for one user)
check [-n, --no-email] [key1 key2 ...]: check grades, default with email on change
kill: kills daemon (started by start)
monitor: gives refreshing version of status in real-time
print [-q, --quiet] [key1 key2 ...]: print all keys (-q, --quiet) or grades
remove [key1 key2 ...]: remove specified accounts from database
run [-q, --quiet] [key1 key2 ...]: run checks; user key(s): selective; -q: no print
set [-i, -t]: set interval between checks (-i) autotries (-t) or both (blank)
start [-n, --no-email] [key1 key2 ...]: forkes run to daemon (PID file=~/.PPE/ppe.pid); keys optional
status: prints various pieces of information relating to the program's status"""

def arg_parse(args, quarter=0, verbose=False):# recursively parse argument list based on quarter (0 = current q) and verbosity
    if len(args) == 0:# base case; if nothing is left to do, exit
        return
    elif args[0] == '-v' or args[0] == '--verbose':
        arg_parse(args[1:], quarter, True)
    elif args[0] == '-Q':# if prompted to set quarter, validate and set
        if args[1] == 'all':# all = -1
            arg_parse(args[2:], -1, verbose)
        elif args[1].isnumeric() and int(args[1]) >= 1 and int(args[1]) <= 4:# 1 <= n <= 4
            arg_parse(args[2:], int(args[1]), verbose)
        else:# if invalid, print message and end
            print("Option '-Q " + args[1] + "' not valid. See 'phoenix --help'.")
            return
    elif args[0] == '-h' or args[0] == '--help':# if prompted for help menu, print help menu and exit
        print(HELPMENU)
        return
    elif args[0] == 'monitor':
        # wrapper for clean exiting
        curses.wrapper(monitor)
        arg_parse(args[1:], quarter, verbose)
    elif args[0] == 'status':
        if len(args) != 1 and (args[1] == '-q' or args[1] == '--quiet'):
            print(status(True))
            arg_parse(args[2:], quarter, verbose)
        else:
            for line in status():
                print(line)
            arg_parse(args[1:], quarter, verbose)
        arg_parse(args[1+len(botlist):], quarter, verbose)
    elif args[0] == 'kill':
        # kill daemon and call arg_parse
        daemon_exit()
        arg_parse(args[1:], quarter, verbose)
    elif args[0] == 'set':
        if len(args) != 1 and (args[1] == '-t' or args[1] == '-i'):# include option
            if args[1] == '-i':
                setStuff(interval=True)
            elif args[1] == '-t':
                setStuff(autotry=True)
            
            arg_parse(args[2:], quarter, verbose)
        else:# don't include option
            setStuff()
            arg_parse(args[1:], quarter, verbose)
    elif args[0] == 'add':
        if len(args) > 1 and (args[1] == '-n' or args[1] == '--no-continue'):# include nocontinue
            add(True)
            arg_parse(args[2:], quarter, verbose)
        else:# don't include nocontinue
            add()
            arg_parse(args[1:], quarter, verbose)
    elif args[0] == 'remove':
        for i in range(1, len(args) + 1):# count all keys, pass all as list (in$
            if i >= len(args) or not args[i].isnumeric():
                remove(args[1:i])
                arg_parse(args[i:], quarter, verbose)
                return
    elif args[0] == 'print' or args[0] == 'run':
        # set boolean quiet to whether quiet output is specified
        quiet = len(args) > 1 and (args[1] == '-q' or args[1] == '--quiet')

        # if quiet tag is specified, start counting keys one later
        if quiet:
            start = 2
        else:
            start = 1
        
        # get botlist and call appropriate command
        botlist = get_botlist(args[start:])
        if args[0] == 'run':
            run(botlist, quiet, verbose, True, quarter)
        elif args[0] == 'print':
            output(botlist, quiet, verbose, quarter)

        # call arg_parse with appropriate arguments
        arg_parse(args[start+len(botlist):], quarter, verbose)
    elif args[0] == 'check' or args[0] == 'start':
        # set boolean quiet to whether quiet output is specified
        quiet = len(args) > 1 and (args[1] == '-n' or args[1] == '--no-email')

        # if quiet tag is specified, start counting keys one later
        if quiet:
            start = 2
        else:
            start = 1
        
        # get botlist, call check or start, and call arg_parse
        botlist = get_botlist(args[start:])
        if args[0] == 'check':
            check(botlist, quiet, quarter)
        else:
            daemon_start(botlist, not quiet, quarter)
        arg_parse(args[start+len(botlist):], quarter, verbose)
    else:# if it's not a valid command exit (-... == option)
        print("PPE: {} '{}' not found. See 'phoenix --help'".format("Option" if args[0][0] == '-' else "Command", args[0]))
        return

if __name__ == "__main__": # main method; calls method to parse argument list ignoring script name
    if len(sys.argv) == 1:
        print("PPE: No commands entered. See 'phoenix --help'")
    else:
        arg_parse(sys.argv[1:])
