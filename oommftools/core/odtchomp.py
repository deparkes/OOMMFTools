from __future__ import print_function
from __future__ import absolute_import

def write(filename, interpreter, delim, fields):
    """
    """
    print("Write out to:", filename)
    refdelim = delim
    f = open(filename, "w")
    #Do keys
    if delim == ",":
        delim = ", "
    if refdelim == " ":
        log("Space delim override: Deleting spaces from field names.")
        reffields = []
        for field in fields:
            reffields.append(field.replace(" ", "_"))
    else:
        reffields = fields


    line = delim.join(reffields) + "\n"
    f.write(line)
    #Do values
    i = 0
    while i < interpreter.getDataLength()-1:
        line = ""
        for key in fields:
            line += str(interpreter.getData()[key][i]) + delim
        line = line.rstrip(delim)
        line += "\n"
        f.write(line)
        i += 1

    #Cleanup
    f.close()

def resolve(lst, keys):
    """
    Return a list of values from a dictionary corresponding to keys provided
    """
    out = []
    for key in keys:
        out.append(lst[key])
    return out

def split_densify(a, delim=" "):
    """
    """
    rets = []
    for p in a.split(delim):
        if p:
            rets.append(p.strip())
    return rets


def log(evt):
    """
    """
    try:
        evt = unicode(evt)
    except:
        evt = str(evt)
    
    print(evt)


def chomp(odt, parent=None):
    """
    """
    retHeaders = []
    retDict = {}
    log("Opening %s" % odt)
    f = open(odt, "r")
    data = f.readlines()
    log("File length: %d lines." % len(data))
    InData = False
    if parent:
        parent.progstart(len(data))
    for i, line in enumerate(data):
        if parent:
            parent.progreport(i)
        line = line.strip()
        #Look out for multiple table headers in the parse!
        if line[0] == "#":
            InData = False
            #Comment or table parse
            if "Columns" in line:
                log("Absorbing header data: Identifying coumns.")
                #Clobber header table
                retHeaders = []
                #Begin slow parse
                line = line.split("Columns:")[1].strip()
                while line:
                    grab = ""
                    line = line.strip()
                    if line[0] == "{":
                        #Group match!
                        grab, line = line.split("}", 1)
                        line = line.strip() #Must clear trailing spaces
                        grab = grab.strip("{}")
                        log("Matching title field by symbol: %s" % grab)
                    else:
                        #Spacesplit match
                        print("In spacesplit match:")
                        check = line.split(" ", 1)
                        if len(check) == 1:
                            grab = check[0]
                            line = ""
                        else:
                            grab, line = check
                        grab = grab.strip()
                        log("Matching title field by space: %s" % grab)
                    if grab:
                        log("Indexing %s at point %d" % (grab, len(retHeaders)))
                        retHeaders.append(grab)
                        if not grab in retDict:
                            log("Identifying new header: %s" % grab)
                            retDict[grab] = np.array([])
            else:
                pass #Currently do nothing on other header lines
        else:
            if not InData:
                log("Processing data block.")
                InData = True
            #Chew actual data
            fields = split_densify(line)
            for i, v in enumerate(fields):
                fieldname = retHeaders[i]
                retDict[fieldname] = np.append(retDict[fieldname], float(v))
    f.close()
    return Interpreter(headers_prettify(retDict), list_prettify(retHeaders))

class Interpreter(object):
    """
    """
    def __init__(self, idict, keys=None):
        self.keys = keys
        if not self.keys:
            self.keys = list(idict.keys())

        self.dict = idict

    def getNames(self):
        return self.keys

    def getData(self):
        return self.dict

    def getDataLength(self):
        return len(self.dict[self.keys[0]])

def list_prettify(inList):
    """
    """
    out = []
    uniquenessCheck = []
    for key in inList:
        uniquenessCheck.append(key.split(":"))
    for key in inList:
        fixedkey = namepolish(key, uniquenessCheck)
        if fixedkey in out:
            log("Uh-oh, you might have caused a key collision! This should be impossible.")
        out.append(fixedkey)
    return out

def headers_prettify(inDict):
    """
    """
    outDict = {}
    uniquenessCheck = []
    for key in list(inDict.keys()):
        uniquenessCheck.append(key.split(":"))
    for key in list(inDict.keys()):
        fixedkey = namepolish(key, uniquenessCheck)
        if fixedkey in outDict:
            log("Uh-oh, you might have caused a key collision! This should be impossible.")
        outDict[fixedkey] = inDict[key]
    return outDict

def namepolish(name, uniquenessCheck):
    """Uniquely identify quantity fields.

    This is pretty ugly, but the key point is this: it filters
    down to the minimum amount of information necessary to uniquely identify a quantity
    It makes things more human-readable

    Parameters
    ----------
    name : str
        One particular 'key' from header output
    uniquenessCheck : list[[list]]
        A list of lists of strings where there are duplicates.

    Returns
    -------
    str
        A string of simplified field headers.

    Examples
    --------
    >>> namepolish('evolver:givenName:quantity',
                    [['evolver', 'givenName', 'quantity'],
                    ['evolver', 'givenName', 'quantity2']])
    'quantity'
    """
    evolver, givenName, quantity = name.split(":")

    protectEvolver = False

    for item in PROTECTED_NAMES:
        if item in evolver:
            protectEvolver = True

    #This is pretty ugly, but the key point is this: it filters
    #down to the minimum amount of information necessary to uniquely identify a quantity
    #It makes things more human-readable
    # If the quantity is duplicated
    if len(_filterOnPos(uniquenessCheck, quantity, 2)) > 1:
        # If there is a givenName present
        if givenName:
            # Take the output from the quantity filter (which we know is > 1 now)
            # filter this output and check for duplicates of the givenName.
            if len(_filterOnPos(_filterOnPos(uniquenessCheck, quantity, 2), givenName, 1)) > 1:
                # Quantity and givenName are both duplicated. We need to keep
                # the evolver name to distinguish between fields.
                # If the evolver should be protected, put it second.
                # It's not clear why the evolver should be first or second
                # position.
                if protectEvolver:
                    newname = givenName + " " + evolver + " " + quantity
                # if evolver should not be protected, put it first.
                else:
                    newname = evolver + " " + givenName + " " + quantity
            # There is a given name present, but no duplicates found.
            # As there are no givenName duplicates, we should be able to
            # uniquely identify the fields without the evolver.
            # We may want to protect the evolver - in this case, include it
            # after the givenName
            elif protectEvolver:
                newname = givenName + " " + evolver + " " + quantity
            # If there are no duplicates in the givenName (the 'quantity' is
            # duplicated), and the evolver is not protected, drop the evolver.
            else:
                newname = givenName + " " + quantity
        # givenName not present. In this case just output evolver and quantity.
        else:
            newname = evolver + " " + quantity
    # Quantity is not duplicated. Each quantity label is unique, so can identify
    # the field usuing quantity alone.
    else:
        newname = quantity
    for item in ALWAYS_CLEAR:
        # Remove evolver prefixes to improve readability
        newname = newname.replace(item, "")
    log("Readability adaptation: %s to %s" % (name, newname))
    return newname

def _filterOnPos(inList, item, dex):
    """Return list (of lists) if a string is found in a particular position in
    that list.

    If the length of 'ret' is more than 1, it means that there is a
    duplicate of the target item in the indicated position.
    It seems to be called 'filter on pos' as it returns lists only
    if the target value is found in the position specified within
    the lists supplied.
    """
    ret = []
    for compare in inList:
        if compare[dex] == item:
            ret.append(compare)
    return ret

def prefix_punt(data):
    """
    """
    # Drop prefix (with _ separator)
    return data.split("_")[-1]