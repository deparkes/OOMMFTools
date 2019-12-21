from core import oommfdecode
import os
import argparse

def cli_main():
    # Create the parser
    main_parser = argparse.ArgumentParser(prog='OOMMFTools',
                                          description='A command line interface to OOMMFTools')
    main_parser.add_argument(
        '--debug',
        action='store_true',
        help='Print debug info'
    )
    # Add the arguments
    subparsers = main_parser.add_subparsers(dest='tool_selection', help='Tools Available')
    decode_parser = subparsers.add_parser("decode")
    decode_parser.add_argument('--pickle', dest="pickle", action='store_true')
    decode_parser.add_argument('--matlab', dest="matlab", action='store_true')
    decode_parser.add_argument("files", help="Input file", nargs="+")
    convert_parser = subparsers.add_parser("convert")
    chomp_parser = subparsers.add_parser("chomp")

    args = main_parser.parse_args()


    if args.tool_selection == 'decode':
        for filename in args.files:
            basename = os.path.basename(os.path.splitext(filename)[0])
            array, headers, extraCaptures = oommfdecode.unpackFile(filename)
            if args.pickle is True:
                oommfdecode.pickleArray(array, headers, extraCaptures, basename + '.pkl')
            if args.matlab is True:
                oommfdecode.matlabifyArray(array, headers, extraCaptures, basename + '.mat')

    if args.tool_selection == 'convert':
        print("Not yet implemented")
    if args.tool_selection == 'chomp':
        print("Not yet implemented")
