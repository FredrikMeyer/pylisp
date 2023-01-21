# (yet another) Python Lisp

## Usage

```bash
>  python pylisp/repl.py
Welcome to pylisp.
>((lambda (x) (+ 2 x)) 5)
7.0
>
```

### Factorial function

```bash
> python pylisp/repl.py
Welcome to pylisp.
>(set! f (lambda (x) (if (< x 2) x (* x (f (dec x))))))
>(f 7)
5040.0
```

## Built-ins

 - lambda
 - set!
 - +, and *
 - if
 
## Want to Have

 - Booleans
 - Multiple args
 - Simple math functions. Maybe import from Python?

## Installing Python

I use [pyenv](https://github.com/pyenv/pyenv#upgrading-with-homebrew) to manage Python versions.

Install Python 3.11.1:

```
pyenv install 3.11.1
```


## Similar projects 

 - [pavpanchekha/pylisp](https://github.com/pavpanchekha/pylisp).
 - [Peter Norvig: (How to Write a (Lisp) Interpreter (in Python))](https://norvig.com/lispy.html).
 - [(An ((Even Better) Lisp) Interpreter (in Python))](https://norvig.com/lispy2.html)
