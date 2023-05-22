"""Scrapes GP service info and dumps to JSON files
"""
import argparse
from pathlib import Path
from . import dump_service_info

SERVICE_URLS = (
    "https://data.wsdot.wa.gov/arcgis/rest/services/Shared/HPMSGetLRSPoint/GPServer",
    "https://data.wsdot.wa.gov/arcgis/rest/services/Shared/JurisdictionProximity/GPServer",
)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description=__doc__)
    output_dir = Path(".", "service_info")
    arg_parser.add_argument(
        "output_dir",
        nargs="?",
        default=output_dir,
        help="The directory where the JSON files will be written to.",
    )
    args = arg_parser.parse_args()
    dump_service_info(SERVICE_URLS, args.output_dir)
