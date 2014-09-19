# -*- coding: utf-8 -*-

""" 
    Mutator Error
"""

class MutatorError(Exception):
    def __init__(self, msg, obj=None):
        self.msg = msg
        self.obj = obj
    def __str__(self):
        return repr(self.msg) + repr(self.obj)
