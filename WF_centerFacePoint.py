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
__title__="Macro CenterFacePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro CenterFacePoint.
Creates a parametric CenterFacePoint from a  Plane
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
m_icon          = "/WF_centerFacePoint.svg"
m_dialog        = None
m_dialog_title  = "Nothing"
m_exception_msg = """Unable to create Center Face Point(s) :
    Select at least one Face !
   
Go to Parameter(s) Window in Task Panel!"""
m_result_msg    = " : Center Face Point(s) created !"
m_menu_text     = "Point(s) = center(Plane)"
m_accel         = ""
m_tool_tip      = """<b>Create Point(s)</b> at Center location 
of each selected Face(s).<br>
<br>
- Select one or several Plane/Face(s) to process and/or<br>
- Select one or several Object(s) to process all Faces at once<br>
- Then Click on the button.<br> 
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window !</i>
"""
###############

class CenterFacePointPanel:  
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


def makeCenterFacePointFeature(group):
    """ Makes a CenterFacePoint parametric feature object. 
    into the given Group
    Returns the new object.
    """ 
    m_name = "CenterFacePoint_P"
    m_part = "Part::FeaturePython"     
    
    try:     
        m_obj = App.ActiveDocument.addObject(str(m_part),str(m_name))
        if group != None :
            addObjectToGrp(m_obj,group,info=1)
        CenterFacePoint(m_obj)
        ViewProviderCenterFacePoint(m_obj.ViewObject)
    except:
        printError_msg( "Not able to add an object to Model!")
        return None
    
    return m_obj


class CenterFacePoint(WF_Point):
    """ The CenterFacePoint feature object. """
    # this method is mandatory
    def __init__(self,selfobj):
        self.name = "CenterFacePoint"
        WF_Point.__init__(self, selfobj, self.name)
        """ Add some custom properties to our CenterFacePoint feature object. """
        selfobj.addProperty("App::PropertyLinkSub","Face",self.name,
                            "Input face")   

        selfobj.setEditorMode("Face", 1)
        selfobj.Proxy = self    
     
    # this method is mandatory   
    def execute(self,selfobj): 
        """ Print a short message when doing a recomputation. """
#         if WF.verbose() != 0:
#             App.Console.PrintMessage("Recompute Python CenterFacePoint feature\n")
                
        if 'Face' not in selfobj.PropertiesList:
            return
        
        n = eval(selfobj.Face[1][0].lstrip('Face'))
#         if WF.verbose() != 0:
#             print_msg("n = " + str(n))    
        
        try: 
            m_face = selfobj.Face[0].Shape.Faces[n-1]
            if WF.verbose() != 0:
                print_msg("m_face = " + str(m_face))            
        
            Vector_point = m_face.CenterOfMass  
          
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
    
            
class ViewProviderCenterFacePoint:
    global path_WF_icons
    icon = '/WF_centerFacePoint.svg'  
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
        return (path_WF_icons + ViewProviderCenterFacePoint.icon)
           
    def setIcon(self, icon = '/WF_centerFacePoint.svg'):
        ViewProviderCenterFacePoint.icon = icon
  
            
class CommandCenterFacePoint:
    """ Command to create CenterFacePoint feature object. """
    def GetResources(self):
        return {'Pixmap'  : path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel'   : m_accel,
                'ToolTip' : m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                pass
                #Gui.Control.showDialog(CenterFacePointPanel())

        run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("CenterFacePoint", CommandCenterFacePoint())


def run():
    m_sel, m_actDoc = getSel(WF.verbose())
      
    try: 
        Number_of_Planes, Plane_List = m_sel.get_planesNames(getfrom=["Planes","Objects"])
        if WF.verbose() != 0:        
            print_msg("Number_of_Planes = " + str(Number_of_Planes))
            print_msg("Plane_List = " + str(Plane_List))
            
        if Number_of_Planes == 0:
            raise Exception(m_exception_msg)
        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir  = "Set"   
            m_group = createFolders(str(m_main_dir))

            # Create a sub group if needed
            if Number_of_Planes > 1 :
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject( str(m_ob.Label) )
                except:
                    printError_msg("Could not Create '"+ str(m_sub_dir) +"' Objects Group!")           
            
            if WF.verbose() != 0:
                print_msg("Group = " + str(m_group.Label))
                
            for i in range( Number_of_Planes ):
                plane = Plane_List[i]            
                App.ActiveDocument.openTransaction("Macro CenterFacePoint")
                selfobj = makeCenterFacePointFeature(m_group)    
                selfobj.Face           = plane
                selfobj.Proxy.execute(selfobj)                   
                                                   
        finally:
            App.ActiveDocument.commitTransaction()
            
        

            
    except Exception as err:
        printError_msg(err.message, title="Macro CenterFacePoint")

                           
if __name__ == '__main__':
    run()