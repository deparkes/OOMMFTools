OOMMFTools
==========

OOMMFTools is a set of utilities designed to assist OOMMF postprocessing.

Originally released by Mark Mascaro as a GUI program, OOMMFTools has since 
been modified to include commandline utilities to allow for easy batch processing of OOMMF data.

## Requirements:
- OOMMF
- Tcl/Tk
- Python 2.7 (command line)
- Scipy
- Numpy
- ffmpeg (Imagemagick)

## Functionality:

###GUI:
- OOMMFDecode - Converts OOMMF vector files into numpy arrays and/or MATLAB data files
- OOMMFConvert- Converts OOMMF vector files into bitmaps and movies
- ODTChomp    - Converts ODT files or subsets thereof into normally-delimited text files

###Command line (release 1.1 and develop branches):
- odt2dat.py - Converts ODT files or subsets thereof into normally-delimited text files
- avf2bmp.py - Converts OOMMF vector files into bitmaps
- bmp2avi.py - Convert bitmaps into movies
- omf2mat.py -  Converts OOMMF vector files into numpy arrays and/or MATLAB data files

For more information see Readme.txt

## Plans:
Make it simpler to use the command line utilities. Reduce setup complexity and 
make give all scripts a similar command-line interface.

