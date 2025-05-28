#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


MAKETIME_DIR="${SCRIPT_DIR}/../../src/maketime"
CMAKE_DIR="${SCRIPT_DIR}/c-static-library"
BUILD_DIR="${SCRIPT_DIR}/build"


mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"


cmake "${CMAKE_DIR}"

make clean

"${MAKETIME_DIR}"/../maketime.sh
