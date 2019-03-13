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
from WF_Objects_base import WF_Point
# from InitGui import m_debug
if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro_NPointsPoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro NPointsPoint.
Creates a parametric NPointsPoint from a list of Points
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
    from WF_utils import *
except ImportError:
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
m_icon = "/WF_nPointsPoint.svg"
m_dialog = "/WF_UI_nPointsPoint.ui"
m_dialog_title = ""
m_exception_msg = """
Unable to create a Mean Point :
- Select several Points(s) and/or
- Select several Line/Edge(s) to process 2 ends points and/or
- Select one or several Plane/Face(s) to process all Points at once and/or
- Select one or several Object(s) to process all Points at once;

and go to Parameter(s) Window in Task Panel!"""
m_result_msg = " : N Points Point created !"
m_menu_text = "Point = center(Points)"
m_accel = ""
m_tool_tip = """<b>Create a Point</b> at MEAN location of all selected points.<br>

<br>
- Select several Points and/or<br>
- Select several Line/Edge(s) to process 2 ends points and/or<br>
- Select one Plane/Face to process all Points at once and/or<br>
- Select one Object to process all Points at once;<br>
- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
###############
m_macro = "Macro NPointsPoint"
###############


# def linkSubList_convertToOldStyle(references):
#     """("input: [(obj1, (sub1, sub2)), (obj2, (sub1, sub2))]\n"
#     "output: [(obj1, sub1), (obj1, sub2), (obj2, sub1), (obj2, sub2)]")"""
#     result = []
#     for tup in references:
#         if type(tup[1]) is tuple or type(tup[1]) is list:
#             for subname in tup[1]:
#                 result.append((tup[0], subname))
#             if len(tup[1]) == 0:
#                 result.append((tup[0], ''))
#         else:
#             # old style references, no conversion required
#             result.append(tup)
#     return result


class NPointsPointPanel:
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
        return (len(Gui.Selection.getSelectionEx(App.activeDocument().Name)) == 0)


def makeNPointsPointFeature(group):
    """ Makes a NPointsPoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "NPointsPoint_P"
    m_part = "Part::FeaturePython"

    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        m_inst = NPointsPoint(m_obj)
        ViewProviderNPointsPoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=m_macro)
        return None

    return m_obj, m_inst


class NPointsPoint(WF_Point):
    """ The NPointsPoint feature object. """
    # this method is mandatory
    def __init__(self, selfobj):
        if m_debug:
            print("running NPointsPoint.__init__ !")

        self.name = "NPointsPoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our NPointsPoint feature object.
        selfobj.addProperty("App::PropertyLinkSubList",
                            "Points",
                            self.name,
                            "List of Points")
        selfobj.Points = []
        selfobj.setEditorMode("Points", 1)

        selfobj.Proxy = self
        # save the object in the class, to store or retrieve specific data from it
        # from within the class
        # self.Object = selfobj

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        if m_debug:
            print("running NPointsPoint.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        if WF.verbose():
            m_msg = "Recompute Python NPointsPoint feature\n"
            App.Console.PrintMessage(m_msg)

        if m_debug:
            print("selfobj.PropertiesList = " + str(selfobj.PropertiesList))

        m_PropertiesList = ['Points',
                            ]
        for m_Property in m_PropertiesList:
            if m_Property not in selfobj.PropertiesList:
                return

        try:
            Vector_point = None
            if m_debug:
                print("selfobj.Points = " + str(selfobj.Points))
            if selfobj.Points is not None:
                m_points = []
                for p in linkSubList_convertToOldStyle(selfobj.Points):
                    n = eval(p[1].lstrip('Vertex'))
                    if m_debug:
                        print("p " + str(p))
                        print_msg("n = " + str(n))
                    m_points.append(p[0].Shape.Vertexes[n - 1].Point)

            Vector_point = meanVectorsPoint(m_points)

            if Vector_point is not None:
                point = Part.Point(Vector_point)
                selfobj.Shape = point.toShape()
                propertiesPoint(selfobj.Label, self.color)
                selfobj.X = float(Vector_point.x)
                selfobj.Y = float(Vector_point.y)
                selfobj.Z = float(Vector_point.z)
                # To be compatible with previous version 2018
                if 'Parametric' in selfobj.PropertiesList:
                    self.created = True
        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

    def onChanged(self, selfobj, prop):
        if WF.verbose():
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")

        if m_debug:
            print("running NPointsPoint.onChanged !")

        WF_Point.onChanged(self, selfobj, prop)

        if prop == "Parametric":
            if 'Parametric' in selfobj.PropertiesList:
                if selfobj.Parametric == 'Not':
                    selfobj.setEditorMode("X", 1)
                    selfobj.setEditorMode("Y", 1)
                    selfobj.setEditorMode("Z", 1)
                else:
                    selfobj.setEditorMode("X", 0)
                    selfobj.setEditorMode("Y", 0)
                    selfobj.setEditorMode("Z", 0)
            propertiesPoint(selfobj.Label, self.color)

        if prop == "Points":
            selfobj.Proxy.execute(selfobj)

    def addSubobjects(self, selfobj, points_list=[]):
        "adds pointlinks to this TwoPointsLine object"
        objs = selfobj.Points
        if points_list:
            s1 = []
            for o in points_list:
                if isinstance(o, tuple) or isinstance(o, list):
                    if o[0].Name != selfobj.Name:
                        s1.append(tuple(o))
                else:
                    for el in o.SubElementNames:
                        if "Point" in el:
                            if o.Object.Name != selfobj.Name:
                                s1.append((o.Object, el))
        selfobj.Points = list(s1)

        selfobj.Proxy.execute(selfobj)
        # self.execute(selfobj)


class ViewProviderNPointsPoint:
    global path_WF_icons
    icon = '/WF_nPointsPoint.svg'

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
        return (path_WF_icons + ViewProviderNPointsPoint.icon)

    def setIcon(self, icon='/WF_nPointsPoint.svg'):
        ViewProviderNPointsPoint.icon = icon


class CommandNPointsPoint:
    """ Command to create NPointsPoint feature object. """
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel': m_accel,
                'ToolTip': m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(NPointsPointPanel())

        run()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("NPointsPoint", CommandNPointsPoint())


def run():
    m_sel, _ = getSel(WF.verbose())

    try:
        Number_of_Vertexes, Vertex_List = m_sel.get_pointsNames(
            getfrom=["Points",
                     "Curves",
                     "Planes",
                     "Objects"])
        if WF.verbose():
            print_msg("Number_of_Vertexes = " + str(Number_of_Vertexes))
            print_msg("Vertex_List = " + str(Vertex_List))

        if Number_of_Vertexes < 2:
            raise Exception(m_exception_msg)

        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set001"
            m_group = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            points = []
            # Case of only 2 points
            if Number_of_Vertexes == 2:
                if WF.verbose():
                    print_msg("Process only 2 points")
                vertex1 = Vertex_List[0]
                vertex2 = Vertex_List[1]
                points.append(vertex1)
                points.append(vertex2)

                if WF.verbose():
                    print_msg("vertex1 = " + str(vertex1))
                    print_msg("vertex2 = " + str(vertex2))

                App.ActiveDocument.openTransaction(m_macro)
                selfobj, m_inst = makeNPointsPointFeature(m_group)
                if m_debug:
                    print("selfobj : " + str(selfobj))
                m_inst.addSubobjects(selfobj, points)
                selfobj.Proxy.execute(selfobj)
            # Case of more than 2 points
            else:
                if WF.verbose():
                    print_msg("Process more than 2 points")
                for i in range(Number_of_Vertexes):
                    vertex1 = Vertex_List[i]
                    points.append(vertex1)
                    if WF.verbose():
                        print_msg("vertex1 = " + str(vertex1))

                App.ActiveDocument.openTransaction(m_macro)
                selfobj, m_inst = makeNPointsPointFeature(m_group)
                if m_debug:
                    print("selfobj : " + str(selfobj))
                m_inst.addSubobjects(selfobj, points)
        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

        App.ActiveDocument.commitTransaction()

    except Exception as err:
        printError_msg(err.args[0], title=m_macro)


if __name__ == '__main__':
    run()
