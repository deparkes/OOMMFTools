"""
Main GUI that manages singleton instances of the other windows
"""
from __future__ import absolute_import

import sys
from user_interfaces.gui import gui_main
from user_interfaces.cli import cli_main

def main():
    if len(sys.argv) <= 1:
        gui_main()
    else:
        cli_main()


if __name__ == '__main__':
    main()