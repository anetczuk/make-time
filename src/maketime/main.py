#!/usr/bin/python3
#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

try:
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=W0611
    import __init__
except ImportError:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass

import sys
import argparse
import logging

import json

from maketime import logger
from maketime.io import write_file
from maketime.parser import read_compile_log


if __name__ == "__main__":
    _LOGGER = logging.getLogger("maketime.main")
else:
    _LOGGER = logging.getLogger(__name__)


# =======================================================================


def process(compilelogfile: str, outfile: str):
    compile_list = read_compile_log(compilelogfile)
    compile_list.sort(key=lambda item: item[1], reverse=True)

    content = json.dumps(compile_list, indent=4)
    if outfile:
        write_file(outfile, content)

    total_label = "Total time"
    max_length = len(total_label)
    for item in compile_list:
        max_length = max(max_length, len(item[0]))
    max_length += 2

    for item, time in compile_list:
        label = item
        if item == "make_time":
            label = total_label
        print(f"{label: <{max_length}} {time:12.6f} sec")


# =======================================================================


def main():
    parser = argparse.ArgumentParser(
        prog="python3 -m maketime.main",
        description="calculate C++ object files compilation time based on `make` output",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--loglevel", action="store", default=None, help="Set log level")
    parser.add_argument("-la", "--logall", action="store_true", help="Log all messages")
    # pylint: disable=C0301
    parser.add_argument("-clf", "--compilelogfile", action="store", required=True, help="Path to make compile log file")
    parser.add_argument("--outfile", action="store", required=False, default="", help="Path to output file")

    ## =================================================

    args = parser.parse_args()

    if args.logall is True:
        logger.configure(logLevel=logging.DEBUG, use_file=False)
    elif args.loglevel is not None:
        loglevel_map = logging.getLevelNamesMapping()
        loglevel = loglevel_map.get(args.loglevel)
        if loglevel is not None:
            logger.configure(logLevel=loglevel, use_file=False)
        else:
            logger.configure(logLevel=logging.INFO, use_file=False)
            _LOGGER.warning("loglevel not found - invalid loglevel name: %s", args.loglevel)
    else:
        # default log level
        logger.configure(logLevel=logging.INFO, use_file=False)

    process(args.compilelogfile, args.outfile)
    return 0


if __name__ == "__main__":
    code = main()
    sys.exit(code)
