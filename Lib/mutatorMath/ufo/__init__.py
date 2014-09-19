""" These are some UFO specific tools for use with Mutator. """

def build(
		documentPath,
		outputUFOFormatVersion=2,
		roundGeometry=True,
		verbose=True,
		logPath=None):
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
		        roundGeometry=True,
		        verbose=verbose,
		        logPath=logPath)
		reader.process()
		results.append(reader.results)
	return results

