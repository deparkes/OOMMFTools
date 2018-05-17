import os


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
