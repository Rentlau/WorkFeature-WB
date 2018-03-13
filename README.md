
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

# <center>WorkFeature-WB :<br> <img src="./Resources/Icons/WF_wf.svg"></center>
### <center>Work Feature workbench with parametric objects For FreeCAD </center>
----------

Updated in March 2018

Workbench utility to create:
- Points (Mid points, Extremum points, Center of circle, Center of Plane,),
- Lines (From 2 points,),
- Planes (From 1 point and 1 Line, Perpendicular from 1 point and 1 Line,),
 
 
github : https://github.com/Rentlau/WorkFeature-WB

Post on FreeCAD Forum : https://forum.freecadweb.org/viewtopic.php?f=9&t=27195

<img src="./Doc/Images/Title02.png?1">

 

 

<b>Version 2018-03</b> <center>by Rentlau_64</center>

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

The development of the macro is done with Python 2.7

### Abstract
----------

Quite all objects created with functions from this workbench are parametric. That mean if the "parent" object change, all children objects will change accordingly !
  

### List of available functions
----------

| Icon                           | Function  |
|:------|:------|
|![alt](./Resources/Icons/WF_centerLinePoint.svg)  | Create Point(s) at Center location of each selected Line(s). <br>Can also create several Points along selected Line(s)|
|![alt](./Resources/Icons/WF_extremaLinePoint.svg)  | Create Point(s) at edges of selected Line(s). |
|![alt](./Resources/Icons/WF_centerCirclePoint.svg)  | Create Point(s) at center location of selected Circle(s). |
|![alt](./Resources/Icons/WF_centerFacePoint.svg)  | Create Point(s) at center location of selected Plane(s). |
|![alt](./Resources/Icons/WF_twoPointsLine.svg)  | Create Line(s) in between two selected Points. |
|![alt](./Resources/Icons/WF_linePointPlane.svg)  | Create Plane(s) crossing a Point and a Line. |
|![alt](./Resources/Icons/WF_perpendicularLinePointPlane.svg)  | Create Planes(s) crossing a Point and perpendicular to a Line. |

### Documentations
----------

Find some more detailed documentations in ./Doc directory :
  - [How to create "Center Line Point(s)"<img src="./Resources/Icons/WF_centerLinePoint.svg">](./Doc/HowTo_WFWB_Create_CenterLinePoint.pdf). <br>

### Tested on FreeCAD

A - 0.16.6712         | B - 0.17.13142
:-------------------------:|:-------------------------:
![alt](./Doc/Images/Version16.png?1) | ![alt](./Doc/Images/Version17.png?1)
