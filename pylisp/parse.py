from typing import Any, List, Literal, Optional, TypedDict

TokenType = Literal["LEFT_PAREN", "RIGHT_PAREN", "NUMBER", "SYMBOL"]


class Token(TypedDict):
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
        if char == " " or char == "(" or char == ")":
            break
        i += 1
    return i


def slurp_token(inp: str) -> tuple[Token, str]:
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
    return (
        Token(token_type="SYMBOL", payload=inp[0:last_char_word]),
        inp[last_char_word:],
    )


def slurp_whitespace(inp: str) -> str:
    i = 1
    while inp[:i].isspace():
        i += 1
    return inp[i - 1 :]


def parse_string(inp: str) -> list[Any] | Any:
    """
    Parse s-expression into binary tree to be used by the evaluator.
    """
    print(f"INPUT STRING: {inp}")
    tokens = tokenize(inp)
    print(f"TOKENIZED: {tokens}")

    stack: List[List[Any]] = [[]]

    if len(tokens) == 1:
        return tokens[0]["payload"]

    current_token = 0
    while current_token < len(tokens):
        if tokens[current_token]["token_type"] == "LEFT_PAREN":
            stack.append([])
        elif tokens[current_token]["token_type"] == "RIGHT_PAREN":
            top = stack.pop()
            stack_len = len(stack)
            stack[stack_len - 1].append(top)
        else:
            stack_len = len(stack)
            stack[stack_len - 1].append(tokens[current_token]["payload"])
        current_token += 1

    print(stack)
    return stack[0][0]
