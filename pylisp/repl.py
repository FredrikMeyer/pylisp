from pylisp.eval import Environment, eval_sexp
from pylisp.parse import parse_string


def main(inp: str):
    r = parse_string(inp)

    return eval_sexp(r, env=Environment(vars={}, outer=None))

if __name__ == '__main__':
    while True:
        inp = input(">> ")
        res = main(inp)
        print(res)

        print(">>")
