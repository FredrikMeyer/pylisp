from pylisp.eval import Environment, add, eval_sexp, Symbol, PrimitiveFunction
from pylisp.parse import parse_string


def main(inp: str):
    try:
        r = parse_string(inp)
        res = eval_sexp(
            r, env=Environment(vars={Symbol("+"): PrimitiveFunction(func=add)}, outer=None)
        )
        return res
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    import cmd

    class CmdL(cmd.Cmd):
        intro = "hei"
        prompt = ">"

        def default(self, inp: str):
            res = main(inp)
            print(res)

    CmdL().cmdloop()
