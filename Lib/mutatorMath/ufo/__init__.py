
""" These are some UFO specific tools for use with Mutator.


	build() is a convenience function for reading and executing a designspace file.
		documentPath: 				filepath to the .designspace document
		outputUFOFormatVersion:		ufo format for output
		verbose:					True / False for lots or no feedback
		logPath:					filepath to a log file
		progressFunc:				an optional callback to report progress.
									see mutatorMath.ufo.tokenProgressFunc

"""


def tokenProgressFunc(state="update", action=None, text=None, tick=0):
	"""
		state: 		string, "update", "reading sources", "wrapping up"
		action:		string, "stop", "start"
		text:		string, value, additional parameter. For instance ufoname.
		tick:		a float between 0 and 1 indicating progress.
	"""
	print("tokenProgressFunc %s: %s\n%s (%s)"%(state, str(action), str(text), str(tick)))

def build(
		documentPath,
		outputUFOFormatVersion=2,
		roundGeometry=True,
		verbose=True,
		logPath=None,
		progressFunc=None,
		):
	"""

		Simple builder for UFO designspaces.

	"""
	from mutatorMath.ufo.document import DesignSpaceDocumentReader
	import os, glob
	if os.path.isdir(documentPath):
		# process all *.designspace documents in this folder
		todo = glob.glob(os.path.join(documentPath, "*.designspace"))
	else:
		# process the 
		todo = [documentPath]
	results = []
	for path in todo:
		reader = DesignSpaceDocumentReader(
				path,
		        ufoVersion=outputUFOFormatVersion,
		        roundGeometry=roundGeometry,
		        verbose=verbose,
		        logPath=logPath,
				progressFunc=progressFunc
		        )
		reader.process()
		results.append(reader.results)
	reader = None
	return results

