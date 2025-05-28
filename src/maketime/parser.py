# Copyright (c) 2022, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging
import re
from datetime import datetime

from maketime.io import read_file


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


## ===================================================================


class BuildLog:

    def __init__(self):
        self.object_queue = []
        self._curr_object_name: str = None
        self._curr_object_time: datetime = None  # start time

    def add_object_start(self, name, start_time):
        self.add_object_end(start_time)
        # start of new object
        self._curr_object_name = name
        self._curr_object_time = start_time

    def add_object_end(self, end_time):
        if self._curr_object_name is None:
            # no object
            return
        diff = end_time - self._curr_object_time
        diff_secs = diff.total_seconds()
        self.object_queue.append((self._curr_object_name, diff_secs))
        self._curr_object_name = None
        self._curr_object_time = None

    def add_object(self, name, start_time, end_time):
        self.add_object_start(name, start_time)
        self.add_object_end(end_time)

    def add_linking_start(self, start_time):
        self.add_object_end(start_time)

    def add_target_finish(self, _target_name, end_time):
        self.add_object_end(end_time)


# output of make -j1 | ts '[%H:%M:%.S]'
def read_compile_log(log_path):
    content = read_file(log_path)
    if content is None:
        _LOGGER.warning("unable to read content from file '%s'", log_path)
        return None

    build_log = BuildLog()

    first_time = None
    last_time = None

    for line in content.splitlines():
        line = line.strip()

        line_time = get_build_timestamp(line)
        if line_time:
            if not first_time:
                first_time = line_time
            last_time = line_time

        object_name = get_after(line, r"Building \S+ object ")
        if object_name:
            build_log.add_object_start(object_name, line_time)
            continue

        linking_name = get_after(line, "Linking ")
        if linking_name:
            build_log.add_linking_start(line_time)
            continue

        target_name = get_after(line, "Built target ")
        if target_name:
            build_log.add_target_finish(target_name, line_time)
            continue

        _LOGGER.warning("unknown entry: %s", line)

    build_log.add_object("make_time", first_time, last_time)

    return build_log.object_queue


def get_after(content, substring):
    found = re.search(rf"({substring})(.*)$", content)
    if not found:
        # not found
        return None
    found_groups = found.groups()
    if not found_groups:
        # not found
        return None
    last_group = found_groups[-1]
    return last_group


def get_build_timestamp(content):
    time_list = re.findall(r"\[(.*?)\] \[", content)
    if len(time_list) != 1:
        return None

    time_text = time_list[0]
    try:
        return datetime.strptime(time_text, "%H:%M:%S.%f")
    except ValueError:
        # content does not match format
        pass
    try:
        return datetime.strptime(time_text, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        # content does not match format
        pass

    raise RuntimeError(f"unable to get time form content: {time_text}")
