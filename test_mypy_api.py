from mypy import api


def parse_error_message(messages: list[str]) -> None:
    for m in messages:
        m_spl = m.split(":")

        file_n = m_spl[0]
        line_no = m_spl[1]
        col = m_spl[2]
        level = m_spl[3].strip()
        messag = " ".join(m_spl[4:])
        print(f"::error file={file_n},line={line_no}::{messag}")


if __name__ == "__main__":
    res = api.run(
        ["-p", "pylisp", "--hide-error-context", "--no-pretty", "--no-error-summary"]
    )

    msgs = res[0].splitlines()

    print(parse_error_message(msgs))
