from typing import Any
import pytest
from pylisp.environment import (
    Expr,
    mult,
    standard_env,
    Environment,
    Symbol,
    UserFunction,
)
from pylisp.eval import (
    apply_sexp,
    check_all_number,
    eval_sexp,
)


@pytest.mark.parametrize(
    ["inp", "expected"],
    [("5", "5"), (5, 5), (["quote", 5], 5), (["quote", ["+", 2, 3]], ["+", 2, 3])],
)
def test_constant(inp: Any, expected: Any) -> None:
    res = eval_sexp(inp, Environment(vars={Symbol("x"): 2}, outer=None))
    assert res == expected


def test_boolean() -> None:
    inp: Expr = ["if", True, 1, 2]
    res = eval_sexp(inp, Environment(vars={Symbol("x"): 2}, outer=None))

    assert res == 1


def test_add() -> None:
    env = standard_env()
    env = env.extend_environment([(Symbol("x"), 2)])
    inp: Expr = [Symbol("+"), 1, 2]
    res = eval_sexp(inp, env)

    assert res == 3

    inp2: Expr = [Symbol("+"), [Symbol("+"), 1, 2], 3]
    res = eval_sexp(inp2, env)

    assert res == 6


def test_lambda() -> None:
    env = standard_env()
    env = env.extend_environment([(Symbol("x"), 2)])
    inp: Expr = ["lambda", [Symbol("x")], [Symbol("+"), 2, "x"]]
    answ = eval_sexp(inp, env)

    print(answ)

    inp2: Expr = [["lambda", [Symbol("x")], [Symbol("+"), 2, Symbol(name="x")]], 3]

    answ2 = eval_sexp(inp2, env)

    print(answ2)
    assert answ2 == 5


def test_lookup_symbol() -> None:
    inp = Symbol(name="x")

    answ = eval_sexp(inp, Environment(vars={Symbol("x"): 2}, outer=None))

    print(answ)

    assert answ == 2


def test_extend_environment() -> None:
    env1 = Environment(vars={Symbol("x"): 2}, outer=None)

    env2 = env1.extend_environment(values=[(Symbol("y"), 3)])

    res = env2.lookup_variable(variable=Symbol(name="y"))

    assert res == 3


def test_apply_sexp() -> None:
    proc = UserFunction(
        body=[Symbol("+"), 1, Symbol(name="x")],
        env=standard_env(),
        args=[Symbol("x")],
    )

    res = apply_sexp(proc, [3])

    print(res)
    assert res == 4


def test_mult() -> None:
    res = mult([1, 2.0, 3])

    assert res == 6.0


def test_check_all_number() -> None:
    res = check_all_number(["1", 2, 3])

    assert res is False

    res = check_all_number([1, 2, 3])
    assert res is True


def test_define() -> None:
    env = standard_env()
    res = eval_sexp(["define", Symbol("x"), 2], env)
    assert res == 2

    val = env.lookup_variable(Symbol("x"))

    assert val == 2
