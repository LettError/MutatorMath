# -*- coding: utf-8 -*-

""" 

	Example of a build script for a specific mutatorMath project.
	A script like this could live near the designspace description.
	It could be called to build a bunch of instances without opening any application. 

"""
from mutatorMath.ufo import build
import os
here = os.path.join(os.getcwd(), 'data')
build(here, outputUFOFormatVersion=2)
print('done')
  