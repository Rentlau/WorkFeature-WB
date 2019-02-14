# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
*   https://github.com/Rentlau/WorkFeature-WB                             *
*                                                                         *
*   Code rewrite by <rentlau_64> from Work Features macro:                *
*   https://github.com/Rentlau/WorkFeature                                *
*                                                                         *
*   This workbench is a supplement to the FreeCAD CAx development system. *
*   http://www.freecadweb.org                                             *
*                                                                         *
*   This workbench is free software; you can redistribute it and/or modify*
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation, either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*   for detail see the LICENSE text file or:                              *
*   https://www.gnu.org/licenses/gpl-3.0.html                             *
*                                                                         *
*   This workbench is distributed in the hope that it will be useful,     *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this workbench;                                    *
*   If not, see <https://www.gnu.org/licenses/>                           *
***************************************************************************
"""
import sys
import os.path
import FreeCAD as App
import Part
from PySide import QtGui, QtCore
import WF
from WF_Objects_base import WF_Plane
# from InitGui import m_debug
if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro ThreePointsPlane"
__author__ = "Rentlau_64"
__brief__ = '''
Macro ThreePointsPlane.
Creates a parametric ThreePointsPlane from 3 points
'''
###############
m_debug = False
###############
# get the path of the current python script
path_WF = os.path.dirname(__file__)

path_WF_icons = os.path.join(path_WF, 'Resources', 'Icons')
path_WF_utils = os.path.join(path_WF, 'Utils')
path_WF_resources = os.path.join(path_WF, 'Resources')
path_WF_ui = os.path.join(path_WF, 'Resources', 'Ui')

if not sys.path.__contains__(str(path_WF_utils)):
    sys.path.append(str(path_WF_utils))
    sys.path.append(str(path_WF_ui))

try:
    from WF_selection import Selection, getSel
    from WF_print import printError_msg, print_msg
    from WF_directory import createFolders, addObjectToGrp
    from WF_geometry import *

except ImportError:
    print("ERROR: cannot load WF modules !")
    sys.exit(1)

###############
m_icon = "/WF_threePointsPlane.svg"
m_dialog = "/WF_UI_threePointsPlane.ui"
m_dialog_title = "Define extension of the plane."

m_exception_msg = """
Unable to create Plane from 3 Points :
- Select three seperated Points !

Go to Parameter(s) Window in Task Panel!"""
m_result_msg = " : Plane from 3 Points created !"
m_menu_text = "Plane = (3 Points)"
m_accel = ""
m_tool_tip = """<b>Create Plane</b>  from three selected Points.<br>
<br>
- Select three Points only<br>
- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
###############
m_macro = "Macro Macro ThreePointsPlane"
m_extension = 100.0
###############


class ThreePointsPlanePanel:
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
        self.form.UI_Plane_extension.setText(str(m_extension))

    def accept(self):
        global m_extension
        m_extension = float(self.form.UI_Plane_extension.text())

        if WF.verbose():
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
        return (len(Gui.Selection.getSelectionEx(App.activeDocument().Name)) == 0)


def makeThreePointsPlaneFeature(group):
    """ Makes a ThreePointsPlane parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "ThreePointsPlane_P"
    m_part = "Part::FeaturePython"

    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        ThreePointsPlane(m_obj)
        ViewProviderThreePointsPlane(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=m_macro)
        return None

    return m_obj


class ThreePointsPlane(WF_Plane):
    """ The ThreePointsPlane feature object. """
    # this method is mandatory
    def __init__(self, selfobj):
        if m_debug:
            print("running ThreePointsPlane.__init__ !")

        self.name = "ThreePointsPlane"
        WF_Plane.__init__(self, selfobj, self.name)
        """ Add some custom properties to our ThreePointsPlane feature object. """
        selfobj.addProperty("App::PropertyLinkSub",
                            "Point1",
                            self.name,
                            "Point1")
        selfobj.addProperty("App::PropertyLinkSub",
                            "Point2",
                            self.name,
                            "Point2")
        selfobj.addProperty("App::PropertyLinkSub",
                            "Point3",
                            self.name,
                            "Point3")

        m_tooltip = """Extensions of plane in percentage of the Line Length.
Positive values upper than 100.0 will enlarge the Plane.
Positive values lower than 100.0 will start to shrink it."""
        selfobj.addProperty("App::PropertyFloat",
                            "Extension",
                            self.name,
                            m_tooltip).Extension = m_extension
        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden
        selfobj.setEditorMode("Point1", 1)
        selfobj.setEditorMode("Point2", 1)
        selfobj.setEditorMode("Point3", 1)

        selfobj.Proxy = self

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        if m_debug:
            print("running ThreePointsPlane.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        if WF.verbose():
            m_msg = "Recompute Python ThreePointsPlane feature\n"
            App.Console.PrintMessage(m_msg)

        try:
            Plane = None
            if selfobj.Point1 is not None and selfobj.Point2 is not None and selfobj.Point3 is not None:
                n1 = eval(selfobj.Point1[1][0].lstrip('Vertex'))
                n2 = eval(selfobj.Point2[1][0].lstrip('Vertex'))
                n3 = eval(selfobj.Point3[1][0].lstrip('Vertex'))
                if m_debug:
                    print_msg(str(selfobj.Point1))
                    print_msg(str(selfobj.Point2))
                    print_msg(str(selfobj.Point3))
                    print_msg("n1 = " + str(n1))
                    print_msg("n2 = " + str(n2))
                    print_msg("n3 = " + str(n3))

                points = []
                point1 = selfobj.Point1[0].Shape.Vertexes[n1 - 1].Point
                point2 = selfobj.Point2[0].Shape.Vertexes[n2 - 1].Point
                point3 = selfobj.Point3[0].Shape.Vertexes[n3 - 1].Point

                if isEqualVectors(point1, point2):
                    m_msg = """Unable to create Plane from 2 equals Points :
                    Points 1 and 2 are equals !
                    """
                    printError_msg(m_msg, title=m_macro)

                if isEqualVectors(point1, point3):
                    m_msg = """Unable to create Plane from 2 equals Points :
                    Points 1 an 3 are equals !
                    """
                    printError_msg(m_msg, title=m_macro)

                if isEqualVectors(point2, point3):
                    m_msg = """Unable to create Plane from 2 equals Points :
                    Points 2 an 3 are equals !
                    """
                    printError_msg(m_msg, title=m_macro)

                points.append(point1)
                points.append(point2)
                points.append(point2)

                Vector_Center = meanVectorsPoint(points)
                xmax, xmin, ymax, ymin, zmax, zmin = minMaxVectorsLimits(points)

                Vector21 = point2 - point1
                Vector31 = point3 - point1
                Plane_Point = Vector_Center
                Plane_Normal = Vector21.cross(Vector31)

                Plane = Part.makePlane(m_extension,
                                       m_extension,
                                       Plane_Point,
                                       Plane_Normal)
                Plane_Center = Plane.CenterOfMass
                Plane_Translate = Plane_Point - Plane_Center
                Plane.translate(Plane_Translate)

#                 Plane = Part.Plane(point1, point2, point3)
#                 .toShape()
            if Plane is not None:
                selfobj.Shape = Plane
                propertiesPlane(selfobj.Label, self.color)
                selfobj.Point1_X = float(point1.x)
                selfobj.Point1_Y = float(point1.y)
                selfobj.Point1_Z = float(point1.z)
                selfobj.Point2_X = float(point2.x)
                selfobj.Point2_Y = float(point2.y)
                selfobj.Point2_Z = float(point2.z)
                selfobj.Point3_X = float(point3.x)
                selfobj.Point3_Y = float(point3.y)
                selfobj.Point3_Z = float(point3.z)
                # To be compatible with previous version 2018
                if 'Parametric' in selfobj.PropertiesList:
                    self.created = True
        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

    def onChanged(self, selfobj, prop):
        if WF.verbose():
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")

        if m_debug:
            print("running ThreePointsPlane.onChanged !")

        WF_Plane.onChanged(self, selfobj, prop)

        if prop == "Parametric":
            if 'Parametric' in selfobj.PropertiesList:
                if selfobj.Parametric == 'Not':
                    selfobj.setEditorMode("Extension", 1)
                else:
                    selfobj.setEditorMode("Extension", 0)
            propertiesPlane(selfobj.Label, self.color)

        if prop == "Extension":
            selfobj.Proxy.execute(selfobj)


class ViewProviderThreePointsPlane:
    global path_WF_icons
    icon = '/WF_threePointsPlane.svg'

    def __init__(self, vobj):
        """ Set this object to the proxy object of the actual view provider """
        vobj.Proxy = self

    # this method is mandatory
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def setEdit(self, vobj, mode):
        return False

    def unsetEdit(self, vobj, mode):
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    # subelements is a tuple of strings
    def onDelete(self, feature, subelements):
        return True

    # This method is optional and if not defined a default icon is shown.
    def getIcon(self):
        """ Return the icon which will appear in the tree view. """
        return (path_WF_icons + ViewProviderThreePointsPlane.icon)

    def setIcon(self, icon='/WF_threePointsPlane.svg'):
        ViewProviderThreePointsPlane.icon = icon


class CommandThreePointsPlane:
    """ Command to create ThreePointsPlane feature object. """
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel': m_accel,
                'ToolTip': m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(ThreePointsPlanePanel())

        run()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("ThreePointsPlane", CommandThreePointsPlane())


def run():
    m_sel, m_actDoc = getSel(WF.verbose())

    try:
        Number_of_Vertexes, Vertex_List = m_sel.get_pointsNames(
            getfrom=["Points",
                     "Curves",
                     "Objects"])
        if WF.verbose():
            print_msg("Number_of_Vertexes = " + str(Number_of_Vertexes))
            print_msg("Vertex_List = " + str(Vertex_List))

        if Number_of_Vertexes < 3:
            raise Exception(m_exception_msg)

        try:
            m_main_dir = "WorkPlanes_P"
            m_sub_dir = "Set001"
            m_group = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            # Create a sub group if needed
            if Number_of_Vertexes > 6:
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=m_macro)
                    printError_msg(m_error_msg)

            if WF.verbose():
                print_msg("Group = " + str(m_group.Label))

            # Case of only 3 points
            if Number_of_Vertexes == 3:
                if WF.verbose():
                    print_msg("Process only 3 points")

                vertex1 = Vertex_List[0]
                vertex2 = Vertex_List[1]
                vertex3 = Vertex_List[2]

                if WF.verbose():
                    print_msg("vertex1 = " + str(vertex1))
                    print_msg("vertex2 = " + str(vertex2))
                    print_msg("vertex3 = " + str(vertex3))

                App.ActiveDocument.openTransaction(m_macro)
                selfobj = makeThreePointsPlaneFeature(m_group)
                selfobj.Point1 = vertex1
                selfobj.Point2 = vertex2
                selfobj.Point3 = vertex3
                selfobj.Extension = m_extension
                selfobj.Proxy.execute(selfobj)
            else:
                pass

        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

        App.ActiveDocument.commitTransaction()

    except Exception as err:
        printError_msg(err.args[0], title=m_macro)


if __name__ == '__main__':
    run()
