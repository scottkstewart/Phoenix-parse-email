# Phoenix-parse-email
Parses phoenix gradebook client and emails changes. Runs on at least Python 3.4. Files contained in ~/.PPE/.

![Example usage](http://i.imgur.com/TASMgCp.gif)
Image above shows example usage; delays/loading time reduced for the sake of demonstration.



**Installation:**

For unix: run install script (assumes either pip module or compatible pip program are installed). Uninstall with uninstall (-n or --no-purge retains the accounts and settings data for small upgrades).
```
git clone https://github.com/scottkstewart/Phoenix-parse-email.git
cd Phoenix-parse-email
./install
```

For anybody else: I can't guarentee compatibility, but the python files are simple enough that you can change the path in the 'phoenix' file to whatever directory you want and run it simply with python3 phoenix [options]. 



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

COMMANDS:

add [-n, --no-continue]: add/change users (-n or --no-continue for one user)

check [-n, --no-email] [key1 key2 ...]: check grades, default with email on change

print [-q, --quiet] [key1 key2 ...]: print all keys (-q, --quiet) or grades. Individual assignments can be viewed with -v or --verbose

set [-i, -t]: set interval between checks (-i) autotries (-t) or both (blank)

remove [key1 key2 ...]: remove specified accounts from database

run [-q, --quiet] [key1 key2 ...]: run checks; user key(s): selective; -q: no print



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

To change a user (123456)  and run them without output (remove, add again, run)
```
phoenix remove 123456 add --no-continue run --quiet
```

To check all users current quarter without email and print all quarters w/assignments
```
phoenix check --no-email -Q all print -v
```



Written by Scott Stewart. Email any questions/problems to scottkstewart16@gmail.com.
