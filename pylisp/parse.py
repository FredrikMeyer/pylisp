"""
The parser functionality. Parses a string and return S-expression tokens.
"""

from typing import Literal, TypedDict, Union
from pylisp.environment import Expr, Symbol

TokenType = Literal[
    "LEFT_PAREN", "RIGHT_PAREN", "NUMBER", "SYMBOL", "KEYWORD", "BOOLEAN", "STRING"
]

KEYWORDS = ("lambda", "if", "quote", "define", "let")


class Token(TypedDict):
    """
    A token represents a piece of syntax.
    """

    token_type: TokenType
    payload: None | str | int | bool


def tokenize(inp: str) -> list[Token]:
    """
    Read a string and produce a list of tokens.
    """
    curr = inp
    tokens: list[Token] = []
    while len(curr) > 0:
        curr = slurp_whitespace(curr)
        if len(curr) == 0:
            break
        token, curr = slurp_token(curr)
        tokens.append(token)
    return tokens


def find_last_non_whitespace(inp: str) -> int:
    """
    Given a string, return the index of last non-whitespace.
    """
    i = 0
    for char in inp:
        if char in (" ", ")", "("):
            break
        i += 1
    return i


def slurp_integer(inp: str) -> tuple[Token, str]:
    """
    Try to slurp an integer.
    """
    curr_ind = 0
    while curr_ind < len(inp) and inp[curr_ind].isdigit():
        curr_ind += 1

    return (Token(token_type="NUMBER", payload=int(inp[:curr_ind])), inp[curr_ind:])


def slurp_string(inp: str) -> tuple[Token, str]:
    curr_ind = 1

    # Find end of string. I.e look for second ".

    while inp[curr_ind] != '"':
        curr_ind += 1

        if curr_ind == len(inp):
            raise RuntimeError("No closing delimiter for string.")

    return (
        Token(token_type="STRING", payload=inp[1:curr_ind]),
        inp[curr_ind + 1 :],
    )


def slurp_token(inp: str) -> tuple[Token, str]:
    """
    Eat a single token and return the token and the rest of the input string.
    """
    first_letter = inp[0]
    if first_letter == "(":
        return (Token(token_type="LEFT_PAREN", payload=None), inp[1:])
    if first_letter == ")":
        return (Token(token_type="RIGHT_PAREN", payload=None), inp[1:])

    if inp[0].isdigit():
        return slurp_integer(inp)

    if inp[0] == '"':
        return slurp_string(inp)

    if inp[0] == "#" and len(inp) >= 2:
        if (false_or_true := inp[1]) in ("f", "t"):
            value = false_or_true == "t"
            return (Token(token_type="BOOLEAN", payload=value), inp[2:])

    last_char_word = find_last_non_whitespace(inp)
    the_word = inp[0:last_char_word]
    if the_word in KEYWORDS:
        return (Token(token_type="KEYWORD", payload=the_word), inp[last_char_word:])

    return (
        Token(token_type="SYMBOL", payload=the_word),
        inp[last_char_word:],
    )


def slurp_whitespace(inp: str) -> str:
    """
    Remove whitespace from beginning of string and return it.
    """
    i = 1
    while inp[:i].isspace():
        i += 1
    return inp[i - 1 :]


Value = str | int | bool | Symbol
ValueExp = Union[list[Union["ValueExp", Value]], Value]


def parse_string(inp: str) -> Expr:
    """
    Parse s-expression into binary tree to be used by the evaluator.
    """
    tokens = tokenize(inp)

    stack: list[list[Expr]] = [[]]

    current_token = 0
    while current_token < len(tokens):
        if tokens[current_token]["token_type"] == "LEFT_PAREN":
            stack.append([])
        elif tokens[current_token]["token_type"] == "RIGHT_PAREN":
            top = stack.pop()
            stack_len = len(stack)
            if stack_len == 0:
                raise RuntimeError("Unbalanced right parenthesis.")
            stack[stack_len - 1].append(top)
        else:
            stack_len = len(stack)
            top_token = tokens[current_token]
            value: str | int | bool | Symbol
            if top_token["token_type"] == "SYMBOL":
                value = Symbol(name=str(top_token["payload"]))
            else:
                payload = top_token["payload"]
                assert payload is not None
                value = payload
            stack[stack_len - 1].append(value)
        current_token += 1

    if len(stack) == 0 or len(stack[0]) == 0:
        raise RuntimeError("Unbalanced parenthesis.")
    return stack[0][0]
