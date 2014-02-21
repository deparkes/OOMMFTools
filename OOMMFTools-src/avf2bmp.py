#!/usr/bin/python
# Script for converting oommf vector files to bitmap
# Usage:
# avf2bmp.py *.omf
# If current folder is named 'raw' it will assume you have a name/raw, name/bmp,
# name/blah folder tree and make a new folder ../bmp
# Otherwise it will make ./bmp and put the output bmp files there.
# TODO: 
# - Make a argparser
# - Make it easier to change the config file used (see argparser)
# - Sort out 'file exists' error
import subprocess
import os
import sys
import shutil
import glob

def get_bmp(path):
    # A function to find the omf magnetisation vector files in a particular folder.
    omf_path = '%s/*.bmp*' % (path)
    #create an array of file names based on the search for omf files.
    files_array = glob.glob(omf_path)
    return files_array

def label_image(filename):
    fpath, filename = os.path.split(filename)
    print "Label image: " + filename
    cmd_to_run = 'convert ' + filename + ' -gravity South -annotate 0 \'%f\' ' + filename
    subprocess.call(cmd_to_run, shell=True)

# Run the oommf conversion tool - this outputs to the current dir
# Watch out for windows paths with a backslash
# Edit the config file to set how the output bmp files will look.
# avf2ppm.configLOWRES makes small images (quicker, but looks ugly)
# avf2ppm.configHIGHRES: Makes high res images for cropping to a region
# avf2ppm.configAUTO: uses automatic settings
# avf2ppm.configBW: uses automatic settings
cmd_to_run = 'tclsh C:/oommf-1.2a5/oommf.tcl avf2ppm -config C:/oommf-1.2a5/avf2ppm.configBW -format B24 -ipat %s' % sys.argv[1]
subprocess.call(cmd_to_run, shell=True)

# Create a folder in which to store the images (unless it already exists)
# I've added a bit to account for my different directory structures. 
# My current preferred way of doing things is to have the oommf output into ./raw
# so I can have the bmp files go into ../bmp. 
# The old style doesn't use the 'raw' folder so I just make './bmp' and put the 
# bmp files there.
path, dir = os.path.split(os.getcwd())
if  dir == 'raw':
	bmp_dir = '../bmp'
else:
	bmp_dir = './bmp'
	
if not os.path.exists(bmp_dir):
    os.makedirs(bmp_dir)

# move bitmaps to this tmp dir
current_dir = os.getcwd()
for i, filename in enumerate(get_bmp(current_dir)): # loop through each file
	label_image(filename)
	shutil.move(filename, bmp_dir)
    

# Annotate the images with their file names. This should help figuring out
# what is going on when they get converted to movies.
#print('Annotate images with file names...\n')
#os.chdir(bmp_dir)
#imf_label_cmd = 'img_label.py %s' % sys.argv[1]
#subprocess.call(img_label_cmd, shell=True)
