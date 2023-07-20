# (yet another) Python Lisp

[![codecov](https://codecov.io/gh/FredrikMeyer/pylisp/branch/main/graph/badge.svg?token=PA2OOMZJ80)](https://codecov.io/gh/FredrikMeyer/pylisp)

See [fredrikmeyer.net/pylisp/](https://fredrikmeyer.net/pylisp/) for a literate style documentation.

## Installation

Run `pip install --editable .`. There are no dependencies.

Run tests with `pytest`, and linting with `flake8 .`

## Usage

```bash
>  python pylisp/repl.py
Welcome to pylisp.
>((lambda (x) (+ 2 x)) 5)
7.0
>
```

Or pipe text:

```bash
> echo '(+ 1 2)' | plsp
3.0
```

### Factorial function

```bash
> python pylisp/repl.py
Welcome to pylisp.
>(define f (lambda (x) (if (< x 2) x (* x (f (dec x))))))
>(f 7)
5040.0
```

## Built-ins

 - lambda
 - define
 - +, and *, <, =, dec
 - if
 - doc (docstring for built-ins)
 - car
 
## Want to Have

 - Multiple args
 - Simple math functions. Maybe import from Python?
 - Quotes
 - Macros
 - Read from file

## Installing Python

I use [pyenv](https://github.com/pyenv/pyenv#upgrading-with-homebrew) to manage Python versions.

Install Python 3.11.1:

```
pyenv install 3.11.1
```

## Build Docs

Docs are built with [`pycco`](https://github.com/pycco-docs/pycco). Build them by running `pip install pycco` and `pycco pylisp/*.py`. I use a simple search-replace to make `eval.py` the index page.


## Similar projects 

 - [pavpanchekha/pylisp](https://github.com/pavpanchekha/pylisp).
 - [Peter Norvig: (How to Write a (Lisp) Interpreter (in Python))](https://norvig.com/lispy.html).
 - [(An ((Even Better) Lisp) Interpreter (in Python))](https://norvig.com/lispy2.html)
 - [lithp](https://github.com/fogus/lithp) by fogus. Written in perhaps more idiomatic Python.
