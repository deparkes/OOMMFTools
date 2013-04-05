
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
from odtchomp import chomp, write
from pprint import pprint
import argparse
import sys
import glob
import os

def get_odt(path):
    # A function to find the odt data files in a particular folder.
    # Since I only want one I have an if statement to try and protect things. Needs improvements.
    # Use os.path.basename(path) to strip away everything but the file name from the path.

    omf_path = '%s/*.odt' % (path)
    #create an array of file names based on the search for omf files.
    files_array = glob.glob(omf_path)
    # Files are ordered alphabetically take first one.
##    files = os.path.basename(files_array[0])
    return files_array

def get_delim(delim):
    if delim == 'comma':
        return ','
    elif delim == 'space':
        return ' '
    elif delim == 'tab':
        return '\t'
    else:
        print "Bad delimiter"

def write_headers(fields, header_out):
    if not header_out:
        header_out = 'headers.txt'
    headerfile = open(header_out, 'w')
    for item in fields:
        headerfile.write("%s\n" % item)
    print "Headers written to %s\n" % header_out

def print_headers(fields):
    pprint(fields)
    

def get_fields(headerfile):
    fields = open(headerfile).read().splitlines()
    return fields



def do_chomp(args):
	in_file = args.in_file
	if args.out_file:
		out_file = args.out_file
	else:
		in_file_strip, file_extension = os.path.splitext(in_file)
		out_file = in_file_strip + '.dat'
		
	verbosity = args.verbose
	show_headers=args.show_headers
	save_headers=args.save_headers    
	if args.fields:
		fields = get_fields(args.fields)
	else:
		fields = False		
	delim = get_delim(args.delim)
		
	if verbosity == 0:
		save_stdout = sys.stdout
		sys.stdout = open('log.txt', 'w') 
		odtfile = chomp(in_file)
		sys.stdout = save_stdout
		if show_headers:
#            print_headers(odtfile.getNames())
			print_headers(odtfile.getNames())
		if save_headers:
			write_headers(odtfile.getNames(), save_headers)
	else:
		odtfile = chomp(in_file)
		if show_headers:
			print_headers(odtfile.getNames())
		if save_headers:
			write_headers(odtfile.getNames(), save_headers)
               
        #Output new file
	if out_file:
		if not fields:
			fields = odtfile.getNames()
	write(out_file, odtfile, delim, fields)
     
def get_args(args = False):    
    parser = argparse.ArgumentParser(description='Command line interface for odtchomp')
    parser.add_argument("in_file", type=str, help="specify .odt file to load", nargs='?')
    parser.add_argument('-f', type=str, action='store', dest='fields', help='File with required headers')    
    parser.add_argument('-p', action="store_true", dest='show_headers', default=False, help='show headers')
    parser.add_argument('-o', dest='out_file', help='Set output file', nargs='?')
    parser.add_argument('out_file',nargs='?', help='Set output file', type=str)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    parser.add_argument('-s', dest='save_headers', help='save headers')
    parser.add_argument('-d', dest='delim', help='specify output delimiter: tab, comma, space', default='tab',nargs='?', choices=['tab','comma','space'])
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    if not args:
        return parser.parse_args()
    else:
        return parser.parse_args(args)

def main():

    args = get_args()
    if args.in_file:
        do_chomp(args)
    else:
		for i, filename in enumerate(get_odt(os.getcwd())): # loop through each file
			args.in_file = filename
			do_chomp(args)
		

    
    # For debugging. If I run this script in a windows command window the following will stop the window from closing before I can read the error message.
    # print "Press return to continue"
    # a=raw_input()    

    
if __name__=="__main__":
    main()
