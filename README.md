# Phoenix-parse-email
Parses phoenix gradebook client and emails changes.

Installation:

For linux: resolve all dependencies (you're on your own), change paths in the file 'phoenix' to match the places where your python files are installed, move the file 'phoenix' to your $PATH, and set the interval/add acounts before running the script.

For anybody else: you're on your own for this (the python files themselves are useable through python {add, setInterval, run}.py or the same with python3). This is a simple enough script that using it on any OS should be simple.

Usage:

phoenix [-h] {add, set, run}

-h: print usage and exit

add: add/change user

set: set interval between checks and connection retries

run: run checks
