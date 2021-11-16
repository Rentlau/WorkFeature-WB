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
__title__="Macro LineFacePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro LineFacePoint.
Creates a parametric LineFacePoint from a Line and a Plane
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
from WF_Objects_base import WF_Point

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
M_ICON_NAME = "WF_lineFacePoint.svg"
M_DIALOG = None
M_DIALOG_TITLE  = "Nothing"
M_EXCEPTION_MSG = """Unable to create (Line,Face) Intersection(s) :
    - Select one or several Line/Edge(s) 
    and Second 
    - Select one or several Plane/Face(s) to process and/or
    - Select one or several Object(s) to process all Faces at once
"""
M_RESULT_MSG    = " : (Line,Face) Intersection(s) created !"
M_MENU_TEXT     = "Point(s) = (Line, Plane)"
M_ACCEL         = ""
M_TOOL_TIP      = """<b>Create Point(s)</b> at the intersection of 
the Line(s) and Plane(s) selected.<br>
<br>
First<br>
- Select one or several Line/Edge(s)<br> 
and Second<br>
- Select one or several Plane/Face(s) to process and/or<br>
- Select one or several Object(s) to process all Faces at once<br>
- Then Click on the button<br>
<br>
Be aware that if the plane is not extended enough the <br>
intersection Point is still created (as if).<br>  
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window !</i>
"""
###############

class LineFacePointPanel:  
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)
                        
    def accept(self):
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


def makeLineFacePointFeature(group):
    """ Makes a LineFacePoint parametric feature object. 
    into the given Group
    Returns the new object.
    """ 
    m_name = "LineFacePoint_P"
    m_part = "Part::FeaturePython"     
    
    try:     
        m_obj = App.ActiveDocument.addObject(str(m_part),str(m_name))
        if group != None :
            addObjectToGrp(m_obj,group,info=1)
        LineFacePoint(m_obj)
        ViewProviderLineFacePoint(m_obj.ViewObject)
    except:
        printError_msg( "Not able to add an object to Model!")
        return None
    
    return m_obj


class LineFacePoint(WF_Point):
    """ The LineFacePoint feature object. """
    # this method is mandatory
    def __init__(self,selfobj):
        self.name = "LineFacePoint"
        WF_Point.__init__(self, selfobj, self.name)
        """ Add some custom properties to our LineFacePoint feature object. """
        selfobj.addProperty("App::PropertyLinkSub","Face",self.name,
                            "Input face")   
        selfobj.addProperty("App::PropertyLinkSub","Edge",self.name,
                            "Input edge")
        selfobj.setEditorMode("Face", 1)
        selfobj.setEditorMode("Edge", 1)
        selfobj.Proxy = self    
     
    # this method is mandatory   
    def execute(self,selfobj): 
        """ Print a short message when doing a recomputation. """
#         if WF.verbose() != 0:
#             App.Console.PrintMessage("Recompute Python LineFacePoint feature\n")
                
        if 'Face' not in selfobj.PropertiesList:
            return
        if 'Edge' not in selfobj.PropertiesList:
            return
        
        n1 = eval(selfobj.Face[1][0].lstrip('Face'))
        n2 = eval(selfobj.Edge[1][0].lstrip('Edge'))
#         if WF.verbose() != 0:
#             print_msg("n1 = " + str(n1)) 
#             print_msg("n2 = " + str(n2))     
        
        try: 
            m_face = selfobj.Face[0].Shape.Faces[n1-1]
            m_edge = selfobj.Edge[0].Shape.Edges[n2-1]
            
            if WF.verbose() != 0:
                print_msg("m_face = " + str(m_face)) 
                print_msg("m_edge = " + str(m_edge))           
                            
            Vector_A = m_edge.valueAt( 0.0 )
            Vector_B = m_edge.valueAt( m_edge.Length )
            Plane_Normal = m_face.normalAt(0,0)
            Plane_Point  = m_face.CenterOfMass
            
            Vector_point = intersecLinePlane(Vector_A, Vector_B, 
                                             Plane_Normal, Plane_Point)  
          
            point = Part.Point( Vector_point )         
            selfobj.Shape = point.toShape()
            propertiesPoint(selfobj.Label)
            selfobj.X = float(Vector_point.x)
            selfobj.Y = float(Vector_point.y)
            selfobj.Z = float(Vector_point.z)
        except:
            pass
                 
    def onChanged(self, selfobj, prop):
        """ Print the name of the property that has changed """
        # Debug mode
        if WF.verbose() != 0:
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")
        
        WF_Point.onChanged(self, selfobj, prop)   
    
            
class ViewProviderLineFacePoint:
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
  
            
class CommandLineFacePoint:
    """ Command to create LineFacePoint feature object. """
    def GetResources(self):
        return {'Pixmap'  : os.path.join(PATH_WF_ICONS, M_ICON_NAME),
                'MenuText': M_MENU_TEXT,
                'Accel'   : M_ACCEL,
                'ToolTip' : M_TOOL_TIP}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if len(Gui.Selection.getSelectionEx(m_act_doc.Name)) == 0:
                pass
                #Gui.Control.showDialog(LineFacePointPanel())

        run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("LineFacePoint", CommandLineFacePoint())


def run():
    m_sel, m_act_doc = getSel(WF.verbose())
      
    try:         
        number_of_edges, edge_list = m_sel.get_segmentsNames(
            getfrom=["Segments","Curves"])
        if WF.verbose() != 0:
            print_msg("number_of_edges = " + str(number_of_edges))
            print_msg("edge_list = " + str(edge_list))
             
        Number_of_Planes, Plane_List = m_sel.get_planesNames(
            getfrom=["Planes","Objects"])
        if WF.verbose() != 0:      
            print_msg("Number_of_Planes = " + str(Number_of_Planes))
            print_msg("Plane_List = " + str(Plane_List))
            
        if number_of_edges == 0 or Number_of_Planes == 0 :
            raise Exception(M_EXCEPTION_MSG)
        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir  = "Set"   
            m_group = createFolders(str(m_main_dir))

            # Create a sub group if needed
            if number_of_edges > 1 or Number_of_Planes > 1:
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_act_doc.getObject( str(m_ob.Label) )
                except:
                    printError_msg("Could not Create '"+ str(m_sub_dir) +"' Objects Group!")           
                        
            if WF.verbose() != 0:
                print_msg("Group = " + str(m_group.Label))
                
            for i in range( number_of_edges ):
                edge = edge_list[i]
                if WF.verbose() != 0:
                    print_msg("edge = " + str(edge))
                
                for j in range( Number_of_Planes ):
                    plane = Plane_List[j]
                    if WF.verbose() != 0:
                        print_msg("plane = " + str(plane))
                                  
                    App.ActiveDocument.openTransaction("Macro LineFacePoint")
                    selfobj = makeLineFacePointFeature(m_group) 
                    selfobj.Edge           = edge  
                    selfobj.Face           = plane
                    selfobj.Proxy.execute(selfobj)                   
                                                   
        finally:
            App.ActiveDocument.commitTransaction()
            
        

            
    except Exception as err:
        printError_msg(err.args[0], title="Macro LineFacePoint")

                           
if __name__ == '__main__':
    run()