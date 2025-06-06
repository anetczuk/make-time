#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import sys
import logging
from logging import handlers


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

log_file = None


def get_logging_output_file(log_dir=None):
    logDir = log_dir
    if not logDir:
        logDir = os.path.join(SCRIPT_DIR, ".")
    logDir = os.path.abspath(logDir)
    os.makedirs(logDir, exist_ok=True)
    if os.path.isdir(logDir) is False:
        ## something bad happened (or unable to create directory)
        logDir = os.getcwd()

    logFile = os.path.join(logDir, "make-time-log.txt")
    return logFile


def configure(logFile=None, logDir=None, logLevel=None, use_file: bool = True):
    # pylint: disable=W0603
    global log_file
    log_file = logFile
    if log_file is None:
        log_file = get_logging_output_file(logDir)

    if logLevel is None:
        logLevel = logging.DEBUG

    formatter = create_formatter()

    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(formatter)
    logging.root.addHandler(consoleHandler)

    if use_file:
        ## rotation of log files, 1048576 equals to 1MB
        fileHandler = handlers.RotatingFileHandler(filename=log_file, mode="a+", maxBytes=1048576, backupCount=999)
        ## fileHandler    = logging.FileHandler( filename=log_file, mode="a+" )
        fileHandler.setFormatter(formatter)
        logging.root.addHandler(fileHandler)

    logging.root.setLevel(logLevel)

    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    logging.getLogger("urllib3").setLevel(logging.INFO)


##     loggerFormat   = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s [%(filename)s:%(lineno)d] %(message)s'
##     dateFormat     = '%Y-%m-%d %H:%M:%S'
##     logging.basicConfig( format   = loggerFormat,
##                          datefmt  = dateFormat,
##                          level    = logging.DEBUG,
##                          handlers = [ fileHandler, consoleHandler ]
##                        )


def configure_console(logLevel=None):
    if logLevel is None:
        logLevel = logging.DEBUG

    consoleHandler = logging.StreamHandler(stream=sys.stdout)

    formatter = create_formatter()

    consoleHandler.setFormatter(formatter)

    logging.root.addHandler(consoleHandler)
    logging.root.setLevel(logLevel)


def create_stdout_handler():
    formatter = create_formatter()
    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(formatter)
    return consoleHandler


def create_formatter(loggerFormat=None):
    if loggerFormat is None:
        ## loggerFormat = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s [%(filename)s:%(lineno)d] %(message)s'
        loggerFormat = (
            "%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(name)s:%(funcName)s "
            "[%(filename)s:%(lineno)d] %(message)s"
        )
    dateFormat = "%Y-%m-%d %H:%M:%S"
    return EmptyLineFormatter(loggerFormat, dateFormat)
    ## return logging.Formatter( loggerFormat, dateFormat )


class EmptyLineFormatter(logging.Formatter):
    """Special formatter storing empty lines without formatting."""

    ## override base class method
    def format(self, record):
        msg = record.getMessage()
        clearMsg = msg.replace("\n", "")
        clearMsg = clearMsg.replace("\r", "")
        if not clearMsg:
            # empty
            return msg
        return super().format(record)


def print_log_tree():
    print(logging.root.manager.loggerDict.keys())  # pylint: disable=no-member


class ExitHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET, message=None):
        super().__init__(level)
        self.raiselevel = level
        self.message = message
        if self.message is None:
            self.message = "exiting program because exit log threshold reached"

    def emit(self, record):
        if record.levelno >= self.raiselevel:
            raise SystemExit(self.message)


def add_exit_handler(exit_log_level=logging.FATAL, message=None):
    handler = ExitHandler(exit_log_level, message)
    logging.root.addHandler(handler)
