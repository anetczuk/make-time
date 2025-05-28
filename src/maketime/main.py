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

from maketime import logger


if __name__ == "__main__":
    _LOGGER = logging.getLogger("maketime.main")
else:
    _LOGGER = logging.getLogger(__name__)


# =======================================================================


def main():
    parser = argparse.ArgumentParser(
        prog="python3 -m maketime.main",
        description="generate build timeline chart of `make` tool execution",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--loglevel", action="store", default=None, help="Set log level")
    parser.add_argument("-la", "--logall", action="store_true", help="Log all messages")

    ## =================================================

    args = parser.parse_args()

    if args.logall is True:
        logger.configure(logLevel=logging.DEBUG)
    elif args.loglevel is not None:
        loglevel_map = logging.getLevelNamesMapping()
        loglevel = loglevel_map.get(args.loglevel)
        if loglevel is not None:
            logger.configure(logLevel=loglevel)
        else:
            logger.configure(logLevel=logging.INFO)
            _LOGGER.info("loglevel not found - invalid loglevel name: %s", args.loglevel)
    else:
        # default log level
        logger.configure(logLevel=logging.INFO)

    return 0


if __name__ == "__main__":
    code = main()
    _LOGGER.info("exiting")
    sys.exit(code)
