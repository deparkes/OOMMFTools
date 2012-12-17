import sys
import os
import chomper
def get_odt(path):
    # A function to find the odt data files in a particular folder.
    # Since I only want one I have an if statement to try and protect things. Needs improvements.
    # Use os.path.basename(path) to strip away everything but the file name from the path.
    import glob
    import os
    omf_path = '%s/*.odt' % (path)
    #create an array of file names based on the search for omf files.
    files_array = glob.glob(omf_path)
    # Files are ordered alphabetically take first one.
##    files = os.path.basename(files_array[0])
    return files_array

def main():
    start_dir = os.path.dirname(sys.argv[0])
    argv = chomper.get_args_b()
    batch_dir = argv.batch_path
    headerfile = argv.fields
    
    if headerfile:

        headerfile = start_dir + '\\' + headerfile
 
    for root, dirs, files in os.walk(batch_dir):

        # make sure that we are at the end of the path
        # i.e. that there are no subdirectories
        if len(dirs) == 0:
            files_array = get_odt(root)
            # loop through all odt files in the folder
            for files in files_array:               
                os.chdir(root)
                print files
                out_file = '%s.txt' % (files)
                
                
                
                if headerfile:
                    chomper_args = '%s %s -f %s' % (files, out_file, headerfile )
                else:
                    chomper_args = '%s %s' % (files, out_file )
                chomper_args = chomper_args.split()
                chomper.do_chomp(chomper.get_args(chomper_args))
    os.chdir(start_dir)
    
    # For debugging. If I run this script in a windows command window the following will stop the window from closing before I can read the error message.
    print "Press return to continue"
    a=raw_input()


if __name__ == "__main__":
    main()
