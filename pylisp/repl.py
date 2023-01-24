import traceback
from pylisp.eval import (
    Environment,
    Expr,
    eval_sexp,
    standard_env,
)
from pylisp.parse import parse_string


def main(inp: str, env: Environment) -> Expr:
    try:
        r = parse_string(inp)
        res = eval_sexp(r, env=env)
        return res
    except Exception as e:
        print(traceback.format_exc())
        return str(e)


if __name__ == "__main__":
    import cmd

    class CmdL(cmd.Cmd):
        intro = "Welcome to pylisp."
        prompt = ">"

        env = standard_env()

        def do_env(self, arg: str) -> None:
            print(self.env)

        def default(self, inp: str) -> None:
            res = main(inp, self.env)
            print(res)

    CmdL().cmdloop()
