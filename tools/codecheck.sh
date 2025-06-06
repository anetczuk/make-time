#!/bin/bash

set -eu
#set -u


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


check_dirs=()
src_dir="$SCRIPT_DIR/../src"
check_dirs+=("$src_dir")
examples_dir="$SCRIPT_DIR/../examples"
if [ -d "$examples_dir" ]; then
    check_dirs+=("$examples_dir")
fi
check_dirs+=("$SCRIPT_DIR")


echo "running black"
black --line-length=120 "${check_dirs[@]}"
exit_code=$?

if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

echo "black -- no warnings found"


## E115 intend of comment
## E126 continuation line over-indented for hanging indent
## E201 whitespace after '('
## E202 whitespace before ')'
## E203 whitespace before ':' - black formatter adds space before
## E221 multiple spaces before equal operator
## E241 multiple spaces after ':'
## E262 inline comment should start with '# '
## E265 block comment should start with '# '
## E266 too many leading '#' for block comment
## E402 module level import not at top of file
## E501 line too long (80 > 79 characters)
## W391 blank line at end of file
## D    all docstyle checks
ignore_errors=E115,E126,E201,E202,E203,E221,E241,E262,E265,E266,E402,E501,W391,D


echo "running pycodestyle"
echo "to ignore warning inline add comment at the end of line: # noqa"
pycodestyle --show-source --statistics --count --ignore="$ignore_errors" "${check_dirs[@]}"
exit_code=$?

if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

echo "pycodestyle -- no warnings found"


## F401 'PyQt5.QtCore' imported but unused
ignore_errors=$ignore_errors,F401


echo "running flake8"
echo "to ignore warning for one line put following comment in end of line: # noqa: <warning-code>"
python3 -m flake8 --show-source --statistics --count --ignore="$ignore_errors" "${check_dirs[@]}"
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo -e "\nflake8 errors found"
    exit $exit_code
fi

echo "flake8 -- no warnings found"


check_files=""
src_files=$(find "$src_dir" -type f -name "*.py")
check_files="${check_files} ${src_files}"
example_files=$(find "$examples_dir" -type f -name "*.py") || true
if [[ "${example_files}" != "" ]]; then
    check_files="${check_files} ${example_files}"
fi
tools_files=$(find "$SCRIPT_DIR" -type f -name "*.py")
check_files="${check_files} ${tools_files}"


echo "running pylint3"
echo "to ignore warning for module put following line on top of file: # pylint: disable=<check_id>"
echo "to ignore warning for one line put following comment in end of line: # pylint: disable=<check_id>"
# shellcheck disable=SC2086
pylint --rcfile="$SCRIPT_DIR/pylint3.config" $check_files
exit_code=$?
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi
echo "pylint3 -- no warnings found"


echo "running bandit"
echo "to ignore warning for one line put following comment in end of line: # nosec"

## [B301:blacklist] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data, possible security issue.
## [B403:blacklist] Consider possible security implications associated with pickle module.
skip_list="B301,B403"

#echo "to ignore warning for one line put following comment in end of line: # nosec
# shellcheck disable=SC2086
bandit --skip "${skip_list}" -r "${check_dirs[@]}" -x "$src_dir/test*"
exit_code=$?
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi
echo "bandit -- no warnings found"


req_path="$src_dir/requirements.txt"
if [ -f "$req_path" ]; then
    echo "running safety"
    safety check -r "$req_path"
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        exit $exit_code
    fi
    echo "safety -- no warnings found"
else
    echo "skipping safety - no requirements file found"
fi


## check shell scripts

found_files=$(find "$src_dir/../" -not -path "*/venv/*" -not -path "*/tmp/*" -type f -name '*.sh' -o -name '*.bash')
echo "founs sh files to check: $found_files"

## SC2002 (style): Useless cat. Consider 'cmd < file | ..' or 'cmd file | ..' instead.
## SC2129: Consider using { cmd1; cmd2; } >> file instead of individual redirects.
## SC2155 (warning): Declare and assign separately to avoid masking return values.
EXCLUDE_LIST="SC2002,SC2129,SC2155"

echo "to suppress line warning add before the line: # shellcheck disable=<code>"
# shellcheck disable=SC2068
shellcheck -a -x --exclude "$EXCLUDE_LIST" ${found_files[@]}
echo "shellcheck -- no warnings found"

echo -e "\nall checks completed"
