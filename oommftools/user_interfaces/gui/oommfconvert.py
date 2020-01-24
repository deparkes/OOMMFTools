
"""
OOMMFConvert
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
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from builtins import str
from builtins import range
from past.utils import old_div
from wx import adv
import wx, os, sys, subprocess, shutil, tempfile, math, re, time, imp
from fnameutil import filterOnExtensions
from core.oommfdecode import slowlyPainfullyMaximize
import _about as about
from core import oommfconvert as oommfconvert

#########
# About #
#########

VERSION = about.__version__
NAME = "OOMMFConvert"
LICENSE = about.__license__
COPYRIGHT = about.__copyright__
WEBSITE = about.__uri__
DESCRIPTION = """OOMMFConvert is an OOMMF postprocessing tool for
generating bitmap and movie files from OMF files
using a simple drag-and-drop interface.
It uses OOMMF's own avf2ppm utility
and employs FFmpeg to link images.
\nOOMMFConvert is part of OOMMFTools."""

########
# DECS #
########

MODE = 'advanced'
#Determine if workarounds are necessary
PY2EXE_COMPENSATION = hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__")
#Codecs: ffmpeg signature, file extension, short name
CODECS = {"HuffYUV": (r" -vcodec huffyuv ",".avi", "HuffYUV"),
          "MPEG4": (r" -sameq ",".mp4","MPEG4"),
          "DivX 3": (r" -sameq -vcodec msmpeg4 ",".avi","DivX3"),
          "H263+": (r" -vcodec h263p ",".avi","H263+")}

if __name__ == "__main__":
    app = wx.App(None)
    #app = wx.App(redirect=True)
    #app = wx.App(redirect=True, filename="oommfconvert.log")

    #app.SetOutputWindowAttributes("OOMMF Console Log", (-1,-1), (550, 400))

SETUP_LOAD = 5
RENDER_LOAD = 10
CLEANUP_LOAD = 5
FRAMEDUPE_LOAD = 1
MOVIE_LOAD = 50

if PY2EXE_COMPENSATION:
    print("Py2EXE detected. Will perform defensive stdin redirection.")

############
# GUI BODY #
############

class MainFrame(wx.Frame):
    def __init__(self, manager=None):
        wx.Frame.__init__(self, manager, -1, " ".join([NAME, VERSION]), size=(700,700))

        BigFont = wx.Font(16, wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_BOLD)
        TinyFont = wx.Font(8, wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)

        self.dt = OOMMFSelectiveTarget(self)
        self.SetDropTarget(self.dt)
        self.config = None
        self.manager = manager
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.OOMMFPath = oommfconvert.getOOMMFPath("." + os.path.sep + "oommf.path")

        #A very simple menubar
        menubar = wx.MenuBar()
        about = wx.Menu()
        about.Append(999, 'About', 'Program information and license')
        menubar.Append(about, "About")
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.showAbout, id=999)

        #NOW we can deal with actual GUI stuff
        panel = wx.Panel(self, -1)

        #Oops, safety for resize events
        self.panel = panel

        #TODO : Deal with DropTarget

        #Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        #OOMMF configuration part

        #Need to block this out so we can have the script call overloaded. I blame ActiveTcl. A lot.

        titleText = wx.StaticText(panel, -1, "Path to OOMMF")
        titleText.SetFont(BigFont)
        sizer.Add(titleText, 0, wx.ALIGN_CENTER | wx.TOP, 10)


        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.TclCall = wx.ComboBox(panel, 101, choices=["tclsh","tclsh85"])
        self.TclCall.SetStringSelection("tclsh")
        hsizer.Add(self.TclCall, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)

        self.OOMMFPathLabel = wx.StaticText(panel, -1, "OOMMF not located.", style = wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_VERTICAL)
        if self.OOMMFPath: self.OOMMFPathLabel.SetLabel(self.OOMMFPath)
        hsizer.Add(self.OOMMFPathLabel, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(hsizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(panel, -1, "Drag and drop or", style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 6)
        self.LoadOOMMFButton = wx.Button(panel, 10, "Load OOMMF")
        self.Bind(wx.EVT_BUTTON, self.GUILocateOOMMF, id=10)
        hsizer.Add(self.LoadOOMMFButton, 0)
        sizer.Add(hsizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)



        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.BOTTOM, 10)

        #Conf-file configuration part


        titleText = wx.StaticText(panel, -1, "Configuration File")
        titleText.SetFont(BigFont)
        sizer.Add(titleText, 0, wx.ALIGN_CENTER | wx.TOP, 10)

        #Now we need a pile of intermediate sizers, sadly
        self.ConfPathLabel = wx.StaticText(panel, -1, "No config loaded.", style = wx.EXPAND | wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        sizer.Add(self.ConfPathLabel, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        self.autoMaxVectors = wx.CheckBox(panel, -1, "Generate Vector Field Maxima")
        self.autoMaxVectors.SetValue(False)
        sizer.Add(self.autoMaxVectors, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        psizer = wx.BoxSizer(wx.HORIZONTAL)
        psizer.Add(wx.StaticText(panel, -1, "Drag and drop or", style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 6)
        self.LoadConfButton = wx.Button(panel, 20, "Load Config")
        self.Bind(wx.EVT_BUTTON, self.GUILocateConf, id=20)
        psizer.Add(self.LoadConfButton, 0)

        sizer.Add(psizer, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.BOTTOM, 10)
        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.BOTTOM, 10)

        # Fancy Stuff
        titleText = wx.StaticText(panel, -1, "Images")
        titleText.SetFont(BigFont)
        sizer.Add(titleText, 0, wx.ALIGN_CENTER | wx.TOP, 10)

        imsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.doImages = wx.CheckBox(panel, -1, "Make Bitmaps")
        self.doImages.SetValue(True)
        imsizer.Add(self.doImages, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 30)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(panel, -1, "Image Magnify%", style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 6)
        self.magnifierSpin = wx.SpinCtrl(panel, 100, "100", min=100, max=1000, size=(50,-1))
        hsizer.Add(self.magnifierSpin, 0)
        imsizer.Add(hsizer, 0)


        sizer.Add(imsizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.BOTTOM, 10)

        # Fancy Stuff
        titleText = wx.StaticText(panel, -1, "Movies")
        titleText.SetFont(BigFont)
        sizer.Add(titleText, 0, wx.ALIGN_CENTER | wx.TOP, 10)

        hsizer = wx.GridSizer(2,3,7,7)

        self.doMovie = wx.CheckBox(panel, -1, "Make Movies")
        hsizer.Add(self.doMovie, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

        joiner = wx.BoxSizer(wx.VERTICAL)
        a = wx.StaticText(panel, -1, "HuffYUV is superior.")
        a.SetFont(TinyFont)
        joiner.Add(a, 0, wx.ALIGN_CENTER)
        a = wx.StaticText(panel, -1, "Consider installing it.")
        a.SetFont(TinyFont)
        joiner.Add(a, 0, wx.ALIGN_CENTER)
        hsizer.Add(joiner, 0, wx.ALIGN_CENTER)

        joiner = wx.BoxSizer(wx.VERTICAL)
        a = wx.StaticText(panel, -1, "Magnifying video may fail")
        a.SetFont(TinyFont)
        joiner.Add(a, 0, wx.ALIGN_CENTER)
        a = wx.StaticText(panel, -1, "violently. User's risk.")
        a.SetFont(TinyFont)
        joiner.Add(a, 0, wx.ALIGN_CENTER)
        hsizer.Add(joiner)


        joiner = wx.BoxSizer()
        self.movieFPS = wx.SpinCtrl(panel, 201, "25", min=1, max=25, size=(50,-1))
        joiner.Add(self.movieFPS, 0, wx.RIGHT, 10)
        joiner.Add(wx.StaticText(panel, -1, "FPS"), 0, wx.ALIGN_CENTER_VERTICAL)
        hsizer.Add(joiner, 0, wx.ALIGN_CENTER)

        self.movieCodec = wx.ComboBox(panel, 200, choices = list(CODECS.keys()), style=wx.CB_READONLY)
        self.movieCodec.SetStringSelection("HuffYUV")
        hsizer.Add(self.movieCodec, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER)

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(wx.StaticText(panel, -1, "Movie Magnify%", style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 6)
        self.movieMagnifierSpin = wx.SpinCtrl(panel, 300, "100", min=100, max=300, size=(50,-1))
        bsizer.Add(self.movieMagnifierSpin, 0, wx.ALIGN_CENTER_VERTICAL)
        hsizer.Add(bsizer, 0, wx.ALIGN_CENTER_VERTICAL)


        sizer.Add(hsizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        sizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.BOTTOM, 10)


        #Clarification

        ins = wx.StaticText(panel, -1, "Drop OOMMF Files Here!")
        ins.SetFont(BigFont)
        sizer.Add(ins, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.TOP, 60)

        #Cleanup initialization
        panel.SetSizer(sizer)

        if self.manager:
            self.CenterOnParent()
        panel.Fit()
        self.Show()

    def onClose(self, evt):
        if self.manager:
            self.manager.droppedWindow(self)
        self.Destroy()

    def showAbout(self, evt):
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

    def GUILocateOOMMF(self, evt):
        dlg = wx.FileDialog(self, "Find OOMMF Location", os.getcwd(), "", "OOMMF TCL File (*.tcl)|*.tcl",wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK and dlg.GetFilename():
            filename = dlg.GetPath()
            #self.fileLabel.SetLabel("Open: " + os.getcwd() + os.path.sep + dlg.GetFilename())
            #self.digest = chomp(dlg.GetPath())
            #self.leftbox.Set(self.digest.getNames())
            self.locateOOMMF(filename)

    def locateOOMMF(self, path):
        self.OOMMFPath = path
        self.OOMMFPathLabel.SetLabel(path)
        f = open("oommf.path", "w")
        f.write(path)
        f.close()
        try:
            self.panel.SendSizeEvent()
        except:
            print("wx.Panel.SendSizeEvent() missed - probably using old wxPython. Cosmetic bug will result.")

    def GUILocateConf(self, evt):
        dlg = wx.FileDialog(self, "Select Configuration File", os.getcwd(), "", "mmDisp Config File (*.config)|*.config",wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK and dlg.GetFilename():
            filename = dlg.GetPath()
            #self.fileLabel.SetLabel("Open: " + os.getcwd() + os.path.sep + dlg.GetFilename())
            #self.digest = chomp(dlg.GetPath())
            #self.leftbox.Set(self.digest.getNames())
            self.locateConf(filename)

    def locateConf(self, path):
        self.config = path
        self.ConfPathLabel.SetLabel(path)
        try:
            self.panel.SendSizeEvent()
        except:
            print("wx.Panel.SendSizeEvent() missed - probably using old wxPython. Cosmetic bug will result.")


###########
# BACKEND #
###########

class OOMMFSelectiveTarget(wx.FileDropTarget):
    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent

    def OnDropFiles(self, x, y, filenames):
        #Find OOMMF, then a config, then files
        oommf = filterOnExtensions(["tcl"], filenames)
        if oommf:
            #What did you DO? Only the last one counts!
            self.parent.locateOOMMF(oommf[-1])
        config = filterOnExtensions(["conf", "config", "cnf"], filenames)
        if config:
            #Again, only the last conf file dropped counts.
            self.parent.locateConf(config[-1])

        if not (self.parent.config and self.parent.OOMMFPath):
            return 0

        #Try to save a lot of work - only do magic if OMF-type files were dropped.
        targets = filterOnExtensions(["omf","ovf","oef","ohf"], filenames)
        if not targets: return 0

        #Save more work by verifying that the user actually wants to make some sort of thing.
        if not self.parent.doImages.GetValue() and not self.parent.doMovie.GetValue():
            #Er... you don't want to do anything?
            return 0

        #Convince user that everything is OK, and provide me with entertainment.
        #Set up a dialog box that will track progress.

        dial = self.initializeProgressBar(targets)

        #To avoid some Py2EXE funkiness, we may need to redirect stdin.
        #Figure out where it needs to go, and catch that.

        childstd = self.findStandardIn()

        #We are now in the danger zone where the progress bar can get locked, and we
        #are going to shield that with some top-level exception handling

        try:

            dial.workDone(SETUP_LOAD, "Checking for Movies")


            #The first thing to do is try to make movies - in some cases, this process will leave behind
            #the images we need, and we can skip the image step entirely.

            print("Entering movie mode.")
            if self.parent.doMovie.GetValue():
                #Make some movies. This also hands off the progressDialog, so it can be updated.
                self.doMovies(targets, childstd, dial)
                #Finish making some movies.
                dial.workDone(CLEANUP_LOAD, "Doing Images")

            #Awkward short-circuit - If you made movies and they have the same magnification as the images, you get to keep the images!
            if self.parent.doMovie.GetValue() and self.parent.movieMagnifierSpin.GetValue() == self.parent.magnifierSpin.GetValue():
                dial.finish()
                return 1

            if self.parent.doImages.GetValue():
                #Oh well, I guess you're stuck making images. Make them!
                self.doImages(targets, childstd, dial)


            dial.workDone(CLEANUP_LOAD, "All Done!")
        except Exception as e:
            wx.MessageBox('Unpacking error: ' + repr(e), "Error")
            print(e)
        finally:
            dial.finish()
            return 1


    def findStandardIn(self):
        #Py2EXE is bad. Failing to set this correctly can cause the packaged version to explode on failure to
        #correctly grab a handle to a shell-like thing, so we deflect that by redirecting stdin to a file, which will always be empty. "Oops."
        if PY2EXE_COMPENSATION:
            childstd = file('null_data', 'a') #Detection methods unreliable
            print("Enforced running windows - py2exe mode. Using dump file stdin.")
        elif hasattr(sys.stdin, 'fileno'):
            childstd = sys.stdin
            print("Using standard stdin")
        elif hasattr(sys.stdin, '_file') and hasattr(sys.stdin._file, 'fileno'):
            childstd = sys.stdin._file
            print("Using hacked stdin adjustment - probably running Windows.")
        else:
            childstderr = file('null_data', 'a')
            print("Definitely using Windows. Using fake stdin.")
        return childstd

    def initializeProgressBar(self, targetList):
        #Cost of setup
        workload = SETUP_LOAD
        #Cost of a single avf2ppm render
        workload += RENDER_LOAD * len(targetList)
        workload += CLEANUP_LOAD
        if self.parent.doMovie.GetValue():
            #Cost of making a movie with ffmpeg; may add cleanup
            workload += MOVIE_LOAD
            if self.parent.doImages.GetValue() and not self.parent.movieMagnifierSpin.GetValue() == self.parent.magnifierSpin.GetValue():
                #Surprise! You get to rerender at a different magnification!
                workload += RENDER_LOAD * len(targetList) + CLEANUP_LOAD #And cleanup
            #Cost of frameduping
            workload += FRAMEDUPE_LOAD * (int(old_div(25, self.parent.movieFPS.GetValue())) * len(targetList))

        dial = SupportDialog("Render In Progress", "", maximum=workload,parent=self.parent)
        dial.Update(0, "This is a suitably long message to ensure the window title renders correctly") #Because this class lacks a size control!
        dial.Fit()
        dial.Update(0, "Initializing Render")
        dial.CenterOnParent()
        return dial

   
    def doImages(self, targetList, stdinRedirect, dial):
        dial.workDone(0, "Rendering")
        imageConfig = {'magnifierSpin': self.parent.magnifierSpin.GetValue(),
                       'autoMaxVectors': self.parent.autoMaxVectors.GetValue(),
                       'config': self.parent.config}
        oommfconvert.doImages(targetList, stdinRedirect, imageConfig, self.parent.TclCall.GetValue(), self.parent.OOMMFPath)
        dial.workDone(RENDER_LOAD, "Rendering")
        dial.workDone(0, "Cleaning Up")

    def doMovies(self, targetList, stdinRedirect, dial):
        print('in the movie function (not core)')
        dial.workDone(0, "Rendering")
        imageConfig = {'magnifierSpin': self.parent.magnifierSpin.GetValue(),
                       'autoMaxVectors': self.parent.autoMaxVectors.GetValue(),
                       'config': self.parent.config}
        oommfconvert.doMovies(targetList, stdinRedirect, imageConfig,self.parent.movieCodec.GetValue(), self.parent.movieFPS.GetValue(), self.parent.TclCall.GetValue(), self.parent.OOMMFPath, self.parent.doImages.GetValue(), CODECS)
        dial.workDone(0, "Rendering Movie")
        dial.workDone(MOVIE_LOAD, "Cleaning")
        return None


class SupportDialog(wx.ProgressDialog):
    def __init__(self, title, message, **kwargs):
        wx.ProgressDialog.__init__(self, title, message, **kwargs)
        self._workDone = 0
        self.workmax = kwargs["maximum"]

    def workDone(self, delta, newmsg):
        self._workDone += delta
        self.Update(self._workDone, newmsg)

    def finish(self):
        self.Update(self.workmax, "Done!")
        self.Destroy()
########
# MAIN #
########
if __name__ == "__main__":
	BigBoss = MainFrame()
	app.MainLoop()
