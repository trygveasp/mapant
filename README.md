# mapant
Python library to process mapant data to e.g. garmin custom maps

Most garmin gps support the CustomMap input type where you can add a raster images to your GPS. Raster image means 
that you have an image background but no points to e.g navigate to. For this you will need an img format like 
available from OpenStreetMap (OSM) via e.g. http://www.frikart.no/index.html

The mapant project available at https://mapant.no provides the possibility to download any area in Norway as png file and a 
world file with suffix .pgw. Those two files are expected as input to this package.

Example of a kmz file generated from the example data and visualized in google earth. 

![alt](https://raw.githubusercontent.com/trygveasp/mapant/main/examples/mapant.png)

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

### Examples:  

Get data to test on. For example from the examples diectory (by wget or simply download the data).
> wget https://raw.githubusercontent.com/trygveasp/mapant/main/examples/mapant-export-211859-6656711-215781-6660648.pgw
>
> wget https://raw.githubusercontent.com/trygveasp/mapant/main/examples/mapant-export-211859-6656711-215781-6660648.png

Run the generation
> mapant2kml -w mapant-export-211859-6656711-215781-6660648.pgw -i mapant-export-211859-6656711-215781-6660648.png 
>-o examples/Example.kmz -nx 4016 -ny 4031 -dx 1536 -dy 1536

See also the unit tests in tests directory


# Tutorial on windows

User guide mapant2kml on windows

### Install python

Open prompt:
 - Windows key + x
 - Run (kjør)
 - Type cmd.exe
 - Type python
 
For me a Windows Store window popped up
Install the free app for Python 3.8

### Install pip
See also https://phoenixnap.com/kb/install-pip-windows (PIP is the Python repository 
package)
 - download https://bootstrap.pypa.io/get-pip.py
 - run “python get-pip.py”

### Install mapant with pip
python -m pip install mapant

So where is it installed? Try running: “pip3 -V”
This will show you the pip installation. The mapant2kml script is installed in the 
Scripts directory in the same location structure. See also example part.

### Install dependency
Mapant2kml has (at least for now) one external dependency in the convert program from 
ImageMagick (https://imagemagick.org/script/download.php) (free, open source)

Install one of the installations, e.g. ImageMagick-7.0.10-35-Q16-HDRI-x64-dll.exe

NB! Tick the box about legacy utilities (convert) which is NOT ticked by default

### Run mapant example
Now we are ready to run the example from https://github.com/trygveasp/mapant#examples. 
Download the data and run mapant2kml as described.


### Visualization of your finished kmz file
Install google earth
open Example.kmz which we generated
You should get the example map shown above.

There is plenty of room for improvement in this windows tools by experienced windows user unlike myself. 
Please come with suggestions on how to thing different and in a simpler way.
