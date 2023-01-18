from functools import reduce
from typing import TypeGuard, TypedDict, Union, Optional
from dataclasses import dataclass


@dataclass
class Symbol:
    name: str


Atom = Union[bool, str, int, float, Symbol]
Expr = Union[list["Expr"], Atom]

Frame = dict[str, Atom]


@dataclass
class Environment:
    vars: Frame
    outer: Optional["Environment"]

    def lookup_variable(self, variable: Symbol):
        name = variable.name
        var = self.vars.get(name)
        if var is not None:
            return var

        if self.outer is not None:
            return self.outer.lookup_variable(variable)

        return None

    def extend_environment(self, values: list[tuple[str, Atom]]):
        return Environment(vars=dict((k, v) for k, v in values), outer=self)


@dataclass
class UserFunction:
    body: Expr
    env: Environment
    args: list[str]


def car(expr: list[Expr]):
    return expr[0]


def cdr(expr: list[Expr]):
    return expr[1:]


def cadr(expr: list[Expr]):
    return expr[1]


def caddr(expr: list[Expr]):
    return expr[2]


def cadddr(expr: list[Expr]):
    return expr[3]


def is_self_evaluating(expr: Expr) -> TypeGuard[Union[bool, str, int, float]]:
    if isinstance(expr, (list, Symbol)):
        return False

    return True


def is_variable(expr: Expr) -> TypeGuard[Symbol]:
    if isinstance(expr, Symbol):
        return True
    return False


def eval_sexp(expr: Expr, env: Environment):
    print("ENV", env)
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
    if car(expr) == "lambda":
        args = cadr(expr)
        body = caddr(expr)
        return UserFunction(body=body, args=args, env=env)

    fn = eval_sexp(car(expr), env)
    args = list(map(lambda e: eval_sexp(e, env), cdr(expr)))

    print(f"FN: {fn}. Args: {args}.")

    return apply_sexp(fn, args)

    raise NotImplementedError(f"Not implemented. Unknown sexp: {expr}")


def apply_sexp(proc: UserFunction | list[Expr], args: list[Atom]):
    # fn = eval_sexp(car(expr), env)
    # args = list(map(lambda e: eval_sexp(e, env), cdr(expr)))

    if proc == "+":
        return add(args)

    if not isinstance(proc, UserFunction):
        raise RuntimeError(f"Unknown function {proc}.")
    procedure_args = proc.args

    if len(procedure_args) != len(args):
        raise RuntimeError(f"Wrong number of args passed to function {proc}.")

    new_env_values = list(zip(procedure_args, args))
    return eval_sexp(proc.body, proc.env.extend_environment(new_env_values))


def add(args: list[int]):
    return reduce(lambda acc, curr: acc + curr, args, 0)
