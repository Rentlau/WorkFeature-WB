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
M_ICON_NAME = "WF_centerCirclePoint.svg"
M_DIALOG = None
M_DIALOG_TITLE  = "Nothing"
M_EXCEPTION_MSG = """Unable to create Center Line Point(s) :
    Select at least one Edge of Circle !"""
   
 #Go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG    = " : Center Circle Point(s) created !"
M_MENU_TEXT     = "Point(s) = center(Arc)"
M_ACCEL         = ""
M_TOOL_TIP      = """<b>Create Point(s)</b> at Center location 
of each selected Circle(s).<br>
<br>
- Select one or several Circle(s), Arc(s) or Ellipse(s)<br>
- Then Click on the button<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window !</i>
"""
###############

class CenterCirclePointPanel:  
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
#         if WF.verbose() != 0:
#             App.Console.PrintMessage("Recompute Python CenterCirclePoint feature\n")

        if 'Edge' not in selfobj.PropertiesList:
            return
              
        n = eval(selfobj.Edge[1][0].lstrip('Edge'))
#         if WF.verbose() != 0:
#             print_msg("n = " + str(n))    
        
        try: 
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
        except:
            pass
                
                 
    def onChanged(self, selfobj, prop):
        """ Print the name of the property that has changed """
        # Debug mode
        if WF.verbose() != 0:
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")
        
        WF_Point.onChanged(self, selfobj, prop)   
    
            
class ViewProviderCenterCirclePoint:
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
  
            
class CommandCenterCirclePoint:
    """ Command to create CenterCirclePoint feature object. """
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
                #Gui.Control.showDialog(CenterCirclePointPanel())

        run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("CenterCirclePoint", CommandCenterCirclePoint())


def run():
    m_sel, m_act_doc = getSel(WF.verbose())
      
    try: 
        Number_of_Curves, Curve_List = m_sel.get_curvesNames(
            getfrom=["Points","Segments","Curves","Planes","Objects"])
        if WF.verbose() != 0:        
            print_msg("Number_of_Curves = " + str(Number_of_Curves))
            print_msg("Curve_List = " + str(Curve_List))
            
        if Number_of_Curves == 0:
            raise Exception(M_EXCEPTION_MSG)
        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir  = "Set"   
            m_group = createFolders(str(m_main_dir))

            # Create a sub group if needed
            if Number_of_Curves > 1 :
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_act_doc.getObject( str(m_ob.Label) )
                except:
                    printError_msg("Could not Create '"+ str(m_sub_dir) +"' Objects Group!")           
            
            if WF.verbose() != 0:
                print_msg("Group = " + str(m_group.Label))
                          
            for i in range( Number_of_Curves ):
                edge = Curve_List[i]            
                App.ActiveDocument.openTransaction("Macro CenterCirclePoint")
                selfobj = makeCenterCirclePointFeature(m_group)    
                selfobj.Edge           = edge
                selfobj.Proxy.execute(selfobj)                   
                                                   
        finally:
            App.ActiveDocument.commitTransaction()
   
    except Exception as err:
        printError_msg(err.args[0], title="Macro CenterCirclePoint")

                           
if __name__ == '__main__':
    run()