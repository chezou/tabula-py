import os

from setuptools import find_packages, setup


def read_file(filename):
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ""


with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    long_description = f.read()


setup(
    name="tabula-py",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    description="Simple wrapper for tabula-java, read tables from PDF into DataFrame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aki Ariga",
    author_email="chezou@gmail.com",
    maintainer="Aki Ariga",
    maintainer_email="chezou@gmail.com",
    license="MIT License",
    url="https://github.com/chezou/tabula-py",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Text Processing :: General",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
    ],
    include_package_data=True,
    packages=find_packages(),
    keywords=["data frame", "pdf", "table"],
    install_requires=["pandas", "numpy", "distro"],
    extras_require={"dev": ["pytest", "flake8", "black", "isort"], "test": ["pytest"]},
)
