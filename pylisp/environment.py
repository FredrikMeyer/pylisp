"""
Functions for defining the environment. Take a look especially at the Environment
class, which implements the logic for lexical scoping.
"""
from functools import reduce
from typing import (
    Callable,
    Generic,
    Sequence,
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
    """
    Returns the third element in a sequence.
    """
    return expr[2]


def cadddr(expr: Sequence[Expr]) -> Expr:
    return expr[3]


def add(args: Sequence[int | float]) -> float:
    return reduce(lambda acc, curr: acc + curr, args, 0.0)


def mult(args: Sequence[int | float]) -> float:
    return reduce(lambda acc, curr: acc * curr, args, 1.0)
