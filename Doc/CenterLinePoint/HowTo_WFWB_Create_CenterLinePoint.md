
#### <center>WorkFeature-WB :<br></center>
#### <center>Work Feature workbench with parametric objects For FreeCAD  <br>
![alt](./Images/Title02.png)
# <center>How to create "Center Line Point(s)"</center>


Updated in August 2019
 
 
github : https://github.com/Rentlau/WorkFeature-WB

# Objective

See the usage of the <b>"CenterLinePoint"</b> Button : ![alt](./Images/WF_centerLinePoint.svg)

![alt](./Images/Tooltip.png)

# Summary

| Object(s) Selected                          | Object(s) created  |
|:------|:------|
| **1 Edge**  ![alt](./Images/CenterLinePoint_001.png)| **1 Point** in the middle ![alt](./Images/CenterLinePoint_002.png)|
| **1 Edge**  ![alt](./Images/CenterLinePoint_001.png)| **3 Points** ![alt](./Images/CenterLinePoint_004.png)|

# How to

A - First open FeeCAD application         | B -Select the FreeCAD File | C - And Select the <b>WorkFeature</b> Workbench 
:-------------------------:|:-------------------------:|:-------------------------:
![alt](./Images/init01.png) | ![alt](./Images/init02.png)| ![alt](./Images/init03.png)

- Click on the **Create Point(s)** button without any object selection will end up 
with a **Macro CenterLinePoint** Popup window message (depending of *Time Out* value 
chosen in General Preference Panel)
and a Parameter window in **Tasks Tab** Panel.
 
In **Tasks Tab** Panel you can define parameters for the **"CenterLinePoint"** function :<br>
![alt](./Images/CenterLinePoint_003.png)

- Click "OK button" on **Macro CenterLinePoint** Popup window message and go to **Tasks Tab** panel to define parameters.<br><br>
- Three parameters can be defined :<br>
    - The <u>**Number of parts**</u>: n (2 by default)<br>
        The selected line(s) can be cut in 2 parts if you want to get the middle point of the line(s).<br>
        The number (n) indicates in how many Parts each selected parent Line/Edge(s) will be cut in.<br>
        Limits : (Min: 2, Max: 100).<br>
    - **<u>Point's location</u>**:
        - If **Check box** checked then points will be created at each ends of Parts. Even at extrema!
            Ie : if Number of Parts is 3 then 5 points will be created!
        - **Part's end number**
            The number indicates at which part's end the point will be located.
            - If the Number of parts is 2 and Point at part's end 1,
            this means that the point will be located in the middle of the Line.
            1/2 means middle of the segment !
            - If the Number of parts is 2 and Point at part's end 2,
            this means that the point will be located at the end of the Line.
            Note this number can be negative.
            - If the Number of parts is 2 and Point at part's end -1,
            this means that the point will be located before the start of the Line.
             Limits : [-1000:1000]. Negative value are allowed.

         **Check box** and **Part's end number** are exclusive!  

Once defined you can click "OK button" of **Tasks Tab** panel to keep these parameters in memory. 

Note that you need to open again this panel in order to change these parameters in memory.

**To generate points:**
- Select one or several Line/Edge(s)
 (you can also select 2 points in place of one Line/Edge) **and/or**
- Select one Plane/Face to process all (4) Edges **and/or**
- Select one Object to process all Edges at once


- Then Click on the <b>"CenterLinePoint"</b> button.

- And new <b>Point(s)</b> are created under **Model Panel** below the **WorkFeature/WorkPoints_P** group (P means Parametric) :<br>

A - Parameters        | B - Results | C - Objects
:-------------------------:|:-------------------------:|:-------------------------:
![alt](./Images/CenterLinePoint_005.png)| ![alt](./Images/CenterLinePoint_002.png)| ![alt](./Images/CenterLinePoint_011.png)
![alt](./Images/CenterLinePoint_006.png)| ![alt](./Images/CenterLinePoint_007.png)| ![alt](./Images/CenterLinePoint_010.png)
![alt](./Images/CenterLinePoint_008.png)| ![alt](./Images/CenterLinePoint_009.png)| ![alt](./Images/CenterLinePoint_012.png)

- You can now play with **Parametric** Parameters of the new Point :<br><br>
![alt](./Images/CenterLinePoint_013.png)
