"""Dumps the contents of binary ArcGIS files.
"""
import argparse
import logging
import zipfile
from enum import Enum
from pathlib import Path
from sys import stderr
from . import dump_7zip_contents, dump_zip_contents


class LOG_LEVEL_CHOICES(Enum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument(
        "input_file",
        nargs="?",
        help="The file to be dumped to the console.",
        type=Path,
    )
    # TODO: Configure log level.
    # arg_parser.add_argument(
    #     "--log-level",
    #     choices=[c.name for c in LOG_LEVEL_CHOICES]
    #     + [str(c.value) for c in LOG_LEVEL_CHOICES],
    # )
    args = arg_parser.parse_args()
    input_file: Path = args.input_file

    if zipfile.is_zipfile(input_file):
        dump_zip_contents(input_file)
    elif py7zr is None:
        stderr.write("Unable to load py7zr.\n")
    elif py7zr.is_7zfile(input_file):
        dump_7zip_contents(input_file)
    else:
        stderr.write(f"{input_file}: This archive type is not supported.\n")
        exit(1)


if __name__ == "__main__":
    main()
