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
__title__="Macro CenterCirclePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro CenterCirclePoint.
Creates a parametric CenterCirclePoint from an Edge
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
m_icon          = "/WF_centerCirclePoint.svg"
m_dialog        = "/WF_UI_centerCirclePoint.ui"
m_dialog_title  = "Nothing"
m_exception_msg = """Unable to create Center Line Point(s) :
    Select at least one Edge of Circle !
   
Go to Parameter(s) Window in Task Panel!"""
m_result_msg    = " : Center Circle Point(s) created !"
m_menu_text     = "Center of Circle(s)"
m_accel         = ""
m_tool_tip      = """<b>Create Point(s)</b> at Center location of each selected Circle(s).<br>
...<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br> 
 - a Parameter(s) Window in Task Panel!</i>
"""
###############

class CenterCirclePointPanel:  
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
                        
    def accept(self):
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


def makeCenterCirclePointFeature(group):
    """ Makes a CenterCirclePoint parametric feature object. 
    into the given Group
    Returns the new object.
    """ 
    m_name = "CenterCirclePoint_P"
    m_part = "Part::FeaturePython"     
    
    try:     
        m_obj = App.ActiveDocument.addObject(str(m_part),str(m_name))
        if group != None :
            addObjectToGrp(m_obj,group,info=1)
        CenterCirclePoint(m_obj)
        ViewProviderCenterCirclePoint(m_obj.ViewObject)
    except:
        printError_msg( "Not able to add an object to Model!")
        return None
    
    return m_obj


class CenterCirclePoint(WF_Point):
    """ The CenterCirclePoint feature object. """
    # this method is mandatory
    def __init__(self,selfobj):
        self.name = "CenterCirclePoint"
        WF_Point.__init__(self, selfobj, self.name)
        """ Add some custom properties to our CenterCirclePoint feature object. """
        selfobj.addProperty("App::PropertyLinkSub","Edge",self.name,
                            "Input edge")   

        selfobj.setEditorMode("Edge", 1)
        selfobj.Proxy = self    
     
    # this method is mandatory   
    def execute(self,selfobj): 
        """ Print a short message when doing a recomputation. """
        if WF.verbose() != 0:
            App.Console.PrintMessage("Recompute Python CenterCirclePoint feature\n")
        
        n = eval(selfobj.Edge[1][0].lstrip('Edge'))
        if WF.verbose() != 0:
            print_msg("n = " + str(n))    

        m_edge = selfobj.Edge[0].Shape.Edges[n-1]
        if WF.verbose() != 0:
            print_msg("m_edge = " + str(m_edge))
            
        
        Vector_point = m_edge.Curve.Center  
#         try :
#             point = m_edge.Curve.Radius
#         except:
#             try:
#                 point = m_edge.Center
#             except:
#                 try:
#                     point = m_edge.Curve.Center
#                 except AttributeError:
#                     continue
#       
        point = Part.Point( Vector_point )         
        selfobj.Shape = point.toShape()
        propertiesPoint(selfobj.Label)
        selfobj.X = float(Vector_point.x)
        selfobj.Y = float(Vector_point.y)
        selfobj.Z = float(Vector_point.z)
                 
    def onChanged(self, selfobj, prop):
        """ Print the name of the property that has changed """
        # Debug mode
        if WF.verbose() != 0:
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")
        
        WF_Point.onChanged(self, selfobj, prop)   
    
            
class ViewProviderCenterCirclePoint:
    global path_WF_icons
    icon = '/WF_centerCirclePoint.svg'  
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
        return (path_WF_icons + ViewProviderCenterCirclePoint.icon)
           
    def setIcon(self, icon = '/WF_centerCirclePoint.svg'):
        ViewProviderCenterCirclePoint.icon = icon
  
            
class CommandCenterCirclePoint:
    """ Command to create CenterCirclePoint feature object. """
    def GetResources(self):
        return {'Pixmap'  : path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel'   : m_accel,
                'ToolTip' : m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(CenterCirclePointPanel())

        run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("CenterCirclePoint", CommandCenterCirclePoint())


def run():
    m_sel, m_actDoc = getSel(WF.verbose())
      
    try: 
        Number_of_Curves, Curve_List = m_sel.get_curvesNames(getfrom=["Points","Segments","Curves","Planes","Objects"])         
        #Number_of_Edges, Edge_List = m_sel.get_segmentsNames(getfrom=["Points","Segments","Curves","Planes","Objects"])
        if WF.verbose() != 0:        
            print_msg("Number_of_Curves = " + str(Number_of_Curves))
            print_msg("Curve_List = " + str(Curve_List))
            
        if Number_of_Curves == 0:
            raise Exception(m_exception_msg)
        try:
            m_main_dir = "WorkPoints_P"   
            m_group = createFolders(str(m_main_dir))
            if WF.verbose() != 0:
                print_msg("Group = " + str(m_group.Label))
            m_sub_dir  = "Set"
            
            # Create a sub group if needed
            if Number_of_Curves > 1 :
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject( str(m_ob.Label) )
                except:
                    printError_msg("Could not Create '"+ str(m_sub_dir) +"' Objects Group!")           

            for i in range( Number_of_Curves ):
                edge = Curve_List[i]            
                App.ActiveDocument.openTransaction("Macro CenterCirclePoint")
                selfobj = makeCenterCirclePointFeature(m_group)    
                selfobj.Edge           = edge
                selfobj.Proxy.execute(selfobj)                   
                                                   
        finally:
            App.ActiveDocument.commitTransaction()
            
        

            
    except Exception as err:
        printError_msg(err.message, title="Macro CenterCirclePoint")

                           
if __name__ == '__main__':
    run()