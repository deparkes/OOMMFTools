import wx

from user_interfaces.gui import odtchomp, oommfconvert, oommfdecode
import _about as about

__version__ = about.__version__
VERSION = about.__version__
NAME = about.__title__
LICENSE = about.__license__
COPYRIGHT = about.__copyright__
WEBSITE = about.__uri__
DESC = about.__summary__

def gui_main():
    APP = wx.App(None)
    q = MainFrame()
    APP.MainLoop()


class MainFrame(wx.Frame):
    """The main oommftools window.

    Creates main window with buttons to open the oommftools sub-
    tools.

    """
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "OOMMFTools", size=(400, 200))

        self.oommfconvert = None
        self.oommfdecode = None
        self.odtchomp = None

        #A very simple menubar
        menubar = wx.MenuBar()
        about = wx.Menu()
        about.Append(999, 'About', 'Program information and license')
        menubar.Append(about, "About")
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.showAbout, id=999)

        panel = wx.Panel(self, -1)
        self.panel = panel

        mainsizer = wx.FlexGridSizer(3, 2, 8, 12)

        mainsizer.Add(wx.Button(panel, 10, "OOMMFDecode"),
                      0, wx.EXPAND | wx.ALIGN_CENTER | wx.TOP | wx.LEFT, 20)
        mainsizer.Add(wx.StaticText(panel, -1,
                                    "Create numpy and MATLAB data"),
                      1, wx.ALIGN_CENTER_VERTICAL | wx.TOP, 20)
        self.Bind(wx.EVT_BUTTON, self.makeDecode, id=10)

        mainsizer.Add(wx.Button(panel, 20, "OOMMFConvert"),
                      0, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT, 20)
        mainsizer.Add(wx.StaticText(panel, -1,
                                    "Create bitmaps and movies"),
                      1, wx.ALIGN_CENTER_VERTICAL)
        self.Bind(wx.EVT_BUTTON, self.makeConvert, id=20)

        mainsizer.Add(wx.Button(panel, 30, "ODTChomp"),
                      0, wx.EXPAND | wx.ALIGN_CENTER | wx.BOTTOM | wx.LEFT, 20)
        mainsizer.Add(wx.StaticText(panel, -1,
                                    "Manage, reduce and convert ODT files"),
                      1, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, 20)
        self.Bind(wx.EVT_BUTTON, self.makeChomp, id=30)

        mainsizer.AddGrowableCol(1, 1)

        panel.SetSizer(mainsizer)
        panel.Fit()
        self.Center()
        self.Show(True)

    def makeDecode(self, evt):
        """Open oommfdecode window
        """
        if not self.oommfdecode:
            self.oommfdecode = oommfdecode.MainFrame(self)

    def makeConvert(self, evt):
        """Open oommfconvert window
        """
        if not self.oommfconvert:
            self.oommfconvert = oommfconvert.MainFrame(self)

    def makeChomp(self, evt):
        """Open odtchomp window.
        """
        if not self.odtchomp:
            self.odtchomp = odtchomp.MainFrame(self)

    def droppedWindow(self, window):
        """Not sure what this does. It's not called by main window.
        """
        if self.oommfdecode == window:
            self.oommfdecode = None
        elif self.oommfconvert == window:
            self.oommfconvert = None
        elif self.odtchomp == window:
            self.odtchomp = None

    def showAbout(self, evt):
        """Show 'About' information
        """
        info = wx.adv.AboutDialogInfo()
        mydesc = (DESC)
        mylicense = (LICENSE)
        info.SetName((NAME))
        info.SetVersion((VERSION))
        info.SetDescription('\n'.join(mydesc))
        info.SetLicense('\n'.join(mylicense))
        info.SetCopyright((COPYRIGHT))
        info.SetWebSite(WEBSITE)
        wx.adv.AboutBox(info)