import nox


@nox.session
def lint(session):
    lint_tools = [
        "ruff",
        "mypy",
        "types-setuptools",
        "Flake8-pyproject",
    ]
    targets = ["tabula", "tests", "noxfile.py"]
    session.install(*lint_tools)
    session.run("ruff", "format", "--check", *targets)
    session.run("ruff", "check", *targets)
    session.run("mypy", *targets)


@nox.session
@nox.parametrize(
    "python,jpype",
    [
        ("3.9", True),
        ("3.10", True),
        ("3.11", True),
        ("3.12", True),
        ("3.13", False),  # jpype does not support Python 3.13 yet
        # ("3.13", True),
    ],
)
def tests(session, jpype):
    if jpype:
        tests_with_jpype(session)
    else:
        tests_without_jpype(session)


def tests_without_jpype(session):
    session.install(".[test]")
    session.run("pytest", "-v", "tests/test_read_pdf_table.py")


def tests_with_jpype(session):
    session.install(".[jpype,test]")
    session.run("pytest", "-v", "tests/test_read_pdf_table.py")
    session.run("pytest", "-v", "tests/test_read_pdf_jar_path.py")
    session.run("pytest", "-v", "tests/test_read_pdf_silent.py")
