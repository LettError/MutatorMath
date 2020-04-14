#!/usr/bin/env python

import sys
from setuptools import setup, Command, find_packages
from distutils import log
import contextlib


@contextlib.contextmanager
def capture_logger(name):
    """ Context manager to capture a logger output with a StringIO stream.
    """
    import logging

    logger = logging.getLogger(name)
    try:
        import StringIO
        stream = StringIO.StringIO()
    except ImportError:
        from io import StringIO
        stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    try:
        yield stream
    finally:
        logger.removeHandler(handler)


class bump_version(Command):

    description = "increment the package version and commit the changes"

    user_options = [
        ("major", None, "bump the first digit, for incompatible API changes"),
        ("minor", None, "bump the second digit, for new backward-compatible features"),
        ("patch", None, "bump the third digit, for bug fixes (default)"),
    ]

    def initialize_options(self):
        self.minor = False
        self.major = False
        self.patch = False

    def finalize_options(self):
        part = None
        for attr in ("major", "minor", "patch"):
            if getattr(self, attr, False):
                if part is None:
                    part = attr
                else:
                    from distutils.errors import DistutilsOptionError
                    raise DistutilsOptionError(
                        "version part options are mutually exclusive")
        self.part = part or "patch"

    def bumpversion(self, part, commit=True, tag=False, message=None,
                    allow_dirty=False):
        """ Run bumpversion.main() with the specified arguments, and return the
        new computed version string.
        """
        import bumpversion

        args = (
            (['--verbose'] if self.verbose > 1 else []) +
            (['--allow-dirty'] if allow_dirty else []) +
            (['--commit'] if commit else ['--no-commit']) +
            (['--tag'] if tag else ['--no-tag']) +
            (['--message', message] if message is not None else []) +
            ['--list', part]
        )
        log.debug(
            "$ bumpversion %s" % " ".join(a.replace(" ", "\\ ") for a in args))

        with capture_logger("bumpversion.list") as out:
            bumpversion.main(args)

        last_line = out.getvalue().splitlines()[-1]
        new_version = last_line.replace("new_version=", "")
        return new_version

    def run(self):
        log.info("bumping '%s' version" % self.part)
        self.bumpversion(self.part)


class release(bump_version):
    """Drop the developmental release '.devN' suffix from the package version,
    open the default text $EDITOR to write release notes, commit the changes
    and generate a git tag.

    Release notes can also be set with the -m/--message option, or by reading
    from standard input.

    If --major, --minor or --patch options are passed, the respective
    'SemVer' digit is also incremented before tagging the release.
    """

    description = "tag a new release"

    user_options = bump_version.user_options + [
        ("message=", 'm', "message containing the release notes"),
    ]

    def initialize_options(self):
        bump_version.initialize_options(self)
        self.message = None

    def finalize_options(self):
        bump_version.finalize_options(self)

        self.bump_first = any(
            getattr(self, a, False) for a in ("major", "minor", "patch"))
        if not self.bump_first:
            import re
            current_version = self.distribution.metadata.get_version()
            if not re.search(r"\.dev[0-9]+", current_version):
                from distutils.errors import DistutilsSetupError
                raise DistutilsSetupError(
                    "current version (%s) has no '.devN' suffix.\n       "
                    "Run 'setup.py bump_version', or use any of "
                    "--major, --minor, --patch options" % current_version)

        message = self.message
        if message is None:
            if sys.stdin.isatty():
                # stdin is interactive, use editor to write release notes
                message = self.edit_release_notes()
            else:
                # read release notes from stdin pipe
                message = sys.stdin.read()

        if not message.strip():
            from distutils.errors import DistutilsSetupError
            raise DistutilsSetupError("release notes message is empty")

        self.message = "Release {new_version}\n\n%s" % (message)

    @staticmethod
    def edit_release_notes():
        """Use the default text $EDITOR to write release notes.
        If $EDITOR is not set, use 'nano'."""
        from tempfile import mkstemp
        import os
        import shlex
        import subprocess

        text_editor = shlex.split(os.environ.get('EDITOR', 'nano'))

        fd, tmp = mkstemp(prefix='bumpversion-')
        try:
            os.close(fd)
            with open(tmp, 'w') as f:
                f.write("\n\n# Write release notes.\n"
                        "# Lines starting with '#' will be ignored.")
            subprocess.check_call(text_editor + [tmp])
            with open(tmp, 'r') as f:
                changes = "".join(
                    l for l in f.readlines() if not l.startswith('#'))
        finally:
            os.remove(tmp)
        return changes

    def run(self):
        if self.bump_first:
            # bump the specified version part but don't commit immediately
            log.info("bumping '%s' version" % self.part)
            self.bumpversion(self.part, commit=False)
            dirty=True
        else:
            dirty=False
        log.info("stripping developmental release suffix")
        # drop '.dev0' suffix, commit with given message and create git tag
        self.bumpversion(
            "release", tag=True,  message=self.message, allow_dirty=dirty)


with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name="MutatorMath",
    version="3.0.1",
    description=("Python for piecewise linear interpolation in multiple "
                 "dimensions with multiple, arbitrarily placed, masters."),
    long_description=long_description,
    author="Erik van Blokland",
    author_email="erik@letterror.com",
    url="https://github.com/LettError/MutatorMath",
    license="BSD 3 Clause",
    packages=find_packages("Lib", exclude=['*.test', '*.test.*']),
    package_dir={"": "Lib"},
    setup_requires=[
        'bumpversion',
    ] if {'release', 'bump_version'}.intersection(sys.argv) else [],
    install_requires=[
        "fonttools>=3.32.0",
        "defcon>=0.3.5",
        "fontMath>=0.4.8",
    ],
    cmdclass={
        "release": release,
        "bump_version": bump_version,
    },
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
    test_suite="mutatorMath.test.run",
)
