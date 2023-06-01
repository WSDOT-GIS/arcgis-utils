"""Dumps all of the GPEnvironment properties.

Designed with the purpose of generating type stubs.
"""

from argparse import ArgumentParser

def main():
    arg_parser = ArgumentParser(description=__doc__)
    arg_parser.parse_args()
    
    from arcpy import env
    
    print("from typing import Any, Optional\n")
    
    
    
    for name, value in sorted(env.iteritems(), key=lambda a: a[0]):
        type_str = None
        if value is None:
            type_str = "Optional[Any]"
        else:
            type_str = type(value).__name__

        if isinstance(value, str):
            value = f"'{value}'"
            
        print(f"{name}: {type_str} = {value}")

if __name__ == "__main__":
    main()