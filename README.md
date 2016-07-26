# Phoenix-parse-email

**NOTE: rolling updates are coming in terms of fixing code and making everything more pythonic. I'm lazy and these changes are essentially untestable so don't assume any of this works until a week or two into the school year.**

Unix utility which parses the Phoenix gradebook client and emails changes. Runs on at least Python 3.4. Files contained in /etc/ppe.

![Example usage](http://i.imgur.com/neM2Kb7.gif)
Image above shows example usage; delays/loading time reduced for the sake of demonstration.

**How it works**

Phoenix-parse-email (PPE) is a utility wrote for unix which incorperates several tools to gather, output, and monitor Loudoun County students' grades via the Phoenix Gradebook Client. It does so by storing (shelve) several 'phoenixChecker' objects (accounts.db), each of which contains the URLS to each individual quarter in the gradebook and a list of 8 'phoenixClass' objects. Each of these 'phoenixClass' objects contains lists of 4 (one for each quarter) urls, percentage/letter grades, and lists of assignments. All of this data is manipulated via commands in the 'phoenix' script, which call functions of the 'phoenixChecker' class that are largely dependent on the 'phoenixClass' class. These functions, mainly centered around notifying the user of changes to their grades, tend to send emails from 'phoenixpythonbot@gmail.com' and log progress in /etc/ppe/runlog and changes in ~/etc/ppe/log.

PPE was created initially as a project to learn computer science concepts past the curriculum of AP Computer science, but now serves as a serious utility for checking grades. It now has the functionality to do the following: (add) persistent 'phoenixClass' objects which correspond to a single student account; (check) any or all accounts, with or without email updates; (start) and (kill) daemonized run processes to email differences; view (status) of daemon including accounts being checked and time until next check; (set) intervals between automatic retries in bad connection and between checks with run; (remove) users from database of accounts; and (run) checks on any number of accounts, with or without echoing the grades as they are checked.

Though PPE is a utility designed to be versatile and easy to use, it is not created to be a wide-reaching program for all users; installation is likely to be a bit difficult and support is not likely to ever come to non-unix systems. The fact of the matter is, this is a personal tool, and I can only guarentee compatibility with systems that I've personally seen compatible: linux mint, debian GNU/Linux, and arch linux.

**Dependencies**

Pip for installation, various python modules (beautifulsoup4, requests, lxml, daemonize, dbm.gnu)

**Installation:**

For unix: run setup.py script (assumes either pip module or compatible pip program are installed). Uninstall with uninstall (-n or --no-purge retains the accounts and settings data for small upgrades).
```
git clone https://github.com/scottkstewart/Phoenix-parse-email.git
cd Phoenix-parse-email
sudo 
```
Occasionally errors have been raised after installation concerning _gdbm; on Arch, no errors were raised, but on debian, a separate "python3-gdbm" package was needed to use dbm.gnu, since dbm.gnu depends on gdbm, which may not exist on some minimal installations. To bypass this without troubleshooting, comment out or delete line 11 in 'phoenix', (import dbm.gnu) and remove the phrase dbm.gnu.error from 268 in 'phoenix' (except dbm.gnu.errror: -> except:). This will allow wider compatibility, but is not an elegant solution; it will end the 'status' command on any exception including KeyboardInterrupt, SystemExit, etc rather than catching the specific error for when the databases are currently busy.


**Upgrades:**

If on unix, one can upgrade by uninstalling (not necessary on small upgrades), syncing with the repository, and installing again. Uninstall for upgrades that affect set options/phoenixClass.py/phoenixChecker.py. Run the following for a small upgrade (from Phoenix-parse-email folder):
```
git pull
./install
```
Or for a larger upgrade (will require accounts to be remade and settings to be set again)
```
./uninstall
git pull
./install
```


**Usage:**
phoenix [options] {command [modifiers] command [modifiers] ...}

OPTIONS:

-h, --help: print usage and exit

-Q n: applies commands to quarter n (1-4), default current, n = all for every Q

-v, --verbose: includes assignments while printing grades

COMMANDS:

add [-n, --no-continue]: add/change users (-n or --no-continue for one user)

check [-n, --no-email] [key1 key2 ...]: check grades, default with email on change

kill: kills daemon (started by start)

monitor: gives refreshing version of status in real-time

print [-q, --quiet] [key1 key2 ...]: print all keys (-q, --quiet) or grades.

remove [key1 key2 ...]: remove specified accounts from database

run [-q, --quiet] [key1 key2 ...]: run checks; user key(s): selective; -q: no print

set [-i, -t]: set interval between checks (-i) autotries (-t) or both (blank)

start [key1 key2 ...]: forks run to daemon (PID file=~/.PPE/ppe.pid); keys optional

status: prints various pieces of information relating to the program's status


**Examples:**

To set both intervals, add a user, and run all users
```
phoenix set add --no-continue run
```
or
```
phoenix set
phoenix add --no-continue
phoenix run
```

To run all users at quarter 2
```
phoenix -Q 2 run
```

To set the interval between checks and print a user 123456
```
phoenix set -i print 123456
```

To remove a user (123456) and run another user (654321) as daemon
```
phoenix remove 123456 start 654321
```

To check all users current quarter without email and print all quarters w/assignments
```
phoenix check --no-email -Q all print -v
```

To view the history of a certain user (123456) in a certain class (AP Phoenix Science) by getting sequential output of log file and searching, first for user than for the course
```
cat ~/.PPE/log | grep 737231 | grep 'AP Phoenix Science'
```

To start daemon and check status (giving 30 seconds for the initial check to go through)
```
phoenix start; sleep 30s; phoenix status
```
**Autorun**

For constant use with daemon, I use a crontab scheduled every fifteen minutes, The command to edit cron may vary between distrobutions, but the line I use should work anywhere. I use the following:
```
*/15 * * * * phoenix start
```

Written by Scott Stewart. Email any questions/problems to scottkstewart16@gmail.com.
