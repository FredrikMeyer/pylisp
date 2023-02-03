"""
**pylisp** is a simple Lisp interpreter.

Modules:

 - This one. Contains the `eval_sexp` and `apply_sexp` functions.
 - [[repl.py]]. An implementation of a simple read-eval loop. Can be run by
   typing `pslp` after installation.
 - [[parse.py]]. Functions for parsing strings into S-expressions.

After installation, run it from the command line with plsp. Or just type
directly `python pylisp/repl.py`.
"""
from functools import reduce
from typing import (
    Callable,
    Generic,
    Sequence,
    TypeGuard,
    TypeVar,
    Union,
    Optional,
)
from dataclasses import dataclass
import operator as op


@dataclass(eq=True, frozen=True)
class Symbol:
    """
    Represents a variable.
    """

    name: str


Atom = Union[bool, str, int, float, Symbol, "UserFunction", "PrimitiveFunction"]
Expr = Union[Sequence["Expr" | Atom], Atom]

"""
A _frame_ is the term used by the authors of SICP to refer to variables in the the
current closure.
"""
Frame = dict[Symbol, Atom]


@dataclass
class Environment:
    """
    Represents the current environment. An environment consists of a frame, together
    with possibly a reference to the outer frame.

    This is how lexical scoping works: variables in the current scope might shadow
    variables in the outer scope.
    """

    vars: Frame
    outer: Optional["Environment"]

    def lookup_variable(self, variable: Symbol) -> Atom | None:
        """
        Lookup variable in the environment. Lexical scoping is used: if the variable is
        not found in the current frame, we look it up in the outer frame recursively.
        """
        var = self.vars.get(variable)
        if var is not None:
            return var

        if self.outer is not None:
            return self.outer.lookup_variable(variable)

        return None

    def extend_environment(self, values: list[tuple[Symbol, Atom]]) -> "Environment":
        """
        Extend the current environment with the values provided by 'values'. Creates
        a new frame.
        """
        return Environment(vars=dict((k, v) for k, v in values), outer=self)

    def update_environment(self, symbol: Symbol, value: Atom) -> None:
        """
        Update the current environment. This attaches a new variable to the
        current frame.
        """
        self.vars[symbol] = value


@dataclass
class UserFunction:
    """
    Represents a lambda function. It has a list of args and a body. It remembers
    the environment in which it was created.
    """

    body: Expr
    env: Environment
    args: list[Symbol]


SubTypeAtom = TypeVar("SubTypeAtom", bound=Expr)


@dataclass
class PrimitiveFunction(Generic[SubTypeAtom]):
    """
    A primitive function is a non-Lisp function, defined in the implementing language.

    We give it a function and a docstring to create it.
    """

    func: Callable[[Sequence[SubTypeAtom]], SubTypeAtom]
    doc: str

    def __call__(self, args: Sequence[SubTypeAtom]) -> SubTypeAtom:
        return self.func(args)


def standard_env() -> Environment:
    """
    The standard environment which includes built-in functions.
    """
    return Environment(
        vars={
            Symbol("+"): PrimitiveFunction(func=add, doc="Add a list of numbers."),
            Symbol("dec"): PrimitiveFunction(
                func=lambda a: a[0] - 1, doc="Decrement a number."
            ),
            Symbol("*"): PrimitiveFunction(
                func=mult, doc="Multiply a list of numbers."
            ),
            Symbol("<"): PrimitiveFunction(
                func=lambda a: op.lt(*a), doc="Less than. Accepts two arguments."
            ),
            Symbol("="): PrimitiveFunction(
                func=lambda a: op.eq(*a), doc="Equals. Accepts two arguments."
            ),
            Symbol("doc"): PrimitiveFunction(
                func=doc, doc="Print a function docstring."
            ),
            Symbol("car"): PrimitiveFunction(
                func=lambda a: car(*a),  # pyright: ignore
                doc="Return first element of list.",
            ),
        },
        outer=None,
    )


def eval_sexp(expr: Expr, env: Environment) -> Atom | Expr:
    """
    Eval the given S-expression. The first half of the eval-apply loop.
    """
    # Self evaluating expressions are symbols, strings, and numbers.
    if is_self_evaluating(expr):
        return expr

    # A variable is a symbol. We try to look it up.
    if is_variable(expr):
        res = env.lookup_variable(expr)
        if res is None:
            raise LookupError(f"No variable {expr}.")
        return res

    # If the input is not a sequence, it should be either a symbol or a value.
    # We raise an error if it is neither.
    if not isinstance(expr, Sequence):
        raise RuntimeError(f"Unknown token type: {expr}.")

    # If we encouter the expression (), raise an error.
    if len(expr) == 0:
        raise RuntimeError("Empty S-expression.")

    # A quoted expression just returns the expression, like this:
    # `(quote (+ 1 2)) -> (+ 1 2)`
    # This is how "code is data" makes sense in Lisp languages.
    if car(expr) == "quote":
        return expr[1:][0]

    if car(expr) == "if":
        return eval_if(expr, env)

    # Define a value:
    # `(define a 2)` sets the symbol a to point to the value 2.
    if car(expr) == "define":
        return eval_define(expr, env)

    # Define a lambda expression.
    if car(expr) == "lambda":
        return eval_lambda(expr, env)

    # We have exhausted the syntax forms (quote, if, lambda, etc...), so our expression
    # is a function that must be evaluated. We do this by evaluating the first element
    # in the sequence:
    # `((if 1 + -) 1 2) -> (+ 1 2)`
    fun = eval_sexp(car(expr), env)

    # If it does not resolve to a function, raise an error.
    if not isinstance(fun, (UserFunction, PrimitiveFunction)):
        raise RuntimeError(
            f"Unknown function: {fun}. Is of type {type(fun)}. Expr: {expr}"
        )

    # We extract the arguments of the function and evaluate them in the current
    # environment.
    args = cdr(expr)
    if not isinstance(args, list):
        raise RuntimeError("Arguments is not a list")
    args_evaluated = list(map(lambda e: eval_sexp(e, env), args))

    # We bounce over to the other half of the eval-apply loop to evaluate the
    # function.
    return apply_sexp(fun, args_evaluated)


def apply_sexp(
    proc: UserFunction | PrimitiveFunction[Expr], args: list[Atom | Expr]
) -> Atom | Expr | UserFunction:
    """
    The other half of the eval-apply loop. Given a function type, reduces it by
    evaluating terms recursively.
    """

    # If the function is a primitive function, just apply it to the arguments.
    if isinstance(proc, PrimitiveFunction):
        return proc(args)

    if not isinstance(proc, UserFunction):
        raise RuntimeError(f"Unknown function {proc}.")
    procedure_args = proc.args

    if len(procedure_args) != len(args):
        raise RuntimeError(f"Wrong number of args passed to function {proc}.")

    if not check_all_atom(args):
        raise RuntimeError("Not all args are atoms.")

    # This line contains a lot. The way to evaluate a lambda function is to extend
    # its environment with values for the symbols in its argument list.
    new_env_values = list(zip(procedure_args, args))
    extended_environment = proc.env.extend_environment(new_env_values)

    # Then we hand the evaluation back to eval_sexp again.
    return eval_sexp(proc.body, extended_environment)


def eval_if(expr: Sequence[Expr], env: Environment) -> Atom | Expr:
    """
    Eval an if block. If condition is (Python) True, then eval first term, else
    eval second term.
    """
    condition = cadr(expr)
    if eval_sexp(condition, env):
        return eval_sexp(caddr(expr), env)

    return eval_sexp(cadddr(expr), env)


def eval_define(expr: Sequence[Expr], env: Environment) -> Atom:
    """
    Evaluate a define-expression.
    """
    name = cadr(expr)
    if check_symbol(name):
        value = eval_sexp(caddr(expr), env)
        if check_atom(value):
            env.update_environment(name, value)
            return value

        raise RuntimeError("Wrong type of arg to define.")

    raise RuntimeError("Value must be symbol.")


def eval_lambda(expr: Sequence[Expr], env: Environment) -> UserFunction:
    """
    Evaluate an S-expression defining a lambda.

    A lambda consists of three things: its body, which is just a sequence of
    S-expressions, its argument list, which is a list of unresolved symbols,
    and finally, a reference to the environment it was created in.
    """
    args = cadr(expr)
    if not isinstance(args, list):
        raise RuntimeError("Syntax error.")

    body = caddr(expr)
    if check_all_symbol(args):
        return UserFunction(body=body, args=args, env=env)

    raise RuntimeError(f"Lambda args must be symbols. Args {args}.")


def doc(expr: Sequence[Expr]) -> Expr:
    """
    Print the docstring of the given function. The argument must be of type
    PrimitiveFunction.
    """
    if len(expr) != 1:
        raise RuntimeError("Need only one argument.")
    first_el = expr[0]

    if not isinstance(first_el, PrimitiveFunction):
        raise RuntimeError("Can only show doc of built-ins.")

    return first_el.doc


def car(expr: Sequence[Expr]) -> Expr:
    """
    Get the first element of a sequence of expressions.
    """
    return expr[0]


def cdr(expr: Sequence[Expr]) -> Expr:
    """
    Return rest of list.
    """
    if not isinstance(expr, list):
        raise RuntimeError("expr must be a list.")
    return expr[1:]


def cadr(expr: Sequence[Expr]) -> Expr:
    """
    Return second element in a sequence.
    """
    return expr[1]


def caddr(expr: Sequence[Expr]) -> Expr:
    return expr[2]


def cadddr(expr: Sequence[Expr]) -> Expr:
    return expr[3]


def add(args: Sequence[int | float]) -> float:
    return reduce(lambda acc, curr: acc + curr, args, 0.0)


def mult(args: Sequence[int | float]) -> float:
    return reduce(lambda acc, curr: acc * curr, args, 1.0)


# === Typeguards ===


# Integrates type checks and assertions.


def check_all_number(atoms: list[Atom | Expr]) -> TypeGuard[list[int | float]]:
    """
    Typeguard to verify that all items in `atoms` is of number type.
    """
    return all(isinstance(x, (int, float)) for x in atoms)


def check_symbol(arg: Expr) -> TypeGuard[Symbol]:
    """
    Typeguard to verify that `arg` is a symbol.
    """
    return isinstance(arg, Symbol)


def check_all_symbol(args: list[Expr | Atom]) -> TypeGuard[list[Symbol]]:
    """
    Typeguard to verify that all items in `args` are symbols.
    """
    return all(isinstance(x, Symbol) for x in args)


def check_atom(arg: Expr | Atom) -> TypeGuard[Atom]:
    """
    Verify that `arg` is an Atom.
    """
    return not isinstance(arg, list)


def check_all_atom(args: list[Expr | Atom]) -> TypeGuard[list[Atom]]:
    return all(not isinstance(x, list) for x in args)


def is_self_evaluating(expr: Expr) -> TypeGuard[Union[bool, str, int, float]]:
    if isinstance(expr, (list, Symbol)):
        return False

    return True


def is_variable(expr: Expr) -> TypeGuard[Symbol]:
    """
    Verify that expr is a variable.
    """
    if isinstance(expr, Symbol):
        return True
    return False
