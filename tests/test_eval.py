import pytest
from pylisp.eval import Environment, Symbol, UserFunction, apply_sexp, eval_sexp


@pytest.mark.parametrize(
    ["inp", "expected"],
    [("5", "5"), (5, 5), (["quote", 5], 5), (["quote", ["+", 2, 3]], ["+", 2, 3])],
)
def test_constant(inp, expected):
    res = eval_sexp(inp, Environment(vars={'x': 2}, outer=None))
    assert res == expected


def test_boolean():
    inp = ["if", True, 1, 2]
    res = eval_sexp(inp, Environment(vars={'x': 2}, outer=None))

    assert res == 1


def test_add():
    inp = ["+", 1, 2]
    res = eval_sexp(inp, Environment(vars={'x': 2}, outer=None))

    assert res == 3

    inp2 = ["+", ["+", 1, 2], 3]
    res = eval_sexp(inp2, Environment(vars={'x': 2}, outer=None))

    assert res == 6

def test_lambda():
    inp = ["lambda", ["x"], ["+", 2, "x"]]
    answ = eval_sexp(inp, Environment(vars={'x': 2}, outer=None))

    print(answ)

    inp2 = [["lambda", ["x"], ["+", 2, Symbol(name="x")]], 3]

    answ2 = eval_sexp(inp2, Environment(vars={'x': 2}, outer=None))

    print(answ2)
    assert answ2 == 5


def test_lookup_symbol():
    inp = Symbol(name="x")

    answ = eval_sexp(inp, Environment(vars={'x': 2}, outer=None))

    print(answ)

    assert answ == 2


def test_extend_environment():
    env1 = Environment(vars={'x': 2}, outer=None)

    env2 = env1.extend_environment(values=[("y", 3)])

    res = env2.lookup_variable(variable=Symbol(name="y"))

    assert res == 3

def test_apply_sexp():
    proc = UserFunction(body=["+", 1, Symbol(name="x")], env=Environment(vars={}, outer=None), args=["x"])

    res = apply_sexp(proc, [3])

    print(res)
    assert res == 4
