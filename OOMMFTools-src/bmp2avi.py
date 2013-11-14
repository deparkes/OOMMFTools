import subprocess
import sys
import glob
import os
import shutil

"""
Use ffmpeg to convert a series of bmp files to an avi video.
Requires ffmpeg to be on the path.
Doing this conversion on a big stack of bitmaps may take a while.
Usage: >bmp2avi.py #converts all bmp images in current folder to avi.

TODO:
- have command line control over ffmpeg options e.g. frame rate
- sort out ffmpeg_command
+ put on github
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

##def enumerate_bmp(bmp_list):
##    temp_dir = './tmp/'
##    if not os.path.exists(temp_dir):
##        os.makedirs(temp_dir)
##    for i, item in enumerate(bmp_list):
##        
##        bmp_list[i] = "%s/%s.bmp" % (temp_dir,i)



# Make tmp dir to put movie processing files in 
print "Making temporary directory..."
tmp_dir = './bmp2avitmp'
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

# Copy bitmaps to this tmp dir
print "Copying bmp files to temp directory"
current_dir = os.getcwd()
for i, filename in enumerate(get_bmp(current_dir)): # loop through each file
    print "Copying file: " + filename
    shutil.copy(filename, tmp_dir)

# Rename these files into a format good for ffmpeg
print "Renaming temp bmp files for ffmpeg processing"
for i, filename in enumerate(get_bmp(tmp_dir)): # loop through each file
    count = "%03d" % i
    newname = "./%s/img%s.bmp" % (tmp_dir,count) # create a function that does step 2, above
    try:
        os.rename(filename, newname)
    except:
        break
    
print "Running ffmpeg"
ffmpeg_command = 'ffmpeg -f image2 -i ./bmp2avitmp/img%03d.bmp -r 15 video.avi'
subprocess.call(ffmpeg_command)

# Clean up by deleting the temporary folder
print "Removing temporary directory"
shutil.rmtree(tmp_dir)
print "Done"