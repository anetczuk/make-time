# Copyright (c) 2022, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging
from typing import Any, List
import re
from datetime import datetime

from maketime.io import read_file


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


## ===================================================================


class BuildLog:

    def __init__(self):
        self.object_queue = []
        self.target_queue = []
        self._curr_object_name: str = None
        self._curr_object_time: datetime = None
        self._linking_start: datetime = None
        self._target_start: datetime = None  ## name of target appears when target finishes

    def add_unknown_entry(self, entry_time):
        if self._target_start is None:
            self._target_start = entry_time

    def add_object_start(self, name, start_time):
        self.add_object_end(start_time)
        # start of new object
        self._curr_object_name = name
        self._curr_object_time = start_time
        if self._target_start is None:
            self._target_start = start_time

    def add_object_end(self, end_time):
        if self._curr_object_name is None:
            # no object
            return
        diff_secs = calculate_time_diff(self._curr_object_time, end_time)
        self.object_queue.append((self._curr_object_name, diff_secs))
        self._curr_object_name = None
        self._curr_object_time = None

    def add_object(self, name, start_time, end_time):
        self.add_object_start(name, start_time)
        self.add_object_end(end_time)

    def add_linking_start(self, start_time):
        self.add_object_end(start_time)
        self._linking_start = start_time

    def add_target_finish(self, target_name, end_time):
        self.add_object_end(end_time)

        linking_secs = 0.0
        if self._linking_start is not None:
            linking_secs = calculate_time_diff(self._linking_start, end_time)
        ## else can happen e.g. when target has no cpp files

        target_secs = 0.0
        if self._target_start is not None:
            target_secs = calculate_time_diff(self._target_start, end_time)

        target_data = {
            "target": target_name,
            "build_time": target_secs,
            "link_time": linking_secs,
            "objects": self.object_queue.copy(),
        }
        self.target_queue.append(target_data)

        self._linking_start = None
        self._target_start = end_time  ## handles cases where there are targets without cpp files
        self.object_queue.clear()


def calculate_time_diff(start_time, end_time):
    diff = end_time - start_time
    diff_secs = diff.total_seconds()
    return diff_secs


# output of make -j1 | ts '[%H:%M:%.S]'
def read_compile_log(log_path: str, sort_data=True):
    content = read_file(log_path)
    if content is None:
        _LOGGER.warning("unable to read content from file '%s'", log_path)
        return None
    return parse_compile_log(content, sort_data)


## content: str - multiline string
def parse_compile_log(content: str, sort_data=True) -> List[Any]:
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

        ## unknown entry
        build_log.add_unknown_entry(line_time)
        # _LOGGER.warning("unknown entry: %s", line)

    compile_list = build_log.target_queue
    if sort_data:
        compile_list.sort(key=lambda item: item["build_time"], reverse=True)
        for target_data in compile_list:
            objects_list = target_data["objects"]
            objects_list.sort(key=lambda item: item[1], reverse=True)

    total_secs = calculate_time_diff(first_time, last_time)
    compile_list.insert(0, {"total_time": total_secs})

    return compile_list


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


def print_log(compile_list):
    max_length = 0
    for target_data in compile_list:
        objects_list = target_data.get("objects")
        if objects_list is None:
            continue
        for item in objects_list:
            max_length = max(max_length, len(item[0]))
    max_length += 2

    for target_data in compile_list:
        total_time = target_data.get("total_time")
        if total_time is not None:
            print("total_time:", total_time, "sec")

        target_name = target_data.get("target")
        if target_name is not None:
            print("target:", target_name)
        build_time = target_data.get("build_time")
        if build_time is not None:
            print("build time:", build_time, "sec")
        link_time = target_data.get("link_time")
        if link_time is not None:
            print("link time: ", link_time, "sec")
        objects_list = target_data.get("objects")
        if objects_list is None:
            continue
        print("objects:")
        objects_list = target_data["objects"]
        for object_data in objects_list:
            label = object_data[0]
            time = object_data[1]
            print(f"   {label: <{max_length}} {time:12.6f} sec")
