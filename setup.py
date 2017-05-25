from setuptools import setup
from setuptools import find_packages
import os

def read_file(filename):
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''


__author__ = 'Michiaki Ariga'

setup(
    name='tabula-py',
    version='0.7.1',
    description='Simple wrapper for tabula, read tables from PDF into DataFrame',
    long_description=read_file('README.md'),
    author=__author__,
    author_email='chezou@gmail.com',
    url='https://github.com/chezou/tabula-py',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Text Processing :: General',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    packages=find_packages(),
    license='MIT License',
    keywords=['data frame', 'pdf', 'table'],
    setup_requires=[
        'flake8',
    ],
    install_requires=[
        'pandas',
        'requests',
    ],
)
