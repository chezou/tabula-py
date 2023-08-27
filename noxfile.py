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
def tests(session):
    session.install(".[test]")
    session.run("pytest", "-v", "tests/test_read_pdf_table.py")
    session.run("pytest", "-v", "tests/test_read_pdf_jar_path.py")
    session.run("pytest", "-v", "tests/test_read_pdf_silent.py")
