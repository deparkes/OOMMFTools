def filterOnExtensions(extensions, inlist):
	worklist = []
	#Sadly, it's not possible to use filter itself here without a nasty eval setup. No thanks!
	for item in inlist:
		if item.rsplit(".",1)[-1] in extensions:
			worklist.append(item)
	return worklist
