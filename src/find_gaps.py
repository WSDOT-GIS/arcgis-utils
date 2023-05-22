"""Returns the total number of features that have more than one part
(e.g., polylines with gaps).
"""
import argparse
import datetime
import logging
from sys import stderr
from pathlib import Path, PurePath
from typing import Iterable

_LOGGER = logging.getLogger()
logging.basicConfig(stream=stderr, level=logging.DEBUG)


def main():
    logger = _LOGGER.getChild(main.__name__)
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument(
        "feature_class", type=lambda p: PurePath(p), help="Path to a feature class"
    )
    arg_parser.add_argument("route_id_field_name")
    args = arg_parser.parse_args()

    fc: PurePath = args.feature_class
    logger.info(f"Feature class is {fc}")

    fc_gdb = Path(fc.parent)
    logger.info(f"file GDB is {fc_gdb}")

    if not fc_gdb.exists():
        raise FileNotFoundError(str(fc_gdb))
    
    route_id_field_name = "RouteID"
    
    list_fields_params = {"dataset": str(fc_gdb), "field_type": "String"}

    logger.debug(f"ListFields parameters: {list_fields_params}")

    arcpy_import_start = datetime.datetime.now()
    logger.info(f"Importing arcpy... ({arcpy_import_start})")
    import arcpy
    import arcpy.da

    arcpy_import_end = datetime.datetime.now()

    logger.info(
        f"arcpy import complete ({arcpy_import_end}). Elapsed: {arcpy_import_end - arcpy_import_start}"
    )

    if not arcpy.Exists(str(fc)):
        raise ValueError(f"Feature class does not seem to exist: {fc}")
    else:
        logger.info(f"{fc} exists")

    fc = str(fc)


    total_count = 0
    multi_parts: dict[str, int] = {}

    cursor: Iterable[tuple[str, arcpy.Polyline]]
    cursor_logger = logger.getChild("cursor")
    cursor_logger.debug(f"Feature class: {fc}")
    field_names = [route_id_field_name, "SHAPE@"]
    cursor_logger.debug(f"Fields: {field_names}")
    with arcpy.da.SearchCursor(fc, field_names=field_names) as cursor:  # type:ignore
        route_id: str
        shape: arcpy.Polyline
        for route_id, shape in cursor:  # type:ignore
            # cursor_logger.debug(f"{i}. {route_id}: {shape.WKT}")
            total_count += 1
            # cursor_logger.debug(f"Feature count is now {total_count}.")
            if shape.partCount != 1:  # type: ignore
                print(f"{route_id} part count:\t{shape.partCount}")  # type: ignore
                multi_parts[route_id] = shape.partCount  # type: ignore
            else:
                # cursor_logger.debug(f"Part count: {shape.partCount}")
                pass

    mp_count = len(multi_parts)
    if mp_count > 0:
        print(f"{mp_count}/{total_count} polyline features had more than one part")
        for [route_id, part_count] in multi_parts.items():
            print(f"\t{route_id}\t{part_count}")
    else:
        print(f"None of the {total_count} features had more than one part.")


if __name__ == "__main__":
    main()
