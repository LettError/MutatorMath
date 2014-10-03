MutatorMath DesignSpace Format
==============================

![A MutatorMath Designspace Document Icon](designspaceDocumentIcon.png)

The UFO support in MutatorMath introduces a useful storage format in xml for MutatorMath designspaces. This document describes the format. 

## Document structure

A document can contain a single `designspace` top level element. The current format version is `3`.

*	The `sources` element contains one or more `source` elements.
* 	The `instances` element contains one or more `instance` elements.

Note: MutatorMath makes a difference between "masters" and "sources". Source indicates the file. Master indicates a particular use in a MutatorMath calculation.

```xml
<?xml version="1.0" ?>
<designspace format="3">
	<sources>
		... a number of source elements
	</sources>
	<instances>
		...	a number of instance elements
	</instances>
</designspace>
```

## The source element

The `source` element stores all the data needed to locate a UFO file and indications on how to use it in a MutatorMath calculation. The source element can contain a number of child elements. The `location` element is required. The `lib`, `groups`, `info`, `kerning` elements are optional. Some types of data can be muted. This means that specific data will not be used to calculate an instance. 

#### Attributes of source element

*	**filename**
	*	string, required.
	*	Path to a UFO, relative to the path of the designspace document.
*	**name**
	*	string, required.
	* 	A unique identifier for this source, can be used to refer to this source.

#### Child elements

*	```<location/>```
	*	Required, see description below.
*	```<lib [copy="1"]/>```:
	* 	If the lib element is present and its copy attribute is set to "1", this source will be the provider of font.lib data.
	* 	Only one source can be the lib data provider.
	*	Optional. If the lib element is not present this source will not be the provider of font.lib data.
*	```<groups [copy="1"]/>```
	*	If the groups element is present and its copy attribute is set to "1", this source will be the provider of font.groups data. 
	*	Only one source can be the groups data provider.
	* 	Optional. If the groups element is not present this source will not be the provider of font.groups data.
*	```<info [copy="1"] [mute="1"]/>``` 
	* 	If the info element is present and the `copy` attribute is set to "1", this source will be the provider of the non numerical attributes of the font.info.
	*	Only one source can be the info data provider. 
	* 	The optional `mute` attribute when set to "1", indicates the numerical attributes of font.info should not be entered into the calculation. 
	* 	Optional. If the info element is not present this source will not be the provider of font.info data, but the numerical font.info data will be entered into the calculation.
*	```<kerning [mute="1"]/>```
	*	Optional. If the kerning is muted it will not be used in the calculation. 

##### Example

```xml
	<source filename="../sources/Bold/font.ufo" name="master_2">
	    <location>
	        <dimension name="weight" xvalue="1.000000"/>
	        <dimension name="width" xvalue="0.000000"/>
	    </location>
	</source>
```
## The instance element

The `instance` element stores all the data needed to perform a MutatorMath calculation and create a new UFO. The isntance element can contain a number of child elements. The `location` element is required. The `lib`, `groups`, `info` elements are optional. An instance element can contain zero or more **glyph** elements. A glyph element can be used to define exceptions in the designspace geometry: for instance, set a different location for one specific glyph, a different set of sources. 

#### Attributes of instance element

*	**filename**
	*	String, required.
	*	Path to a UFO, relative to the path of the designspace document.
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
	*	Required, see description below.
*	```<info/>```
	*	Optional.
	*	Add this element if the instance needs to calculate the font.info data.
*	```<kerning/>```
	*	Optional.
	*	Add this element if the instance needs to calculate the font.kerning data.
*	```<glyph/>```
	*	Optional. The glyph element 

#### Example

```xml
<instance familyname="MyFamily" filename="../instance/Medium.ufo" stylename="Medium">
	<location>
		<dimension name="weight" xvalue="0.500000"/>
	</location>
</instance>
```


## The location element

The location element describes a point in the designspace. Locations are used to position a source as a master, and to indicate where the instances are to be calculated. A location element usually contains one or more dimension child elements.

#### dimension element

*	```<dimension name="" xvalue="" [yvalue=""]/>```
	*	The required **name** attribute is the name of the dimension. For instance "width" or "weight".
	*	The required **xvalue** attribute contains a string representation of distance in this dimension.
	*	Use the optional **yvalue** attribute if this dimension is to be anisotropic.

#### Example

```xml
	<!-- location with one dimension -->
	<location>
		<dimension name="weight" xvalue="0.500000"/>
	</location>

	<!-- location with one anisotropic dimension -->
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

## Notes on this document

Initial version of this specification. The package is rather new and changes are to be expected.

