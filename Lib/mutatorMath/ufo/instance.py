# -*- coding: utf-8 -*-

from mutatorMath.objects.error import MutatorError
from mutatorMath.objects.mutator import Mutator, buildMutator

import warnings

from fontMath.mathKerning import MathKerning
from fontMath.mathInfo import MathInfo
from fontMath.mathGlyph import MathGlyph

from ufoLib.validators import kerningValidatorReportPairs

import defcon

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
            verbose=False,
            logger=None):
        self.path = path
        self.font = self._fontClass()
        self.ufoVersion = ufoVersion
        self.roundGeometry = roundGeometry
        self.sources = {} 
        self.muted = dict(kerning=[], info=[], glyphs={})
        self.familyName = None
        self.styleName = None
        self.postScriptFontName = None
        self.locationObject = None
        self.unicodeValues = {}
        self.verbose=verbose
        self.logger=logger
        self._failed = []            # list of glyphnames we could not generate
        self._missingUnicodes = []   # list of glyphnames with missing unicode values
            
    def setSources(self, sources):
        """ Set a list of sources."""
        self.sources = sources

    def setMuted(self, muted):
        """ Set the mute states. """
        self.muted = muted
    
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
                self.logger.info("Some glyphs were removed from groups: %s", ", ".join(skipping))
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
            if len(u) > 1:
                msg = u", ".join([str(v) for v in u.keys()])
                if self.verbose:
                    self.logger.info("\tMultiple unicode values for glyph %s: %s"%(name, msg))
                continue
            if len(u) == 0:
                self._missingUnicodes.append(name)
                continue
            k = u.keys()
            self.unicodeValues[name] = k[0]
        return self.unicodeValues
                
    def getAvailableGlyphnames(self):
        """ Return a list of all glyphnames we have masters for."""
        glyphNames = {}
        for locationName, (source, loc) in self.sources.items():
            for glyph in source:
                glyphNames[glyph.name] = 1
        names = glyphNames.keys()
        names.sort()
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
            bias, m = buildMutator(items)
        except:
            self.logger.exception("Error processing font info. %s", items)
            return
        instanceObject = m.makeInstance(instanceLocation)
        if self.roundGeometry:
            try:
                instanceObject = instanceObject.round()
            except AttributeError:
                warnings.warn("MathInfo object missing round() method.")
        else:
            self._roundSelectedFontInfo(instanceObject)
        instanceObject.extractInfo(self.font.info)

        # handle the copyable info fields
        if copySourceName is not None:
            if not copySourceName in sources:
                if self.verbose and self.logger:
                    self.logger.info("Copy info source %s not found, skipping.", copySourceName)
                    return
            copySourceObject, loc = sources[copySourceName]
            self._copyFontInfo(self.font.info, copySourceObject.info)

    def _roundSelectedFontInfo(self, fontInfo):
        """self.roundGeometry is false. However, most FontInfo fields have to be integer.
        Exceptions are:
            any of the PostScript Blue values.
            postscriptStemSnapH, postscriptStemSnapV, postscriptSlantAngle
        The Blue values should be rounded to 2 decimal places, with the exception
        of postscriptBlueScale.
        I round the float values because most Type1/Type2 rasterizers store
        point and stem coordinates as Fixed numbers with 8 bits. You end up
        cumulative rounding errors if you pass in relative values with more
        than 2 decimal places. Other FontInfo float values are stored as Fixed
        number with 16 bits,and can support 6 decimal places.
        """
        listType = type([])
        strType = type("")
        
        fiKeys = dir(fontInfo)
        for fieldName in fiKeys:
            if fieldName.startswith("_"):
                continue
            srcValue = getattr(fontInfo, fieldName)
            if type(srcValue) != listType:
                try:
                    realValue = float(srcValue)
                except (TypeError, ValueError):
                    continue
                intValue = int(realValue)
                if intValue == realValue:
                    continue
                
                if ("Blue" in fieldName) or (fieldName == "postscriptSlantAngle"):
                    if fieldName == "postscriptBlueScale":
                        # round to 6 places
                        rndValue = round(realValue*1000000)/1000000.0
                        if rndValue != realValue:
                            setattr(fontInfo, fieldName, rndValue)
                    else:
                        # round to 2 places
                        rndValue = round(realValue*100)/100.0
                        if rndValue != realValue:
                            setattr(fontInfo, fieldName, rndValue)
                else:
                    intValue = int(round(realValue))
                    setattr(fontInfo, fieldName, intValue)
                    
            elif ("Blue" in fieldName) or fieldName.startswith("postscriptStemSnap"):
                # It is a list.
                for i in range(len(srcValue)):
                    realValue = float(srcValue[i])
                    intVal = int(realValue)
                    if intValue == realValue:
                        continue
                    # round to 2 places
                    rndValue = round(realValue*100)/100.0
                    if rndValue != realValue:
                        srcValue[i] = rndValue

    def _copyFontInfo(self, targetInfo, sourceInfo):
        """ Copy the non-calculating fields from the source info.
            
            Based on UFO3 info attributes. 
            http://unifiedfontobject.org/versions/ufo3/fontinfo.html

            Not all of these fields might be present in UFO2 masters.
            Not all of these fields will export to UFO2 instances. 
        """
        targetInfo.versionMajor = sourceInfo.versionMajor
        targetInfo.versionMinor = sourceInfo.versionMinor
        targetInfo.copyright = sourceInfo.copyright
        targetInfo.trademark = sourceInfo.trademark
        targetInfo.note = sourceInfo.note
        targetInfo.openTypeGaspRangeRecords = sourceInfo.openTypeGaspRangeRecords
        #targetInfo.rangeMaxPPEM = sourceInfo.rangeMaxPPEM
        targetInfo.openTypeHeadCreated = sourceInfo.openTypeHeadCreated
        targetInfo.openTypeHeadFlags = sourceInfo.openTypeHeadFlags
        targetInfo.openTypeNameDesigner = sourceInfo.openTypeNameDesigner
        targetInfo.openTypeNameDesignerURL = sourceInfo.openTypeNameDesignerURL
        targetInfo.openTypeNameManufacturer = sourceInfo.openTypeNameManufacturer
        targetInfo.openTypeNameManufacturerURL = sourceInfo.openTypeNameManufacturerURL
        targetInfo.openTypeNameLicense = sourceInfo.openTypeNameLicense
        targetInfo.openTypeNameLicenseURL = sourceInfo.openTypeNameLicenseURL
        targetInfo.openTypeNameVersion = sourceInfo.openTypeNameVersion
        targetInfo.openTypeNameUniqueID = sourceInfo.openTypeNameUniqueID
        targetInfo.openTypeNameDescription = sourceInfo.openTypeNameDescription
        #targetInfo.openTypeNamePreferredFamilyName = sourceInfo.openTypeNamePreferredFamilyName
        #targetInfo.openTypeNamePreferredSubfamilyName = sourceInfo.openTypeNamePreferredSubfamilyName
        #targetInfo.openTypeNameCompatibleFullName = sourceInfo.openTypeNameCompatibleFullName
        targetInfo.openTypeNameSampleText = sourceInfo.openTypeNameSampleText
        targetInfo.openTypeNameWWSFamilyName = sourceInfo.openTypeNameWWSFamilyName
        targetInfo.openTypeNameWWSSubfamilyName = sourceInfo.openTypeNameWWSSubfamilyName
        targetInfo.openTypeNameRecords = sourceInfo.openTypeNameRecords
        targetInfo.openTypeOS2Selection = sourceInfo.openTypeOS2Selection
        targetInfo.openTypeOS2VendorID = sourceInfo.openTypeOS2VendorID
        targetInfo.openTypeOS2Panose = sourceInfo.openTypeOS2Panose
        targetInfo.openTypeOS2FamilyClass = sourceInfo.openTypeOS2FamilyClass
        targetInfo.openTypeOS2UnicodeRanges = sourceInfo.openTypeOS2UnicodeRanges
        targetInfo.openTypeOS2CodePageRanges = sourceInfo.openTypeOS2CodePageRanges
        targetInfo.openTypeOS2Type = sourceInfo.openTypeOS2Type
        
        #targetInfo.postscriptFontName = sourceInfo.postscriptFontName
        #targetInfo.postscriptFullName = sourceInfo.postscriptFullName
        targetInfo.postscriptIsFixedPitch = sourceInfo.postscriptIsFixedPitch
        targetInfo.postscriptForceBold = sourceInfo.postscriptForceBold
        targetInfo.postscriptDefaultCharacter = sourceInfo.postscriptDefaultCharacter
        targetInfo.postscriptWindowsCharacterSet = sourceInfo.postscriptWindowsCharacterSet
        
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
                    self.logger.info("Muting kerning data for %s", instanceLocation)
                continue
            if len(source.kerning.keys())>0:
                items.append((sourceLocation, MathKerning(source.kerning)))
        # items.sort()
        if items:
            m = None
            try:
                bias, m = buildMutator(items)
            except:
                self.logger.exception("Error processing kerning data. %s", items)
                return
            instanceObject = m.makeInstance(instanceLocation)
            instanceObject.round() # Kerning values must be integer, so we don't check self.roundGeometry
            instanceObject.extractKerning(self.font)
        
    def addGlyph(self, glyphName, unicodeValue=None, instanceLocation=None, sources=None, note=None):
        """
        Calculate a new glyph and add it to this instance.
        
        *   glyphName:   The name of the glyph
        *   unicodeValue:   The unicode value for this glyph (optional)
        *   instanceLocation:   Location for this glyph
        *   sources:    List of sources for this glyph.
        *   note:   Note for this glyph.
        """
        self.font.newGlyph(glyphName)
        glyphObject = self.font[glyphName]
        if note is not None:
            glyphObject.note = note
            # why does this not save?
        if unicodeValue is not None:
            glyphObject.unicode = unicodeValue
        if instanceLocation is None:
            instanceLocation = self.locationObject
        glyphMasters = []
        if sources is None:
            # glyph has no special requests, add the default sources
            #sources = self.sources
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
            if self.verbose and self.logger:
                self.logger.info("\tGlyph %s has special masters %s", glyphName, sources)
            glyphMasters = sources
        # make the glyphs
        try:
            self._calculateGlyph(glyphObject, instanceLocation, glyphMasters)
        except:
            self._failed.append(glyphName)
            if self.verbose and self.logger:
                self.logger.exception("\tGlyph %s failed", glyphName)
    
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
        bias, m = buildMutator(items)
        instanceObject = m.makeInstance(instanceLocationObject)
        if self.roundGeometry:
            try:
                instanceObject = instanceObject.round()
            except AttributeError:
                warnings.warn("MathGlyph object missing round() method.")
        else:
        	instanceObject.width = int(round(instanceObject.width)) # Width values must be integer.
        try:
            instanceObject.extractGlyph(targetGlyphObject, onlyGeometry=True)
        except TypeError:
            self.logger.info("MathGlyph object extractGlyph() does not support onlyGeometry attribute.")
            instanceObject.extractGlyph(targetGlyphObject)
    
    def validateKerning(self):
        " Make sure the kerning validates before saving. "
        self.logger.info("Validating kerning...")
        validates, errors, pairs = kerningValidatorReportPairs(self.font.kerning, self.font.groups)
        if validates:
            return
        self.logger.info("Warning: removed these invalid kerning pairs:\n\t%s"%"\n\t".join(errors))
        for pair in pairs:
            if pair in self.font.kerning:
                del self.font.kerning[pair]


    def save(self):
        """ Save the UFO."""
        self.validateKerning()
        try:
            self.font.save(self.path, self.ufoVersion)
        except defcon.DefconError as error:
            if self.logger:
                self.logger.exception("Error generating.")
            return False, error.report
        return True, None
        
