import os
def getOOMMFPath(pathToCheck):
    #Check if we have a saved OOMMF path to use as config data
    if os.path.exists("." + os.path.sep + "oommf.path"):
        f = open("." + os.path.sep + "oommf.path")
        lines = f.readlines()
        f.close()
        path = lines[-1].strip()
        #But we also have to validate the path on this particular computer
        if os.path.exists(path) and path.rsplit(".")[-1] == "tcl":
            return path
            print('self.OOMMFPath = path')
        else:
            return None
            #Cleanup bogus config file
            os.remove("." + os.path.sep + "oommf.path")
            print('clean up bogus config file')
    else:
        #No file at all!
        return None
        print('no file found') 
