"""
OOMMFDecoder
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

import oommfdecode as decode
import sys
import pickle
from pprint import pprint


def main():

    array, headers, extra = decode.unpackFile(sys.argv[1])
    decode.matlabifyArray(array, headers, extra, 'filename_matlab.mat')
    decode.pickleArray(array, headers, extra, 'filename_pickle.mat')
   
if __name__=="__main__":
    main()

