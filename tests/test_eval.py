import pytest
from pylisp.eval import (
    Environment,
    Symbol,
    UserFunction,
    apply_sexp,
    eval_sexp,
    mult,
    standard_env,
)


@pytest.mark.parametrize(
    ["inp", "expected"],
    [("5", "5"), (5, 5), (["quote", 5], 5), (["quote", ["+", 2, 3]], ["+", 2, 3])],
)
def test_constant(inp, expected):
    res = eval_sexp(inp, Environment(vars={Symbol("x"): 2}, outer=None))
    assert res == expected


def test_boolean():
    inp = ["if", True, 1, 2]
    res = eval_sexp(inp, Environment(vars={Symbol("x"): 2}, outer=None))

    assert res == 1


def test_add():
    env = standard_env()
    env = env.extend_environment([(Symbol("x"), 2)])
    inp = [Symbol("+"), 1, 2]
    res = eval_sexp(inp, env)

    assert res == 3

    inp2 = [Symbol("+"), [Symbol("+"), 1, 2], 3]
    res = eval_sexp(inp2, env)

    assert res == 6


def test_lambda():
    env = standard_env()
    env = env.extend_environment([(Symbol("x"), 2)])
    inp = ["lambda", [Symbol("x")], [Symbol("+"), 2, "x"]]
    answ = eval_sexp(inp, env)

    print(answ)

    inp2 = [["lambda", [Symbol("x")], [Symbol("+"), 2, Symbol(name="x")]], 3]

    answ2 = eval_sexp(inp2, env)

    print(answ2)
    assert answ2 == 5


def test_lookup_symbol():
    inp = Symbol(name="x")

    answ = eval_sexp(inp, Environment(vars={Symbol("x"): 2}, outer=None))

    print(answ)

    assert answ == 2


def test_extend_environment():
    env1 = Environment(vars={Symbol("x"): 2}, outer=None)

    env2 = env1.extend_environment(values=[(Symbol("y"), 3)])

    res = env2.lookup_variable(variable=Symbol(name="y"))

    assert res == 3


def test_apply_sexp():
    proc = UserFunction(
        body=[Symbol("+"), 1, Symbol(name="x")],
        env=standard_env(),
        args=[Symbol("x")],
    )

    res = apply_sexp(proc, [3])

    print(res)
    assert res == 4


def test_mult():
    res = mult([1, 2., 3])

    assert res == 6.
