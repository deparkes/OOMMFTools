import oommfdecode as decode
import sys
import pickle
from pprint import pprint
array, headers, extra = decode.unpackFile(sys.argv[1])
decode.matlabifyArray(array, headers, extra, 'filename_matlab.mat')
decode.pickleArray(array, headers, extra, 'filename_pickle.mat')
f = open('./filename_pickle.mat', 'r')
x = pickle.load(f)
pprint(x)
f.close()

