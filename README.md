# Phoenix-parse-email
Parses phoenix gradebook client and emails changes. Runs on at least Python 3.4. Files contained in ~/.PPE/.


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

phoenix [-h] {command [options], command [options] ...}
-h: print usage and exit

add [-n, --no-continue]: add/change users (-n or --no-continue for one user)

print [-q, --quiet] [key1, key2, ...]: print all keys (-q, --quiet) or grades

set [-i, -t]: set interval between checks (-i) autotries (-t) or both (blank)

remove [key1, key2, ...]: remove specified accounts from database

run [key1, key2, ...]: run checks, optional user key(s) for selective run

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

To run all users at any point
```
phoenix run
```

To set the interval between checks and print a user 123456
```
phoenix set -i print 123456
```

To change a user (123456)  and run them (remove, add again, run)
```
phoenix remove 123456 add --no-continue run
```

Written by Scott Stewart. Email any questions/problems to scottkstewart16@gmail.com.
