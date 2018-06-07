# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import os
import posixpath
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

import logging
def initializeLogger(proposedLogPath):
    logging.basicConfig(filename=proposedLogPath, level=logging.INFO, format='%(asctime)s %(message)s')

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
        self.root.append(ET.Element("axes"))
        self.root.append(ET.Element("sources"))
        self.root.append(ET.Element("instances"))
        self.logger = None
        if verbose:
            self.logger = logging.getLogger("mutatorMath")
        self.currentInstance = None

    def save(self, pretty=True):
        """ Save the xml. Make pretty if necessary. """
        self.endInstance()
        if pretty:
            _indent(self.root, whitespace=self._whiteSpace)
        tree = ET.ElementTree(self.root)
        tree.write(self.path, encoding="utf-8", method='xml', xml_declaration=True)
        if self.logger:
            self.logger.info("Writing %s", self.path)

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

    def _posixPathRelativeToDocument(self, otherPath):
        relative = os.path.relpath(otherPath, os.path.dirname(self.path))
        return posixpath.join(*relative.split(os.path.sep))

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
            familyName=None,
            styleName=None,
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
        *   familyName:     family name for this UFO (to be able to work on the names without reading the whole UFO)
        *   styleName:      style name for this UFO (to be able to work on the names without reading the whole UFO)

        Note: no separate flag for mute font: the source is just not added.
        """
        sourceElement = ET.Element("source")
        sourceElement.attrib['filename'] = self._posixPathRelativeToDocument(path)
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

        if familyName is not None:
            sourceElement.attrib['familyname'] = familyName
        if styleName is not None:
            sourceElement.attrib['stylename'] = styleName


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
            instanceElement.attrib['filename'] = self._posixPathRelativeToDocument(fileName)
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
            unicodes=None,
            location=None,
            masters=None,
            note=None,
            mute=False,
            ):
        """ Add a new glyph to the current instance.
            * name: the glyph name. Required.
            * unicodes: unicode values for this glyph if it needs to be different from the unicode values associated with this glyph name in the masters.
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
        if unicodes is not None:
            glyphElement.attrib['unicode'] = " ".join([hex(u) for u in unicodes])
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

    def writeWarp(self, warpDict):
        """ Write a list of (in, out) values for a warpmap """
        warpElement = ET.Element("warp")
        axisNames = sorted(warpDict.keys())
        for name in axisNames:
            axisElement = ET.Element("axis")
            axisElement.attrib['name'] = name
            for a, b in warpDict[name]:
                warpPt = ET.Element("map")
                warpPt.attrib['input'] = str(a)
                warpPt.attrib['output'] = str(b)
                axisElement.append(warpPt)
            warpElement.append(axisElement)
        self.root.append(warpElement)

    def addAxis(self, tag, name, minimum, maximum, default, warpMap=None):
        """ Write an axis element.
            This will be added to the <axes> element.
         """
        axisElement = ET.Element("axis")
        axisElement.attrib['name'] = name
        axisElement.attrib['tag'] = tag
        axisElement.attrib['minimum'] = str(minimum)
        axisElement.attrib['maximum'] = str(maximum)
        axisElement.attrib['default'] = str(default)
        if warpMap is not None:
            for a, b in warpMap:
                warpPt = ET.Element("map")
                warpPt.attrib['input'] = str(a)
                warpPt.attrib['output'] = str(b)
                axisElement.append(warpPt)
        self.root.findall('.axes')[0].append(axisElement)


class DesignSpaceDocumentReader(object):
    """ Read a designspace description.
        Build Instance objects, generate them.

        *   documentPath:   path of the document to read
        *   ufoVersion:     target UFO version
        *   roundGeometry:  apply rounding to all geometry

    """
    _fontClass = defcon.Font
    _glyphClass = defcon.Glyph
    _libClass = defcon.Lib
    _glyphContourClass = defcon.Contour
    _glyphPointClass = defcon.Point
    _glyphComponentClass = defcon.Component
    _glyphAnchorClass = defcon.Anchor
    _kerningClass = defcon.Kerning
    _groupsClass = defcon.Groups
    _infoClass = defcon.Info
    _featuresClass = defcon.Features

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
        self.documentFormatVersion = 0
        self.sources = {}
        self.instances = {}
        self.axes = {}      # dict with axes info
        self.axesOrder = [] # order in which the axes were defined
        self.warpDict = None # let's stop using this one
        self.libSource = None
        self.groupsSource = None
        self.infoSource = None
        self.featuresSource = None
        self.progressFunc=progressFunc
        self.muted = dict(kerning=[], info=[], glyphs={})
        self.verbose = verbose
        self.logger = None
        if self.verbose:
            self.logger = logging.getLogger("mutatorMath")
        self.results = {}   # dict with instancename / filepaths for post processing.
        tree = ET.parse(self.path)
        self.root = tree.getroot()
        self.readVersion()
        assert self.documentFormatVersion >= 3

        self.readAxes()
        self.readWarp()
        self.readSources()

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
        paths = []
        for name in self.sources.keys():
            paths.append(self.sources[name][0].path)
        return paths

    def process(self, makeGlyphs=True, makeKerning=True, makeInfo=True):
        """ Process the input file and generate the instances. """
        if self.logger:
            self.logger.info("Reading %s", self.path)
        self.readInstances(makeGlyphs=makeGlyphs, makeKerning=makeKerning, makeInfo=makeInfo)
        self.reportProgress("done", 'stop')

    def readVersion(self):
        """ Read the document version.
        ::
            <designspace format="3">
        """
        ds = self.root.findall("[@format]")[0]
        raw_format = ds.attrib['format']
        try:
            self.documentFormatVersion = int(raw_format)
        except ValueError:
            # as of fontTools >= 3.27 'format' is formatted as a float "4.0"
            self.documentFormatVersion = float(raw_format)

    def readWarp(self):
        """ Read the warp element

        ::
            <warp>
                <axis name="weight">
                    <map input="0" output="0" />
                    <map input="500" output="200" />
                    <map input="1000" output="1000" />
                </axis>
            </warp>

        """
        warpDict = {}
        for warpAxisElement in self.root.findall(".warp/axis"):
            axisName = warpAxisElement.attrib.get("name")
            warpDict[axisName] = []
            for warpPoint in warpAxisElement.findall(".map"):
                inputValue = float(warpPoint.attrib.get("input"))
                outputValue = float(warpPoint.attrib.get("output"))
                warpDict[axisName].append((inputValue, outputValue))
        self.warpDict = warpDict

    def readAxes(self):
        """ Read the axes element.
        """
        for axisElement in self.root.findall(".axes/axis"):
            axis = {}
            axis['name'] = name = axisElement.attrib.get("name")
            axis['tag'] = axisElement.attrib.get("tag")
            axis['minimum'] = float(axisElement.attrib.get("minimum"))
            axis['maximum'] = float(axisElement.attrib.get("maximum"))
            axis['default'] = float(axisElement.attrib.get("default"))
            # we're not using the map for anything.
            axis['map'] = []
            for warpPoint in axisElement.findall(".map"):
                inputValue = float(warpPoint.attrib.get("input"))
                outputValue = float(warpPoint.attrib.get("output"))
                axis['map'].append((inputValue, outputValue))
            # there are labelnames in the element
            # but we don't need them for building the fonts.
            self.axes[name] = axis
            self.axesOrder.append(axis['name'])

    def readSources(self):
        """ Read the source elements.

        ::

            <source filename="LightCondensed.ufo" location="location-token-aaa" name="master-token-aaa1">
                <info mute="1" copy="1"/>
                <kerning mute="1"/>
                <glyph mute="1" name="thirdGlyph"/>
            </source>

        """
        for sourceCount, sourceElement in enumerate(self.root.findall(".sources/source")):
            # shall we just read the UFO here?
            filename = sourceElement.attrib.get('filename')
            # filename is a path relaive to the documentpath. resolve first.
            sourcePath = os.path.abspath(os.path.join(os.path.dirname(self.path), filename))
            sourceName = sourceElement.attrib.get('name')
            if sourceName is None:
                # if the source element has no name attribute
                # (some authoring tools do not need them)
                # then we should make a temporary one. We still need it for reference.
                sourceName = "temp_master.%d"%(sourceCount)
            self.reportProgress("prep", 'load', sourcePath)
            if not os.path.exists(sourcePath):
                raise MutatorError("Source not found at %s"%sourcePath)
            sourceObject = self._instantiateFont(sourcePath)
            # read the locations
            sourceLocationObject = None
            sourceLocationObject = self.locationFromElement(sourceElement)

            if sourceLocationObject is None:
               raise MutatorError("No location defined for source %s"%sourceName)

            # read lib flag
            for libElement in sourceElement.findall('.lib'):
                if libElement.attrib.get('copy') == '1':
                    self.libSource = sourceName

            # read the groups flag
            for groupsElement in sourceElement.findall('.groups'):
                if groupsElement.attrib.get('copy') == '1':
                    self.groupsSource = sourceName

            # read the info flag
            for infoElement in sourceElement.findall(".info"):
                if infoElement.attrib.get('copy') == '1':
                    self.infoSource = sourceName
                if infoElement.attrib.get('mute') == '1':
                    self.muted['info'].append(sourceName)

            # read the features flag
            for featuresElement in sourceElement.findall(".features"):
                if featuresElement.attrib.get('copy') == '1':
                    if self.featuresSource is not None:
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
                if self.logger:
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

    def readInstance(self, key, makeGlyphs=True, makeKerning=True, makeInfo=True):
        """ Read a single instance element.

            key: an (attribute, value) tuple used to find the requested instance.

        ::

            <instance familyname="SuperFamily" filename="OutputNameInstance1.ufo" location="location-token-aaa" stylename="Regular">

        """
        attrib, value = key
        for instanceElement in self.root.findall('.instances/instance'):
            if instanceElement.attrib.get(attrib) == value:
                self._readSingleInstanceElement(instanceElement, makeGlyphs=makeGlyphs, makeKerning=makeKerning, makeInfo=makeInfo)
                return
        raise MutatorError("No instance found with key: (%s, %s)." % key)

    def readInstances(self, makeGlyphs=True, makeKerning=True, makeInfo=True):
        """ Read all instance elements.

        ::

            <instance familyname="SuperFamily" filename="OutputNameInstance1.ufo" location="location-token-aaa" stylename="Regular">

        """
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
        if self.verbose and self.logger:
            self.logger.info("\tGenerating instance %s", os.path.basename(instancePath))
        filenameTokenForResults = os.path.basename(filename)

        instanceObject = self._instanceWriterClass(instancePath,
            ufoVersion=self.ufoVersion,
            roundGeometry=self.roundGeometry,
            axes = self.axes,
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
                unicodes = self.unicodeMap.get(n, None)
                try:
                    instanceObject.addGlyph(n, unicodes)
                except AssertionError:
                    if self.verbose and self.logger:
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
                # Depending on the ufoversion we might or might not expect the kerningGroupConversionRenameMaps attribute.
                if hasattr(groupSourceObject, "kerningGroupConversionRenameMaps"):
                    renameMap = groupSourceObject.kerningGroupConversionRenameMaps
                else:
                    renameMap = {}
                instanceObject.setGroups(groupSourceObject.groups, kerningGroupConversionRenameMaps=renameMap)

        # lib items
        if self.libSource is not None:
            if self.libSource in self.sources:
                libSourceObject, loc = self.sources[self.libSource]
                instanceObject.setLib(libSourceObject.lib)

        # save the instance. Done.
        success, report = instanceObject.save()
        if not success and self.logger:
            # report problems other than validation errors and failed glyphs
            self.logger.info("%s:\nErrors generating: %s", filename, report)

        # report failed glyphs
        failed = instanceObject.getFailed()
        if failed:
            failed.sort()
            msg = "%s:\nErrors calculating %s glyphs: \n%s"%(filename, len(failed),"\t"+"\n\t".join(failed))
            self.reportProgress('error', 'glyphs', msg)
            if self.verbose and self.logger:
                self.logger.info(msg)

        # report missing unicodes
        missing = instanceObject.getMissingUnicodes()
        if missing:
            missing.sort()
            msg = "%s:\nPossibly missing unicodes for %s glyphs: \n%s"%(filename, len(missing),"\t"+"\n\t".join(missing))
            self.reportProgress('error', 'unicodes', msg)

        # store
        self.instances[postScriptFontName] = instanceObject
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
        unicodes = glyphElement.attrib.get('unicode')
        if unicodes == None:
            unicodes = self.unicodeMap.get(glyphName, None)
        else:
            try:
                unicodes = [int(u, 16) for u in unicodes.split(" ")]
            except ValueError:
                raise MutatorError("unicode values %s are not integers" % unicodes)

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
        instanceObject.addGlyph(glyphName, unicodes, instanceLocation, glyphSources, note=note)

    def _instantiateFont(self, path):
        """
        Return a instance of a font object
        with all the given subclasses
        """
        return self._fontClass(path,
            libClass=self._libClass,
            kerningClass=self._kerningClass,
            groupsClass=self._groupsClass,
            infoClass=self._infoClass,
            featuresClass=self._featuresClass,
            glyphClass=self._glyphClass,
            glyphContourClass=self._glyphContourClass,
            glyphPointClass=self._glyphPointClass,
            glyphComponentClass=self._glyphComponentClass,
            glyphAnchorClass=self._glyphAnchorClass)
