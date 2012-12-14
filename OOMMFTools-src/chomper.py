from odtchomp import chomp, write
from pprint import pprint
import argparse
import sys

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
	out_file = args.out_file
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
    parser.add_argument("in_file", type=str, help="specify .odt file to load")
    parser.add_argument('-f', type=str, action='store', dest='fields', help='File with required headers')
    parser.add_argument('-p', action="store_true", dest='show_headers', default=False, help='show headers')
    parser.add_argument('-o', dest='out_file', help='Set output file')
    parser.add_argument('out_file',nargs='?', help='Set output file', type=str)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    parser.add_argument('-s', dest='save_headers', help='save headers')
    parser.add_argument('-d', dest='delim', help='specify output delimiter: tab, comma, space', default='tab',nargs='?', choices=['tab','comma','space'])
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    if not args:
        return parser.parse_args()
    else:
        return parser.parse_args(args)

def get_args_b(args = False):
    
    parser = argparse.ArgumentParser(description='Command line interface for odtchomp')
    parser.add_argument("batch_path", type=str, help="specify .odt batch path")
    parser.add_argument('-f', type=str, action='store', dest='fields', help='File with required headers')
    parser.add_argument('-o', dest='out_file', help='Set output file')
    parser.add_argument('out_file',nargs='?', help='Set output file', type=str)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    parser.add_argument('-s', dest='save_headers', help='save headers')
    parser.add_argument('-d', dest='delim', help='specify output delimiter: tab, comma, space', default='tab',nargs='?', choices=['tab','comma','space'])
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    if not args:
        return parser.parse_args()
    else:
        return parser.parse_args(args)
