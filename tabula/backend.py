import os
import subprocess
from logging import getLogger
from typing import List, Optional

from .errors import JavaNotFoundError
from .util import TabulaOption

logger = getLogger(__name__)

JAVA_NOT_FOUND_ERROR = (
    "`java` command is not found from this Python process."
    "Please ensure Java is installed and PATH is set for `java`"
)
TABULA_JAVA_VERSION = "1.0.5"
JAR_NAME = f"tabula-{TABULA_JAVA_VERSION}-jar-with-dependencies.jar"
JAR_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_CONFIG = {"JAR_PATH": os.path.join(JAR_DIR, JAR_NAME)}


def jar_path() -> str:
    return os.environ.get("TABULA_JAR", DEFAULT_CONFIG["JAR_PATH"])


class TabulaVm:
    def __init__(self, java_options: List[str], silent: Optional[bool]) -> None:
        try:
            import jpype
            import jpype.imports

            if not jpype.isJVMStarted():
                jpype.addClassPath(jar_path())

                # Workaround to enforce the silent option. See:
                # https://github.com/tabulapdf/tabula-java/issues/231#issuecomment-397281157
                if silent:
                    java_options.extend(
                        (
                            "-Dorg.slf4j.simpleLogger.defaultLogLevel=off",
                            "-Dorg.apache.commons.logging.Log"
                            "=org.apache.commons.logging.impl.NoOpLog",
                        )
                    )

                jpype.startJVM(*java_options, convertStrings=False)

            import java.lang as lang
            import technology.tabula as tabula
            from org.apache.commons.cli import DefaultParser

            self.tabula = tabula
            self.parser = DefaultParser()
            self.lang = lang

        except (ModuleNotFoundError, ImportError) as e:
            logger.warning(
                "Error importing jpype dependencies. Fallback to subprocess."
            )
            logger.warning(e)
            self.tabula = None
            self.parse = None
            self.lang = None

    def call_tabula_java(
        self, options: TabulaOption, path: Optional[str] = None
    ) -> str:
        sb = self.lang.StringBuilder()
        args = options.build_option_list()
        if path:
            args.insert(0, path)

        cmd = self.parser.parse(self.tabula.CommandLineApp.buildOptions(), args)
        self.tabula.CommandLineApp(sb, cmd).extractTables(cmd)
        return str(sb.toString())


class SubprocessTabula:
    def __init__(
        self, java_options: List[str], silent: Optional[bool], encoding: str
    ) -> None:
        # Workaround to enforce the silent option. See:
        # https://github.com/tabulapdf/tabula-java/issues/231#issuecomment-397281157
        if silent:
            java_options.extend(
                (
                    "-Dorg.slf4j.simpleLogger.defaultLogLevel=off",
                    "-Dorg.apache.commons.logging.Log"
                    "=org.apache.commons.logging.impl.NoOpLog",
                )
            )

        self.java_options = java_options
        self.encoding = encoding

    def call_tabula_java(
        self, options: TabulaOption, path: Optional[str] = None
    ) -> str:
        args = (
            ["java"]
            + self.java_options
            + ["-jar", jar_path()]
            + options.build_option_list()
        )
        if path:
            args.append(path)

        try:
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                check=True,
            )
            if result.stderr:
                logger.warning(f"Got stderr: {result.stderr.decode(self.encoding)}")
            return result.stdout.decode(self.encoding)
        except FileNotFoundError:
            raise JavaNotFoundError(JAVA_NOT_FOUND_ERROR)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error from tabula-java:\n{e.stderr.decode(self.encoding)}\n")
            raise
