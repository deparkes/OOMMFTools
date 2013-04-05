import subprocess
import sys
import glob
import os
import shutil

"""
Use ffmpeg to convert a series of bmp files to an avi video.
Requires ffmpeg to be on the path.
Doing this conversion on a big stack of bitmaps may take a while.

Usage:
Run on all bmp files in current folder
bmp2avi.py

Requirements:
python 2.x
ffmpeg folder on $PATH

TODO:
- Have command line option for changing framerate
"""

def get_bmp(path):
    # A function to find the omf magnetisation vector files in a particular folder.
    # Since I only want one I have an if statement to try and protect things. Needs improvements.
    # Use os.path.basename(path) to strip away everything but the file name from the path.
    # print os.getcwd()
    # os.chdir('../output/15um90umBarWithCrosses.bmp/strain_0');
    omf_path = '%s/*.bmp' % (path)
    #create an array of file names based on the search for omf files.
    files_array = glob.glob(omf_path)
    return files_array

# Make tmp dir to put movie processing files in 
tmp_dir = './bmp2avitmp'
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

# Copy bitmaps to this tmp dir
current_dir = os.getcwd()
for i, filename in enumerate(get_bmp(current_dir)): # loop through each file
    shutil.copy(filename, tmp_dir)

# Rename these files into a format good for ffmpeg
for i, filename in enumerate(get_bmp(tmp_dir)): # loop through each file
    count = "%03d" % i
    newname = "./%s/img%s.bmp" % (tmp_dir,count) # create a function that does step 2, above
    try:
        os.rename(filename, newname)
    except:
        break
    
ffmpeg_command = 'ffmpeg -f image2 -i ./bmp2avitmp/img%03d.bmp -r 15 video.avi'
subprocess.call(ffmpeg_command)

# Clean up by deleting the temporary folder
shutil.rmtree(tmp_dir)
