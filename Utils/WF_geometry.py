# -*- coding: utf-8 -*-
import FreeCAD as App
if App.GuiUp:
    import FreeCADGui as Gui
from WF_print import print_msg

tolerance=1e-12

def isColinearVectors(A, B, C, tolerance=1e-12):
    """ Return true if the 3 points are aligned.
    """
    Vector_1 = B - A
    Vector_2 = C - B
    Vector_3 = Vector_1.cross(Vector_2)
        
    if abs(Vector_3.x) <= tolerance and abs(Vector_3.y) <= tolerance and abs(Vector_3.z) <= tolerance:
        return True
    
    return False
    

def isEqualVectors(A, B, tolerance=1e-12):
    Vector = B - A
    
    if abs(Vector.x) <= tolerance and abs(Vector.y) <= tolerance and abs(Vector.z) <= tolerance:
        return True
    
    return False
    
    
def centerLinePoint(edge):
    """ Return the center point of the Line.
    """
    Vector_A = edge.Vertexes[0].Point
    Vector_B = edge.Vertexes[-1].Point
    Vector_AB = Vector_B + Vector_A
    
    return Vector_AB.multiply(0.5)


def alongLinePoint(edge, index, number,info=0):
    """ Return the point at index/number of the Line.
    """
    Vector_A = edge.Vertexes[0].Point
    Vector_B = edge.Vertexes[-1].Point
    distance = Vector_B.sub(Vector_A).Length / 2
    
    if number != 0:
        distance = index * (edge.Length / number)    
    Vector_A = Vector_A.add(Vector_B.sub(Vector_A).normalize().multiply( distance ))    

    return Vector_A


def printPoint(point, msg=""):
    """ Print x,y and z of a point:vector.
    """    
    if point.__class__.__name__ != "Vector":
        print_msg("Not a Vector to print !")
        return

    print_msg(str(msg) + " " +
              "x =" + str(point.x) + ", "
              "y =" + str(point.y) + ", "
              "z =" + str(point.z))
    return


def propertiesPoint(Point_User_Name):
    """ Define the properties of a Work feature Point.
    PointColor
    PointSize
    Transparency  
    """
    try:
        Gui.ActiveDocument.getObject(Point_User_Name).PointColor = (1.00,0.67,0.00)
    except:
        print_msg("Not able to set PointColor !")
    try:
        Gui.ActiveDocument.getObject(Point_User_Name).PointSize = 5.00 
    except:
        print_msg("Not able to set PointSize !")
    try:
        Gui.ActiveDocument.getObject(Point_User_Name).Transparency = 0
    except:
        print_msg("Not able to set Transparency !")
        
    return 

def propertiesLine(Line_User_Name, color=(1.00,0.67,0.00)):
    """ Define the properties of a Work feature Line.
    PointColor
    LineColor
    LineWidth
    PointSize
    Transparency  
    """
    try:
        Gui.ActiveDocument.getObject(Line_User_Name).PointColor = color
    except:
        print_msg("Not able to set PointColor !")
    try:
        Gui.ActiveDocument.getObject(Line_User_Name).LineColor = color
    except:
        print_msg("Not able to set LineColor !")
    try:
        Gui.ActiveDocument.getObject(Line_User_Name).LineWidth = 2.00 
    except:
        print_msg("Not able to set LineWidth !")
    try:
        Gui.ActiveDocument.getObject(Line_User_Name).PointSize = 2.00 
    except:
        print_msg("Not able to set PointSize !")
    try:
        Gui.ActiveDocument.getObject(Line_User_Name).Transparency = 0
    except:
        print_msg("Not able to set Transparency !")
        
    return  
