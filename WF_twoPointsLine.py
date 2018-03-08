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
__title__="Macro TwoPointsLine"
__author__ = "Rentlau_64"
__brief__ = '''
Macro TwoPointsLine.
Creates a parametric TwoPointsLine from two points
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
from WF_Objects_base import WF_Line

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
m_icon          = "/WF_twoPointsLine.svg"
m_dialog        = "/WF_UI_twoPointsLine.ui"
m_dialog_title  = "Define Start and End location to create Line(s)."
m_exception_msg = """Unable to create Line(s) from 2 Points :
    Select two or several Points !
    
Go to Parameter(s) Window in Task Panel!"""
m_result_msg    = " : Line(s) from 2 Points created !"
m_menu_text     = "Line(s) = (Point, Point)"
m_accel         = ""
m_tool_tip      = """<b>Create Line(s)</b> from at least two selected Points.<br>
...<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br> 
 - a Parameter(s) Window in Task Panel!</i>
"""
m_line_ext      = 0.0
###############
 
class TwoPointsLinePanel:  
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
        self.form.UI_Line_extension.setText(str(m_line_ext))
        
    def accept(self):
        global m_line_ext
        
        m_line_ext = float(self.form.UI_Line_extension.text())
        
        if WF.verbose() != 0:
            print_msg("m_line_ext = " + str(m_line_ext))
            
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

def makeTwoPointsLineFeatureFromList(selectionset,group):
    """ Makes a TwoPointsLine parametric feature object from a selection set.
    into the given Group
    Returns the new object.
    """
    m_name = "TwoPointsLine_P"
    m_part = "Part::FeaturePython"
        
    if not isinstance(selectionset,list):
        selectionset = [selectionset]    
    try: 
        m_obj = App.ActiveDocument.addObject(str(m_part),str(m_name))
        if group != None :
            addObjectToGrp(m_obj,group,info=1)
        TwoPointsLine(m_obj)
        ViewProviderTwoPointsLine(m_obj.ViewObject)
        m_obj.Proxy.addSubobjects(m_obj,selectionset)
    except:
        printError_msg( "Not able to add a complete object to Model!")
        return None
    
    return m_obj

def makeTwoPointsLineFeature(group):
    """ Makes a TwoPointsLine parametric feature object. 
    into the given Group
    Returns the new object.
    """
    m_name = "TwoPointsLine_P"
    m_part = "Part::FeaturePython"
        
    try: 
        m_obj = App.ActiveDocument.addObject(str(m_part),str(m_name))
        if group != None :
            addObjectToGrp(m_obj,group,info=1)
        TwoPointsLine(m_obj)
        ViewProviderTwoPointsLine(m_obj.ViewObject)
    except:
        printError_msg( "Not able to add a complete object to Model!")
        return None
    
    return m_obj


class TwoPointsLine(WF_Line):
    """ The TwoPointsLine feature object. """
    # this method is mandatory
    def __init__(self,selfobj):
        self.name = "TwoPointsLine"
        WF_Line.__init__(self, selfobj, self.name)
        """ Add some custom properties to our TwoPointsLine feature object. """
        selfobj.addProperty("App::PropertyLinkSub","Point1",self.name,
                            "Start point")  
        selfobj.addProperty("App::PropertyLinkSub","Point2",self.name,
                            "End point")
        
#         selfobj.addProperty("App::PropertyLinkSubList","Points",self.name,
#                         "Linked points")
        
        selfobj.addProperty("App::PropertyFloat","Extension",self.name,
                            "Extension at extrema").Extension=0.0
        selfobj.setEditorMode("Point1", 1)
        selfobj.setEditorMode("Point2", 1)
        selfobj.Proxy = self    
    
    # this method is mandatory    
    def execute(self,selfobj): 
        """ Print a short message when doing a recomputation. """
        if WF.verbose() != 0:
            App.Console.PrintMessage("Recompute Python TwoPointsLine feature\n")

#         if selfobj.Points != None:
#             print selfobj.Points
#             for i in selfobj.Points:
#                 print i
#                 print i[0]
#             
#             n1 = eval(selfobj.Points[0][1][0].lstrip('Vertex'))
#             n2 = eval(selfobj.Points[1][1][0].lstrip('Vertex')) 
#             
#             print n1
#             print n2
#                         
#             point1 = selfobj.Points[0][0].Shape.Vertexes[n1-1].Point
#             point2 = selfobj.Points[1][0].Shape.Vertexes[n2-1].Point
#             
#             Axis_dir = point2 - point1
#             Point_E1 = point2            
#             Point_E2 = point1
#             m_line_ext = selfobj.Extension
#             if m_line_ext != 0.0:
#                 Point_E1 = point2 +  Axis_dir.normalize().multiply(m_line_ext)   
#                 if m_line_ext >= 0.0:            
#                     Point_E2 = point1 -  Axis_dir.normalize().multiply(m_line_ext)
#                 else:
#                     Point_E2 = point1 +  Axis_dir.normalize().multiply(m_line_ext)
#             if Point_E1 == Point_E2:
#                 Point_E1 = Point_E1 + Axis_dir.multiply(0.1)
#                 Point_E2 = Point_E2 - Axis_dir.multiply(0.9)            
#              
#             print Point_E1.x
#             print Point_E2
#             # must be Part.makeLine ((x,y,z),(x,y,z))               
#             line = Part.makeLine( coordVectorPoint(Point_E2), coordVectorPoint(Point_E1) )
#             selfobj.Shape = line
#             propertiesLine(selfobj.Label) 
                       
        if selfobj.Point1 != None and selfobj.Point2 != None :
            n1 = eval(selfobj.Point1[1][0].lstrip('Vertex'))
            n2 = eval(selfobj.Point2[1][0].lstrip('Vertex'))    
             
            point1 = selfobj.Point1[0].Shape.Vertexes[n1-1].Point
            point2 = selfobj.Point2[0].Shape.Vertexes[n2-1].Point
     
            Axis_dir = point2 - point1
            Point_E1 = point2            
            Point_E2 = point1
            m_line_ext = selfobj.Extension
            if m_line_ext != 0.0:
                Point_E1 = point2 +  Axis_dir.normalize().multiply(m_line_ext)
                if m_line_ext >= 0.0:            
                    Point_E2 = point1 -  Axis_dir.normalize().multiply(m_line_ext)
                else:
                    Point_E2 = point1 +  Axis_dir.normalize().multiply(m_line_ext)
            
            if isEqualVectors (Point_E1,Point_E2):
                m_msg = """Unable to create Line(s) from 2 Points :
                Given Points are equals !
                """
                printError_msg(m_msg , title="Macro TwoPointsLine")
                
            line = Part.makeLine( coordVectorPoint(Point_E2), coordVectorPoint(Point_E1) )
            selfobj.Shape = line
            propertiesLine(selfobj.Label)             
#                             
#             line = Part.Line( Point_E2, Point_E1 )
#             selfobj.Shape = line.toShape()
#             propertiesLine(selfobj.Label)
#             selfobj.X1 = float(point1.x)
#             selfobj.Y1 = float(point1.y)
#             selfobj.Z1 = float(point1.z)
#             selfobj.X2 = float(point2.x)
#             selfobj.Y2 = float(point2.y)
#             selfobj.Z2 = float(point2.z)
        
        #printPoint(Vector_point, msg=m_result_msg)        if Number_of_Points == 2:                  
        
    def onChanged(self, selfobj, prop):
        """ Print the name of the property that has changed """
        # Debug mode
        if WF.verbose() != 0:
            App.Console.PrintMessage("Change property: " + str(prop) + "\n")
                
        if selfobj.parametric == 'No' :
            selfobj.setEditorMode("Extension", 1)  
        else :
            selfobj.setEditorMode("Extension", 0)   
            
        if prop == "Extension":
            selfobj.Proxy.execute(selfobj)
        if prop == "Point1":
            selfobj.Proxy.execute(selfobj)
        if prop == "Point2":
            selfobj.Proxy.execute(selfobj)
            
        WF_Line.onChanged(self, selfobj, prop)

        
    def addSubobjects(self,selfobj,pointlinks):
        "adds pointlinks to this TwoPointsLine object"
        objs = selfobj.Points
        for o in pointlinks:
            if isinstance(o,tuple) or isinstance(o,list):
                if o[0].Name != selfobj.Name:
                    objs.append(tuple(o))
            else:
                for el in o.SubElementNames:
                    if "Point" in el:
                        if o.Object.Name != selfobj.Name:
                            objs.append((o.Object,el))
        selfobj.Points = objs
        selfobj.Proxy.execute(selfobj)
        #self.execute(selfobj)
            
class ViewProviderTwoPointsLine:
    global path_WF_icons  
    icon = '/WF_twoPointsLine.svg'
    def __init__(self, vobj):
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
        return (path_WF_icons + ViewProviderTwoPointsLine.icon)
    
    def setIcon(self, icon = '/WF_twoPointsLine.svg'):
        ViewProviderTwoPointsLine.icon = icon
        
                     
class CommandTwoPointsLine:       
    """ Command to create TwoPointsLine feature object. """
    def GetResources(self):
        return {'Pixmap'  : path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel'   : m_accel,
                'ToolTip' : m_tool_tip}
        
    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(TwoPointsLinePanel())
        run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("TwoPointsLine", CommandTwoPointsLine())

   
def run():
    m_sel, m_actDoc = getSel(WF.verbose())
 
    try:        
        Number_of_Vertexes, Vertex_List = m_sel.get_pointsNames(getfrom=["Points","Curves","Objects"])
        if WF.verbose() != 0:        
            print_msg("Number_of_Vertexes = " + str(Number_of_Vertexes))
            print_msg("Vertex_List = " + str(Vertex_List))
            
        if Number_of_Vertexes < 2:
            raise Exception(m_exception_msg)
        try:
            m_main_dir = "WorkAxis_P"   
            m_group = createFolders(str(m_main_dir))
            if WF.verbose() != 0:
                print_msg("Group = " + str(m_group.Label))
            m_sub_dir  = "Set"
            
            # Create a sub group if needed
            if Number_of_Vertexes > 2:
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject( str(m_ob.Label) )
                except:
                    printError_msg("Could not Create '"+ str(m_sub_dir) +"' Objects Group!")           
                                 
            if (Number_of_Vertexes % 2 == 0): #even
                if WF.verbose() != 0:
                    print_msg("Even number of points")
                if Number_of_Vertexes == 2:
                    vertex1 = Vertex_List[0]
                    vertex2 = Vertex_List[1]
                    
                    if WF.verbose() != 0:
                        print_msg("vertex1 = " + str(vertex1))
                        print_msg("vertex2 = " + str(vertex2)) 
                                 
                    App.ActiveDocument.openTransaction("Macro TwoPointsLine")
                    selfobj = makeTwoPointsLineFeature(m_group)    
                    selfobj.Point1 = vertex1
                    selfobj.Point2 = vertex2
#                     selfobj = makeTwoPointsLineFeatureFromList([vertex1,vertex2],m_group)
                    selfobj.Extension = m_line_ext              
                    selfobj.Proxy.execute(selfobj) 
                else :
                    for i in range(0,Number_of_Vertexes-1,2):
                        vertex1 = Vertex_List[i]
                        vertex2 = Vertex_List[i+1]
                        
                        if WF.verbose() != 0:
                            print_msg("vertex1 = " + str(vertex1))
                            print_msg("vertex2 = " + str(vertex2)) 
                                     
                        App.ActiveDocument.openTransaction("Macro TwoPointsLine")
                        selfobj = makeTwoPointsLineFeature(m_group)    
                        selfobj.Point1 = vertex1
                        selfobj.Point2 = vertex2
#                         selfobj = makeTwoPointsLineFeatureFromList([vertex1,vertex2],m_group)
                        selfobj.Extension = m_line_ext              
                        selfobj.Proxy.execute(selfobj)   
            else: #odd
                if WF.verbose() != 0:
                    print_msg("Odd number of points")              
                for i in range(Number_of_Vertexes-1):
                    vertex1 = Vertex_List[i]
                    vertex2 = Vertex_List[i+1]
                                 
                    App.ActiveDocument.openTransaction("Macro TwoPointsLine")
                    selfobj = makeTwoPointsLineFeature(m_group)    
                    selfobj.Point1 = vertex1
                    selfobj.Point2 = vertex2
                    selfobj.Extension = m_line_ext              
                    selfobj.Proxy.execute(selfobj)

        finally:
            App.ActiveDocument.commitTransaction()
            
    except Exception as err:
        printError_msg(err.message, title="Macro TwoPointsLine")

                           
if __name__ == '__main__':
    run()