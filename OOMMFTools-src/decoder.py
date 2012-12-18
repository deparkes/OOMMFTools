import oommfdecode
import argparse
def do_decode(args):
    in_file = args.in_file
    out_file = args.out_file
    if not out_file:
        out_file = 'outfile.mat'
        
    array, headers, extra = oommfdecode.unpackFile(in_file)
    oommfdecode.matlabifyArray(array, headers, extra, out_file)
    oommfdecode.pickleArray(array, headers, extra, out_file)


def get_args(args = False):
    
    parser = argparse.ArgumentParser(description='Command line interface for oommfdecode')
    parser.add_argument('-b', type=str, action='store', dest='batch_path', help='Specify batch path')
    parser.add_argument("in_file", type=str, help="specify oommf vector file to load", nargs='?')
    parser.add_argument('-p', action="store_true", dest='show_headers', default=False, help='show headers')
    parser.add_argument('-o', dest='out_file', help='Set output file')
    parser.add_argument('out_file',nargs='?', help='Set output file', type=str)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    if not args:
        return parser.parse_args()
    else:
        return parser.parse_args(args)
