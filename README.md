# Phoenix-parse-email
Parses phoenix gradebook client and emails changes. Runs on at least Python 3.4. Files contained in ~/.PPE/.


Installation:

For unix: run install script. Uninstall with uninstall.
```
git clone https://github.com/scottkstewart/Phoenix-parse-email.git
cd Phoenix-parse-email
./install
```

For anybody else: I can't guarentee compatibility, but the python files are simple enough that you can change the path in the 'phoenix' file to whatever directory you want and run it simply with python3 phoenix [options]. 


Usage:

phoenix [-h] {add [-n, --no-continue], set [-i, -t], run [key1, key2, ...]}

-h: print usage and exit

add: add/change users (-n or --no-continue specifies only one addition)

set: set interval between checks (-i) and connection retries (-t) or both (blank)

run: run checks, optional user key(s) for selective run


Examples:

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

Written by scott stewart. Email any questions/problems to scottkstewart16@gmail.com.
