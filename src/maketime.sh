#!/bin/bash

set -eu

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


make -j1 "$@" | ts '[%H:%M:%.S]' | tee compile-log.txt

"${SCRIPT_DIR}"/maketime/main.py --compilelogfile "compile-log.txt"
