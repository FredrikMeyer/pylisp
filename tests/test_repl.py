from pylisp.eval import Symbol, UserFunction, standard_env
from pylisp.repl import main


def test_factorial():
    env = standard_env()
    res = main("(define f (lambda (x) (if (< x 2) x (* x (f (dec x))))))", env)

    factorial_function = env.lookup_variable(Symbol("f"))

    assert isinstance(factorial_function, UserFunction)

    res2 = main("(f 5)", env)

    assert res2 == 120.0
