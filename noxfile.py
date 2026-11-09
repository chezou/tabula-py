import nox


@nox.session
def lint(session):
    lint_tools = [
        "ruff",
        # ty is pre-1.0 and its diagnostics change between releases
        "ty==0.0.99",
        "Flake8-pyproject",
        # Required for ty to resolve imports in noxfile.py
        "nox",
    ]
    targets = ["tabula", "tests", "noxfile.py"]
    # Install tabula-py itself so that ty can resolve its dependencies
    session.install(".[jpype,test]", *lint_tools)
    session.run("ruff", "format", "--check", *targets)
    session.run("ruff", "check", *targets)
    session.run(
        "ty",
        "check",
        "--python",
        session.virtualenv.location,
        "--output-format",
        "concise",
        *targets,
    )


@nox.session
@nox.parametrize(
    "python,jpype",
    [
        ("3.11", True),
        ("3.12", True),
        ("3.13", True),
        ("3.14", True),
        # jpype1 does not support Python 3.15 yet
        ("3.15", False),
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
