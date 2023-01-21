from functools import reduce
from typing import Any, Callable, TypeGuard, Union, Optional
from dataclasses import dataclass
import operator as op


@dataclass(eq=True, frozen=True)
class Symbol:
    """
    Represents a variable.
    """

    name: str


Atom = Union[bool, str, int, float, Symbol, "UserFunction", "PrimitiveFunction"]
Expr = Union[list["Expr" | Atom], Atom]

Frame = dict[Symbol, Atom]


@dataclass
class Environment:
    """
    Represents the current environment.
    """

    vars: Frame
    outer: Optional["Environment"]

    def lookup_variable(self, variable: Symbol) -> Atom | None:
        """
        Lookup variable in environment. Lexical scoping is used: if the variable is
        not found in the current frame, we look it up in the outer frame recursively.
        """
        var = self.vars.get(variable)
        if var is not None:
            return var

        if self.outer is not None:
            return self.outer.lookup_variable(variable)

        return None

    def extend_environment(self, values: list[tuple[Symbol, Atom]]) -> "Environment":
        return Environment(vars=dict((k, v) for k, v in values), outer=self)

    def update_environment(self, symbol: Symbol, value: Atom) -> None:
        self.vars[symbol] = value


@dataclass
class UserFunction:
    body: Expr
    env: Environment
    args: list[Symbol]


@dataclass
class PrimitiveFunction:
    func: Callable
    doc: str

    def __call__(self, args: list[Atom]) -> Any:
        return self.func(args)


def standard_env() -> Environment:
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
                func=lambda a: print(a[0].doc), doc="Print a function docstring."
            ),
        },
        outer=None,
    )


def car(expr: list[Expr | Atom]):
    return expr[0]


def cdr(expr: list[Expr | Atom]):
    return expr[1:]


def cadr(expr: list[Expr | Atom]):
    return expr[1]


def caddr(expr: list[Expr | Atom]):
    return expr[2]


def cadddr(expr: list[Expr | Atom]):
    return expr[3]


def is_self_evaluating(expr: Expr) -> TypeGuard[Union[bool, str, int, float]]:
    if isinstance(expr, (list, Symbol)):
        return False

    return True


def is_variable(expr: Expr) -> TypeGuard[Symbol]:
    if isinstance(expr, Symbol):
        return True
    return False


def eval_sexp(expr: Expr, env: Environment) -> Atom | Expr | UserFunction:
    if is_self_evaluating(expr):
        return expr
    if is_variable(expr):
        res = env.lookup_variable(expr)
        if res is None:
            raise LookupError(f"No variable {expr}.")
        return res

    if not isinstance(expr, list):
        raise RuntimeError(f"Unknown token type: {expr}.")
    if len(expr) == 0:
        raise RuntimeError("Empty S-expression.")
    if car(expr) == "quote":
        return expr[1:][0]
    if car(expr) == "if":
        if eval_sexp(cadr(expr), env):
            return eval_sexp(caddr(expr), env)
        else:
            return eval_sexp(cadddr(expr), env)

    if car(expr) == "set!":
        name = cadr(expr)
        if check_symbol(name):
            value = eval_sexp(caddr(expr), env)
            if check_atom(value):
                env.update_environment(name, value)
                return value
            else:
                raise RuntimeError("Wrong type of arg to set!.")
        else:
            raise RuntimeError("Value must be symbol.")
    if car(expr) == "lambda":
        args = cadr(expr)
        if not isinstance(args, list):
            raise RuntimeError("Syntax error.")

        body = caddr(expr)
        if check_all_symbol(args):
            return UserFunction(body=body, args=args, env=env)

        raise RuntimeError(f"Lambda args must be symbols. Args {args}.")

    fn = eval_sexp(car(expr), env)
    if not isinstance(fn, (UserFunction, PrimitiveFunction)):
        raise RuntimeError(
            f"Unknown function: {fn}. Is of type {type(fn)}. Expr: {expr}"
        )

    args = list(map(lambda e: eval_sexp(e, env), cdr(expr)))

    return apply_sexp(fn, args)


def apply_sexp(
    proc: UserFunction | PrimitiveFunction, args: list[Atom | Expr]
) -> Atom | Expr | UserFunction:
    if isinstance(proc, PrimitiveFunction):
        if check_all_atom(args):
            return proc(args)
        # if check_all_number(args):
        #     return add(args)

        raise RuntimeError("Not all arguments are numbers.")

    if not isinstance(proc, UserFunction):
        raise RuntimeError(f"Unknown function {proc}.")
    procedure_args = proc.args

    if len(procedure_args) != len(args):
        raise RuntimeError(f"Wrong number of args passed to function {proc}.")

    if not check_all_atom(args):
        raise RuntimeError("Not all args are atoms.")
    new_env_values = list(zip(procedure_args, args))

    return eval_sexp(proc.body, proc.env.extend_environment(new_env_values))


def check_all_number(atoms: list[Atom | Expr]) -> TypeGuard[list[int | float]]:
    return all(isinstance(x, (int, float)) for x in atoms)


def check_symbol(arg: Expr) -> TypeGuard[Symbol]:
    return isinstance(arg, Symbol)


def check_all_symbol(args: list[Expr | Atom]) -> TypeGuard[list[Symbol]]:
    return all(isinstance(x, Symbol) for x in args)


def check_atom(arg: Expr | Atom) -> TypeGuard[Atom]:
    return not isinstance(arg, list)


def check_all_atom(args: list[Expr | Atom]) -> TypeGuard[list[Atom]]:
    return all(not isinstance(x, list) for x in args)


def add(args: list[int | float]) -> float:
    return reduce(lambda acc, curr: acc + curr, args, 0.0)


def mult(args: list[int | float]) -> float:
    return reduce(lambda acc, curr: acc * curr, args, 1.0)
