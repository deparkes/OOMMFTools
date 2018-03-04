
"""
ODTChomp
Copyright (C) 2010  Mark Mascaro

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""

import os
from wx import adv
import wx
import numpy as np
from fnameutil import filterOnExtensions
import _about as about


#########
# About #
#########

VERSION = about.__version__
NAME = "ODTChomp"
LICENSE = about.__license__
COPYRIGHT = about.__copyright__
WEBSITE = about.__uri__
DESCRIPTION = """ODTChomp is an OOMMF postprocessing tool for
extracting columns from and unifying delimitation
of ODT table files.
\nODTChomp is part of OOMMFTools."""



########
# DECS #
########

#Readability magic below
ALWAYS_CLEAR = ["Oxs_"]

PROTECTED_NAMES = ["Exchange"]

#######
# GUI #
#######

class MainFrame(wx.Frame):
    """Main frame for odtchomp
    """
    def __init__(self, manager=None):
        wx.Frame.__init__(self, None, -1, "ODT Chomper 0.9", size=(900, 500))
        self.watching = []
        self.delim = " "

        #Let's try to get a proto-digest from a file to memorize the ODT layout
        if os.path.exists("." + os.path.sep + "odt.layout"):
            f = open("." + os.path.sep + "odt.layout")
            lines = f.readlines()
            f.close()
            lines = [line.strip() for line in lines]
            self.digest = Interpreter({}, keys=lines)
        else:
            #No file at all!
            self.digest = None

        self.exportPath = os.getcwd()

        self.dt = ODTDropTarget(self)
        self.SetDropTarget(self.dt)
        self.manager = manager

        self.Bind(wx.EVT_CLOSE, self.onClose)

        #A very simple menubar
        menubar = wx.MenuBar()
        about = wx.Menu()
        about.Append(999, 'About', 'Program information and license')
        menubar.Append(about, "About")
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.showAbout, id=999)

        panel = wx.Panel(self, -1)
        self.panel = panel #OK, I do need a reference to this to send size events later
        #Point Zero: Major Box Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        #Deal with import button
        self.importButton = wx.Button(panel, 1, "Import")
        sizer.Add(self.importButton, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        self.Bind(wx.EVT_BUTTON, self.importFile, id=1)


        #Deal with active label
        self.fileLabel = wx.StaticText(panel, -1, "No File Loaded", style=wx.ALIGN_CENTER)
        sizer.Add(self.fileLabel, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.BOTTOM, 15)

        #Listboxes! Prepare horizontal sizer
        tsizer = wx.BoxSizer()

        #Do left listbox
        llbsizer = wx.BoxSizer(wx.VERTICAL)
        lefttitle = wx.StaticText(panel, -1, "Available Data Fields", style=wx.ALIGN_CENTER)
        self.leftbox = wx.ListBox(panel, 10, choices=[], style=wx.LB_SINGLE)
        llbsizer.Add(lefttitle, 0, wx.ALIGN_CENTER)
        llbsizer.Add(self.leftbox, 1, wx.ALIGN_CENTER | wx.EXPAND | wx.TOP, 10)
        tsizer.Add(llbsizer, 1, wx.ALIGN_CENTER | wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.leftbox.Bind(wx.EVT_LEFT_DCLICK, self.takeData)

        midbsizer = wx.BoxSizer(wx.VERTICAL)

        #Add/Remove Buttons
        a = wx.Button(panel, 20, "-->")
        self.Bind(wx.EVT_BUTTON, self.takeData, id=20)
        b = wx.Button(panel, 21, "<--")
        self.Bind(wx.EVT_BUTTON, self.puntData, id=21)
        c = wx.Button(panel, 22, "+All")
        self.Bind(wx.EVT_BUTTON, self.takeAll, id=22)
        d = wx.Button(panel, 23, "-All")
        self.Bind(wx.EVT_BUTTON, self.puntAll, id=23)

        midbsizer.Add(a, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        midbsizer.Add(b, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        midbsizer.Add(c, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        midbsizer.Add(d, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        #Radio Controls

        label = wx.StaticText(panel, -1, "File Delimiter")
        self.spaceDelim = wx.RadioButton(panel, 30, "Space", style=wx.RB_GROUP)
        self.tabDelim = wx.RadioButton(panel, 31, "Tab")
        self.commaDelim = wx.RadioButton(panel, 32, "Comma")
        self.Bind(wx.EVT_RADIOBUTTON, self.setDelim, id=30)
        self.Bind(wx.EVT_RADIOBUTTON, self.setDelim, id=31)
        self.Bind(wx.EVT_RADIOBUTTON, self.setDelim, id=32)
        self.spaceDelim.SetValue(True)

        midbsizer.Add((-1, 10))
        midbsizer.Add(label, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 10)
        midbsizer.Add(self.spaceDelim, 0, wx.LEFT | wx.BOTTOM, 2)
        midbsizer.Add(self.tabDelim, 0, wx.LEFT | wx.BOTTOM, 2)
        midbsizer.Add(self.commaDelim, 0, wx.LEFT | wx.BOTTOM, 2)

        tsizer.Add(midbsizer, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)

        #Final Listbox
        rlbsizer = wx.BoxSizer(wx.VERTICAL)
        righttitle = wx.StaticText(panel, -1, "Exported Data Fields", style=wx.ALIGN_CENTER)
        self.rightbox = wx.ListBox(panel, 11, choices=[], style=wx.LB_SINGLE)
        rlbsizer.Add(righttitle, 0, wx.ALIGN_CENTER)
        rlbsizer.Add(self.rightbox, 1, wx.ALIGN_CENTER | wx.EXPAND | wx.TOP, 10)
        tsizer.Add(rlbsizer, 1, wx.ALIGN_CENTER | wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.rightbox.Bind(wx.EVT_LEFT_DCLICK, self.puntData)


        #U/D buttons
        udbsizer = wx.BoxSizer(wx.VERTICAL)
        a = wx.Button(panel, 50, "Move Up")
        b = wx.Button(panel, 51, "Move Down")

        self.Bind(wx.EVT_BUTTON, self.bumpUp, id=50)
        self.Bind(wx.EVT_BUTTON, self.bumpDown, id=51)

        udbsizer.Add(a, 0, wx.CENTER | wx.BOTTOM, 10)
        udbsizer.Add(b, 0, wx.CENTER | wx.BOTTOM, 10)
        tsizer.Add(udbsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)


        #Clean up horizontal sizers
        sizer.Add(tsizer, 1, wx.EXPAND | wx.BOTTOM, 20)

        # Export!
        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.BOTTOM, 15)

        self.batchModeCheckbox = wx.CheckBox(panel, 60, "Drag-Drop Batch Mode")
        self.batchModeCheckbox.SetValue(False)
        sizer.Add(self.batchModeCheckbox, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        self.Bind(wx.EVT_CHECKBOX, self.fixBatchMode, id=60)

        self.exportButton = wx.Button(panel, 70, "Export")
        self.exportButton._secondLevelEnable = False
        sizer.Add(self.exportButton, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        self.Bind(wx.EVT_BUTTON, self.exportFile, id=70)
        self.exportButton.Disable()

        #Late-game setup
        if self.digest:
            self.leftbox.Set(self.digest.getNames())

        #Cleanup
        panel.SetSizer(sizer)
        if self.manager:
            self.CenterOnParent()
        self.Show()

    def onClose(self, evt):
        """
        """
        if self.manager:
            self.manager.droppedWindow(self)
        self.Destroy()

    def setDelim(self, evt):
        """
        """
        if self.spaceDelim.GetValue():
            self.delim = " "
        elif self.tabDelim.GetValue():
            self.delim = "\t"
        elif self.commaDelim.GetValue():
            self.delim = ","

    def fixBatchMode(self, evt):
        """
        """
        if self.batchModeCheckbox.GetValue():
            print "Batch mode disable."
            self.importButton.Disable()
            self.exportButton.Disable()
        else:
            print "Batch mode enable."
            self.importButton.Enable()
            if self.exportButton._secondLevelEnable:
                self.exportButton.Enable()

    def importFile(self, evt):
        """
        """
        dlg = wx.FileDialog(self, "Import ODT File",
                            os.getcwd(), "",
                            "OOMMF ODT Data (*.odt)|*.odt",
                            wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK and dlg.GetPath():
            #self.fileLabel.SetLabel("Open: " + os.getcwd() + os.path.sep + dlg.GetFilename())
            self._importFile(dlg.GetPath())

    def _importFile(self, filename):
        """
        """
        print "Import enable."
        self.fileLabel.SetLabel("Open: " + filename)
        self.digest = chomp(filename)
        self.leftbox.Set(self.digest.getNames())
        self.panel.SendSizeEvent()
        self.exportPath = os.path.dirname(filename)
        self.exportButton._secondLevelEnable = True
        self.exportButton.Enable()
        #Cache the autolayout
        f = open("." + os.path.sep + "odt.layout", "w")
        f.write("\n".join(self.digest.getNames()))
        f.close()

    def _lightImportFile(self, filename):
        """
        """
        #returns (Interpreter, exportPathname)
        return (chomp(filename), os.path.dirname(filename))

    def exportFile(self, evt):
        """
        """
        dlg = wx.FileDialog(self,
                            'Export Translated File',
                            self.exportPath, "",
                            "Plaintext ODT Data (*.txt)|*.txt",
                            wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK and dlg.GetPath():
            filename = dlg.GetPath()
            self.exportPath = os.path.dirname(dlg.GetPath())
            write(filename, self.digest, self.delim, self.watching)

    def takeData(self, evt):
        """
        """
        if self.digest and self.leftbox.GetSelections():
            sel = self.leftbox.GetSelections()[0]
            keys = self.digest.getNames()
            if not keys[sel] in self.watching:
                self.watching.append(keys[sel])
                self.rightbox.Set(self.watching)

    def takeAll(self, evt):
        """
        """
        if self.digest:
            self.watching = self.digest.getNames()
            self.rightbox.Set(self.watching)

    def puntData(self, evt):
        """
        """
        if self.digest and self.rightbox.GetSelections():
            self.watching.pop(self.rightbox.GetSelections()[0])
            self.rightbox.Set(self.watching)

    def puntAll(self, evt):
        """
        """
        if self.digest:
            self.watching = []
            self.rightbox.Set(self.watching)
            #self.leftbox.Set(self.digest.getNames())

    def bumpUp(self, evt):
        """
        """
        if self.digest and self.rightbox.GetSelections() and self.rightbox.GetSelections()[0] > 0:
            dex = self.rightbox.GetSelections()[0]
            pull = self.watching.pop(dex)
            self.watching.insert(dex-1, pull)
            self.rightbox.Set(self.watching)
            self.rightbox.SetSelection(dex-1)

    def bumpDown(self, evt):
        """
        """
        if self.digest and self.rightbox.GetSelections() and self.rightbox.GetSelections()[0] < len(self.watching)-1:
            dex = self.rightbox.GetSelections()[0]
            pull = self.watching.pop(dex)
            self.watching.insert(dex+1, pull)
            self.rightbox.Set(self.watching)
            self.rightbox.SetSelection(dex+1)

    def showAbout(self, evt):
        """
        """
        info = wx.adv.AboutDialogInfo()
        mydesc = DESCRIPTION
        mylicense = LICENSE
        info.SetName(NAME)
        info.SetVersion(VERSION)
        info.SetDescription("".join(mydesc))
        info.SetLicense("".join(mylicense))
        info.SetCopyright(COPYRIGHT)
        info.SetWebSite(WEBSITE)
        wx.adv.AboutBox(info)

###########
# BACKEND #
###########

class ODTDropTarget(wx.FileDropTarget):
    """
    """
    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent

    def OnDropFiles(self, x, y, filenames):
        """
        """
        namepotential = filterOnExtensions(["odt"], filenames)
        if not self.parent.batchModeCheckbox.GetValue() or not self.parent.digest:
            #normal mode
            if namepotential:
                self.parent._importFile(namepotential[0])
            return 0
        else:
            #batch mode
            for fname in namepotential:
                interp, outDir = self.parent._lightImportFile(fname)
                outfname = fname.rsplit(os.path.sep, 1)[1].split(".")[0] + ".txt"
                print outDir, outfname
                write(outDir + os.path.sep + outfname, interp, self.parent.delim, self.parent.watching)
            return 1

def write(filename, interpreter, delim, fields):
    """
    """
    print "Write out to:", filename
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
    print evt



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
                        print "In spacesplit match:"
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
    for key in inDict.keys():
        uniquenessCheck.append(key.split(":"))
    for key in inDict.keys():
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

########
# MAIN #
########
if __name__ == "__main__":
    app = wx.App(None)
    BigBoss = MainFrame()
    app.MainLoop()
