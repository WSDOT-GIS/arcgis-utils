"""Dumps the contents of binary ArcGIS files.
"""
from importlib import util
import importlib
import json
import logging
import re
from types import ModuleType
import xml.etree.ElementTree as ETree
import zipfile
from enum import Enum
from pathlib import Path, PurePath
from sys import stderr
from typing import NamedTuple, Optional, Union

_LOGGER = logging.getLogger()
_NEW_LINE = "\n"

arcpy_spec = util.find_spec("arcpy")
if arcpy_spec:
    _LOGGER.debug(f"arcpy is available. {arcpy_spec}")
else:
    _LOGGER.warning("arcpy is not available.")

py7zr: Union[ModuleType, None] = None
try:
    py7yr = importlib.import_module("py7zr")
except ImportError:
    stderr.write(
        "\nCould not import py7zr. Please install it to enable 7-Zip support.\n"
    )
    py7zr = None

# _known_zip_suffixes = [f".{s}" for s in ("atbx", "aprx")]
_known_xml_suffixes = (".rc", ".pkinfo")
"""Files with these extensions are expected to be XML."""

_known_lzma_suffixes = (".gpkx", ".sd")
"""Files with these extensions are 7-Zip archives."""


class DetectedFileType(Enum):
    JSON = "json"
    XML = "xml"
    ZIP = "zip"
    SEVEN_ZIP = "7z"
    OLD_TOOLBOX = "tbx"
    OLD_MAP_SERVICE_DEFINITION = "msd"
    RLTX = "rltx"
    PYTHON = "py"


_BINARY_FILETYPES = [
    DetectedFileType.OLD_TOOLBOX,
    DetectedFileType.OLD_MAP_SERVICE_DEFINITION,
    DetectedFileType.SEVEN_ZIP,
    DetectedFileType.ZIP,
    DetectedFileType.RLTX,
]
"""A list of file types that are binary rather than text."""


_FENCE_TYPES = {
    # DetectedFileType.JSON: "json",
    # DetectedFileType.XML: "xml",
    # DetectedFileType.ZIP: "zip",
    # DetectedFileType.SEVEN_ZIP: "7z",
    # DetectedFileType.OLD_TOOLBOX: "tbx",
    # DetectedFileType.OLD_MAP_SERVICE_DEFINITION: "msd",
    # DetectedFileType.RLTX: "rltx",
    DetectedFileType.PYTHON: "py",
}
"""Dictionary of file suffixes mapped to DetectedFileTypes.
Only those file types who's enum values are different from the 
code fence specifier are included here.

Example:

```python
file_type: str | DetectedFileType = DetectedFileType.PYTHON
_FENCE_TYPES.get(file_type, file_type.lower()) # Returns "py"

file_type = DetectedFileType.JSON
# The dict does not have a corresponding key, so it uses default and returns "json".
_FENCE_TYPES.get(file_type, file_type.lower()) 
```
"""


def json_to_str(decoded_content: str):
    decoded_content = json.dumps(json.loads(decoded_content), indent=2)
    return decoded_content


class XmlToStrOutput(NamedTuple):
    decoded_content: str
    detected_file_type: DetectedFileType


def xml_to_str(decoded_content: str) -> XmlToStrOutput:
    logger = _LOGGER.getChild(xml_to_str.__name__)
    detected_file_type = DetectedFileType.XML
    try:
        x = ETree.fromstring(decoded_content)
        dumped_bytes = ETree.tostring(x)
        decoded_content = dumped_bytes.decode()
    except ETree.ParseError as ex:
        logger.warning(f'Failed to parse XML from "{decoded_content[:20]}"')
        logger.exception(ex)
        try:
            decoded_content = json_to_str(decoded_content)
        except json.JSONDecodeError as j_ex:
            logger.exception(j_ex)
    return XmlToStrOutput(decoded_content, detected_file_type)


def detect_file_type(path: Union[str, PurePath]) -> Optional[DetectedFileType]:
    """Detect file type based on filename suffix

    Args:
        path: Path to a file. The file does not actually need to exist.

    Returns:
        The file type if known, or None if the type is not supported by this function.
    """
    logger = _LOGGER.getChild(detect_file_type.__name__)
    if isinstance(path, str):
        path = PurePath(path)

    logger.debug(f'{({"stem": path.stem, "suffix": path.suffix})}')

    def test_re(pattern: str, detected_type: DetectedFileType):
        if re.match(pattern, path.suffix, re.IGNORECASE):
            return detected_type
        return None

    detected_file_type = None

    for dft in DetectedFileType:
        detected_file_type = test_re(fr"\.{dft.value}", dft)
        if detected_file_type:
            break

    if not detected_file_type and path.suffix in _known_xml_suffixes:
        return DetectedFileType.XML

    return detected_file_type


def dump_bytes(
    content_bytes: bytes,
    filename: Optional[str] = None,
    file_type: Optional[DetectedFileType] = None,
) -> Union[bytes, str]:
    """Dumps the input content bytes to stdout, first converting to text if possible.

    Args:
        content_bytes: Input bytes
        filename: A filename. Defaults to None.
        file_type: Specify a file type. Defaults to None.

    Returns:
        Either the decoded text from content_bytes, or the original content_bytes if the
        conversion was not possible.
    """
    logger = _LOGGER.getChild(dump_bytes.__name__)

    # log arguments as debug message. Trim content bytes to 40 chars.
    logger.debug(f"args: {({content_bytes[:40], filename, file_type})}")

    # If a file type was not specified but a filename was, try to determine
    # the file type based on the filename's suffix.
    if not file_type and filename:
        file_type = detect_file_type(filename)
        logger.debug(f"{file_type} type detected for {filename}")

    # If the file type is one of the known binary file types,
    # Immediately dump the binary contents and exit.
    if file_type in _BINARY_FILETYPES:
        print(f"```\n{content_bytes}\n```\n")
        return content_bytes

    # Try to decode the bytes into a string.
    # If this fails, log the exception and then
    # write and return the bytes.
    try:
        decoded_content = content_bytes.decode()
    except UnicodeDecodeError as u_ex:
        logger.exception(u_ex)
        return content_bytes

    # Log the first 40 chars of the decoded content.
    logger.debug(f"decoded content: {decoded_content[:40]}...")

    # initialize the markdown fence specifier. E.g., python, json, or xml.
    decoded_content, fence_type = get_fenced_content(file_type, decoded_content)

    print(f"\n```{fence_type}\n{decoded_content}\n```\n")

    return decoded_content


def get_fenced_content(file_type: Optional[DetectedFileType], decoded_content: str):
    fence_type: str = ""

    if file_type:
        fence_type = _FENCE_TYPES.get(file_type, file_type.value.lower())

    if file_type == DetectedFileType.JSON:
        decoded_content = json_to_str(decoded_content)
    elif file_type == DetectedFileType.XML:
        (decoded_content, _) = xml_to_str(decoded_content)
    return decoded_content, fence_type


def dump_zip_info(z: zipfile.ZipFile, f: zipfile.ZipInfo):
    print(f"## {f.filename}\n")
    print(f"\n```\n{f}\n```\n")
    content_bytes = z.read(f)
    dump_bytes(content_bytes, f.filename)


def dump_zip_contents(input_file: Path):
    logger = _LOGGER.getChild(dump_zip_contents.__name__)
    logger.debug(f"input file: {input_file}")

    try:
        with zipfile.ZipFile(input_file, "r") as z:
            inner_files = z.filelist
            logger.debug(f"Files within {input_file}:\n\t{inner_files}")
            for f in inner_files:
                detect_file_type(f.filename)
                dump_zip_info(z, f)
    except zipfile.BadZipFile as bzf_ex:
        message = (
            f"There was an issue when attempting to unzip {input_file}.\n\t{bzf_ex}"
        )
        logger.exception(bzf_ex)
        stderr.writelines([_NEW_LINE, message, _NEW_LINE])
        raise


def dump_7zip_contents(input_file: Path):
    logger = _LOGGER.getChild(dump_7zip_contents.__name__)
    logger.debug(f'Input file: "{input_file}')

    if not py7zr:
        stderr.writelines(
            [
                _NEW_LINE,
                f"The py7zr module is not installed, so the content of {input_file} \
                cannot be dumped.",
                _NEW_LINE,
            ]
        )
        content = input_file.read_bytes()
        print(content)
        return

    try:
        with py7zr.SevenZipFile(input_file, "r") as z:
            contents = z.readall()
            if not contents:
                raise TypeError(
                    f"Expected {py7zr.SevenZipFile.readall.__name__} \
                        to return a non-null value."
                )
            for k, v in contents.items():
                print(f"## {k}\n")
                with v:
                    content_bytes = v.read()
                dump_bytes(content_bytes, k)
    except py7zr.DecompressionError as ex:
        logger.exception(ex)
        raise
