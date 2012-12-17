
"""
ODTChomper
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
    if not args.batch_path:
        chomper.do_chomp(args)
    else:
        start_dir = os.path.dirname(sys.argv[0])
        chomper.do_chomp_batch(args)
        os.chdir(start_dir)
    
    # For debugging. If I run this script in a windows command window the following will stop the window from closing before I can read the error message.
    # print "Press return to continue"
    # a=raw_input()    

    
if __name__=="__main__":
    main()
