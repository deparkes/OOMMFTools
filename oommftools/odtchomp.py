
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
from __future__ import print_function
from __future__ import absolute_import



from builtins import str
from builtins import object
import os
from wx import adv
import wx
import numpy as np
from .fnameutil import filterOnExtensions
from . import _about as about
from .core import odtchomp

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
            self.digest = odtchomp.Interpreter({}, keys=lines)
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
            print("Batch mode disable.")
            self.importButton.Disable()
            self.exportButton.Disable()
        else:
            print("Batch mode enable.")
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
        print("Import enable.")
        self.fileLabel.SetLabel("Open: " + filename)
        self.digest = odtchomp.chomp(filename)
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
        return (odtchomp.chomp(filename), os.path.dirname(filename))

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
            odtchomp.write(filename, self.digest, self.delim, self.watching)

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
                print(outDir, outfname)
                odtchomp.write(outDir + os.path.sep + outfname, interp, self.parent.delim, self.parent.watching)
            return 1



########
# MAIN #
########
if __name__ == "__main__":
    app = wx.App(None)
    BigBoss = MainFrame()
    app.MainLoop()
