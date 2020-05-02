
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
from ...fnameutil import filterOnExtensions
from ... import _about as about
from ...core import oommfdecode

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
                    oommfdecode.pickleArray(data, headers, extraData, filename)
                elif dlg.ShowModal() == wx.ID_CANCEL:
                    return # the user changed their mind

        if self.doMATLAB.GetValue():
            with wx.FileDialog(self, 'Export MATLAB Data', LASTPATH, "",
                               "MATLAB Data (*.mat)|*.mat",
                               wx.FD_SAVE) as dlg:
                if dlg.ShowModal() == wx.ID_OK and dlg.GetFilename():
                    filename = dlg.GetPath()
                    LASTPATH = os.path.dirname(filename)
                    oommfdecode.matlabifyArray(data, headers, extraData, filename)
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
        arrays, headers, extra = self.groupUnpack(oommf,
                                             SupportDialog("Decode in Progress",
                                                           "Decoding...",
                                                           maximum=len(oommf)))

        #One final step before we're done - let's try to sort based on the sim time
        #using a standard decorate-sort-undecorate, with a twist for the variable number of keys

        #Let's start by finding the original indices - making a copy is key

        arrays, extra = oommfdecode.sortBySimTime(extra, arrays)

        self.parent.gatherData(arrays, headers, extra)
        return 1


    def groupUnpack(self, targetlist, progdialog=None):
        """
        """
        try:
            (decodedArrays, headers, extraData) = oommfdecode.groupUnpack(targetlist)
            if progdialog:
                progdialog.workDone(1, "Decoding...")
                time.sleep(0.01) #Should facilitate redraw thread coming to life
        except Exception as e:
            if progdialog: progdialog.finish()
            wx.MessageBox('Unpacking error: ' + repr(e), "Error")
            print(e)
        else:
            if progdialog: progdialog.finish()
        return (decodedArrays, headers, extraData)

########
# MAIN #
########
if __name__ == "__main__":
    BigBoss = MainFrame()
    app.MainLoop()
