"""
Parse mypy output to be able to display it nicely in Github Actions.

https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message
"""

import sys
from mypy import api


def parse_error_message(messages: list[str]) -> None:
    """
    Loop through error messages and parse them.
    """
    for m in messages:
        m_spl = m.split(":")

        file_n = m_spl[0]
        line_no = m_spl[1]
        col = m_spl[2]
        level = m_spl[3].strip()
        messag = " ".join(m_spl[4:])
        print(f"::{level} file={file_n},line={line_no},col={col}::{messag}")


if __name__ == "__main__":
    res = api.run(
        ["-p", "pylisp", "--hide-error-context", "--no-pretty", "--no-error-summary"]
    )

    msgs = res[0].splitlines()
    parse_error_message(msgs)

    sys.exit(res[2])
