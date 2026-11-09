import nox

PYTHON_VERSIONS = ["3.11", "3.12", "3.13", "3.14", "3.15"]
# Latest Python version supported by jpype1
JPYPE_PYTHON_VERSION = "3.14"


@nox.session(python=JPYPE_PYTHON_VERSION)
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


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run tests without jpype, calling tabula-java via subprocess."""
    session.install(".[test]")
    session.run("pytest", "-v", "tests/test_read_pdf_table.py", "tests/test_util.py")


@nox.session(python=JPYPE_PYTHON_VERSION)
def tests_jpype(session):
    """Run tests with jpype."""
    session.install(".[jpype,test]")
    session.run(
        "pytest",
        "-v",
        "tests/test_read_pdf_table.py",
        "tests/test_read_pdf_jar_path.py",
        "tests/test_read_pdf_silent.py",
    )
