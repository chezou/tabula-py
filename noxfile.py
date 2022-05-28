import nox


@nox.session
def lint(session):
    lint_tools = ["black", "isort", "flake8", "mypy", "types-setuptools"]
    targets = ["tabula", "tests", "noxfile.py"]
    session.install(*lint_tools)
    session.run("flake8", *targets)
    session.run("black", "--diff", "--check", *targets)
    session.run("isort", "--check-only", *targets)
    session.run("mypy", *targets)


@nox.session
def tests(session):
    session.install(".[test]")
    session.run("pytest", "-v")
