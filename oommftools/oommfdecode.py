
"""
OOMMFDecode
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
from __future__ import print_function
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from builtins import hex
from builtins import zip
from builtins import range
import time
from collections import defaultdict
import pickle as pickle
from wx import adv
import os
import wx
import struct
import numpy as np
import scipy.io as spio
from .fnameutil import filterOnExtensions
from . import _about as about

#########
# About #
#########

VERSION = about.__version__
NAME = "OOMMFDecode"
LICENSE = about.__license__
COPYRIGHT = about.__copyright__
WEBSITE = about.__uri__
DESCRIPTION = """OOMMFDecode is an OOMMF postprocessing tool for
converting OVF files or batches of same into numpy
arrays or MATLAB data files. Just drag and drop.
\nOOMMFDecode is part of OOMMFTools."""


########
# DECS #
########

LASTPATH = os.getcwd()
if __name__ == "__main__":
    #app = wx.App(None)
    #app = wx.App(None)
    #app = wx.App(redirect=True)
    app = wx.App(redirect=True, filename="oommfdecode.log")

#######
# GUI #
#######

class MainFrame(wx.Frame):
    """Main oommfdecode frame
    """
    def __init__(self, manager=None):
        
        wx.Frame.__init__(self, None, -1, " ".join([NAME, VERSION]), size=(340, 400))

        BigFont = wx.Font(16, wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_BOLD)
        TinyFont = wx.Font(8, wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)

        self.dt = OOMMFSelectiveTarget(self)
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

        #NOW we can deal with actual GUI stuff - store a reference for forced resize, if it comes up
        panel = wx.Panel(self, -1)
        self.panel = panel

        sizer = wx.BoxSizer(wx.VERTICAL)

        titleText = wx.StaticText(panel, -1, "OMF File Decoding")
        titleText.SetFont(BigFont)
        sizer.Add(titleText, 0, wx.ALIGN_CENTER | wx.TOP, 24)

        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 18)

        self.doNumpy = wx.CheckBox(panel, -1, "Create pickled numpy")
        sizer.Add(self.doNumpy, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

        self.doMATLAB = wx.CheckBox(panel, -1, "Create MATLAB data")
        sizer.Add(self.doMATLAB, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.TOP, 18)

        ins = wx.StaticText(panel, -1, "Drop OOMMF Files Here!")
        ins.SetFont(BigFont)
        sizer.Add(ins, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.TOP, 80)

        panel.SetSizer(sizer)
        if self.manager:
            self.CenterOnParent()
        panel.Fit()
        self.Show()

    def gatherData(self, data, headers, extraData):
        """
        """
        global LASTPATH
        #Outputs are array, headers, filenam
        if self.doNumpy.GetValue():
            with wx.FileDialog(self, 'Export Pickled numpy Data',
                               LASTPATH, "", "Pickled Data (*.pnp)|*.pnp",
                               wx.FD_SAVE) as dlg:
                if dlg.ShowModal() == wx.ID_OK and dlg.GetFilename():
                    filename = dlg.GetPath()
                    LASTPATH = os.path.dirname(filename)
                    pickleArray(data, headers, extraData, filename)
                elif dlg.ShowModal() == wx.ID_CANCEL:
                    return # the user changed their mind

        if self.doMATLAB.GetValue():
            with wx.FileDialog(self, 'Export MATLAB Data', LASTPATH, "",
                               "MATLAB Data (*.mat)|*.mat",
                               wx.FD_SAVE) as dlg:
                if dlg.ShowModal() == wx.ID_OK and dlg.GetFilename():
                    filename = dlg.GetPath()
                    LASTPATH = os.path.dirname(filename)
                    matlabifyArray(data, headers, extraData, filename)
                elif dlg.ShowModal() == wx.ID_CANCEL:
                    return # the user changed their mind

    def showAbout(self, evt):
        """
        """
        info = wx.adv.AboutDialogInfo()
        mydesc = DESCRIPTION
        mylicense = LICENSE
        info.SetName(NAME)
        info.SetVersion(VERSION)
        info.SetDescription(''.join(mydesc))
        info.SetLicense(''.join(mylicense))
        info.SetCopyright(COPYRIGHT)
        info.SetWebSite(WEBSITE)
        wx.adv.AboutBox(info)

    def onClose(self, evt):
        """
        """
        if self.manager:
            self.manager.droppedWindow(self)
        self.Destroy()

class SupportDialog(wx.ProgressDialog):
    """
    """
    def __init__(self, title, message, **kwargs):
        wx.ProgressDialog.__init__(self, title, message, **kwargs)
        self._workDone = 0
        self.workmax = kwargs["maximum"]

    def workDone(self, delta, newmsg):
        """
        """
        self._workDone += delta
        self.Update(self._workDone, newmsg)

    def finish(self):
        """
        """
        self.Update(self.workmax, "Done!")

####################
# BACKEND DECODING #
####################

class OOMMFSelectiveTarget(wx.FileDropTarget):
    """
    """
    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent

    def OnDropFiles(self, x, y, filenames):
        """
        """
        oommf = filterOnExtensions(["omf", "ovf", "oef", "ohf"], filenames)
        if not oommf or not (self.parent.doNumpy.GetValue() or self.parent.doMATLAB.GetValue()):
            return 0 #You got dropped some bad files!
        global LASTPATH
        LASTPATH = os.path.dirname(oommf[0])
        arrays, headers, extra = groupUnpack(oommf,
                                             SupportDialog("Decode in Progress",
                                                           "Decoding...",
                                                           maximum=len(oommf)))

        #One final step before we're done - let's try to sort based on the sim time
        #using a standard decorate-sort-undecorate, with a twist for the variable number of keys

        #Let's start by finding the original indices - making a copy is key
        originalTimeIndex = list(extra["SimTime"])
        if len(set(extra["MIFSource"])) == 1:
            if not -1 in extra["SimTime"]:
                extra["SimTime"], arrays = list(zip(*sorted(zip(originalTimeIndex, arrays))))
                #Sadly, the cleverness ends here - the rest must be bruteforced.
                for key in extra:
                    if not key == "SimTime": #We did that one.
                        junk, extra[key] = list(zip(*sorted(zip(originalTimeIndex, extra[key]))))

        self.parent.gatherData(arrays, headers, extra)
        return 1

def groupUnpack(targetlist, progdialog=None):
    """
    """
    decodedArrays = []
    headers = {}
    extraData = defaultdict(list)
    firstTime = True
    try:
        for target in targetlist:
            collect = unpackFile(target)
            if firstTime:
                firstTime = False
                headers = collect[1]
            decodedArrays.append(collect[0])
            #Unpack extra collected data
            for key, value in list(collect[2].items()):
                extraData[key].append(value)
            if progdialog:
                progdialog.workDone(1, "Decoding...")
                time.sleep(0.01) #Should facilitate redraw thread coming to life

    except Exception as e:
        if progdialog: progdialog.finish()
        wx.MessageBox('Unpacking error: ' + repr(e), "Error")
        print(e)
    else:
        if progdialog: progdialog.finish()
    return (np.array(decodedArrays), headers, extraData)

def unpackFile(filename):
    """
    """
    with open(filename, 'rb') as f:
        headers = {} #I know valuemultiplier isn't always present. This is checked later.
        extraCaptures = {'SimTime':-1, 'Iteration':-1, 'Stage':-1, "MIFSource":""}
        #Parse headers
        a = ""
        while not "Begin: Data" in a:
            
            a = f.readline().strip().decode()
            #Determine if it's actually something we need as header data
            for key in ["xbase",
                        "ybase",
                        "zbase",
                        "xstepsize",
                        "ystepsize",
                        "zstepsize",
                        "xnodes",
                        "ynodes",
                        "znodes",
                        "valuemultiplier"]:
                if key in a:
                    headers[key] = float(a.split()[2]) #Known position FTW
            #All right, it may also be time data, which we should capture
            if "Total simulation time" in a:
                #Split on the colon to get the time with units;
                #strip spaces and split on the space to separate time and units
                #Finally, pluck out the time, stripping defensively
                #(which should be unnecessary).
                extraCaptures['SimTime'] = float(a.split(":")[-1].strip().split()[0].strip())
            if "Iteration:" in a:
                #Another tricky split...
                extraCaptures['Iteration'] = float(a.split(":")[2].split(",")[0].strip())
            if "Stage:" in a:
                extraCaptures['Stage'] = float(a.split(":")[2].split(",")[0].strip())
            if "MIF source file" in a:
                extraCaptures['MIFSource'] = a.split(":", 2)[2].strip()


        #Initialize array to be populated
        outArray = np.zeros((int(headers["xnodes"]),
                             int(headers["ynodes"]),
                             int(headers["znodes"]),
                             3))

        #Determine decoding mode and use that to populate the array
        print("Data indicator:", a)
        decode = a.split()
        if decode[3] == "Text":
            return _textDecode(f, outArray, headers, extraCaptures)
        elif decode[3] == "Binary" and decode[4] == "4":
            #Determine endianness
            endianflag = f.read(4)
            if struct.unpack(">f", endianflag)[0] == 1234567.0:
                print("Big-endian 4-byte detected.")
                dc = struct.Struct(">f")
            elif struct.unpack("<f", endianflag)[0] == 1234567.0:
                print("Little-endian 4-byte detected.")
                dc = struct.Struct("<f")
            else:
                raise Exception("Can't decode 4-byte byte order mark: " + hex(endianflag))
            return _binaryDecode(f, 4, dc, outArray, headers, extraCaptures)
        elif decode[3] == "Binary" and decode[4] == "8":
            #Determine endianness
            endianflag = f.read(8)
            if struct.unpack(">d", endianflag)[0] == 123456789012345.0:
                print("Big-endian 8-byte detected.")
                dc = struct.Struct(">d")
            elif struct.unpack("<d", endianflag)[0] == 123456789012345.0:
                print("Little-endian 8-byte detected.")
                dc = struct.Struct("<d")
            else:
                raise Exception("Can't decode 8-byte byte order mark: " + hex(endianflag))
            return _binaryDecode(f, 8, dc, outArray, headers, extraCaptures)
        else:
            raise Exception("Unknown OOMMF data format:" + decode[3] + " " + decode[4])



def _textDecode(filehandle, targetarray, headers, extraCaptures):
    """
    """
    valm = headers.get("valuemultiplier", 1)
    for k in range(int(headers["znodes"])):
        for j in range(int(headers["ynodes"])):
            for i in range(int(headers["xnodes"])):
                #numpy is fantastic - splice in a tuple
                text = filehandle.readline().strip().split()
                targetarray[i, j, k] = (float(text[0])*valm,
                                        float(text[1])*valm,
                                        float(text[2])*valm)
    print("Decode complete.")
    return (targetarray, headers, extraCaptures)


def _binaryDecode(filehandle, chunksize, decoder, targetarray, headers, extraCaptures):
    """
    """
    valm = headers.get("valuemultiplier", 1)
    for k in range(int(headers["znodes"])):
        for j in range(int(headers["ynodes"])):
            for i in range(int(headers["xnodes"])):
                for coord in range(3): #Slowly populate, coordinate by coordinate
                    targetarray[i, j, k, coord] = decoder.unpack(filehandle.read(chunksize))[0] * valm
    print("Decode complete.")
    return (targetarray, headers, extraCaptures)

def pickleArray(array, headers, extraCaptures, filename):
    """
    """
    temp = dict(headers)
    temp.update(extraCaptures)
    f = open(filename, 'wb')
    pickle.dump((array, temp), f)
    f.close()

def matlabifyArray(array, headers, extraCaptures, filename):
    """
    """
    GridSize = np.array([float(headers["xstepsize"]),
                         float(headers["ystepsize"]),
                         float(headers["zstepsize"])])
    OutDict = {"OOMMFData":array, "GridSize":GridSize}
    OutDict.update(extraCaptures)
    spio.savemat(filename, OutDict)

def slowlyPainfullyMaximize(filenames):
    """
    This is a special utility function used by OOMMFConvert to find the single largest-magnitude
    vector in a set of vector files
    """
    #There is no nice way to do this.
    def mag(a, b, c):
        """
        """
        return np.sqrt(a**2 + b**2 + c**2)
    maxmag = 0

    for filename in filenames:
        thisArray, headers, extraCaps = unpackFile(filename)
        for k in range(int(headers["znodes"])):
            for j in range(int(headers["ynodes"])):
                for i in range(int(headers["xnodes"])):
                    maxmag = max(maxmag, mag(*thisArray[i, j, k]))
    return maxmag
########
# MAIN #
########
if __name__ == "__main__":
    BigBoss = MainFrame()
    app.MainLoop()
