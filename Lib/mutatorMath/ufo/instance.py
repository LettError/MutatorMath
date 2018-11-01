# -*- coding: utf-8 -*-

from mutatorMath.objects.error import MutatorError
from mutatorMath.objects.mutator import Mutator, buildMutator
from mutatorMath.objects.bender import Bender, noBend

from fontTools.ufoLib import (
    fontInfoAttributesVersion1,
    fontInfoAttributesVersion2,
    fontInfoAttributesVersion3,
)

import warnings, logging

import fontMath

from fontMath.mathKerning import MathKerning
from fontMath.mathInfo import MathInfo
from fontMath.mathGlyph import MathGlyph

import defcon
import os

class InstanceWriter(object):
    """ 
            Simple object to build a UFO instance.
            Collect the data needed for an instance
            and generate it as fast as possible.

            Make a font object.
            Add data straight to the font.
            Calculate the data immediately, while reading the document.
            Don't edit the data.
            Don't represent the data.
    """
    _fontClass = defcon.objects.font.Font
    _tempFontLibGlyphMuteKey = "_mutatorMath.temp.mutedGlyphNames"
    
    def __init__(self, path, ufoVersion=1,
            roundGeometry=False,
            axes=None,
            verbose=False,
            logger=None):
        self.path = path
        self.font = self._fontClass()
        self.ufoVersion = ufoVersion
        self.roundGeometry = roundGeometry
        if axes is not None:
            self.axes = axes
        else:
            self.axes = {}
        self.sources = {} 
        self.muted = dict(kerning=[], info=[], glyphs={})   # muted data in the masters
        self.mutedGlyphsNames = []                          # muted glyphs in the instance
        self.familyName = None
        self.styleName = None
        self.postScriptFontName = None
        self.locationObject = None
        self.unicodeValues = {}
        self.verbose=verbose
        self.logger = None
        if self.verbose:
            self.logger = logging.getLogger("mutatorMath")

        self._failed = []            # list of glyphnames we could not generate
        self._missingUnicodes = []   # list of glyphnames with missing unicode values
            
    def setSources(self, sources):
        """ Set a list of sources."""
        self.sources = sources

    def setMuted(self, muted):
        """ Set the mute states. """
        self.muted.update(muted)

    def muteGlyph(self, glyphName):
        """ Mute the generating of this specific glyph. """
        self.mutedGlyphsNames.append(glyphName)
    
    def setGroups(self, groups, kerningGroupConversionRenameMaps=None):
        """ Copy the groups into our font. """
        skipping = []
        for name, members in groups.items():
            checked = []
            for m in members:
                if m in self.font:
                    checked.append(m)
                else:
                    skipping.append(m)
            if checked:
                self.font.groups[name] = checked
        if skipping:
            if self.verbose and self.logger:
                self.logger.info("\tNote: some glyphnames were removed from groups: %s (unavailable in the font)", ", ".join(skipping))
        if kerningGroupConversionRenameMaps:
            # in case the sources were UFO2, 
            # and defcon upconverted them to UFO3
            # and now we have to down convert them again,
            # we don't want the UFO3 public prefixes in the group names
            self.font.kerningGroupConversionRenameMaps = kerningGroupConversionRenameMaps

    def getFailed(self):
        """ Return the list of glyphnames that failed to generate."""
        return self._failed

    def getMissingUnicodes(self):
        """ Return the list of glyphnames with missing unicode values. """
        return self._missingUnicodes

    def setLib(self, lib):
        """ Copy the lib items into our font. """
        for name, item in lib.items():
            self.font.lib[name] = item

    def setPostScriptFontName(self, name):
        """ Set the postScriptFontName. """
        self.font.info.postscriptFontName = name

    def setStyleMapFamilyName(self, name):
        """ Set the stylemap FamilyName. """
        self.font.info.styleMapFamilyName = name

    def setStyleMapStyleName(self, name):
        """ Set the stylemap StyleName. """
        self.font.info.styleMapStyleName = name

    def setStyleName(self, name):
        """ Set the styleName. """
        self.font.info.styleName = name
    
    def setFamilyName(self, name):
        """ Set the familyName"""
        self.font.info.familyName = name

    def copyFeatures(self, featureSource):
        """ Copy the features from this source """
        if featureSource in self.sources:
            src, loc = self.sources[featureSource]
            if isinstance(src.features.text, str):
                self.font.features.text = u""+src.features.text
            elif isinstance(src.features.text, unicode):
                self.font.features.text = src.features.text

    def makeUnicodeMapFromSources(self):
        """ Create a dict with glyphName -> unicode value pairs
            using the data in the sources. 
            If all master glyphs have the same unicode value
            this value will be used in the map.
            If master glyphs have conflicting value, a warning will be printed, no value will be used.
            If only a single master has a value, that value will be used.
        """
        values = {}
        for locationName, (source, loc) in self.sources.items():
            # this will be expensive in large fonts
            for glyph in source:
                if glyph.unicodes is not None:
                    if glyph.name not in values:
                        values[glyph.name] = {}
                for u in glyph.unicodes:
                    values[glyph.name][u] = 1
        for name, u in values.items():
            if len(u) == 0:
                # only report missing unicodes if the name has no extension
                if "." not in name:
                    self._missingUnicodes.append(name)
                continue
            k = list(u.keys())
            self.unicodeValues[name] = k
        return self.unicodeValues
                
    def getAvailableGlyphnames(self):
        """ Return a list of all glyphnames we have masters for."""
        glyphNames = {}
        for locationName, (source, loc) in self.sources.items():
            for glyph in source:
                glyphNames[glyph.name] = 1
        names = sorted(glyphNames.keys())
        return names
    
    def setLocation(self, locationObject):
        """ Set the location directly. """
        self.locationObject = locationObject
    
    def addInfo(self, instanceLocation=None, sources=None, copySourceName=None):
        """ Add font info data. """
        if instanceLocation is None:
            instanceLocation = self.locationObject
        infoObject = self.font.info
        infoMasters = []
        if sources is None:
            sources = self.sources
        items = []
        for sourceName, (source, sourceLocation) in sources.items():
            if sourceName in self.muted['info']:
                # info in this master was muted, so do not add.
                continue
            items.append((sourceLocation, MathInfo(source.info)))
        try:
            bias, m = buildMutator(items, axes=self.axes)
        except:
            if self.logger:
                self.logger.exception("Error processing font info. %s", items)
            return
        instanceObject = m.makeInstance(instanceLocation)
        if self.roundGeometry:
            try:
                instanceObject = instanceObject.round()
            except AttributeError:
                warnings.warn("MathInfo object missing round() method.")
        instanceObject.extractInfo(self.font.info)

        # handle the copyable info fields
        if copySourceName is not None:
            if not copySourceName in sources:
                if self.verbose and self.logger:
                    self.logger.info("Copy info source %s not found, skipping.", copySourceName)
                    return
            copySourceObject, loc = sources[copySourceName]
            self._copyFontInfo(self.font.info, copySourceObject.info)

    def _copyFontInfo(self, targetInfo, sourceInfo):
        """ Copy the non-calculating fields from the source info.
        """
        infoAttributes = [
            "versionMajor",
            "versionMinor",
            "copyright",
            "trademark",
            "note",
            "openTypeGaspRangeRecords",
            "openTypeHeadCreated",
            "openTypeHeadFlags",
            "openTypeNameDesigner",
            "openTypeNameDesignerURL",
            "openTypeNameManufacturer",
            "openTypeNameManufacturerURL",
            "openTypeNameLicense",
            "openTypeNameLicenseURL",
            "openTypeNameVersion",
            "openTypeNameUniqueID",
            "openTypeNameDescription",
            "#openTypeNamePreferredFamilyName",
            "#openTypeNamePreferredSubfamilyName",
            "#openTypeNameCompatibleFullName",
            "openTypeNameSampleText",
            "openTypeNameWWSFamilyName",
            "openTypeNameWWSSubfamilyName",
            "openTypeNameRecords",
            "openTypeOS2Selection",
            "openTypeOS2VendorID",
            "openTypeOS2Panose",
            "openTypeOS2FamilyClass",
            "openTypeOS2UnicodeRanges",
            "openTypeOS2CodePageRanges",
            "openTypeOS2Type",
            "postscriptIsFixedPitch",
            "postscriptForceBold",
            "postscriptDefaultCharacter",
            "postscriptWindowsCharacterSet"
        ]
        for infoAttribute in infoAttributes:
            copy = False
            if self.ufoVersion == 1 and infoAttribute in fontInfoAttributesVersion1:
                copy = True
            elif self.ufoVersion == 2 and infoAttribute in fontInfoAttributesVersion2:
                copy = True
            elif self.ufoVersion == 3 and infoAttribute in fontInfoAttributesVersion3:
                copy = True
            if copy:
                value = getattr(sourceInfo, infoAttribute)
                setattr(targetInfo, infoAttribute, value)

    def addKerning(self, instanceLocation=None, sources=None):
        """
        Calculate the kerning data for this location and add it to this instance.
        
        *   instanceLocation:   Location object
        *   source: dict of {sourcename: (source, sourceLocation)}
        """
        items = []
        kerningObject = self.font.kerning
        kerningMasters = []
        if instanceLocation is None:
            instanceLocation = self.locationObject

        if sources is None:
            # kerning has no special requests, add the default sources
            sources = self.sources
        for sourceName, (source, sourceLocation) in sources.items():
            if sourceName in self.muted['kerning']:
                # kerning in this master was muted, so do not add.
                if self.verbose and self.logger:
                    self.logger.info("\tMuting kerning data for %s", instanceLocation)
                continue
            if len(source.kerning.keys())>0:
                items.append((sourceLocation, MathKerning(source.kerning, source.groups)))
        if items:
            m = None
            try:
                bias, m = buildMutator(items, axes=self.axes)
            except:
                if self.logger:
                    self.logger.exception("\tError processing kerning data. %s", items)
                return
            instanceObject = m.makeInstance(instanceLocation)
            if self.roundGeometry:
                instanceObject.round()
            instanceObject.extractKerning(self.font)
        
    def addGlyph(self, glyphName, unicodes=None, instanceLocation=None, sources=None, note=None):
        """
        Calculate a new glyph and add it to this instance.
        
        *   glyphName:   The name of the glyph
        *   unicodes:   The unicode values for this glyph (optional)
        *   instanceLocation:   Location for this glyph
        *   sources:    List of sources for this glyph.
        *   note:   Note for this glyph.
        """
        self.font.newGlyph(glyphName)
        glyphObject = self.font[glyphName]
        if note is not None:
            glyphObject.note = note
            # why does this not save?
        if unicodes is not None:
            glyphObject.unicodes = unicodes
        if instanceLocation is None:
            instanceLocation = self.locationObject
        glyphMasters = []
        if sources is None:
            # glyph has no special requests, add the default sources
            for sourceName, (source, sourceLocation) in self.sources.items():
                if glyphName in self.muted['glyphs'].get(sourceName, []):
                    # this glyph in this master was muted, so do not add.
                    continue
                d = dict(   font=source,
                            location=sourceLocation,
                            glyphName=glyphName)
                glyphMasters.append(d)
        else:
            # use the glyph sources provided
            # if self.verbose and self.logger:
            #     self.logger.info("\tGlyph %s has special masters %s", glyphName, sources)
            glyphMasters = sources
        # make the glyphs
        try:
            self._calculateGlyph(glyphObject, instanceLocation, glyphMasters)
        except:
            self._failed.append(glyphName)
    
    def _calculateGlyph(self, targetGlyphObject, instanceLocationObject, glyphMasters):
        """
        Build a Mutator object for this glyph.

        *   name:   glyphName
        *   location:   Location object
        *   glyphMasters:    dict with font objects.
        """
        sources = None
        items = []

        for item in glyphMasters:
            locationObject = item['location']
            fontObject = item['font']
            glyphName = item['glyphName']
            if not glyphName in fontObject:
                continue
            glyphObject = MathGlyph(fontObject[glyphName])
            items.append((locationObject, glyphObject))
        bias, m = buildMutator(items, axes=self.axes)
        instanceObject = m.makeInstance(instanceLocationObject)
        if self.roundGeometry:
            try:
                instanceObject = instanceObject.round()
            except AttributeError:
                if self.verbose and self.logger:
                    self.logger.info("MathGlyph object missing round() method.")


        try:
            instanceObject.extractGlyph(targetGlyphObject, onlyGeometry=True)
        except TypeError:
            # this causes ruled glyphs to end up in the wrong glyphname
            # but defcon2 objects don't support it
            pPen = targetGlyphObject.getPointPen()
            targetGlyphObject.clear()
            instanceObject.drawPoints(pPen)
            targetGlyphObject.width = instanceObject.width
    
    def save(self):
        """ Save the UFO."""

        # handle glyphs that were muted
        for name in self.mutedGlyphsNames:
            if name not in self.font: continue
            if self.logger:
                self.logger.info("removing muted glyph %s", name)
            del self.font[name]
            # XXX housekeeping:
            # remove glyph from groups / kerning as well?
            # remove components referencing this glyph?

        # fontTools.ufoLib no longer calls os.makedirs for us if the
        # parent directories of the Font we are saving do not exist.
        # We want to keep backward compatibility with the previous
        # MutatorMath behavior, so we create the instance' parent
        # directories if they do not exist. We assume that the users
        # knows what they are doing...
        directory = os.path.dirname(os.path.normpath(self.path))
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        try:
            self.font.save(os.path.abspath(self.path), self.ufoVersion)
        except defcon.DefconError as error:
            if self.logger:
                self.logger.exception("Error generating.")
            return False, error.report
        return True, None
        
