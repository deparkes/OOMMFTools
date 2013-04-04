
"""
odt2dat.py
Basic Usage: 
For batch operation on a whole folder:
odt2dat.py

For operating on a single file:
odt2dat.py my_file.odt

If you don't specify an output name, the program will use the basename of the
input file as the output filename, with a .dat file extension.

Specify output file:
odt2dat.py my_file.odt -o out_file_name.dat

For further help:
odt2dat.py -h

The business end of this script is based on 'odtchomp' from the OOMMFTools.

Requirements:
Python 2.7
chomper.py
odtchomp.py

Copyright (C) 2012  Duncan Parkes
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
import chomper
import os
import sys
def main():

    args = chomper.get_args()
    if args.in_file:
        chomper.do_chomp(args)
    else:
		for i, filename in enumerate(chomper.get_odt(os.getcwd())): # loop through each file
			args.in_file = filename
			chomper.do_chomp(args)
		

    
    # For debugging. If I run this script in a windows command window the following will stop the window from closing before I can read the error message.
    # print "Press return to continue"
    # a=raw_input()    

    
if __name__=="__main__":
    main()
