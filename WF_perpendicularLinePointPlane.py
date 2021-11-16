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
__title__="Macro PerpendicularLinePointPlane"
__author__ = "Rentlau_64"
__brief__ = '''
Macro PerpendicularLinePointPlane.
Creates a parametric PerpendicularLinePointPlane from a point and a line
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
 
PATH_WF_ICONS     = os.path.join(path_WF, 'Resources', 'Icons')
PATH_WF_UTILS     = os.path.join(path_WF, 'Utils')
path_WF_resources = os.path.join(path_WF, 'Resources')
PATH_WF_UI        = os.path.join(path_WF, 'Resources', 'Ui')
 
if not sys.path.__contains__(str(PATH_WF_UTILS)):
    sys.path.append(str(PATH_WF_UTILS))
    sys.path.append(str(PATH_WF_UI))
     
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
M_ICON_NAME = "WF_perpendicularLinePointPlane.svg"
M_DIALOG = "WF_UI_linePointPlane.ui"
M_DIALOG_TITLE  = "Define extension of the plane."

M_EXCEPTION_MSG = """Unable to create Plane :
    Select one Line and one Point only
    with the Point NOT on the Line !

Go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG    = " : Plane created !"
M_MENU_TEXT     = "Plane = (Point, _|Line)"
M_ACCEL         = ""
M_TOOL_TIP      = """<b>Create Plane</b> given one Point and one perpendicular Line.<br>
...<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br> 
 - a Parameter(s) Window in Task Panel!</i>
""" 
m_extension      = 100.0
###############

class PerpendicularLinePointPlanePanel:  
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)
        self.form.UI_Plane_extension.setText(str(m_extension))
                        
    def accept(self):
        global m_extension
        m_extension = float(self.form.UI_Plane_extension.text())        
  
        if WF.verbose() != 0:
            print_msg("m_extension = " + str(m_extension))
            
        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if len(Gui.Selection.getSelectionEx(m_act_doc.Name)) != 0:
                run()
        return True
    
    def reject(self):
        Gui.Control.closeDialog()
        return False
    
    def shouldShow(self):    
        return (len(Gui.Selection.getSelectionEx(App.activeDocument().Name)) == 0 )   


def makePerpendicularLinePointPlaneFeature(group):
    """ Makes a PerpendicularLinePointPlane parametric feature object. 
    into the given Group
    Returns the new object.
    """ 
    m_name = "PerpendicularLinePointPlane_P"
    m_part = "Part::FeaturePython"     
    
    try:     
        m_obj = App.ActiveDocument.addObject(str(m_part),str(m_name))
        if group != None :
            addObjectToGrp(m_obj,group,info=1)
        PerpendicularLinePointPlane(m_obj)
        ViewProviderPerpendicularLinePointPlane(m_obj.ViewObject)
    except:
        printError_msg( "Not able to add an object to Model!")
        return None
    
    return m_obj


class PerpendicularLinePointPlane(WF_Plane):
    """ The PerpendicularLinePointPlane feature object. """
    # this method is mandatory
    def __init__(self,selfobj):
        self.name = "PerpendicularLinePointPlane"
        WF_Plane.__init__(self, selfobj, self.name)
        """ Add some custom properties to our PerpendicularLinePointPlane feature object. """
        selfobj.addProperty("App::PropertyLinkSub","Edge",self.name,
                            "Input edge")
        selfobj.addProperty("App::PropertyLinkSub","Point",self.name,
                            "Input point")
        m_tooltip = """Extensions of plane in percentage of the Line Length.
Positive values upper than 100.0 will enlarge the Plane.
Positive values lower than 100.0 will start to shrink it.""" 
        selfobj.addProperty("App::PropertyFloat","Extension",self.name,
                            m_tooltip).Extension=100.0 
        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden 
        selfobj.setEditorMode("Edge", 1)
        selfobj.setEditorMode("Point", 1)
        selfobj.Proxy = self    
     
    # this method is mandatory   
    def execute(self,selfobj): 
        """ Print a short message when doing a recomputation. """
#         if WF.verbose() != 0:
#             App.Console.PrintMessage("Recompute Python PerpendicularLinePointPlane feature\n")
                
        if 'Edge' not in selfobj.PropertiesList:
            return         
        if 'Point' not in selfobj.PropertiesList:
            return 
        if 'Extension' not in selfobj.PropertiesList:
            return
          
        if selfobj.Edge != None and selfobj.Point != None :
            points = []
            
            n1 = eval(selfobj.Point[1][0].lstrip('Vertex'))
            n2 = eval(selfobj.Edge[1][0].lstrip('Edge'))
#             if WF.verbose() != 0:
#                 print_msg("n1 = " + str(n1))
#                 print_msg("n2 = " + str(n2))

            try: 
                point_C = selfobj.Point[0].Shape.Vertexes[n1-1].Point
                points.append(point_C)
                
                point_A = selfobj.Edge[0].Shape.Edges[n2-1].Vertexes[0].Point
                point_B = selfobj.Edge[0].Shape.Edges[n2-1].Vertexes[-1].Point
    
                points.append(point_A)
                points.append(point_B)
                
                # Projection point P on a Line given one Line and One Point C.
                if isColinearVectors(point_A, point_B, point_C, tolerance=1e-12):
                    point_P = point_C
                    length = selfobj.Edge[0].Length
                else:
                    point_P, Distance, point_Pprime = intersectPerpendicularLine(point_A, point_B, point_C)
                    xmax, xmin, ymax, ymin, zmax, zmin = minMaxVectorsLimits(points)
    
                    length = xmax - xmin
                    if (ymax - ymin) > length:
                        length = ymax - ymin
                    if (zmax - zmin) > length:
                        length = zmax - zmin
                    if length == 0:
                        length = 10.0
                
                Edge_Length = length
                if selfobj.Extension == 0.0 :
                    selfobj.Extension = 100.0
                if selfobj.Extension < 0.0 :
                    selfobj.Extension *= -1
                
                Edge_Length = length * (selfobj.Extension / 100.0)    
                
                Plane_Point  = point_P +  (point_C - point_P).multiply(0.5)
                Plane_Normal = point_B - point_A
                            
                Plane_face = Part.makePlane(Edge_Length, Edge_Length, 
                                            Plane_Point, Plane_Normal )
                Plane_Center = Plane_face.CenterOfMass
                Plane_Translate =  Plane_Point - Plane_Center
                Plane_face.translate( Plane_Translate )
                selfobj.Shape = Plane_face
                
                propertiesPlane(selfobj.Label)
            except:
                pass
                
    def onChanged(self, selfobj, prop):
        """ Print the name of the property that has changed """
        # Debug mode
        if WF.verbose() != 0:
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")
        
        if 'parametric' in selfobj.PropertiesList:
            if selfobj.parametric == 'Not' :
                selfobj.setEditorMode("Extension", 1)
            else :
                selfobj.setEditorMode("Extension", 0)
            
        if prop == "Extension":            
            selfobj.Proxy.execute(selfobj)

        WF_Plane.onChanged(self, selfobj, prop)   
    
            
class ViewProviderPerpendicularLinePointPlane:
    global PATH_WF_ICONS
    icon = M_ICON_NAME
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
        return os.path.join(PATH_WF_ICONS, self.icon)
           
    def setIcon(self, icon=M_ICON_NAME):
        self.icon = icon
  
            
class CommandPerpendicularLinePointPlane:
    """ Command to create PerpendicularLinePointPlane feature object. """
    def GetResources(self):
        return {'Pixmap'  : os.path.join(PATH_WF_ICONS, M_ICON_NAME),
                'MenuText': M_MENU_TEXT,
                'Accel'   : M_ACCEL,
                'ToolTip' : M_TOOL_TIP}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if len(Gui.Selection.getSelectionEx(m_act_doc.Name)) == 0:
                Gui.Control.showDialog(PerpendicularLinePointPlanePanel())

        run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("PerpendicularLinePointPlane", CommandPerpendicularLinePointPlane())


def run():
    m_sel, _ = getSel(WF.verbose())
      
    try:        
        number_of_edges, edge_list = m_sel.get_segmentsNames(getfrom=["Segments","Curves","Planes","Objects"])        
        number_of_vertexes, vertex_list = m_sel.get_pointsNames(getfrom=["Points","Curves","Objects"])
        
        if WF.verbose() != 0:
            print_msg("number_of_edges = " + str(number_of_edges))
            print_msg("edge_list = " + str(edge_list))        
            print_msg("number_of_vertexes = " + str(number_of_vertexes))
            print_msg("vertex_list = " + str(vertex_list))
                
        if number_of_edges < 1:
            raise Exception(M_EXCEPTION_MSG)
        if number_of_vertexes < 1:
            raise Exception(M_EXCEPTION_MSG)
        try:
            m_main_dir = "WorkPlanes_P"
            m_sub_dir  = "Set"    
            m_group = createFolders(str(m_main_dir))
                        
            # Create a sub group if needed
            # To develop
            
            if WF.verbose() != 0:
                print_msg("Group = " + str(m_group.Label))
                               
            edge = edge_list[0]
            vertex =  vertex_list [0] 
               
            App.ActiveDocument.openTransaction("Macro PerpendicularLinePointPlane")
            selfobj = makePerpendicularLinePointPlaneFeature(m_group)    
            selfobj.Edge      = edge
            selfobj.Point     = vertex
            selfobj.Extension = m_extension
            selfobj.Proxy.execute(selfobj)
                       
        finally:
            App.ActiveDocument.commitTransaction()
            
    except Exception as err:
        printError_msg(err.args[0], title="Macro PerpendicularLinePointPlane")

                           
if __name__ == '__main__':
    run()