"""Returns all of the possible choices for the arcpy.GetIDMessage function
as CSV.
"""
from argparse import ArgumentParser
from typing import NamedTuple
import re

def main():
    arg_parser = ArgumentParser(
        description=__doc__,
        epilog="""Example:
        
    python ./src/utils/dump_id_messages.py > arcpy_id_messages.csv""",
    )
    arg_parser.add_argument(
        "--min", default=0, type=int, help="Integer that defines the minimum ID range."
    )
    arg_parser.add_argument(
        "--max",
        default=10000,
        type=int,
        help="Integer that defines the maximum ID range.",
    )

    args = arg_parser.parse_args()

    min: int = args.min
    max: int = args.max

    import csv
    from sys import stdout
    from arcpy import GetIDMessage

    class IdMessageTuple(NamedTuple):
        id: int
        message: str
        
    format_param_re = re.compile(r"%")
    
    def get_messages():
        """Get all of the ArcGIS ID messages

        Yields
        ------
            A tuple will be yielded for each message:
            
            * message id
            * message format string
            * number of parameters for the format string
        """
        # Get all of the ID messages and yield tuples of ID,message
        messages = (IdMessageTuple(i, GetIDMessage(f"{i}")) for i in range(min, max))
        for i, message in messages:
            # Skip None messages.
            if not message:
                continue
            
            # Find all the string format parameters
            matches = format_param_re.findall(message)
            # Yield the id, message, and number of parameters for the format string.
            yield i,message,len(matches)

    # Create the CSV writer for stdout.
    # Since it's stdout we don't use a with statement.
    writer = csv.writer(stdout, lineterminator="\n")
    
    # Write the header row.
    writer.writerow(("ID", "Message", "ArgumentCount"))

    # Get message data generator
    messages = get_messages()
    
    # Write data to stdout.
    writer.writerows(messages)


if __name__ == "__main__":
    main()
