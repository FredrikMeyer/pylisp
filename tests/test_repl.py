from pylisp.environment import Symbol, UserFunction, standard_env
from pylisp.repl import main, repl
import pytest


def test_factorial() -> None:
    env = standard_env()
    main("(define f (lambda (x) (if (< x 2) x (* x (f (dec x))))))", env)

    factorial_function = env.lookup_variable(Symbol("f"))

    assert isinstance(factorial_function, UserFunction)

    res2 = main("(f 5)", env)

    assert res2 == 120.0


def test_exception_is_printed(capsys: pytest.CaptureFixture[str]) -> None:
    env = standard_env()
    res = main("(", env)
    std_ouput = capsys.readouterr().out

    print(std_ouput)
    assert "Traceback" in std_ouput

    assert isinstance(res, str)
    assert "Unbalanced parenthesis" in res


def test_docstring() -> None:
    env = standard_env()
    res = main("(doc +)", env)

    assert res == "Add a list of numbers."


def test_let() -> None:
    env = standard_env()
    res = main("(let ((x 2) (y 3)) (+ x y))", env)

    assert res == 5.0


def test_repl(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO("(+ 1 2)\n:quit"))

    repl()

    std_ouput = capsys.readouterr().out

    print(std_ouput)

    assert "3.0" in std_ouput
