
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

# <center>WorkFeature-WB :<br> <img src="./Resources/Icons/WF_wf.svg"></center>
### <center>Work Feature workbench with parametric objects For FreeCAD </center>
----------

Updated in March 2018

Workbench utility to create:
- Points (Mid points, Extremum points),
- Lines (From 2 points,),
- Planes (From 1 point and 1 Line),
 
 
github : https://github.com/Rentlau/WorkFeature-WB

Post on FreeCAD Forum : https://forum.freecadweb.org/viewtopic.php?f=9&t=27195

<img src="./Doc/Images/Title01.png">

 

 

<b>Version 2018-02</b> <center>by Rentlau_64</center>

###  Installing
----------

Download and install FreeCAD from [wiki Download page](http://www.freecadweb.org/wiki/Download) and install this workbench by (e.g, on Linux system): 
  - Cloning the repository from github (https://github.com/Rentlau/WorkFeature-WB) using:

```
mkdir /home/path_to_WorkFeature-WB
cd /home/path_to_WorkFeature-WB/
git clone https://github.com/Rentlau/WorkFeature-WB.git
```

  - or download from github the zip file : <b>WorkFeature-WB-master.zip</b> and extract it into "/home/path_to_WorkFeature-WB/"

  - Then by making a symbolic link or copy the folder into "freecad installation folder"/Mod (most of the time <b>/home/.FreeCAD/Mod/</b>) :

```
ln -s (path_to_WorkFeature-WB) (path_to_freecad)/Mod
```

### Requirements
----------

- <b>FreeCAD</b> : Download and install FreeCAD from [wiki Download page](http://www.freecadweb.org/wiki/Download).<br>
- <b>python numpy</b> module

The development of the macro is done with Python2.7

### Abstract
----------

Quite all objects created with functions from this workbench are parametric. That mean if the "parent" object change, all children objects will change accordingly !
  

### Documentations
----------

Find some documentation in ./Doc directory :
  - [How to create "Center Line Point(s)"<img src="./Resources/Icons/WF_centerLinePoint.svg">](./Doc/HowTo_WFWB_Create_CenterLinePoint.pdf). <br>

### Tested on FreeCAD

A - 0.16.6712         | B - 0.17.13142
:-------------------------:|:-------------------------:
![alt](./Doc/Images/Version16.png?1) | ![alt](./Doc/Images/Version17.png?1)
