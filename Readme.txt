OOMMFTools
Summary...

Current features...
Replicate OOMMFTools, but with command line versions. Good for 
Planned features...

Current issues...
Limited use of imagemagick, could be better automated
Make it so that the different programs/components work in more or less the 
same way.
Requires editing of the individual files

Requirements:
- Python (2.7) [All]
- wxPython (Unicode) [GUI Programs]
- ...
- numpy [OOMMFDecode]
- scipy [OOMMFDecode]
- FFmpeg [OOMMFConvert, bmp2avi]
- OOMMF [OOMMFConvert, avf2bmp]
- Tcl/Tk [OOMMFConvert, avf2bmp]
Imagemagick (for making videos, converting and labelling images)

Installation/setup
1. Download OOMMFTools Release 2.0 from github
2. Add OOMMFTools directory to system path (How?)
3. a) Set correct path to OOMMF in avf2bmp.py and oommf.bat
   b) Set correct path to tcl in avf2bmp.py and oommf.bat
   (These scripts need to call oommf in order to work, so need to know where
	oommf can be found and how to run it (with tcl).)

Usage:
The general way to operate is to run the scripts from the target directory.
Possible ways of doing this include:
	- run 'cmd' and navigate to the target directory
	- find the target directory in windows explorer, right clight and 
		"open command window here"
	- open the target directory, click in the address bar and type 'cmd'.
From this command line run the relevant command.