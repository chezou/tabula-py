import os

from setuptools import find_packages, setup


def read_file(filename):
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ""


about = {}
with open(os.path.join(os.path.dirname(__file__), "tabula", "__version__.py")) as f:
    exec(f.read(), about)

with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    about["__long_description__"] = f.read()


setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=about["__long_description__"],
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    maintainer=about["__maintainer__"],
    maintainer_email=about["__maintainer_email__"],
    license=about["__license__"],
    url=about["__url__"],
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
