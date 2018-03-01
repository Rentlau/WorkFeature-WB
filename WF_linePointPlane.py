# -*- coding: utf-8 -*-
"""
***************************************************************************
*   FreeCAD Work Feature workbench                                        *
*                                                                         *
*   Copyright (c) 2017 <rentlau_64>                                       *
*   Code rewrite by <rentlau_64> from Work Features macro:                *
*   https://github.com/Rentlau/WorkFeature                                *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *  
*   http://www.freecadweb.org                                             *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the COPYING and COPYING.LESSER text files.             *
*   http://en.wikipedia.org/wiki/LGPL                                     *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA or see <http://www.gnu.org/licenses/>                             *
***************************************************************************
"""
__title__="Macro LinePointPlane"
__author__ = "Rentlau_64"
__brief__ = '''
Macro LinePointPlane.
Creates a parametric LinePointPlane from a point and a line
'''
###############

###############
import sys
import os.path
import FreeCAD as App
if App.GuiUp:
    import FreeCADGui as Gui
import Part
from PySide import QtGui,QtCore
import WF
from WF_Objects_base import WF_Plane

# get the path of the current python script 
path_WF = os.path.dirname(__file__)
 
path_WF_icons     = os.path.join(path_WF, 'Resources', 'Icons')
path_WF_utils     = os.path.join(path_WF, 'Utils')
path_WF_resources = os.path.join(path_WF, 'Resources')
path_WF_ui        = os.path.join(path_WF, 'Resources', 'Ui')
 
if not sys.path.__contains__(str(path_WF_utils)):
    sys.path.append(str(path_WF_utils))
    sys.path.append(str(path_WF_ui))
     
try:
    from WF_selection import Selection, getSel
    from WF_print import printError_msg, print_msg
    from WF_directory import createFolders, addObjectToGrp
    from WF_geometry import *
    #from WF_utils import *
except:
    print "ERROR: cannot load WF modules !!"
    sys.exit(1)

###############
m_icon          = "/WF_linePointPlane.svg"
m_dialog        = "/WF_UI_linePointPlane.ui"
m_dialog_title  = "Define extension of the plane."

m_exception_msg = """Unable to create Plane :
    Select one Line and one Point only
    with the Point NOT on the Line !

Go to Parameter(s) Window in Task Panel!"""
m_result_msg    = " : Plane created !"
m_menu_text     = "Plane = (Point, Axis)"
m_accel         = ""
m_tool_tip      = """<b>Create Plane</b> crossing one Point and one Line.<br>
...<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br> 
 - a Parameter(s) Window in Task Panel!</i>
""" 
m_extension      = 150.0
###############

class LinePointPlanePanel:  
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
        self.form.UI_Plane_extension.setText(str(m_extension))
                        
    def accept(self):
        global m_extension
        m_extension = float(self.form.UI_Plane_extension.text())        
  
        if WF.verbose() != 0:
            print_msg("m_extension = " + str(m_extension))
            
        Gui.Control.closeDialog()
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) != 0:
                run()
        return True
    
    def reject(self):
        Gui.Control.closeDialog()
        return False
    
    def shouldShow(self):    
        return (len(Gui.Selection.getSelectionEx(App.activeDocument().Name)) == 0 )   


def makeLinePointPlaneFeature(group):
    """ Makes a LinePointPlane parametric feature object. 
    into the given Group
    Returns the new object.
    """ 
    m_name = "LinePointPlane_P"
    m_part = "Part::FeaturePython"     
    
    try:     
        m_obj = App.ActiveDocument.addObject(str(m_part),str(m_name))
        if group != None :
            addObjectToGrp(m_obj,group,info=1)
        LinePointPlane(m_obj)
        ViewProviderLinePointPlane(m_obj.ViewObject)
    except:
        printError_msg( "Not able to add an object to Model!")
        return None
    
    return m_obj


class LinePointPlane(WF_Plane):
    """ The LinePointPlane feature object. """
    # this method is mandatory
    def __init__(self,selfobj):
        self.name = "LinePointPlane"
        WF_Plane.__init__(self, selfobj, self.name)
        """ Add some custom properties to our LinePointPlane feature object. """
        selfobj.addProperty("App::PropertyLinkSub","Edge",self.name,
                            "Input edge")
        selfobj.addProperty("App::PropertyLinkSub","Point",self.name,
                            "Input point")
        selfobj.addProperty("App::PropertyFloat","Extension",self.name,
                            "Extension at extrema").Extension=150.0 
        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden 
        selfobj.setEditorMode("Edge", 1)
        selfobj.setEditorMode("Point", 1)
        selfobj.Proxy = self    
     
    # this method is mandatory   
    def execute(self,selfobj): 
        """ Print a short message when doing a recomputation. """
        if WF.verbose() != 0:
            App.Console.PrintMessage("Recompute Python LinePointPlane feature\n")
        
        if selfobj.Edge != None and selfobj.Point != None :
            points = []
            
            n1 = eval(selfobj.Point[1][0].lstrip('Vertex'))
            point_C = selfobj.Point[0].Shape.Vertexes[n1-1].Point
            points.append(point_C)
            
            n2 = eval(selfobj.Edge[1][0].lstrip('Edge'))
            point_A = selfobj.Edge[0].Shape.Edges[n2-1].Vertexes[0].Point
            point_B = selfobj.Edge[0].Shape.Edges[n2-1].Vertexes[-1].Point

            points.append(point_A)
            points.append(point_B)
            
            if isColinearVectors(point_A, point_B, point_C, tolerance=1e-12):
                printError_msg(m_exception_msg, title="Macro LinePointPlane")
                return
            
            Vector_Center = meanVectorsPoint(points)
            xmax, xmin, ymax, ymin, zmax, zmin = minMaxVectorsLimits(points)

            length = xmax - xmin
            if (ymax - ymin) > length:
                length = ymax - ymin
            if (zmax - zmin) > length:
                length = zmax - zmin
            if length == 0:
                length = 10.0
                         
            Edge_Vector = point_B - point_A
            AC_Vector = point_C - point_A
            
            Edge_Length = length
            if selfobj.Extension == 0.0 :
                selfobj.Extension = 100.0
            if selfobj.Extension < 0.0 :
                selfobj.Extension *= -1
                
            if selfobj.Extension > 100.0 :
                Edge_Length = length * (selfobj.Extension / 100.0)
            elif m_extension < 100.0 :
                Edge_Length = length / (selfobj.Extension / 100.0)
            
            Plane_Point  = Vector_Center
            Plane_Normal = Edge_Vector.cross( AC_Vector )
                        
            Plane_face = Part.makePlane(Edge_Length, Edge_Length, 
                                        Plane_Point, Plane_Normal )
            Plane_Center = Plane_face.CenterOfMass
            Plane_Translate =  Plane_Point - Plane_Center
            Plane_face.translate( Plane_Translate )
            selfobj.Shape = Plane_face
            
            properties_plane(selfobj.Label)

                
    def onChanged(self, selfobj, prop):
        """ Print the name of the property that has changed """
        # Debug mode
        if WF.verbose() != 0:
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")
        
        if selfobj.parametric == 'No' :
            selfobj.setEditorMode("Extension", 1)
        else :
            selfobj.setEditorMode("Extension", 0)
            
        if prop == "Extension":            
            selfobj.Proxy.execute(selfobj)

        WF_Plane.onChanged(self, selfobj, prop)   
    
            
class ViewProviderLinePointPlane:
    global path_WF_icons
    icon = '/WF_linePointPlane.svg'  
    def __init__(self,vobj):
        """ Set this object to the proxy object of the actual view provider """
        vobj.Proxy = self
    
    # this method is mandatory    
    def attach(self, vobj): 
        self.ViewObject = vobj
        self.Object = vobj.Object
  
    def setEdit(self,vobj,mode):
        return False
    
    def unsetEdit(self,vobj,mode):
        return

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
    
    # subelements is a tuple of strings
    def onDelete(self, feature, subelements): 
        return True
    
    # This method is optional and if not defined a default icon is shown.
    def getIcon(self):        
        """ Return the icon which will appear in the tree view. """
        return (path_WF_icons + ViewProviderLinePointPlane.icon)
           
    def setIcon(self, icon = '/WF_linePointPlane.svg'):
        ViewProviderLinePointPlane.icon = icon
  
            
class CommandLinePointPlane:
    """ Command to create LinePointPlane feature object. """
    def GetResources(self):
        return {'Pixmap'  : path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel'   : m_accel,
                'ToolTip' : m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(LinePointPlanePanel())

        run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("LinePointPlane", CommandLinePointPlane())


def run():
    m_sel, _ = getSel(WF.verbose())
      
    try:        
        Number_of_Edges, Edge_List = m_sel.get_segmentsNames(getfrom=["Segments","Curves","Planes","Objects"])        
        Number_of_Vertexes, Vertex_List = m_sel.get_pointsNames(getfrom=["Points","Curves","Objects"])
        
        if WF.verbose() != 0:
            print_msg("Number_of_Edges = " + str(Number_of_Edges))
            print_msg("Edge_List = " + str(Edge_List))        
            print_msg("Number_of_Vertexes = " + str(Number_of_Vertexes))
            print_msg("Vertex_List = " + str(Vertex_List))
                
        if Number_of_Edges < 1:
            raise Exception(m_exception_msg)
        if Number_of_Vertexes < 1:
            raise Exception(m_exception_msg)
        try:
            m_main_dir = "WorkPlanes_P"   
            m_group = createFolders(str(m_main_dir))
            if WF.verbose() != 0:
                print_msg("Group = " + str(m_group.Label))
                               
            edge = Edge_List[0]
            vertex =  Vertex_List [0] 
               
            App.ActiveDocument.openTransaction("Macro LinePointPlane")
            selfobj = makeLinePointPlaneFeature(m_group)    
            selfobj.Edge      = edge
            selfobj.Point     = vertex
            selfobj.Extension = m_extension
            selfobj.Proxy.execute(selfobj)
                       
        finally:
            App.ActiveDocument.commitTransaction()
            
    except Exception as err:
        printError_msg(err.message, title="Macro LinePointPlane")

                           
if __name__ == '__main__':
    run()