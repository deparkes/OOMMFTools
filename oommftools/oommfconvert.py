
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

from wx import adv
import wx, os, sys, subprocess, shutil, tempfile, math, re, time, imp
from fnameutil import filterOnExtensions
from oommfdecode import slowlyPainfullyMaximize

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
    print "Py2EXE detected. Will perform defensive stdin redirection."

############
# GUI BODY #
############

class MainFrame(wx.Frame):
    def __init__(self, manager=None):
        wx.Frame.__init__(self, manager, -1, "OOMMF Bitmap/Movie Converter 0.8", size=(700,700))

        BigFont = wx.Font(16, wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_BOLD)
        TinyFont = wx.Font(8, wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)

        self.dt = OOMMFSelectiveTarget(self)
        self.SetDropTarget(self.dt)
        self.config = None
        self.manager = manager
        self.Bind(wx.EVT_CLOSE, self.onClose)

        #Check if we have a saved OOMMF path to use as config data
        if os.path.exists("." + os.path.sep + "oommf.path"):
            f = open("." + os.path.sep + "oommf.path")
            lines = f.readlines()
            f.close()
            path = lines[-1].strip()
            #But we also have to validate the path on this particular computer
            if os.path.exists(path) and path.rsplit(".")[-1] == "tcl":
                self.OOMMFPath = path
            else:
                self.OOMMFPath = None
                #Cleanup bogus config file
                os.remove("." + os.path.sep + "oommf.path")
        else:
            #No file at all!
            self.OOMMFPath = None

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

        self.movieCodec = wx.ComboBox(panel, 200, choices = CODECS.keys(), style=wx.CB_READONLY)
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
        mydesc = """OOMMFConvert is an OOMMF postprocessing tool for
generating bitmap and movie files from OMF files
using a simple drag-and-drop interface.
It uses OOMMF's own avf2ppm utility
and employs FFmpeg to link images.
\nOOMMFConvert is part of OOMMFTools."""
        mylicense = """OOMMFConvert is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version."""
        info.SetName("OOMMF Bitmap/Movie Converter")
        info.SetVersion("0.8")
        info.SetDescription(mydesc)
        info.SetLicense(mylicense)
        info.SetCopyright('(C) 2010 Mark Mascaro')
        info.SetWebSite('http://web.mit.edu/daigohji/projects/OOMMFTools/')
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
            print "wx.Panel.SendSizeEvent() missed - probably using old wxPython. Cosmetic bug will result."

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
            print "wx.Panel.SendSizeEvent() missed - probably using old wxPython. Cosmetic bug will result."


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

            print "Entering movie mode."
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
            print e
        finally:
            dial.finish()
            return 1


    def findStandardIn(self):
        #Py2EXE is bad. Failing to set this correctly can cause the packaged version to explode on failure to
        #correctly grab a handle to a shell-like thing, so we deflect that by redirecting stdin to a file, which will always be empty. "Oops."
        if PY2EXE_COMPENSATION:
            childstd = file('null_data', 'a') #Detection methods unreliable
            print "Enforced running windows - py2exe mode. Using dump file stdin."
        elif hasattr(sys.stdin, 'fileno'):
            childstd = sys.stdin
            print "Using standard stdin"
        elif hasattr(sys.stdin, '_file') and hasattr(sys.stdin._file, 'fileno'):
            childstd = sys.stdin._file
            print "Using hacked stdin adjustment - probably running Windows."
        else:
            childstderr = file('null_data', 'a')
            print "Definitely using Windows. Using fake stdin."
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
            workload += FRAMEDUPE_LOAD * (int(25 / self.parent.movieFPS.GetValue()) * len(targetList))

        dial = SupportDialog("Render In Progress", "", maximum=workload,parent=self.parent)
        dial.Update(0, "This is a suitably long message to ensure the window title renders correctly") #Because this class lacks a size control!
        dial.Fit()
        dial.Update(0, "Initializing Render")
        dial.CenterOnParent()
        return dial

    def spliceConfig(self, percentMagnitude, checkVectors = False, filenames = []):
        print checkVectors
        #Rewrite the file
        oldconf = open(self.parent.config, "r")
        oldconflines = oldconf.readlines()
        oldconf.close()
        print "Getting temporary file handle for modconfig."
        oshandle, newconfdir = tempfile.mkstemp(suffix=".tmp", dir=".")
        try:
            os.close(oshandle)
        except:
            print "Error: Windows failed all over closing the file handle."
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

    def resolveConfiguration(self, filenames):
        if self.parent.magnifierSpin.GetValue() != 100 or self.parent.autoMaxVectors.GetValue():
            confpath = self.spliceConfig(self.parent.magnifierSpin.GetValue(), self.parent.autoMaxVectors.GetValue(), filenames)
            cleanconfig = True
        else:
            cleanconfig = False
            confpath = self.parent.config
        return (confpath, cleanconfig)

    def doImages(self, targetList, stdinRedirect, dial):
        confpath, cleanconfig = self.resolveConfiguration(targetList)

        dial.workDone(0, "Rendering")
        for i, omf in enumerate(sorted(targetList)):
            pathTo, fname = omf.rsplit(os.path.sep, 1)
            command = self.parent.TclCall.GetValue() + ' "' + self.parent.OOMMFPath + '" avf2ppm -f -v 2 -format b24 -config "' + confpath + '" "' + omf + '"'
            if os.name == 'nt':
                print "Watching stdin redirect:", stdinRedirect
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
                        for line in a: print line.strip()
            else:
                print "probably posix mode."
                if MODE == "basic":
                    os.system(command)
                elif MODE == "advanced":
                    pipe = subprocess.Popen(command, shell=True, stdin = sys.stdin, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
                    a = pipe.readlines()
                    #THIS should at least use STDout
                    if a:
                        for line in a: print line.strip()

            dial.workDone(RENDER_LOAD, "Rendering")

        #Clean up temporaries
        dial.workDone(0, "Cleaning Up")
        if cleanconfig:
            try:
                os.remove(confpath)
            except:
                print "Uh, failed to let conf go for some reason... you should probably tell doublemark@mit.edu"

    def doMovies(self, targetList, stdinRedirect, dial):
        #Make temporary directory
        moviepath = tempfile.mkdtemp()
        print "Temporary directory obtained."
        #Identify filename length, and perform AWFUL HACK to sidestep ffmpeg restrictions
        framedupes = int(25 / self.parent.movieFPS.GetValue())
        maxdigits = int(math.ceil(math.log10(len(targetList) * framedupes)))

        #Deal with overload-options by writing a temporary configuration file
        confpath, cleanconfig = self.resolveConfiguration(targetList)

        dial.workDone(0, "Rendering")
        for i, omf in enumerate(sorted(targetList)):
            frameRepeatOffset = 0
            pathTo, fname = omf.rsplit(os.path.sep, 1)
            command = self.parent.TclCall.GetValue() + ' "' + self.parent.OOMMFPath + '" avf2ppm -f -v 2 -format b24 -config "' + confpath + '" "' + omf + '"'
            if os.name == 'nt':
                if MODE == "basic":
                    os.system(command)
                elif MODE == "advanced":
                    if not r":\\" in omf:
                        #Non-networked
                        pipe = subprocess.Popen(command, shell=True, stdin = stdinRedirect, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
                    else:
                        #Avoid network stupidity.
                        pipe = subprocess.Popen(command, shell=False, stdin = stdinRedirect, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
                    a = pipe.readlines()
                    #*Really*? It's not using stdout?
                    if a:
                        for line in a: print line.strip()
            else:
                if MODE == "basic":
                    os.system(command)
                elif MODE == "advanced":
                    pipe = subprocess.Popen(command, shell=True, stdin = sys.stdin, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
                    a = pipe.readlines()
                    #*Really*? It's not using stdout?
                    if a:
                        for line in a: print line.strip()
            dial.workDone(RENDER_LOAD, "Frame Duplicating")

            #Copy and duplicate image, placing files in the movie temp directory
            fname = omf.rsplit(".",1)[0] + ".bmp"
            for j in range(framedupes):
                shutil.copy(fname, moviepath+os.path.sep +str(framedupes*i + j).rjust(maxdigits,"0") +".bmp")
                j += 1
                dial.workDone(FRAMEDUPE_LOAD, "Frame Duplicating")
            dial.workDone(0, "Rendering")

            #Housecleaning - if not making images, you should clean this up.
            if not self.parent.doImages.GetValue():
                os.remove(fname)

        #Finally, make the actual movie!
        #You know, we should steal the last pathto as a place to put the movie, and perhaps also the basename
        #This is bad use of scoping blah blah
        fname = moviepath+os.path.sep +str(framedupes*i + j).rjust(maxdigits,"0") +".bmp"
        try:
            basename = fname.rsplit("-",2)[-3]
        except:
            basename = fname
        print(CODECS[self.parent.movieCodec.GetValue()])
        outname = "["+CODECS[self.parent.movieCodec.GetValue()][2]+"]"+ CODECS[self.parent.movieCodec.GetValue()][1]
        print(outname)
        print('pathTo' + pathTo)
        command = r'ffmpeg -f image2 -an -y -i ' + moviepath + os.path.sep + r'%0' + str(maxdigits) + r'd.bmp ' + CODECS[self.parent.movieCodec.GetValue()][0]
        command += ' "' + os.path.join(pathTo, outname) + '"'
        print(command)
        dial.workDone(0, "Rendering Movie")
        print "Movie render mode prepared."

        if os.name == 'nt':
            if MODE == "basic":
                os.system(command)
            elif MODE == "advanced":
                if not r":\\" in omf:
                    pipe = subprocess.Popen(command, shell=True, stdin = stdinRedirect, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
                else:
                    #Avoid network stupidity.
                    pipe = subprocess.Popen(command, shell=False, stdin = stdinRedirect, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
        else:
            if MODE == "basic":
                os.system(command)
            elif MODE == "advanced":
                pipe = subprocess.Popen(command, shell=True, stdin = sys.stdin, stdout=subprocess.PIPE,  stderr=subprocess.STDOUT).stdout
        a = pipe.readlines()
        #THIS should at least use STDout
        if a:
            for line in a: print line.strip()

        dial.workDone(MOVIE_LOAD, "Cleaning")
        #Clean up temporaries
        shutil.rmtree(moviepath)
        if cleanconfig:
            try:
                os.remove(confpath)
            except:
                print "Can't let go for some reason... you should probably tell doublemark@mit.edu"
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
