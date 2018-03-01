# -*- coding: utf-8 -*-
import FreeCAD as App
if App.GuiUp:
    import FreeCADGui as Gui
from WF_print import print_msg

tolerance=1e-12

def init_min_max():
    """ Return min and max values from System.
    min_val, max_val = init_min_max
    """
    import sys
    if sys.version < '3.0.0':    
        max_val = sys.maxint
        min_val = -sys.maxint - 1
    else:# for python 3.0 use sys.maxsize
        max_val = sys.maxsize
        min_val = -sys.maxsize - 1
    return min_val, max_val


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
    """ Return true if the 2 points are equal.
    """
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


def alongLinePoint(edge, index, number):
    """ Return the point at index/number of the Line.
    1/2 means middle of the line.
    1/3 means one third of the line...
    """
    Vector_A = edge.Vertexes[0].Point
    Vector_B = edge.Vertexes[-1].Point
    distance = Vector_B.sub(Vector_A).Length / 2
    
    if number != 0:
        distance = index * (edge.Length / number)    
    Vector_A = Vector_A.add(Vector_B.sub(Vector_A).normalize().multiply( distance ))    

    return Vector_A


def meanVectorsPoint(vertexes):
    """ Return the mean point of all selected Vectors. 
    """
    Vector_mean = App.Vector(0.0,0.0,0.0)
    m_vertx = vertexes
    m_num = len(m_vertx)
    
    if vertexes == None:
        print_msg("ERROR : vertexes == None, leaving meanVectorsPoint()")
        return Vector_mean
    if m_num < 1:
        print_msg("ERROR : len(vertexes) < 1 , meanVectorsPoint()")
        return Vector_mean
    m_list = []
    for m_vert in m_vertx:
        m_list.append(m_vert.x)
        m_list.append(m_vert.y)
        m_list.append(m_vert.z)
        
    import numpy
    V = numpy.array(m_list)    
    Vre = V.reshape(m_num,3)
    C = sum(Vre,0)/m_num
        
    Vector_mean = App.Vector(C[0], C[1] , C[2])

    return Vector_mean


def minMaxVectorsLimits(vertexes):
    """ Return the min and max limits along the 3 Axis for all selected Vectors.
    """
    xmax = xmin = ymax = ymin = zmax = zmin = 0
    m_vertx = vertexes
    m_num = len(m_vertx)
    
    if vertexes == None:
        print_msg("ERROR : vertexes == None, leaving minMaxVectorsLimits()")
        return xmax, xmin, ymax, ymin, zmax, zmin

    if m_num < 1:
        print_msg("ERROR : len(vertexes) < 1 , leaving minMaxVectorsLimits()")
        return xmax, xmin, ymax, ymin, zmax, zmin

    min_val, max_val = init_min_max()        
    xmin = ymin = zmin = max_val
    xmax = ymax = zmax = min_val

    for m_vert in m_vertx:
        xmax = max(xmax, m_vert.x)
        xmin = min(xmin, m_vert.x)
        ymax = max(ymax, m_vert.y)
        ymin = min(ymin, m_vert.y)
        zmax = max(zmax, m_vert.z)
        zmin = min(zmin, m_vert.z)
    
    return xmax, xmin, ymax, ymin, zmax, zmin


def intersectPerpendicularLine(A, B, C,):
    """ Return the intersection between the Line L defined by A and B
    and the Line perpendicular crossing the point C.
    This is also the projection of C onto the Line L.
    Return aso the distance between C and the the projection.
    Return also the symetric point of C versus the Line.
    """
    import math
    # L is the line defined by 2 points A(ax, ay, az) and B(bx, by, bz), and
    # may be also defined as the line crossing A(ax, ay, az) and along the 
    # direction AB = U(bx-ax, by-ay, bz-az)
    # If U(ux, uy, uz) = U(bx-ax, by-ay, bz-az) the Line L is the set of 
    # points M as defined by eq(1):
    # Vector(MA) = k * Vector(U)
    # with k Real 
    if A == B:
        return None
    ax, ay, az = A.x, A.y, A.z
    bx, by, bz = B.x, B.y, B.z
    cx, cy, cz = C.x, C.y, C.z
    ux, uy, uz = bx - ax, by - ay, bz - az
    #U = App.Vector(ux, uy, uz)
    # We look for T(tx, ty, tz) on the Line L
    # eq(1) in parametric form; k exists and follows eq(2):
    # tx = ax + k * ux 
    # ty = ay + k * uy
    # tz = az + k * uz
    
    # and vector V(vx, vy, vz) defined by point C and point T
    # vx, vy, vz = tx - cx, ty - cy, tz - cz
    # V must be perpendicular to the Line L 
    # We consider Dot product between U and V and give us eq(3) 
    # U.V = 0
    # so ux * vx + uy * vy + uz * vz = 0
    # ux * (tx - cx) + uy * (ty - cy) + uz * (tz - cz) = 0
    # ux * (ax + k * ux  - cx) + uy * (ay + k * uy - cy) + uz * (az + k * uz  - cz) = 0
    # ux*ax + ux*(k*ux) - ux*cx + uy*ay + uy*(k*uy) - uy*cy +  uz*az + uz*(k*uz) - uz*cz = 0
    if (ux*ux + uy*uy + uz*uz) == 0.0:
        return None
    k = (ux*cx + uy*cy + uz*cz - ux*ax - uy*ay - uz*az)/(ux*ux + uy*uy + uz*uz)   
    tx = ax + k * ux 
    ty = ay + k * uy
    tz = az + k * uz
    T = App.Vector(tx, ty, tz)
    vx, vy, vz = tx - cx, ty - cy, tz - cz
    V = App.Vector(vx, vy, vz)
    distance = math.sqrt(V.dot(V))
    Tprime = T + V
    
    return T, distance, Tprime

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


def properties_plane(Plane_User_Name):
    """ Define the properties of a Work feature Plane.
    PointColor
    LineColor
    ShapeColor
    Transparency  
    """
    try:
        Gui.ActiveDocument.getObject(Plane_User_Name).PointColor = (1.00,0.67,0.00)
    except:
        print_msg("Not able to set PointColor !")
    try:
        Gui.ActiveDocument.getObject(Plane_User_Name).LineColor = (1.00,0.67,0.00)
    except:
        print_msg("Not able to set LineColor !")
    try:
        Gui.ActiveDocument.getObject(Plane_User_Name).ShapeColor = (0.00,0.33,1.00)
    except:
        print_msg("Not able to set ShapeColor !")
    try:
        Gui.ActiveDocument.getObject(Plane_User_Name).Transparency = 75
    except:
        print_msg("Not able to set Transparency !")
        
    return 
