#!/usr/bin/env python

from setuptools import setup

setup(name = "MutatorMath",
      version = "1.8",
      description = "Python for piecewise linear interpolation in multiple dimensions with multiple, arbitrarily placed, masters.",
      author = "Erik van Blokland",
      author_email = "erik@letterror.com",
      url = "https://github.com/LettError/MutatorMath",
      license = "BSD 3 Clause",
      packages = [
              "mutatorMath",
              "mutatorMath.objects",
              "mutatorMath.ufo",
      ],
      package_dir = {"":"Lib"},
)
