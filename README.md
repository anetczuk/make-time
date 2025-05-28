# make-time

Calculate C++ object files compilation time based on `make` output.


## Example output

Example output with list of compiled objects and it's duration:
```
Total time                                         0.426148 sec
CMakeFiles/hello_library.dir/src/Hello.cpp.o       0.254017 sec
CMakeFiles/hello_binary.dir/src/main.cpp.o         0.023657 sec
```


## Running

Use of application requires two steps:

1. obtaining log data from *make* application,
2. executing the tool.

It can be even easier: just execute `maketime.sh` as replacement of `make` command. All command-line arguments 
will be forwarded to `make` itself.


#### Obtaining data from *make*

*make-time* as input needs log data from *make* tool. The log have to be obtained running following command:
```
    make -j1 <optional_targets> | ts '[%H:%M:%.S]' | tee compile_log.txt
```
`ts` command can be installed by command `sudo apt install moreutils`.


#### Running the application

To run application simply execute followoing command:
```
python3 -m maketime.main -clf compile_log.txt
```

Application accepts following arguments:

<!-- insertstart include="doc/cmdargs.txt" pre="\n" post="\n" -->
```
usage: python3 -m maketime.main [-h] [--loglevel LOGLEVEL] [-la] -clf
                                COMPILELOGFILE [--outfile OUTFILE]

calculate C++ object files compilation time based on `make` output

options:
  -h, --help            show this help message and exit
  --loglevel LOGLEVEL   Set log level (default: None)
  -la, --logall         Log all messages (default: False)
  -clf COMPILELOGFILE, --compilelogfile COMPILELOGFILE
                        Path to make compile log file (default: None)
  --outfile OUTFILE     Path to output file (default: )
```

<!-- insertend -->


## Installation

Installation of package can be done by:
 - to install package from downloaded ZIP file execute: `pip3 install --user -I file:make-time-master.zip#subdirectory=src`
 - to install package directly from GitHub execute: `pip3 install --user -I git+https://github.com/anetczuk/make-time.git#subdirectory=src`
 - uninstall: `pip3 uninstall maketime`

Installation for development:
 - `install-deps.sh` to install package dependencies only (`requirements.txt`)
 - `install-package.sh` to install package in standard way through `pip` (with dependencies)
 - `install-devel.sh` to install package in developer mode using `pip` (with dependencies)


## Development

All tests, linters and content generators can be executed by simple script `./process-all.sh`.

Unit tests are executed by `./src/testmaketime/runtests.py`.

Code linters can be run by `./tools/checkall.sh`.

In case of pull requests please run `process-all.sh` before the request.


## License

```
BSD 3-Clause License

Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
