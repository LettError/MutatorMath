MutatorMath DesignSpace Format (old)
====================================

![A MutatorMath Designspace Document Icon](designspaceDocumentIcon.png)

Please refer to the [designSpaceDocument](https://github.com/LettError/designSpaceDocument) repository for an up to data specification of the file.

The UFO support in MutatorMath introduces a useful storage format in XML for MutatorMath designspaces. This document describes the format.

## Document structure

The document must contain a single **designspace** top level element. The current format version is `3`. The designspace element must contain one **sources** element and one **instances** element.

*	The **sources** element contains one or more **source** elements.
* 	The **instances** element contains one or more **instance** elements.

The designspace format makes a difference between "masters" and "sources". Source specifically indicates the UFO file. Master indicates a particular use of a source in a MutatorMath calculation. In general: the sources bring data to the calculation, instances take data out.

The font.info contains different kinds of data. Some are strings (names, urls, copyrights), some are numerical but not geometrical (versions, PANOSE). The designspace offers some controls

Both instance and source elements contain paths to files. These paths are expected to be relative to the path of the .designspace document. This allows the same .designspace to be deployed to multiple locations, but still reference the proper source files. It also allows sources to be stored in their own directories, and instances to be created into their own directories.

## An example of a DesignSpace description

```xml
<?xml version="1.0" ?>
<designspace format="3">
    <sources>
        <source filename="../sources/Light/font.ufo" name="master_1">
            <lib copy="1"/>
            <groups copy="1"/>
            <info copy="1"/>
            <location>
                <dimension name="weight" xvalue="0.000000"/>
            </location>
        </source>
        <source filename="../sources/Bold/font.ufo" name="master_2">
            <location>
                <dimension name="weight" xvalue="1.000000"/>
            </location>
        </source>
    </sources>
    <instances>
        <instance familyname="MyFamily" filename="../instance/Medium.ufo" stylename="Medium">
            <location>
                <dimension name="weight" xvalue="0.500000"/>
            </location>
            <info/>
            <kerning/>
        </instance>
    </instances>
</designspace>
```

## The Elements

```xml
<?xml version="1.0" ?>
<designspace format="3">

	<!-- optional: list of axis elements -->
	<axes>
		<axis	
				<!-- required: 4 letter axis tag see OpenType axis tags -->
				tag="aaaa"
				<!-- optional: human readable name -->
				name="nice name for axis"
				<!-- required: minimum value for axis -->
				minimum="72"
				<!-- required: maximum value for axis -->
				maximum="1000"
				<!-- optional: default value for axis -->
				default="96"
		/>
			<!-- optional child element: avar table values, "map"
            <map input="<number>" output="<number>" />
        </axis>
	</axes>

	<!-- required: one sources element -->
	<sources>
		<!-- required: one or more source elements -->
		<source
			<!-- required: path to UFO source -->
			filename=""
			<!-- optional: unique identifier for this source -->
			[name=""]
		>
			<!-- required location element -->
			<location/>

			<!-- optional: flags for which data this master should provide or mute -->
			[<lib copy="1"/>]
			[<groups copy="1"/>]
			[<info [copy="1"][mute="1"]/>]
			[<kerning mute="1"/>]

			<!-- optional: flag to mute a specific source glyph -->
			[<glyph name="" mute="1"/>]
		</source>
	</sources>



	<!-- required: one instances element -->
	<instances>
		<!-- required: one ore more instance elements -->
		<instance
			<!-- required: path to UFO instance -->
			filename=""
			<!-- required: familyname and stylename -->
			familyname=""
			stylename=""
			<!-- optional: some more names -->
			[postscriptfontname=""]
			[stylemapfamilyname=""]
			[stylemapstylename=""]
		>
			<!-- required location element -->
			<location/>
			
			<!-- if present, calculate the font.info for this instance -->
			[<info>
				<!-- if location is present, calculate the font.info at this location -->
				[<location/>]
			</info>]
			
			<!-- if present, calculate the font.kerning for this instance -->
			[<kerning>
				<!-- if location is present, calculate the kerning at this location -->
				[<location/>]
			</kerning>]

			<!-- optional: special definitions for specific glyphs.
				It is expected that an instance will always generate all glyphs.
				The special definitions in the **glyphs** element are expected
				to complement the basic glyphset.
		    -->
			[<glyphs>
				<!-- required: one or more glyph elements -->
				<glyph
					<!-- required: the AGL glyphname -->
					name=""
					<!-- optional: unicode value for this glyph -->
					[unicode=""]
				>

					<!-- optional: alternative location for this glyph. -->
					[<location/>]
				
					<!-- optional: a note for this glyph -->
					[<note>
						nice glyph!
					</note>]


					<!-- optional: a list of alternative sources for this glyph. 
						If present these masters supersede any masters defined by the instance.
						This expects these masters to form a complete designspace.
					-->
					[<masters>
						<!-- required: one or more master elements -->
						<master
							<!-- required: source identifier for this master -->
							source=""
							<!-- optional: alternative glyph for this master -->
							[glyphname=""]
						>
							<!-- required alternative location for this master -->
							<location/>
						</master>
					</masters>]

				</glyph>
			</glyphs>]

		</instance>
	</instances>

</designspace>
```

## The axis element


## The source element

The **source** element stores all the data needed to locate a UFO file and indicates on how to use the different kinds of data in a MutatorMath calculation. The source element can contain a number of child elements. The **location** element is required, it positions the source in the designspace. The **lib**, **groups**, **info**, **kerning** elements are optional. Some types of data can be muted: this means that specific data will not be used to calculate an instance. 

#### Attributes of the source element

*	**filename**
	*	Required, string.
	*	Path to a UFO, **relative to the path of the designspace document.**
*	**name**
	*	Required, string.
	* 	A unique identifier for this source, can be used to refer to this source, for instance in the **master** element.

#### Child elements

*	```<location/>```
	*	Required.
*	```<lib copy="1"/>```:
	* 	If the **lib** element is present and its copy attribute is set to "1", this source will be the provider of font.lib data.
	* 	Only one source can be the lib data provider.
	*	Optional. If the lib element is not present this source will not be the provider of font.lib data.
*	```<groups copy="1"/>```
	*	If the **groups** element is present and its copy attribute is set to "1", this source will be the provider of font.groups data. 
	*	Only one source can be the groups data provider.
	* 	Optional. If the groups element is not present this source will not be the provider of font.groups data.
*	```<info [copy="1"] [mute="1"]/>``` 
	* 	If the **info** element is present and the `copy` attribute is set to "1", this source will be the provider of the non numerical attributes of the font.info.
	*	Only one source can be the info data provider. 
	* 	The optional `mute` attribute when set to "1", indicates the numerical attributes of font.info should excluded from the calculation. 
	* 	If the info element is not present this source will not be the provider of font.info data, but the numerical font.info data will be entered into the calculation.
*	```<kerning mute="1"/>```
	*	Optional. If present, this kerning from this source is to be excluded from calculations.
*	```<glyph name="" mute="1"/>```
	*	Optional. If present, this glyph from this source is to be excluded from calculations.

##### Example

```xml
	<source filename="../sources/Bold/font.ufo" name="master_2">
		<!-- insert this master at weight=1, width=0 -->
	    <location>
	        <dimension name="weight" xvalue="1.000000"/>
	        <dimension name="width" xvalue="0.000000"/>
	    </location>
		<lib copy="1"/>
		<groups copy="1"/>
		<info copy="1"/>
		<kerning mute="1"/>
		<glyph name="AE.alt" mute="1"/>
</source>
```
## The instance element

The `instance` element stores all the data needed to perform a MutatorMath calculation with the previously defined sources and create a new UFO. The instance element can contain a number of child elements. The `location` element is required, it defines a point in the designspace. The `lib`, `groups`, `info` elements are optional. Wrapped in the **glyphs** element, an instance  can contain zero or more **glyph** elements. A glyph element can be used to define exceptions in the designspace geometry: for instance, set a different location for one specific glyph, a different set of sources. 

It is expected the instance generates all glyphs that are available in the sources. An instance may have special definitions for some glyphs, these complement the basic glyphset.

The familyname and stylename are necessary to make UFOs. Some additional names can be added. 

#### Attributes of the instance element

*	**filename**
	*	String, required.
	*	Path to a UFO, **relative to the path of the designspace document.**
	*	If this path does not exist, it should be created when the instance is processed.
*	**familyname**
	* 	String, required.
	*	FamilyName field for the new instance. Corresponds with font.info.familyName.
*	**stylename**
	* 	String, required.
	*	StyleName field for the new instance. Corresponds with font.info.familyName.
*	**postscriptfontname**
	*	String, optional
	*	PostScript FontName, corresponds with font.info.postScriptFontName
*	**stylemapfamilyname**
	*	String, optional
	*	Stylemap familyname, corresponds with font.info.styleMapFamilyName
*	**stylemapstylename**
	*	String, optional
	*	Stylemap stylename, corresponds with font.info.styleMapStyleName

#### Child elements

*	```<location/>```
	*	Required.
*	```<info/>```
	*	Optional.
	*	Add this element if the instance needs to calculate the font.info data. If the info element contains a location element this supercedes the instance location.
*	```<glyphs>...</glyphs>```
	*	Optional. The glyphs element can contain one or more **glyph** elements. 
*	```<kerning/>```
	*	Optional.
	*	Add this element if the instance needs to calculate the font.kerning data. If the kerning element contains a location element this supercedes the instance location.
	*	A kerning element may have one child **location** element. If present this location should be used in calculating the kerning.

#### Example

```xml
<instance familyname="MyFamily" filename="../Medium.ufo" stylename="Medium">
	<location>
		<dimension name="weight" xvalue="0.500000"/>
	</location>
	<glyphs>
        <glyph name="N">
            <location>
                <dimension name="width" xvalue="0.700000"/>
            </location>
            <masters>
                <master glyphname="N.alt" source="master_1">
                    <location>
						<dimension name="weight" xvalue="0.490000"/>
                    </location>
                </master>
                <master glyphname="N.alt" source="master_2">
                    <location>
						<dimension name="weight" xvalue="0.490000"/>
                    </location>
                </master>
            </masters>
        </glyph>
	</glyphs>
</instance>
```


## The location element

The location element describes a point in the designspace. Locations are used to position a source as a master, and to indicate where the instances are to be calculated. Location elements are used in several places in a designspace. A location element has no attributes, but needs to contain at least one **dimension** child elements.

```xml
	<location>
		<dimension name="" xvalue="" [yvalue=""]/>
		[...]
	</location>
```

#### Attributes of the dimension element

*	**name**
	*	Required, string. Name of the dimension. For instance "width" or "weight".
*	**xvalue**
	*	Required, value. A string representation of distance in this dimension.
*	**yvalue**
	*	Optional value if this dimension is to be anisotropic.

#### Examples

```xml
	<!-- location with a single dimension -->
	<location>
		<dimension name="weight" xvalue="0.500000"/>
	</location>

	<!-- location with a single anisotropic dimension -->
	<location>
		<dimension name="weight" xvalue="0.500000" yvalue="0.48728"/>
	</location>

	<!-- location with two dimensions -->
	<location>
		<dimension name="weight" xvalue="0.500000"/>
		<dimension name="width" xvalue="0.500000"/>
	</location>

	<!-- location with seven dimensions just so you know you can't get away with some botched up old multiple master interface. -->
	<location>
		<dimension name="weight" xvalue="0.500000"/>
		<dimension name="width" xvalue="0.500000"/>
		<dimension name="optical" xvalue="72"/>
		<dimension name="serif" xvalue="-100"/>
		<dimension name="slant" xvalue="4"/>
		<dimension name="wobble" xvalue="1000"/>
		<dimension name="splatter" xvalue="1000", yvalue="400"/>
	</location>

```

## The glyph element

The optional **glyph** element can be used in a instance element to store information about masters and locations that are different from the ones defined for the instance.

```xml
	<glyphs>
		<!-- required: one or more glyph elements -->
		<glyph
			<!-- required: the AGL glyphname -->
			name=""
			<!-- optional: unicode value for this glyph -->
			[unicode=""]
		>

			<!-- optional: alternative location for this glyph. -->
			[<location/>]
		
			<!-- optional: a note for this glyph -->
			[<note>
				nice glyph!
			</note>]

			[<masters>
				...a number of master elements
			</masters>]

		</glyph>
	</glyphs>
```

#### Attributes of the glyph element

*	**name**
	*	Required, string. The glyph name.
*	**unicode**
	*	Optional, hex. The unicode value of the glyph, expressed as a string in the format **"0xFF"**. If no unicode value is given, use the unicode for this glyph used in the sources. 

#### Child elements of the glyph element

*	```<location/>```
	*	Optional, location element. If the location element is present it will be the location for this glyph. If it is not present, the location defined for the instance will be used.
*	```<note>...</note>```
	*	Optional, string. Corresponds with the **defcon** glyph.note attribute. 
*	```<masters>...</masters>```
	* a list of master elements.

## The master element

Used in the masters element to specify which glyphs from which sources have to be used for this glyph.

```xml
	<masters>
		<master
			[source="sourcename"]
			[glyphname='a.alt']
		>
			[<location/>]
		</master>
		...
	</masters>
```

#### Attributes of the master element

*	**source**
	*	Optional, string.
	*	Name of the source, must match with the **name** attribute of exactly one **source** element.
*	**glyphname**
	*	Optional, string
	*	Alternative glyphname if data is to come from a different glyph.

#### Child elements of the master element

*	**location**
	*	Optional. 
	*	If a location element is present, use this alternative location for this master. If no location is present, use the location defined for the source. 


## Notes on this document

Initial version of this specification. The package is rather new and changes are to be expected.

