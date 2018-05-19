import os
import subprocess
import shutil
import tempfile
import math
from past.utils import old_div
from .oommfdecode import slowlyPainfullyMaximize


def getOOMMFPath(pathFileToCheck):
    # Check if we have a saved OOMMF path to use as config data
    if os.path.exists(pathFileToCheck):
        f = open(pathFileToCheck)
        lines = f.readlines()
        f.close()
        path = lines[-1].strip()
        # But we also have to validate the path on this particular computer
        if os.path.exists(path) and path.rsplit(".")[-1] == "tcl":
            return path
        else:
            return None
            # Cleanup bogus config file
            os.remove(pathFileToCheck)
    else:
        # No file at all!
        return None


def spliceConfig(percentMagnitude, checkVectors=False, filenames=[], configPath=None):
    print(checkVectors)
    # Rewrite the file
    oldconf = open(configPath, "r")
    oldconflines = oldconf.readlines()
    oldconf.close()
    print("Getting temporary file handle for modconfig.")
    oshandle, newconfdir = tempfile.mkstemp(suffix=".tmp", dir=".")
    try:
        os.close(oshandle)
    except:
        print("Error: Windows failed all over closing the file handle.")
    newconf = open(newconfdir, "w")

    # OK, let's see if we need to recover vectors

    for line in oldconflines:
        # Only one data point for line. Let's deal with our cases.
        if "misc,datascale" in line and checkVectors:
            newMax = slowlyPainfullyMaximize(filenames)
            newconf.write("    misc,datascale " + str(newMax) + "\n")
        elif not percentMagnitude == 100:
            if "misc,zoom" in line:
                # newconf.write(line)
                # Don't stop clobbering zoom!
                newconf.write("    misc,zoom 0\n")
            elif "misc,default" in line:
                # This was not nearly as true as I'd hoped
                # Just in case this ever looks at the viewport, clobber the viewport.
                pass
            elif "misc,height" in line:
                newval = int(re.findall(r"[0-9]+", line)
                             [0]) * percentMagnitude / 100.0
                newconf.write("    misc,height " + str(newval) + "\n")
            elif "misc,width" in line:
                newval = int(re.findall(r"[0-9]+", line)
                             [0]) * percentMagnitude / 100.0
                newconf.write("    misc,width " + str(newval) + "\n")
            else:
                newconf.write(line)
    newconf.close()
    return newconfdir


def resolveConfiguration(filenames, magnifierSpin, autoMaxVectors, configPath):
    if magnifierSpin != 100 or autoMaxVectors:
        configPath = spliceConfig(
            magnifierSpin, autoMaxVectors, filenames, configPath)
        cleanconfig = True
    else:
        cleanconfig = False
    return (configPath, cleanconfig)


def convertOmfToImage(omf, tclCall, oommfPath, confpath, stdinRedirect, mode='advanced'):
    pathTo, fname = omf.rsplit(os.path.sep, 1)
    command = tclCall + ' "' + oommfPath + \
        '" avf2ppm -f -v 2 -format b24 -config "' + confpath + '" "' + omf + '"'
    runSubProcess(command, stdinRedirect, mode, omf)


def runSubProcess(command, stdinRedirect, mode, checkPath):
    if mode == "basic":
        os.system(command)
    elif mode == 'advanced':
        pipe = subprocess.Popen(command, **getSubProcessArgs(command,
                                                    stdinRedirect, 
                                                    checkPath)).stdout
        a = pipe.readlines()
        # THIS should at least use STDout
        if a:
            for line in a:
                print(line.strip())

def getSubProcessArgs(command, stdinRedirect, checkPath):
    if os.name == 'nt':
        print("Watching stdin redirect:", stdinRedirect)
        if not r":\\" in checkPath:
            subProcessArgs = {
                                'shell': True,
                                'stdin': stdinRedirect,
                                'stdout': subprocess.PIPE,
                                'stderr': subprocess.STDOUT
                                }
        else:
            # Avoid network stupidity.
            subProcessArgs = {
                                'shell': False,
                                'stdin': stdinRedirect,
                                'stdout': subprocess.PIPE,
                                'stderr': subprocess.STDOUT
                                }
    else:
        print("probably posix mode.")
        subProcessArgs = {
                            'shell': True,
                            'stdin': sys.stdin,
                            'stdout': subprocess.PIPE,
                            'stderr':subprocess.STDOUT
                            }
    
    return subProcessArgs


def makeMovieFromImages(moviePath, pathTo, maxDigits, movieCodec, stdinRedirect, codecs, mode='advanced'):
    command = buildMovieCommand(moviePath, pathTo, maxDigits, codecs[movieCodec])
    runSubProcess(command, stdinRedirect, mode, pathTo)


def buildMovieCommand(moviePath, pathTo, maxDigits, movieCodec):
    """Build movie command.

    CODECS[movieCodec]:
    "MPEG4": (r" -sameq ",".mp4","MPEG4")
    """
    outname = "["+movieCodec[2]+"]" + movieCodec[1]
    command = r'ffmpeg -f image2 -an -y -i ' + moviePath + os.path.sep + \
        r'%0' + str(maxDigits) + r'd.bmp ' + movieCodec[0]
    command += ' "' + os.path.join(pathTo, outname) + '"'
    return command


def createTempImagesForMovie(targetList, moviepath, framedupes, maxdigits, tclCall, OOMMFPath, confpath, stdinRedirect, removeImages=False):
    print("Temporary directory obtained.")

    for i, omf in enumerate(sorted(targetList)):
        frameRepeatOffset = 0
        convertOmfToImage(omf, tclCall, OOMMFPath, confpath, stdinRedirect)
        # Copy and duplicate image, placing files in the movie temp directory
        print('copying files to temp directory')
        fname = omf.rsplit(".", 1)[0] + ".bmp"
        for j in range(framedupes):
            shutil.copy(*buildShutilSourceDestination(fname,
                                                      moviepath, 
                                                      framedupes*i + j, 
                                                      maxdigits,
                                                      ))
            j += 1
        # Housecleaning - if not making images, you should clean this up.
        if not removeImages:
            os.remove(fname)


def buildShutilSourceDestination(fname, moviepath, framedupes, maxdigits):
    return (fname, moviepath+os.path.sep + 
                        str(framedupes).rjust(maxdigits, "0") + ".bmp")

def doImages(targetList, stdinRedirect, config_parent, tclCall, OOMMFPath):
    confpath, cleanconfig = resolveConfiguration(targetList, 
                                                 config_parent.magnifierSpin.GetValue(),
                                                 config_parent.autoMaxVectors.GetValue(),
                                                 config_parent.config)

    for i, omf in enumerate(sorted(targetList)):
        convertOmfToImage(omf, tclCall, OOMMFPath, confpath, stdinRedirect)
    # Clean up temporaries
    if cleanconfig:
        cleanupConfig(confpath)


def doMovies(targetList, stdinRedirect, config_parent, movieCodec, movieFPS, tclCall, OOMMFPath, doImages, codecs):
    # Make temporary directory
    moviepath = tempfile.mkdtemp()
    # Deal with overload-options by writing a temporary configuration file
    confpath, cleanconfig = resolveConfiguration(targetList, 
                                                 config_parent.magnifierSpin.GetValue(),
                                                 config_parent.autoMaxVectors.GetValue(),
                                                 config_parent.config)
    # Identify filename length, and perform AWFUL HACK to sidestep ffmpeg restrictions
    framedupes = int(old_div(25, movieFPS))
    maxdigits = int(math.ceil(math.log10(len(targetList) * framedupes)))
    createTempImagesForMovie(targetList, moviepath, framedupes, maxdigits,
                             tclCall, OOMMFPath, confpath, stdinRedirect, doImages)

    pathTo = targetList[0].rsplit(os.path.sep, 1)
    # Finally, make the actual movie!
    # You know, we should steal the last pathto as a place to put the movie, and perhaps also the basename
    # This is bad use of scoping blah blah

    makeMovieFromImages(
        moviepath, pathTo[0], maxdigits, movieCodec, stdinRedirect, codecs)
    # Clean up temporaries
    shutil.rmtree(moviepath)
    if cleanconfig:
        cleanupConfig(confpath)


def cleanupConfig(configPath):
    try:
        os.remove(configPath)
    except:
        print("Can't let go for some reason... you should probably tell doublemark@mit.edu")
