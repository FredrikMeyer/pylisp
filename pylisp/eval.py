"""
**pylisp** is a simple Lisp interpreter.

Modules:

 - This one. Contains the `eval_sexp` and `apply_sexp` functions.
 - [[environment.py]]. Contains definitions for environments and variables.
 - [[repl.py]]. An implementation of a simple read-eval loop. Can be run by
   typing `pslp` after installation.
 - [[parse.py]]. Functions for parsing strings into S-expressions.

After installation, run it from the command line with plsp. Or just type
directly `python pylisp/repl.py`.
"""
from typing import (
    Sequence,
    TypeGuard,
    Union,
)
from pylisp.environment import (
    Expr,
    Symbol,
    cadddr,
    caddr,
    cadr,
    car,
    cdr,
    Environment,
    Atom,
    UserFunction,
    PrimitiveFunction,
)

# === Eval and Apply ===


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

    if car(expr) == "let":
        return eval_let(expr, env)

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


def eval_let(expr: Sequence[Expr], env: Environment) -> Expr:
    """
    Eval a let expression:
    ```
    >(let ((x 2) (y 3)) (+ x y))
    5.0
    ```
    """
    bindings = cadr(expr)

    if not check_bindings(bindings):
        raise RuntimeError("Wrong type of bindings.")

    binding_symbols = [binding[0] for binding in bindings]
    binding_vals = [binding[1] for binding in bindings]

    body = caddr(expr)

    # We evaluate a let expression by transforming it into a lambda.
    # The expression `(let ((x 2)) (+ x 1))` is equivalent to the lambda
    # expression `((lambda (x) (+ x 1)) 2)`.
    return eval_sexp([["lambda", binding_symbols, body], *binding_vals], env)


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


def check_bindings(exprs: Expr) -> TypeGuard[list[list[Expr]]]:
    """
    Verify that `exprs` is a list of lists.
    """
    if not isinstance(exprs, list):
        return False

    return all(isinstance(inner_list, list) for inner_list in exprs)
