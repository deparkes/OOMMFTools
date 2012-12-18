import oommfdecode
import argparse
import os


def do_decode(args):
    in_file = args.in_file
    out_file = args.out_file
    file_type = args.file_type

    if not out_file:
        out_file = in_file
    
    array, headers, extra = oommfdecode.unpackFile(in_file)
    
    if file_type == 'matlab':
        oommfdecode.matlabifyArray(array, headers, extra, out_file + '.mat')
    elif file_type == 'pickle':
        oommfdecode.pickleArray(array, headers, extra, out_file + '.pkl')
    else:
        oommfdecode.pickleArray(array, headers, extra, out_file + '.pkl')
        oommfdecode.matlabifyArray(array, headers, extra, out_file + '.mat')
            
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
    parser.add_argument('-p', action="store_true", dest='show_headers', default=False, help='show headers')
    parser.add_argument('-o', dest='out_file', help='Set output file')
    parser.add_argument('-t', dest='file_type', help='specify output file types', default='matlab',nargs='?', choices=['matlab', 'pickle', 'both'])
    parser.add_argument('out_file',nargs='?', help='Set output file', type=str)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    if not args:
        return parser.parse_args()
    else:
        return parser.parse_args(args)
