"""
Simple REPL functionality for pylisp.
"""
import traceback
from pylisp.eval import (
    Environment,
    Expr,
    eval_sexp,
    standard_env,
)
from pylisp.parse import parse_string


def main(inp: str, env: Environment) -> Expr:
    """
    The main method. Input is any string and an environment to run in.
    """
    try:
        parsed_string = parse_string(inp)
        res = eval_sexp(parsed_string, env=env)
        return res
    except Exception as exception:
        print(traceback.format_exc())
        return str(exception)


def repl() -> None:
    """
    Run a simple REPL.
    """
    import cmd

    class CmdL(cmd.Cmd):
        """
        Subclass of cmd.Cmd. Makes a simple read-eval loop.
        """

        intro = "Welcome to pylisp."
        prompt = ">"

        env = standard_env()

        should_exit = False

        def do_env(self, _: str) -> None:
            """
            Print the current environment.
            """
            print(self.env)

        def default(self, line: str) -> None:
            res = main(line, self.env)
            print(res)

        def postcmd(self, stop: bool, line: str) -> bool:
            return line == ":quit"

    CmdL().cmdloop()


if __name__ == "__main__":
    repl()
