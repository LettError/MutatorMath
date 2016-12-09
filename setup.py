#!/usr/bin/env python

from setuptools import setup


with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name="MutatorMath",
    version="2.0.0",
    description=("Python for piecewise linear interpolation in multiple "
                 "dimensions with multiple, arbitrarily placed, masters."),
    long_description=long_description,
    author="Erik van Blokland",
    author_email="erik@letterror.com",
    url="https://github.com/LettError/MutatorMath",
    license="BSD 3 Clause",
    packages=[
        "mutatorMath",
        "mutatorMath.objects",
        "mutatorMath.ufo",
    ],
    package_dir={"": "Lib"},
    install_requires=[
        "ufoLib>=2.0.0",
        "defcon>=0.2.0",
        "fontMath>=0.4.1",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
