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
from FreeCAD import Base
from PySide import QtGui, QtCore
import WF
from WF_Objects_base import WF_Point
from WF_Objects_base import WF_Line
import WF_twoPointsLine as twoPL
# from InitGui import m_debug
if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro_ProjectedPoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro ProjectedPoint.
Creates a parametric ProjectedPoint from a list of Points
'''
###############
m_debug = True
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
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
m_icon = "/WF_projectedPoint.svg"
m_dialog = "/WF_UI_projectedPoint.ui"
m_dialog_title = ""
m_exception_msg = """
Unable to create a Projected Point(s) :
 - Select one or several Points(s) and/or
 - Select one or several Line/Edge(s) to process 2 ends points and/or

and go to Parameter(s) Window in Task Panel!"""
# - Select one or several Plane/Face(s) to process all Points at once and/or
# - Select one or several Object(s) to process all Points at once;
m_result_msg = " : Projected Point(s) created !"
m_menu_text = "Point = projected(Points)"
m_accel = ""
m_tool_tip = """<b>Create projected point(s)</b> on chosen or main Planes.<br>

<br>
- Select one or several Points and/or<br>
 - Select one or several Line/Edge(s) to process 2 ends points and/or<br>

- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
# - Select one Plane/Face to process all Points at once and/or<br>
# - Select one Object to process all Points at once;<br>
###############
m_macro = "Macro ProjectedPoint"
m_sel_plane = "XY plane"
m_sel_multi = ["XY, YZ planes",
               "XY, XZ planes",
               "YZ, XZ planes",
               "XY, YZ, XZ planes"
               # "Already Selected planes",
               ]
m_sel_planeList = ["Defined plane",
                   "XY plane",
                   "YZ plane",
                   "XZ plane",
                   # "XY, YZ planes",
                   # "XY, XZ planes",
                   # "YZ, XZ planes",
                   # "XY, YZ, XZ planes"
                   # "Already Selected planes",
                   ]
m_proj_line = False
m_group = None
###############


class ProjectedPointPanel:
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
        self.form.UI_ProjectePoint_comboBox.setCurrentIndex(self.form.UI_ProjectePoint_comboBox.findText(m_sel_plane))
        self.form.UI_ProjectePoint_checkBox.setCheckState(QtCore.Qt.Unchecked)
        if m_proj_line:
            self.form.UI_ProjectePoint_checkBox.setCheckState(QtCore.Qt.Checked)

    def accept(self):
        global m_sel_plane
        global m_proj_line
        m_sel_plane = self.form.UI_ProjectePoint_comboBox.currentText()
        m_proj_line = self.form.UI_ProjectePoint_checkBox.isChecked()

        if WF.verbose():
            print_msg("m_sel_plane = " + str(m_sel_plane))
            print_msg("m_proj_line = " + str(m_proj_line))

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


def makeProjectedPointFeature(group):
    """ Makes a ProjectedPoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "ProjectedPoint_P"
    m_part = "Part::FeaturePython"

    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        ProjectedPoint(m_obj)
        ViewProviderProjectedPoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=m_macro)
        return None

    return m_obj


class ProjectedPoint(WF_Point):
    """ The ProjectedPoint feature object. """
    # this method is mandatory
    def __init__(self, selfobj):
        if m_debug:
            print("running ProjectedPoint.__init__ !")

        self.name = "ProjectedPoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our ProjectedPoint feature object.
        selfobj.addProperty("App::PropertyLinkSub",
                            "Point",
                            self.name,
                            "Input Point")
        selfobj.addProperty("App::PropertyLinkSub",
                            "Plane",
                            self.name,
                            "Input Plane")
        m_tooltip = """Indicates the projection plane.
        """
        selfobj.addProperty("App::PropertyEnumeration",
                            "At",
                            self.name,
                            m_tooltip)
        if (sys.version_info > (3, 0)):
            # Python 3 code in this block
            selfobj.At = [v.encode('utf8').decode('utf-8') for v in m_sel_planeList]
            selfobj.At = 'XY plane'.encode('utf8').decode('utf-8')
        else:
            # Python 2 code in this block
            selfobj.At = [v.encode('utf8') for v in m_sel_planeList]
            selfobj.At = 'XY plane'.encode('utf8')

        selfobj.setEditorMode("Point", 1)
        selfobj.setEditorMode("Plane", 1)

        selfobj.Proxy = self

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        if m_debug:
            print("running ProjectedPoint.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        if WF.verbose():
            m_msg = "Recompute Python ProjectedPoint feature\n"
            App.Console.PrintMessage(m_msg)

        if m_debug:
            print("selfobj.PropertiesList = " + str(selfobj.PropertiesList))

        m_PropertiesList = ['Point',
                            "Plane",
                            "At",
                            # "Show",
                            ]
        for m_Property in m_PropertiesList:
            if m_Property not in selfobj.PropertiesList:
                return

        try:
            Vector_point = None
            if m_debug:
                print_msg("selfobj.Point = " + str(selfobj.Point))
                print_msg("selfobj.Plane = " + str(selfobj.Plane))
                # print_msg("selfobj.Show = " + str(selfobj.Show))

            if selfobj.Point is not None:
                n = eval(selfobj.Point[1][0].lstrip('Vertex'))
                if m_debug:
                    print_msg("n = " + str(n))

                point_A = selfobj.Point[0].Shape.Vertexes[n - 1].Point
                x = point_A.x
                y = point_A.y
                z = point_A.z
                # No selected plane so projection on one of MAIN planes
                if selfobj.Plane is None:
                    if selfobj.At == "XY plane":
                        Vector_point = Base.Vector(x, y, 0.0)
                    elif selfobj.At == "YZ plane":
                        Vector_point = Base.Vector(0.0, y, z)
                    elif selfobj.At == "XZ plane":
                        Vector_point = Base.Vector(x, 0.0, z)
                    else:
                        printError_msg("Not valid plane option!", title=m_macro)

                # A selected plane
                else:
                    pass
#                     p=App.Vector(1,1,1)
#                     p.projectToPlane(App.Vector(0,0,0),App.Vector(1,0,1))
#                     projectToPlane parameters are (point on plane,normal direction)

            if Vector_point is not None:
                point = Part.Point(Vector_point)
                selfobj.Shape = point.toShape()
                propertiesPoint(selfobj.Label, self.color)
                selfobj.X = float(Vector_point.x)
                selfobj.Y = float(Vector_point.y)
                selfobj.Z = float(Vector_point.z)

                if m_proj_line and not self.created:
                    point_1 = selfobj.Point
                    object_1 = selfobj
                    twoPL.buildFromOnePointAndOneObject(point_1, object_1, m_group)

                # To be compatible with previous version 2018
                if 'Parametric' in selfobj.PropertiesList:
                    self.created = True
        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

    def onChanged(self, selfobj, prop):
        if WF.verbose():
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")

        if m_debug:
            print("running ProjectedPoint.onChanged !")

        WF_Point.onChanged(self, selfobj, prop)

        if prop == "Parametric":
            if 'Parametric' in selfobj.PropertiesList:
                if selfobj.Parametric == 'Not':
                    selfobj.setEditorMode("At", 1)
                else:
                    selfobj.setEditorMode("At", 0)
            propertiesPoint(selfobj.Label, self.color)

        if prop == "At":
            selfobj.Proxy.execute(selfobj)
        if m_debug:
            print("running ProjectedPoint.onChanged done!")

    def addSubobjects(self, selfobj, points_list=[]):
        "adds Line to this ProjectedPoint object"
#         objs = selfobj.Points
#         if points_list:
#             s1 = []
#             for o in points_list:
#                 if isinstance(o, tuple) or isinstance(o, list):
#                     if o[0].Name != selfobj.Name:
#                         s1.append(tuple(o))
#                 else:
#                     for el in o.SubElementNames:
#                         if "Point" in el:
#                             if o.Object.Name != selfobj.Name:
#                                 s1.append((o.Object, el))
#         selfobj.Points = list(s1)

        selfobj.Proxy.execute(selfobj)
        # self.execute(selfobj)


class ViewProviderProjectedPoint:
    global path_WF_icons
    icon = '/WF_projectedPoint.svg'

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
        return (path_WF_icons + ViewProviderProjectedPoint.icon)

    def setIcon(self, icon='/WF_projectedPoint.svg'):
        ViewProviderProjectedPoint.icon = icon


class CommandProjectedPoint:
    """ Command to create ProjectedPoint feature object. """
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel': m_accel,
                'ToolTip': m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(ProjectedPointPanel())

        run()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("ProjectedPoint", CommandProjectedPoint())


def run():
    global m_group
    m_sel, m_actDoc = getSel(WF.verbose())

    def touch(selfobj):
        if str(selfobj.Parametric) == 'Interactive':
            selfobj.Parametric = 'Dynamic'
            selfobj.touch()
            selfobj.Parametric = 'Interactive'
        if str(selfobj.Parametric) == 'Not':
            selfobj.Parametric = 'Dynamic'
            selfobj.touch()
            selfobj.Parametric = 'Not'

    try:
        Number_of_Vertexes, Vertex_List = m_sel.get_pointsNames(
            getfrom=["Points",
                     "Curves",
                     "Planes",
                     "Objects"
                     ])
        if WF.verbose():
            print_msg("Number_of_Vertexes = " + str(Number_of_Vertexes))
            print_msg("Vertex_List = " + str(Vertex_List))

        if Number_of_Vertexes < 1:
            raise Exception(m_exception_msg)

        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set001"
            m_group = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            # Create a sub group if needed
            if Number_of_Vertexes > 1 or m_sel_plane in m_sel_multi or m_proj_line:
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=m_macro)
                    printError_msg(m_error_msg)

            if WF.verbose():
                print_msg("Group = " + str(m_group.Label))

            for point in Vertex_List:
                if WF.verbose():
                    print_msg("Selected plane" + str(m_sel_plane))

                # Possible selections
                # "XY plane",
                # "YZ plane",
                # "XZ plane",
                # "XY, YZ planes",
                # "XY, XZ planes",
                # "YZ, XZ planes",
                # "XY, YZ, XZ planes"
                # "Already Selected planes",

                if m_sel_plane in ["XY plane",
                                   "XY, YZ planes",
                                   "XY, XZ planes",
                                   "XY, YZ, XZ planes"]:
                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj = makeProjectedPointFeature(m_group)
                    selfobj.Point = point
                    selfobj.At = "XY plane"
                    selfobj.Proxy.execute(selfobj)
                    touch(selfobj)

                if m_sel_plane in ["YZ plane",
                                   "XY, YZ planes",
                                   "YZ, XZ planes",
                                   "XY, YZ, XZ planes"]:
                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj = makeProjectedPointFeature(m_group)
                    selfobj.Point = point
                    selfobj.At = "YZ plane"
                    selfobj.Proxy.execute(selfobj)
                    touch(selfobj)
                if m_sel_plane in ["XZ plane",
                                   "XY, XZ planes",
                                   "YZ, XZ planes",
                                   "XY, YZ, XZ planes"]:
                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj = makeProjectedPointFeature(m_group)
                    selfobj.Point = point
                    selfobj.At = "XZ plane"
                    selfobj.Proxy.execute(selfobj)
                    touch(selfobj)
#                 if m_proj_line:
#                     point_B = Vector_point
#                     if WF.verbose():
#                         print_msg("point_A = " + str(point_A))
#                         print_msg("point_B = " + str(point_B))
#                     App.ActiveDocument.openTransaction("Macro TwoPointsLine")
#                     selfobj2 = twoPL.makeTwoPointsLineFeature(m_group)
#                     selfobj2.Point1 = point_A
#                     selfobj2.Point2 = point_B
#                     selfobj2.Extension = 0.0
#                     selfobj2.Proxy.execute(selfobj2)
        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

        App.ActiveDocument.commitTransaction()

    except Exception as err:
        printError_msg(err.args[0], title=m_macro)


if __name__ == '__main__':
    run()
