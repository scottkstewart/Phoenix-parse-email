# Phoenix-parse-email
Parses phoenix gradebook client and emails changes. Runs on at least Python 3.4. Files contained in ~/.PPE/.


**Installation:**

For unix: run install script. Uninstall with uninstall (-n or --no-purge retains the accounts and settings data for small upgrades).
```
git clone https://github.com/scottkstewart/Phoenix-parse-email.git
cd Phoenix-parse-email
./install
```

For anybody else: I can't guarentee compatibility, but the python files are simple enough that you can change the path in the 'phoenix' file to whatever directory you want and run it simply with python3 phoenix [options]. 


**Upgrades:**

If on unix, one can upgrade by uninstalling (without purging on small upgrades), syncing with the repository, and installing again. Using the --no-purge flag will allow you to retain data, but will not work for large upgrades that affect set options/phoenixClass.py/phoenixChecker.py. Run the following for a small upgrade (from Phoenix-parse-email folder):
```
./uninstall --no-purge
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

phoenix [-h] {add [-n, --no-continue], set [-i, -t], run [key1, key2, ...]}

-h: print usage and exit

add: add/change users (-n or --no-continue specifies only one addition)

set: set interval between checks (-i) and connection retries (-t) or both (blank)

run: run checks, optional user key(s) for selective run


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

To set the interval between checks and run a user 123456
```
phoenix set -i run 123456
```

Written by Scott Stewart. Email any questions/problems to scottkstewart16@gmail.com.
