import warnings
import platform


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc


def deprecated_option(option):
    warnings.warn("Call to deprecated option {}.".format(option),
                  category=DeprecationWarning, stacklevel=2)


def java_version():
    import subprocess

    # TODO: Remove this Python 2 compatibility code if possible
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = IOError

    try:
        res = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT)
        res = res.decode()

    except FileNotFoundError as e:
        res = "`java -version` faild. `java` command is not found from this Python process. Please ensure Java is installed and PATH is set for `java`"

    return res


def environment_info():
    import sys
    import distro
    from .__version__ import __version__

    print("""Python version:
    {}
Java version:
    {}
tabula-py version: {}
platform: {}
uname:
    {}
linux_distribution: {}
mac_ver: {}
    """.format(
        sys.version,
        java_version().strip(),
        __version__,
        platform.platform(),
        str(platform.uname()),
        distro.linux_distribution(),
        platform.mac_ver(),
    ))
