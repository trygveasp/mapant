# mapant
Python library to process mapant data to e.g. garmin custom maps

Most garmin gps support the CustomMap input type where you can add a raster images to your GPS. Raster image means 
that you have an image background but no points to e.g navigate to. For this you will need an img format like 
available from OpenStreetMap (OSM) via e.g. http://www.frikart.no/index.html

The mapant project available at https://mapant.no provides the possibility to download any area in Norway as png file and a 
world file with suffix .pgw. Those two files are expected as input to this package.

Example of a kmz file generated from the example data and visualized in google earth. 

![alt](https://github.com/trygveasp/mapant/tree/main/src/examples/mapant.png)

The result kmz file can be uploaded to your garmin GPS in the /GARMIN/CustomMaps folder. 
See alsp step 14,15, and 16 in https://support.garmin.com/en-US/?faq=cVuMqGHWaM7wTFWMkPNLN9

# Pre-requirements:
ImageMagick
https://imagemagick.org/script/download.php

# Installation:
This package is available from pypi with the python pip intallation command
> pip3 install mapant 

Or in a local user installation:
> pip3 install --user mapant 

#Examples:  

Get data to test on. For example from the examples diectory.
> wget -b https://github.com/trygveasp/mapant/tree/main/src/examples/mapant-export-211859-6656711-215781-6660648.pgw
>
> wget -b https://github.com/trygveasp/mapant/tree/main/src/examples/mapant-export-211859-6656711-215781-6660648.png

Run the generation
> mapant2kml -w mapant-export-211859-6656711-215781-6660648.pgw -i mapant-export-211859-6656711-215781-6660648.png 
>-o examples/Example.kmz -nx 4016 -ny 4031 -dx 1536 -dy 1536
