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
__title__="Macro ExtremaLinePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro ExtremaLinePoint.
Creates a parametric ExtremaLinePoint from an Edge
'''
###############
m_debug = False
###############
import sys
import os.path
import FreeCAD as App
if App.GuiUp:
    import FreeCADGui as Gui
import Part
from PySide import QtGui,QtCore

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
    from WF_selection import *
    from WF_print import printError_msg
    from WF_geometry import *
    #from WF_utils import *
except:
    print "ERROR: cannot load WF modules !!"
    sys.exit(1)

###############
m_icon          = '/WF_extremaLinePoint.svg'
m_icons         = ['/WF_startLinePoint.svg', '/WF_endtLinePoint.svg', '/WF_extremaLinePoint.svg']
m_dialog        = '/WF_UI_extremaLinePoint.ui'
m_dialog_title  = 'Define Start and End location for selected Line(s).'
m_exception_msg = """Unable to create Extrema Line Point(s) :
    Select one or several Line/Edge(s) and/or
    Select one Plane/Face to process all (4) Edges and/or
    Select one Object to process all Edges at once !"""
m_result_msg    = " : Extrema Line Point(s) created !"
m_menu_text     = "Extrema of Line(s) "
m_accel         = ""
m_tool_tip      = """<b>Create Point(s)</b> at Start and End location of each selected Line(s).<br>
...<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br> 
 - a Parameter(s) Window in Task Panel!</i>
"""
m_location      = "Both ends"
m_locations     = ["Begin", "End", "Both ends"]
###############
 
class ExtremaLinePointPanel:  
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
        
    def accept(self):
        global m_location
        m_location = self.form.UI_ExtremaLinePoint_comboBox.currentText()
        Gui.Control.closeDialog()
        return True
    
    def reject(self):
        Gui.Control.closeDialog()
        return True
    
    def shouldShow(self):    
        return (len(Gui.Selection.getSelectionEx(App.activeDocument().Name)) == 0 )   


def makeExtremaLinePointFeature():
    """ Makes a ExtremaLinePoint" parametric feature object. 
    
    Returns the new object.
    """    
    obj = App.ActiveDocument.addObject("Part::FeaturePython","ExtremaLinePoint")
    ExtremaLinePoint(obj)
    ViewProviderExtremaLinePoint(obj.ViewObject)
    return obj


class ExtremaLinePoint:
    """ The ExtremaLinePoint feature object. """
    # this method is mandatory
    def __init__(self,selfobj): 
        """ Add some custom properties to our ExtremaLinePoint feature object. """
        selfobj.addProperty("App::PropertyLinkSub","Edge","ExtremaLinePoint","Input edge")  
        selfobj.addProperty("App::PropertyEnumeration","At","ExtremaLinePoint","Location Definition").At=["Begin","End"]
        selfobj.addProperty("App::PropertyFloat","X","ExtremaLinePoint","X of the point").X=1.0
        selfobj.addProperty("App::PropertyFloat","Y","ExtremaLinePoint","Y of the point").Y=1.0
        selfobj.addProperty("App::PropertyFloat","Z","ExtremaLinePoint","Z of the point").Z=1.0        
        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden 
        selfobj.setEditorMode("X", 1) 
        selfobj.setEditorMode("Y", 1) 
        selfobj.setEditorMode("Z", 1)      
        selfobj.Proxy = self    
    
    # this method is mandatory    
    def execute(self,selfobj): 
        """ Print a short message when doing a recomputation. """
        if m_debug != 0:
            App.Console.PrintMessage("Recompute Python ExtremaLinePoint feature\n")
        
        n = eval(selfobj.Edge[1][0].lstrip('Edge'))
        if selfobj.At == "Begin":       
            Vector_point = selfobj.Edge[0].Shape.Edges[n-1].Vertexes[0].Point
        else:
            Vector_point = selfobj.Edge[0].Shape.Edges[n-1].Vertexes[-1].Point
                        
        point = Part.Point( Vector_point )
        selfobj.Shape = point.toShape()
        propertiesPoint(selfobj.Label)
        selfobj.X = float(Vector_point.x)
        selfobj.Y = float(Vector_point.y)
        selfobj.Z = float(Vector_point.z)
        
        #printPoint(Vector_point, msg=m_result_msg)                  
        
    def onChanged(self, selfobj, prop):
        """ Print the name of the property that has changed """
        if m_debug != 0:
            App.Console.PrintMessage("Change property: " + str(prop) + "\n")
        if prop == "At":
            selfobj.Proxy.execute(selfobj)
        
            
class ViewProviderExtremaLinePoint:
    global path_WF_icons
    icon = '/WF_extremaLinePoint.svg'  
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
        return (path_WF_icons + ViewProviderExtremaLinePoint.icon)
    
    def setIcon(self, icon = '/WF_extremaLinePoint.svg'):
        ViewProviderExtremaLinePoint.icon = icon
        
                     
class CommandExtremaLinePoint:       
    """ Command to create ExtremaLinePoint feature object. """
    def GetResources(self):
        return {'Pixmap'  : path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel'   : m_accel,
                'ToolTip' : m_tool_tip}
        
    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(ExtremaLinePointPanel())
        run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("ExtremaLinePoint", CommandExtremaLinePoint())

   
def run():
    m_actDoc = App.activeDocument()
    if m_actDoc == None:
        message = "No Active document selected !"
        return (None, message)
    if not m_actDoc.Name:
        message = "No Active document.name selected !"
        return (None, message) 
       
    m_selEx  = Gui.Selection.getSelectionEx(m_actDoc.Name)                    
    m_sel    = Selection(m_selEx)
 
    if m_sel == None :
        print_msg("Unable to create a Selection Object !") 
        return None

    if m_debug != 0:
        print_msg("m_actDoc=" + str(m_actDoc))
        print_msg("m_actDoc.Name=" + str(m_actDoc.Name))
        print_msg("m_selEx=" + str(m_selEx))         
        print_msg("m_sel=" + str(m_sel))
 
    try:        
        Number_of_Edges, Edge_List = m_sel.get_segmentsNames(getfrom=["Segments","Curves","Planes","Objects"])
        if m_debug != 0:        
            print_msg("Number_of_Edges=" + str(Number_of_Edges))
            
        if Number_of_Edges == 0:
            raise Exception(m_exception_msg)
        try:               
            for i in range( Number_of_Edges ):
                edge = Edge_List[i]                              
                App.ActiveDocument.openTransaction("Macro ExtremaLinePoint")
                
                if m_debug != 0:
                    App.Console.PrintMessage("m_location : " + str(m_location))
     
                if m_location in  ["Begin", "Both ends"] : 
                    selfobj1 = makeExtremaLinePointFeature()    
                    selfobj1.Edge = edge
                    selfobj1.At = "Begin"              
                    selfobj1.Proxy.execute(selfobj1)
                if m_location in  ["End", "Both ends"] : 
                    selfobj2 = makeExtremaLinePointFeature()    
                    selfobj2.Edge = edge
                    selfobj2.At = "End"
                    selfobj2.Proxy.execute(selfobj2)
        finally:
            App.ActiveDocument.commitTransaction()
            
    except Exception as err:
        printError_msg(err.message, title="Macro ExtremaLinePoint")

                           
if __name__ == '__main__':
    run()