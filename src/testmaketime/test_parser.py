#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest

from maketime.parser import parse_compile_log


class BuildLogTest(unittest.TestCase):

    def test_parse_compile_log_normal(self):
        content = """
[12:51:27.539655] [ 25%] Building CXX object CMakeFiles/hello_library.dir/src/Hello.cpp.o
[12:51:27.897072] [ 50%] Linking CXX static library libhello_library.a
[12:51:28.071788] [ 50%] Built target hello_library
[12:51:28.089967] [ 75%] Building CXX object CMakeFiles/hello_binary.dir/src/main.cpp.o
[12:51:28.119030] [100%] Linking CXX executable hello_binary
[12:51:28.196915] [100%] Built target hello_binary
"""
        output = parse_compile_log(content)
        self.assertEqual(3, len(output))
        self.assertDictEqual({"total_time": 0.65726}, output[0])
        self.assertDictEqual(
            {
                "build_time": 0.532133,
                "link_time": 0.174716,
                "objects": [("CMakeFiles/hello_library.dir/src/Hello.cpp.o", 0.357417)],
                "target": "hello_library",
            },
            output[1],
        )
        self.assertDictEqual(
            {
                "build_time": 0.125127,
                "link_time": 0.077885,
                "objects": [("CMakeFiles/hello_binary.dir/src/main.cpp.o", 0.029063)],
                "target": "hello_binary",
            },
            output[2],
        )

    def test_parse_compile_log_empty_target(self):
        content = """
[15:20:55.038095] [  0%] Generating Header.h.stamp
[15:20:55.076559] [  0%] Built target target-a
[15:20:57.329023] [  0%] Building CXX object Log.cpp.o
[15:20:57.820038] [  0%] Building CXX object LogUtils.cpp.o
[15:20:58.396720] [  0%] Linking CXX static library liblogger.a
[15:20:58.470617] [  0%] Built target logger
"""
        output = parse_compile_log(content)
        self.assertEqual(3, len(output))
        self.assertDictEqual({"total_time": 3.432522}, output[0])
        self.assertDictEqual(
            {
                "build_time": 3.394058,
                "link_time": 0.073897,
                "objects": [("LogUtils.cpp.o", 0.576682), ("Log.cpp.o", 0.491015)],
                "target": "logger",
            },
            output[1],
        )
        self.assertDictEqual({"build_time": 0.038464, "link_time": 0.0, "objects": [], "target": "target-a"}, output[2])
