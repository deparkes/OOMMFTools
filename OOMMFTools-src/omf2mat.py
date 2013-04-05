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
- decoder.py
- oommfdecode.py

TODO:
- Make usage the same as bmp2avi and odt2dat, i.e. default behaviour is to
	operate on all possible files in the current folder.
- Say output filename in screen output.

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

import sys
import decoder
import os
def main():
    args = decoder.get_args()
    
    if not args.batch_path:
        # The batch processor only finds compatible files. This makes sure the user
        # doesn't try to convert the wrong type of file.
        if not args.in_file.lower().endswith(('.omf', '.ohf', '.oef', '.ovf')):
            print "Please enter valid OOMMF file: ['.omf', '.ohf', '.oef', '.ovf']"
            sys.exit(1)
        decoder.do_decode(args)
    else:
        start_dir = os.path.dirname(sys.argv[0])
        decoder.batch_decoder(args)
        os.chdir(start_dir)
if __name__=="__main__":
    main()

