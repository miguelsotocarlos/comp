#!/usr/bin/env python3

# Copyright (C) 2024 Carlos Miguel Soto <miguelsotocarlos@gmail.com>
# This software is licensed under the MIT License.

import glob
import subprocess
import os
from pathlib import Path
import sys
from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests
import os
import os

TEMPLATE = """#include <bits/stdc++.h>
 
using namespace std;
 
#define forsn(i,s,n) for(int i = int(s);i<int(n);i++)
#define dforsn(i,s,n) for(int i = int(n)-1;i>=int(s);i--)
#define forn(i,n) forsn(i,0,n)
#define dforn(i,n) dforsn(i,0,n)
#define fore(i,s,n) forsn(i,s,n)
 
#define ALL(x) (x).begin(),(x).end()
#define SZ(x) int((x).size())
#define DBG(x) cout<<#x<<" = "<<(x)<<endl
 
#define fst first
#define snd second
#define pb push_back
#define mp make_pair
 
template<class x> ostream & operator<<(ostream & out, vector<x> v){
    out<<"[ ";
    for(auto y : v) out<<y<<" ";
    out<<" ]";
    return out;
}

typedef double ld;
typedef long long ll;

int main() {
    cin.tie(0);
    ios::sync_with_stdio(0);
}
"""

@dataclass
class Testcase:
    index: int
    input: str
    output: str

@dataclass
class Problem:
    name: str
    testcases: list[Testcase]

def extract_text(node):
    lines = list(map(lambda x: x.get_text(), node.find_all("div", class_="test-example-line")))
    if len(lines) == 0:
        pre = node.find("pre")
        lines.append(pre.get_text())
    return "\n".join(lines)

def extract_sample(index, node):
    i = extract_text(node.find("div", class_="input"))
    o = extract_text(node.find("div", class_="output"))
    return Testcase(index, i, o)

def extract_problem(node):
    name = node.find("div", class_="title").get_text().strip().split(".")[0]
    samples = node.find_all("div", class_="sample-test")
    testcases = [extract_sample(i+1, sample) for i, sample in enumerate(samples)]
    return Problem(name, testcases)


def get_problems(contest: int):
    url = f"https://codeforces.com/contest/{contest}/problems"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    problems = soup.find_all("div", class_="problem-statement")
    if len(problems) == 0:
        raise ValueError("No problems found: {page}")
    return [extract_problem(problem) for problem in problems]

def printwithcol(text, col):
        last_has_newline = False
        print(col, end='')
        for line in text.splitlines(keepends=True):
            if line.endswith('\n'):
                last_has_newline = True
            else:
                last_has_newline = False
            print(line, end='')
        print('\033[0m', end='')
        if not last_has_newline:
            print()

def compile_latest_problem(flags):
    sources = glob.glob('*.cpp')
    source = max(sources, key=os.path.getmtime)
    basename = os.path.splitext(source)[0]

    opts = ['-Wall', '-Wextra', '-Wconversion', '-DLOCAL', '-std=c++17']
    if '--perf' in flags:
        opts += ['-O2']
    else:
        opts += ['-D_GLIBCXX_DEBUG','-g', '-ggdb3']

    code = subprocess.run(['g++', *opts, '-o', basename, source]).returncode

    if code != 0:
        printwithcol("Compilation failed. No tests run.", '\033[91m')
        return

    testcases = sorted(glob.glob(basename+'*.in'))

    for testcase in testcases:
        print("== " + testcase + " ==")

        print("Input:")
        printwithcol(Path(testcase).read_text().strip(), '\033[95m')

        output_file = testcase.replace('.in', '.out')
        if os.path.exists(output_file):
            expected_output = open(output_file).read().strip()
            print("Expected:")
            printwithcol(expected_output, '\033[93m')

        print("Actual:")
        output = subprocess.run(['./'+basename], input=open(testcase).read(), capture_output=True, text=True)
        if output.stdout:
            printwithcol(output.stdout.strip(), '\033[92m')
        if output.stderr:
            printwithcol(output.stderr.strip(), '\033[35m')

        print()

def initialize_file(path):
    print(f"initializing {path}...")
    if not path.endswith(".cpp"):
        path += ".cpp"
    Path(path).write_text(TEMPLATE)

def load_from_cf(contest=None):
    if contest is None:
        cwd = os.getcwd()
        components = cwd.split('/')
        last_number = None
        for component in reversed(components):
            if component.isdigit():
                last_number = component
                break
        contest = last_number
    
    if contest is None:
        raise ValueError("No number contest provided and no component found in the path.")

    print(f"Loading cf contest {contest}...")
    problems = get_problems(int(contest))
    for problem in problems:
        initialize_file(problem.name)
        for testcase in problem.testcases:
            Path(f"{problem.name}{testcase.index}.in").write_text(testcase.input)
            Path(f"{problem.name}{testcase.index}.out").write_text(testcase.output)

def uninstalled():
    return sys.argv[0].endswith(".py")

def install():
    installation_dir = Path(os.path.expanduser("~/.local/bin"))
    installation_file = installation_dir / "comp"
    if not installation_dir.exists():
        installation_dir.mkdir(parents=True)
    current_file = os.path.abspath(__file__)
    os.symlink(current_file, str(installation_file))
    os.chmod(str(installation_file), 0o755)

def main():
    all_args = sys.argv[1:]
    args = list(filter(lambda x: not x.startswith('--'), all_args))
    flags = list(filter(lambda x: x.startswith('--'), all_args))

    if uninstalled():
        input("Press enter to install, or Ctrl+C to cancel")
        install()
        print("Installed. Run 'comp' to use.")
        return

    if args == []:
        compile_latest_problem(flags)

    elif args[0] == "init":
        if len(args[1:]) == 0:
            raise ValueError("No files to initialize")
        for prob in args[1:]:
            initialize_file(prob)

    elif args[0] == "cf":
        if len(args) > 2:
            raise ValueError("Too many arguments")
        if len(args) == 2:
            load_from_cf(args[1])
        elif len(args) == 1:
            load_from_cf()

if __name__=="__main__":
    main()