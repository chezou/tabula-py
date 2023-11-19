import nox


@nox.session
def lint(session):
    lint_tools = [
        "black",
        "isort",
        "flake8",
        "mypy",
        "types-setuptools",
        "Flake8-pyproject",
    ]
    targets = ["tabula", "tests", "noxfile.py"]
    session.install(*lint_tools)
    session.run("flake8", *targets)
    session.run("black", "--diff", "--check", *targets)
    session.run("isort", "--check-only", *targets)
    session.run("mypy", *targets)


@nox.session
@nox.parametrize(
    "python,jpype",
    [
        ("3.8", True),
        ("3.9", True),
        ("3.10", True),
        ("3.11", True),
        ("3.12", False),
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
