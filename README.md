# Comp utility
Small utility to compile and test C++ code for competitive programming.

## Installation
To install the dependencies, run `python3 -m pip install bs4 requests`. Then, run `python3 main.py` to install the program as the `comp` executable in `~/.local/bin/comp`.

## Usage
  - `comp`: Compile the oldest C++ file in the dir and run its associated testcases.
  - `comp cf [contest]`: Download the codeforces testcases for the associated contest. If the `contest` argument is not provided, the last number in the path of cwd will be used.
  - `comp init [problem...]`: Initialize the C++ files for the provided problems with a template. For example: `comp init A B C` creates files `A.cpp`, `B.cpp` and `C.cpp` and populates them with a template.