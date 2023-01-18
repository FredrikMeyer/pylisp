import pytest
from pylisp.parse import parse_string, slurp_token, slurp_whitespace, tokenize, Token


def test_single_value():
    res = parse_string("5")

    assert not isinstance(res, list)

    assert res == 5


def test_simple_expression():
    res = parse_string("(+ 1 2)")

    assert isinstance(res, list)
    assert len(res) == 3

    assert res[0] == "+"
    assert res[1] == 1
    assert res[2] == 2


def test_nested():
    res = parse_string("(+ (+ 1 2) 3)")

    assert len(res) == 3
    print("RES", res)
    assert len(res[1]) == 3
    assert res[1][0] == "+"
    assert res[1][1] == 1
    assert res[1][2] == 2


@pytest.mark.parametrize(
    "inp,exp",
    [
        ("(+ 1 2)", ["+", 1, 2]),
        ("(+ (* 2 4) (+ 1 2))", ["+", ["*", 2, 4], ["+", 1, 2]]),
        ("(+ 2 x)", ["+", 2, "x"])
    ],
)
def test_many(inp: str, exp):
    res = parse_string(inp)
    assert res == exp


def test_unbalanced():
    with pytest.raises(IndexError):
        parse_string("(+ 1 2))")
    with pytest.raises(IndexError):
        parse_string("((+ 1 2)")


def test_read_next_token():
    read_left_paren = slurp_token("(+ 2 3)")
    token, rest = read_left_paren
    assert token == Token(token_type="LEFT_PAREN", payload=None)
    assert rest == "+ 2 3)"

    read_number = slurp_token("4 4 4")
    token, rest = read_number
    assert token == Token(token_type="NUMBER", payload=4)
    assert rest == " 4 4"

    read_string = slurp_token("hei 4")
    token, rest = read_string
    assert token == Token(token_type="SYMBOL", payload="hei")
    assert rest == " 4"


def test_slurp_whitespace():
    res = slurp_whitespace("   hei")

    assert res == "hei"


def test_tokenize():
    res = tokenize("(+ 2 3)")

    assert res == [
        Token(token_type="LEFT_PAREN", payload=None),
        Token(token_type="SYMBOL", payload="+"),
        Token(token_type="NUMBER", payload=2),
        Token(token_type="NUMBER", payload=3),
        Token(token_type="RIGHT_PAREN", payload=None),
    ]

    res2 = tokenize("(+ 23 43)")

    assert res2 == [
        Token(token_type="LEFT_PAREN", payload=None),
        Token(token_type="SYMBOL", payload="+"),
        Token(token_type="NUMBER", payload=23),
        Token(token_type="NUMBER", payload=43),
        Token(token_type="RIGHT_PAREN", payload=None),
    ]
