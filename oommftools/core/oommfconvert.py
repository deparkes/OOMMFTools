import os
import subprocess

def getOOMMFPath(pathFileToCheck):
    #Check if we have a saved OOMMF path to use as config data
    if os.path.exists(pathFileToCheck):
        f = open(pathFileToCheck)
        lines = f.readlines()
        f.close()
        path = lines[-1].strip()
        #But we also have to validate the path on this particular computer
        if os.path.exists(path) and path.rsplit(".")[-1] == "tcl":
            return path
        else:
            return None
            #Cleanup bogus config file
            os.remove(pathFileToCheck)
    else:
        #No file at all!
        return None


def spliceConfig(percentMagnitude, checkVectors = False, filenames = [], configParent=None):
    print(checkVectors)
    #Rewrite the file
    oldconf = open(configParent.config, "r")
    oldconflines = oldconf.readlines()
    oldconf.close()
    print("Getting temporary file handle for modconfig.")
    oshandle, newconfdir = tempfile.mkstemp(suffix=".tmp", dir=".")
    try:
        os.close(oshandle)
    except:
        print("Error: Windows failed all over closing the file handle.")
    newconf = open(newconfdir, "w")

    #OK, let's see if we need to recover vectors

    for line in oldconflines:
        #Only one data point for line. Let's deal with our cases.
        if "misc,datascale" in line and checkVectors:
            newMax = slowlyPainfullyMaximize(filenames)
            newconf.write("    misc,datascale " + str(newMax)+ "\n")
        elif not percentMagnitude == 100:
            if "misc,zoom" in line:
        #newconf.write(line)
        #Don't stop clobbering zoom!
                newconf.write("    misc,zoom 0\n")
            elif "misc,default" in line:
        #This was not nearly as true as I'd hoped
                pass #Just in case this ever looks at the viewport, clobber the viewport.
            elif "misc,height" in line:
                newval = int(re.findall(r"[0-9]+", line)[0]) * percentMagnitude / 100.0
                newconf.write("    misc,height " + str(newval) + "\n")
            elif "misc,width" in line:
                newval = int(re.findall(r"[0-9]+", line)[0]) * percentMagnitude / 100.0
                newconf.write("    misc,width " + str(newval) + "\n")
            else:
                newconf.write(line)
    newconf.close()
    return newconfdir


def resolveConfiguration(filenames, config_parent):
    if config_parent.magnifierSpin.GetValue() != 100 or config_parent.autoMaxVectors.GetValue():
        confpath = spliceConfig(config_parent.magnifierSpin.GetValue(), config_parent.autoMaxVectors.GetValue(), filenames, config_parent)
        cleanconfig = True
    else:
        cleanconfig = False
        confpath = config_parent.config
    return (confpath, cleanconfig) 


def convertOmfToImage(omf, tclCall, oommfPath, confpath, stdinRedirect, mode='advanced'):
    MODE = mode
    pathTo, fname = omf.rsplit(os.path.sep, 1)
    command = tclCall + ' "' + oommfPath + '" avf2ppm -f -v 2 -format b24 -config "' + confpath + '" "' + omf + '"'
    if os.name == 'nt':
        print("Watching stdin redirect:", stdinRedirect)
        if MODE == "basic":
            os.system(command)
        elif MODE == "advanced":
            if not r":\\" in omf:
                pipe = subprocess.Popen(command, shell=True, stdin = stdinRedirect, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
            else:
                #Avoid network stupidity.
                pipe = subprocess.Popen(command, shell=False, stdin = stdinRedirect, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
            a = pipe.readlines()
            #*Really*? It's not using stdout?
            if a:
                for line in a: print(line.strip())
    else:
        print("probably posix mode.")
        if MODE == "basic":
            os.system(command)
        elif MODE == "advanced":
            pipe = subprocess.Popen(command, shell=True, stdin = sys.stdin, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
            a = pipe.readlines()
            #THIS should at least use STDout
            if a:
                for line in a: print(line.strip())