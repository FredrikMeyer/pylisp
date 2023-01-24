from typing import Literal, TypedDict
from pylisp.eval import Expr, Symbol

TokenType = Literal["LEFT_PAREN", "RIGHT_PAREN", "NUMBER", "SYMBOL", "KEYWORD"]

KEYWORDS = ("lambda", "if", "quote", "set!")


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
        curr_ind = 0
        while curr_ind < len(inp) and inp[curr_ind].isdigit():
            curr_ind += 1

        return (Token(token_type="NUMBER", payload=int(inp[:curr_ind])), inp[curr_ind:])

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
ValueExp = list["ValueExp" | "Value"] | Value


def parse_string(inp: str) -> Expr:
    """
    Parse s-expression into binary tree to be used by the evaluator.
    """
    tokens = tokenize(inp)

    stack: list[list[Expr]] = [[]]

    if len(tokens) == 1:
        # We only have a single symbol/value.
        val = tokens[0]["payload"]
        assert val is not None
        return val

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
