# Phoenix-parse-email
Parses phoenix gradebook client and emails changes. Files contained in ~/.PPE/


Installation:

For unix: run install script. Uninstall with uninstall.
```
git clone https://github.com/scottkstewart/Phoenix-parse-email.git
cd Phoenix-parse-email
./install
```

For anybody else: you're on your own for this (the python files themselves are useable through python {add, setInterval, run}.py or the same with python3). This is a simple enough script that using it on any OS should be simple.

Usage:

phoenix [-h] {add, set, run}

-h: print usage and exit

add: add/change user

set: set interval between checks and connection retries

run: run checks
