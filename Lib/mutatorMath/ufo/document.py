# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import os
import xml.etree.ElementTree as ET

import defcon
from mutatorMath.objects.error import MutatorError
from mutatorMath.objects.location import Location
from mutatorMath.objects.mutator import Mutator
from mutatorMath.ufo.instance import InstanceWriter


"""

    Read and write mutator math designspace files. 

    A DesignSpaceDocumentWriter object can be instructed to write a properly formed
    description of a designspace for UFO fonts.

    A DesignSpaceDocumentReader object can then execute such a designspace document
    and generate the UFO's described.

"""

def newLogger(proposedLogPath):
    """ Create a new logging object at this path """
    logging.basicConfig(filename=proposedLogPath,
            level=logging.INFO,
            filemode="w",
            format='%(asctime)s MutatorMath %(message)s',
            )
    return logging.getLogger("mutatorMath")

def _indent(elem, whitespace="    ", level=0):
    # taken from http://effbot.org/zone/element-lib.htm#prettyprint
    i = "\n" + level * whitespace
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + whitespace
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, whitespace, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class DesignSpaceDocumentWriter(object):
    """
    Writer for a design space description file.

    *   path:   path for the document
    *   toolVersion: version of this tool
    """

    _whiteSpace = "    "
        
    def __init__(self, path, toolVersion=3, verbose=False):
        self.path = path
        self.toolVersion = toolVersion
        self.verbose = verbose
        self.root = ET.Element("designspace")
        self.root.attrib['format'] = "%d"%toolVersion
        self.root.append(ET.Element("sources"))
        self.root.append(ET.Element("instances"))
        self.currentInstance = None

    def save(self, pretty=True):
        """ Save the xml. Make pretty if necessary. """
        self.endInstance()
        if pretty:
            _indent(self.root, whitespace=self._whiteSpace)
        tree = ET.ElementTree(self.root)
        tree.write(self.path, encoding="utf-8", method='xml', xml_declaration=True)
    
    def _makeLocationElement(self, locationObject, name=None):
        """ Convert Location object to an locationElement."""
        
        locElement = ET.Element("location")
        if name is not None:
           locElement.attrib['name'] = name
        for dimensionName, dimensionValue in locationObject.items():
           dimElement = ET.Element('dimension')
           dimElement.attrib['name'] = dimensionName
           if type(dimensionValue)==tuple:
               dimElement.attrib['xvalue'] = "%f"%dimensionValue[0]
               dimElement.attrib['yvalue'] = "%f"%dimensionValue[1]
           else:
               dimElement.attrib['xvalue'] = "%f"%dimensionValue
           locElement.append(dimElement)
        return locElement
    
    def addSource(self,
            path,
            name, 
            location, 
            copyLib=False, 
            copyGroups=False, 
            copyInfo=False,
            copyFeatures=False,
            muteKerning=False, 
            muteInfo=False,
            mutedGlyphNames=None,
        ):
        """
        Add a new UFO source to the document.
        *   path:           path to this UFO, will be written as a relative path to the document path.
        *   name:           reference name for this source
        *   location:       name of the location for this UFO
        *   copyLib:        copy the contents of this source to instances
        *   copyGroups:     copy the groups of this source to instances
        *   copyInfo:       copy the non-numerical fields from this source.info to instances.
        *   copyFeatures:   copy the feature text from this source to instances
        *   muteKerning:    mute the kerning data from this source
        *   muteInfo:       mute the font info data from this source

        Note: no separate flag for mute font: the source is just not added. 
        """
        sourceElement = ET.Element("source")
        pathRelativeToDocument = os.path.relpath(path, os.path.dirname(self.path))
        sourceElement.attrib['filename'] = pathRelativeToDocument
        sourceElement.attrib['name'] = name
        if copyLib:
            libElement = ET.Element('lib')
            libElement.attrib['copy'] = "1"
            sourceElement.append(libElement)

        if copyGroups:
            groupsElement = ET.Element('groups')
            groupsElement.attrib['copy'] = "1"
            sourceElement.append(groupsElement)

        if copyFeatures:
            featuresElement = ET.Element('features')
            featuresElement.attrib['copy'] = "1"
            sourceElement.append(featuresElement)

        if copyInfo or muteInfo:
            # copy info: 
            infoElement = ET.Element('info')
            if copyInfo:
                infoElement.attrib['copy'] = "1"
            if muteInfo:
                infoElement.attrib['mute'] = "1"
            sourceElement.append(infoElement)

        if muteKerning:
            # add kerning element to the source
            kerningElement = ET.Element("kerning")
            kerningElement.attrib["mute"] = '1'
            sourceElement.append(kerningElement)

        if mutedGlyphNames:
            # add muted glyphnames to the source
            for name in mutedGlyphNames:
                glyphElement = ET.Element("glyph")
                glyphElement.attrib["name"] = name
                glyphElement.attrib["mute"] = '1'
                sourceElement.append(glyphElement)

        locationElement = self._makeLocationElement(location)
        sourceElement.append(locationElement)
        self.root.findall('.sources')[0].append(sourceElement)

    def startInstance(self, name=None,
            location=None,
            familyName=None,
            styleName=None,
            fileName=None,
            postScriptFontName=None,
            styleMapFamilyName=None,
            styleMapStyleName=None,

            ):
        """ Start a new instance.
            Instances can need a lot of configuration. 
            So this method starts a new instance element. Use endInstance() to finish it.

            *   name: the name of this instance
            *   familyName: name for the font.info.familyName field. Required.
            *   styleName: name fot the font.info.styleName field. Required.
            *   fileName: filename for the instance UFO file. Required.
            *   postScriptFontName: name for the font.info.postScriptFontName field. Optional.
            *   styleMapFamilyName: name for the font.info.styleMapFamilyName field. Optional.
            *   styleMapStyleName: name for the font.info.styleMapStyleName field. Optional.
        """
        if self.currentInstance is not None:
            # We still have the previous one open
            self.endInstance()
        instanceElement = ET.Element('instance')
        if name is not None:
            instanceElement.attrib['name'] = name
        if location is not None:
            locationElement = self._makeLocationElement(location)
            instanceElement.append(locationElement)
        if familyName is not None:
            instanceElement.attrib['familyname'] = familyName
        if styleName is not None:
            instanceElement.attrib['stylename'] = styleName
        if fileName is not None:
            pathRelativeToDocument = os.path.relpath(fileName, os.path.dirname(self.path))
            instanceElement.attrib['filename'] = pathRelativeToDocument
        if postScriptFontName is not None:
            instanceElement.attrib['postscriptfontname'] = postScriptFontName
        if styleMapFamilyName is not None:
            instanceElement.attrib['stylemapfamilyname'] = styleMapFamilyName
        if styleMapStyleName is not None:
            instanceElement.attrib['stylemapstylename'] = styleMapStyleName

        self.currentInstance = instanceElement
    
    def endInstance(self):
        """ 
            Finalise the instance definition started by startInstance().
        """
        if self.currentInstance is None:
            return
        allInstances = self.root.findall('.instances')[0].append(self.currentInstance)
        self.currentInstance = None
    
    def writeGlyph(self,
            name,
            unicodeValue=None,
            location=None,
            masters=None,
            note=None,
            mute=False,
            ):
        """ Add a new glyph to the current instance. 
            * name: the glyph name. Required.
            * unicodeValue: unicode value for this glyph if it needs to be different from the unicode value associated with this glyph name in the masters.
            * location: a design space location for this glyph if it needs to be different from the instance location. 
            * masters: a list of masters and locations for this glyph if they need to be different from the masters specified for this instance.
            * note: a note for this glyph
            * mute: if this glyph is muted. None of the other attributes matter if this one is true.
        """
        if self.currentInstance is None:
            return
        glyphElement = ET.Element('glyph')
        if mute:
            glyphElement.attrib['mute'] = "1"
        if unicodeValue is not None:
            glyphElement.attrib['unicode'] = hex(unicodeValue)
        if location is not None:
            locationElement = self._makeLocationElement(location)
            glyphElement.append(locationElement)
        if name is not None:
            glyphElement.attrib['name'] = name
        if note is not None:
            noteElement = ET.Element('note')
            noteElement.text = note
            glyphElement.append(noteElement)
        if masters is not None:
            mastersElement = ET.Element("masters")
            for glyphName, masterName, location in masters:
                masterElement = ET.Element("master")
                if glyphName is not None:
                    masterElement.attrib['glyphname'] = glyphName
                masterElement.attrib['source'] = masterName
                if location is not None:
                    locationElement = self._makeLocationElement(location)
                    masterElement.append(locationElement)
                mastersElement.append(masterElement)
            glyphElement.append(mastersElement)
        if self.currentInstance.findall('.glyphs') == []:
            glyphsElement = ET.Element('glyphs')
            self.currentInstance.append(glyphsElement)
        else:
            glyphsElement = self.currentInstance.findall('.glyphs')[0]
        glyphsElement.append(glyphElement)

    def writeInfo(self, location=None, masters=None):
        """ Write font into the current instance.
            Note: the masters attribute is ignored at the moment.
        """
        if self.currentInstance is None:
            return
        infoElement = ET.Element("info")
        if location is not None:
            locationElement = self._makeLocationElement(location)
            infoElement.append(locationElement)
        self.currentInstance.append(infoElement)
    
    def writeKerning(self, location=None, masters=None):
        """ Write kerning into the current instance.
            Note: the masters attribute is ignored at the moment.
        """
        if self.currentInstance is None:
            return
        kerningElement = ET.Element("kerning")
        if location is not None:
            locationElement = self._makeLocationElement(location)
            kerningElement.append(locationElement)
        self.currentInstance.append(kerningElement)
    
    
class DesignSpaceDocumentReader(object):
    """ Read a designspace description.
        Build Instance objects, generate them.
        
        *   documentPath:   path of the document to read
        *   ufoVersion:     target UFO version
        *   roundGeometry:  apply rounding to all geometry

    """
    _fontClass = defcon.objects.font.Font
    _instanceWriterClass = InstanceWriter
    _tempFontLibGlyphMuteKey = "_mutatorMath.temp.mutedGlyphNames"
    _tempFontLocationKey = "_mutatorMath.temp.fontLocation"

    
    def __init__(self, documentPath,
            ufoVersion,
            roundGeometry=False,
            verbose=False,
            logPath=None,
            progressFunc=None
            ):
        self.path = documentPath
        self.ufoVersion = ufoVersion
        self.roundGeometry = roundGeometry
        self.verbose = verbose
        self.documentFormatVersion = 0
        self.sources = {}
        self.instances = {}
        self.libSource = None
        self.groupsSource = None
        self.infoSource = None
        self.featuresSource = None
        self.progressFunc=progressFunc
        self.muted = dict(kerning=[], info=[], glyphs={})
        if logPath is None:
            logPath = os.path.join(os.path.dirname(documentPath), "mutatorMath.log")
        self.logger = newLogger(logPath)
        if self.verbose:
            self.logger.info("Executing designspace document: %s", documentPath)
        self.results = {}   # dict with instancename / filepaths for post processing.

    def reportProgress(self, state, action, text=None, tick=None):
        """ If we want to keep other code updated about our progress.

            state:      'prep'      reading sources
                        'generate'  making instances
                        'done'      wrapping up
                        'error'     reporting a problem
            
            action:     'start'     begin generating
                        'stop'      end generating
                        'source'    which ufo we're reading

            text:       <file.ufo>  ufoname (for instance)
            tick:       a float between 0 and 1 indicating progress.

        """
        if self.progressFunc is not None:
            self.progressFunc(state=state, action=action, text=text, tick=tick)

    def getSourcePaths(self, makeGlyphs=True, makeKerning=True, makeInfo=True):
        """ Return a list of paths referenced in the document."""
        tree = ET.parse(self.path)        
        self.root = tree.getroot()
        self.readVersion()
        assert self.documentFormatVersion == 3
        self.warpDict = None
        # self.readWarp()
        self.readSources()
        paths = []
        for name in self.sources.keys():
            paths.append(self.sources[name][0].path)
        return paths

    def process(self, makeGlyphs=True, makeKerning=True, makeInfo=True):
        """ Process the input file and generate the instances. """
        tree = ET.parse(self.path)        
        self.root = tree.getroot()
        self.readVersion()
        assert self.documentFormatVersion == 3
        self.readSources()
        self.readInstances(makeGlyphs=makeGlyphs, makeKerning=makeKerning, makeInfo=makeInfo)
        self.logger.info('Done')
        self.reportProgress("done", 'stop')
    
    def readVersion(self):
        """ Read the document version.
        ::
            <designspace format="3">
        """
        ds = self.root.findall("[@format]")[0]
        self.documentFormatVersion = int(ds.attrib['format'])
        
    def readSources(self):
        """ Read the source elements.
        
        ::
            
            <source filename="LightCondensed.ufo" location="location-token-aaa" name="master-token-aaa1">
                <info mute="1" copy="1"/>
                <kerning mute="1"/>
                <glyph mute="1" name="thirdGlyph"/>
            </source>
        
        """
        for sourceElement in self.root.findall(".sources/source"):
            # shall we just read the UFO here?
            filename = sourceElement.attrib.get('filename')
            # filename is a path relaive to the documentpath. resolve first.
            sourcePath = os.path.join(os.path.dirname(self.path), filename)
            sourceName = sourceElement.attrib.get('name')
            self.reportProgress("prep", 'load', sourcePath)
            if not os.path.exists(sourcePath):
                raise MutatorError("Source not found at %s"%sourcePath)
            sourceObject = self._fontClass(sourcePath)
            
            # read the locations
            sourceLocationObject = None
            sourceLocationObject = self.locationFromElement(sourceElement)

            if sourceLocationObject is None:
               raise MutatorError("No location defined for source %s"%sourceName)

            # read lib flag
            for libElement in sourceElement.findall('.lib'):
                if libElement.attrib.get('copy') == '1':
                    if self.libSource is not None:
                        if self.verbose:
                            self.logger.info("\tError: Lib copy source already defined: %s, %s", sourceName, self.libSource)
                        self.libSource = None
                    else:
                        self.libSource = sourceName

            # read the groups flag
            for groupsElement in sourceElement.findall('.groups'):
                if groupsElement.attrib.get('copy') == '1':
                    if self.groupsSource is not None:
                        if self.verbose:
                            self.logger.info("\tError: Groups copy source already defined: %s, %s", sourceName, self.groupsSource)
                        self.groupsSource = None
                    else:
                        self.groupsSource = sourceName
            
            # read the info flag
            for infoElement in sourceElement.findall(".info"):
                if infoElement.attrib.get('copy') == '1':
                    if self.infoSource is not None:
                        if self.verbose:
                            self.logger.info("\tError: Info copy source already defined: %s, %s", sourceName, self.infoSource)
                        self.infoSource = None
                    else:
                        self.infoSource = sourceName
                if infoElement.attrib.get('mute') == '1':
                    self.muted['info'].append(sourceName)
                    if self.verbose:
                        self.logger.info("\tFont info from %s is muted.", sourceName)

            # read the features flag
            for featuresElement in sourceElement.findall(".features"):
                if featuresElement.attrib.get('copy') == '1':
                    if self.featuresSource is not None:
                        if self.verbose:
                            self.logger.info("\tError: Features copy source already defined: %s, %s", sourceName, self.featuresSource)
                        self.featuresSource = None
                    else:
                        self.featuresSource = sourceName

            mutedGlyphs = []
            for glyphElement in sourceElement.findall(".glyph"):
                glyphName = glyphElement.attrib.get('name')
                if glyphName is None:
                    continue
                if glyphElement.attrib.get('mute') == '1':
                    if not sourceName in self.muted['glyphs']:
                        self.muted['glyphs'][sourceName] = []
                    self.muted['glyphs'][sourceName].append(glyphName)
            
            for kerningElement in sourceElement.findall(".kerning"):
                if kerningElement.attrib.get('mute') == '1':
                    self.muted['kerning'].append(sourceName)

            # store
            self.sources[sourceName] = sourceObject, sourceLocationObject
            self.reportProgress("prep", 'done')

    def locationFromElement(self, element):
        """ 
            Find the MutatorMath location of this element, either by name or from a child element.
        """
        elementLocation = None
        for locationElement in element.findall('.location'):
            elementLocation = self.readLocationElement(locationElement)
            break
        return elementLocation

    def readLocationElement(self, locationElement):
        """ Format 0 location reader """
        loc = Location()
        for dimensionElement in locationElement.findall(".dimension"):
            dimName = dimensionElement.attrib.get("name")
            xValue = yValue = None
            try:
                xValue = dimensionElement.attrib.get('xvalue')
                xValue = float(xValue)
            except ValueError:
                self.logger.info("KeyError in readLocation xValue %3.3f", xValue)
            try:
                yValue = dimensionElement.attrib.get('yvalue')
                if yValue is not None:
                    yValue = float(yValue)
            except ValueError:
                pass
            if yValue is not None:
                loc[dimName] = (xValue, yValue)
            else:
                loc[dimName] = xValue
        return loc

    def readInstances(self, makeGlyphs=True, makeKerning=True, makeInfo=True):
        """ Read all instance elements. 
        
        ::
        
            <instance familyname="SuperFamily" filename="OutputNameInstance1.ufo" location="location-token-aaa" stylename="Regular">
        
        """
        instanceElements = self.root.findall('.instances/instance')
        for instanceElement in self.root.findall('.instances/instance'):
            self._readSingleInstanceElement(instanceElement, makeGlyphs=makeGlyphs, makeKerning=makeKerning, makeInfo=makeInfo)
    
    def _readSingleInstanceElement(self, instanceElement, makeGlyphs=True, makeKerning=True, makeInfo=True):
        """ Read a single instance element.
            If we have glyph specifications, only make those.
            Otherwise make all available glyphs.
        """
        # get the data from the instanceElement itself
        filename = instanceElement.attrib.get('filename')

        instancePath = os.path.join(os.path.dirname(self.path), filename)
        self.reportProgress("generate", 'start', instancePath)
        filenameTokenForResults = os.path.basename(filename)

        if self.verbose:
            self.logger.info("Writing %s to %s", os.path.basename(filename), instancePath)

        instanceObject = self._instanceWriterClass(instancePath,    
            ufoVersion=self.ufoVersion,
            roundGeometry=self.roundGeometry, 
            verbose=self.verbose,
            logger=self.logger
            )
        self.results[filenameTokenForResults] = instancePath

        # set the masters
        instanceObject.setSources(self.sources)
        self.unicodeMap = instanceObject.makeUnicodeMapFromSources()
        instanceObject.setMuted(self.muted)
        familyname = instanceElement.attrib.get('familyname')
        if familyname is not None:
            instanceObject.setFamilyName(familyname)
        stylename = instanceElement.attrib.get('stylename')
        if stylename is not None:
            instanceObject.setStyleName(stylename)
        postScriptFontName = instanceElement.attrib.get('postscriptfontname')
        if postScriptFontName is not None:
            instanceObject.setPostScriptFontName(postScriptFontName)
        styleMapFamilyName = instanceElement.attrib.get('stylemapfamilyname')
        if styleMapFamilyName is not None:
            instanceObject.setStyleMapFamilyName(styleMapFamilyName)
        styleMapStyleName = instanceElement.attrib.get('stylemapstylename')
        if styleMapStyleName is not None:
            instanceObject.setStyleMapStyleName(styleMapStyleName)

        # location
        instanceLocation = self.locationFromElement(instanceElement)

        if instanceLocation is not None:
            instanceObject.setLocation(instanceLocation)
        
        if makeGlyphs:

            # step 1: generate all glyphs we have mutators for. 
            names = instanceObject.getAvailableGlyphnames()
            for n in names:
                unicodeValue = self.unicodeMap.get(n, None)
                try:
                    instanceObject.addGlyph(n, unicodeValue)
                except AssertionError:
                    if self.verbose:
                        self.logger.info("Problem making glyph %s, skipping.", n)
            # step 2: generate all the glyphs that have special definitions.
            for glyphElement in instanceElement.findall('.glyphs/glyph'):
                self.readGlyphElement(glyphElement, instanceObject)

        # read the kerning
        if makeKerning:
            for kerningElement in instanceElement.findall('.kerning'):
                self.readKerningElement(kerningElement, instanceObject)
                break

        # read the fontinfo
        if makeInfo:
            for infoElement in instanceElement.findall('.info'):
                self.readInfoElement(infoElement, instanceObject)

        # copy the features
        if self.featuresSource is not None:
            instanceObject.copyFeatures(self.featuresSource)

        # copy the groups
        if self.groupsSource is not None:
            if self.groupsSource in self.sources:
                groupSourceObject, loc = self.sources[self.groupsSource]
                # copy the groups from the designated source to the new instance
                # note: setGroups will filter the group members
                # only glyphs present in the font will be added to the group.
                instanceObject.setGroups(groupSourceObject.groups, kerningGroupConversionRenameMaps=groupSourceObject.kerningGroupConversionRenameMaps)

        # lib items
        if self.libSource is not None:
            if self.libSource in self.sources:
                libSourceObject, loc = self.sources[self.libSource]
                instanceObject.setLib(libSourceObject.lib)
        
        # save the instance. Done.
        success, report = instanceObject.save()
        if not success:
            # report problems other than validation errors and failed glyphs
            self.logger.info("%s:\nErrors generating: %s", filename, report)

        # report failed glyphs
        failed = instanceObject.getFailed()
        if failed:
            failed.sort()
            msg = "%s:\nErrors calculating %s glyphs: \n%s"%(filename, len(failed),"\n".join(failed))
            self.reportProgress('error', 'glyphs', msg)
            if self.verbose:
                self.logger.info(msg)

        # report missing unicodes
        missing = instanceObject.getMissingUnicodes()
        if missing:
            missing.sort()
            msg = "%s:\nMissing unicodes for %s glyphs: \n%s"%(filename, len(missing),"\n".join(missing))
            self.reportProgress('error', 'unicodes', msg)
            if self.verbose:
                self.logger.info(msg)

        # report failed kerning pairs
        failed = instanceObject.getKerningErrors()
        if failed:
            failed.sort()
            msg = "%s:\nThese kerning pairs failed validation and have been removed:\n%s"%(filename, "\n".join(failed))
            self.reportProgress('error', 'kerning', msg)
            if self.verbose:
                self.logger.info(msg)

        self.reportProgress("generate", 'stop', filenameTokenForResults)

    def readInfoElement(self, infoElement, instanceObject):
        """ Read the info element.
            
            ::
            
                <info/>
            
                <info">
                <location/>
                </info>
                
            """
        infoLocation = self.locationFromElement(infoElement)
        instanceObject.addInfo(infoLocation, copySourceName=self.infoSource)
        
    def readKerningElement(self, kerningElement, instanceObject):
        """ Read the kerning element.
        
        ::
                
                Make kerning at the location and with the masters specified at the instance level.
                <kerning/>

        """
        kerningLocation = self.locationFromElement(kerningElement)
        instanceObject.addKerning(kerningLocation)
                    
    def readGlyphElement(self, glyphElement, instanceObject):
        """
        Read the glyph element. 
        
        ::
        
            <glyph name="b" unicode="0x62"/>

            <glyph name="b"/>

            <glyph name="b">
                <master location="location-token-bbb" source="master-token-aaa2"/>
                <master glyphname="b.alt1" location="location-token-ccc" source="master-token-aaa3"/>

                <note>
                    This is an instance from an anisotropic interpolation.
                </note>
            </glyph>
        
        """
        # name
        glyphName = glyphElement.attrib.get('name')
        if glyphName is None:
            raise MutatorError("Glyph object without name attribute.")
        
        # mute
        mute = glyphElement.attrib.get("mute")
        if mute == "1":
            instanceObject.muteGlyph(glyphName)
            # we do not need to stick around after this
            return

        # unicode
        unicodeValue = glyphElement.attrib.get('unicode')
        if unicodeValue == None:
            unicodeValue = self.unicodeMap.get(glyphName, None)
        else:
            try:
                unicodeValue = int(unicodeValue, 16)
            except ValueError:
                raise MutatorError("unicode value %s is not integer"%unicodeValue)
        
        # note
        note = None
        for noteElement in glyphElement.findall('.note'):
            note = noteElement.text
            break

        # location
        instanceLocation = self.locationFromElement(glyphElement)
        
        # masters
        glyphSources = None
        for masterElement in glyphElement.findall('.masters/master'):
            fontSourceName = masterElement.attrib.get('source')
            fontSource, fontLocation = self.sources.get(fontSourceName)
            if fontSource is None:
                raise MutatorError("Unknown glyph master: %s"%masterElement)
            sourceLocation = self.locationFromElement(masterElement)
            if sourceLocation is None:
                # if we don't read a location, use the instance location
                sourceLocation = fontLocation
            masterGlyphName = masterElement.attrib.get('glyphname')
            if masterGlyphName is None:
                # if we don't read a glyphname, use the one we have
                masterGlyphName = glyphName
            d = dict(   font=fontSource,
                        location=sourceLocation,
                        glyphName=masterGlyphName)
            if glyphSources is None:
                glyphSources = []
            glyphSources.append(d)
        # calculate the glyph
        instanceObject.addGlyph(glyphName, unicodeValue, instanceLocation, glyphSources, note=note)


