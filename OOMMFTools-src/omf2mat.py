"""
omf2mat.py

Usage:
Basic usage
omf2mat.py target_file.omf

Specify output filename (if not specified uses input filename as basis)

Run on all vector (omf, ohf etc.) files in the current folder 
omf2mat.py -b .

Display help 
omf2mat.py -h 
usage: omf2mat.py [-h] [-b BATCH_PATH] [-o OUT_FILE]
                  [-t [{matlab,pickle,both}]] [--version]
                  [in_file] [out_file]

Command line interface for oommfdecode

positional arguments:
  in_file               specify oommf vector file to load
  out_file              Set output file

optional arguments:
  -h, --help            show this help message and exit
  -b BATCH_PATH         Specify batch path
  -o OUT_FILE           Set output file
  -t [{matlab,pickle,both}]
                        specify output file types
  --version             show program's version number and exit

Requirements:
- Python 2.7
- oommfdecode.py

TODO:
- Make usage the same as bmp2avi and odt2dat, i.e. default behaviour is to
	operate on all possible files in the current folder.
- Say output filename in screen output.
- Strip out omf/ohf etc. file type
- Sort out the bit that actually calls to oommfdecode - this could be tidier.

Copyright (C) 2012  Duncan Parkes
ppxdep@nottingham.ac.uk

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

import oommfdecode
import argparse
import os
import sys

def do_decode(args):
    in_file = args.in_file
    out_file = args.out_file
    file_type = args.file_type
				
    if not out_file:
        out_file = in_file
        
	
    array, headers, extra = oommfdecode.unpackFile(in_file)
    # It's not good that there is all this repitition of lines.    
    if file_type == 'matlab':
        print 'Generating matlab compatible output'
        out_dir = '../mat/'
        if not os.path.exists(out_dir):
			os.makedirs(out_dir)
        oommfdecode.matlabifyArray(array, headers, extra, out_dir + out_file + '.mat')
    elif file_type == 'pickle':
        out_dir = '../pkl/'
        if not os.path.exists(out_dir):
			os.makedirs(out_dir)
        print 'Generating numpy compatible output'
        oommfdecode.pickleArray(array, headers, extra, out_dir + out_file + '.pkl')
    else:
        print 'Generating output compatible with numpy and matlab'
        out_dir = '../mat/'
        if not os.path.exists(out_dir):
			os.makedirs(out_dir)
        oommfdecode.pickleArray(array, headers, extra, out_dir + out_file + '.pkl')
        out_dir = '../pkl/'
        if not os.path.exists(out_dir):
			os.makedirs(out_dir)
        oommfdecode.matlabifyArray(array, headers, extra, out_dir + out_file + '.mat')
            
def batch_decoder(args):
    batch_path = args.batch_path
    for r,d,f in os.walk(batch_path):
        for files in f:
            if files.endswith(('.omf', '.ohf', '.oef', '.ovf')):
                for avf in files.split():
                    args.in_file = os.path.join(r,avf)
                    do_decode(args)

def get_args(args = False):
    
    parser = argparse.ArgumentParser(description='Command line interface for oommfdecode')
    parser.add_argument('-b', type=str, action='store', dest='batch_path', help='Specify batch path')
    parser.add_argument("in_file", type=str, help="specify oommf vector file to load", nargs='?')
    parser.add_argument('-o', dest='out_file', help='Set output file')
    parser.add_argument('-t', dest='file_type', help='specify output file types', default='matlab',nargs='?', choices=['matlab', 'pickle', 'both'])
    parser.add_argument('out_file',nargs='?', help='Set output file', type=str)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    if not args:
        return parser.parse_args()
    else:
        return parser.parse_args(args)

def main():
    args = get_args()
    
    if not args.batch_path:
        # The batch processor only finds compatible files. This makes sure the user
        # doesn't try to convert the wrong type of file.
        if not args.in_file.lower().endswith(('.omf', '.ohf', '.oef', '.ovf')):
            print "Please enter valid OOMMF file: ['.omf', '.ohf', '.oef', '.ovf']"
            sys.exit(1)
        do_decode(args)
    else:
        start_dir = os.path.dirname(sys.argv[0])
        batch_decoder(args)
        os.chdir(start_dir)
if __name__=="__main__":
    main()

