"""
Utility module providing some convenient functions.
"""

import platform


def java_version():
    """Show Java version

    Returns:
        str: Result of ``java -version``
    """
    import subprocess

    try:
        res = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT)
        res = res.decode()

    except FileNotFoundError:
        res = (
            "`java -version` faild. `java` command is not found from this Python"
            "process. Please ensure Java is installed and PATH is set for `java`"
        )

    return res


def environment_info():
    """Show environment information for reporting.

    Returns:
        str:
            Detailed information like Python version, Java version,
            or OS environment, etc.
    """

    import sys

    import distro

    from tabula import __version__

    print(
        f"""Python version:
    {sys.version}
Java version:
    {java_version().strip()}
tabula-py version: {__version__}
platform: {platform.platform()}
uname:
    {str(platform.uname())}
linux_distribution: ('{distro.name()}', '{distro.version()}', '{distro.codename()}')
mac_ver: {platform.mac_ver()}"""
    )
