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

__title__ = "Macro_CenterLinePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro CenterLinePoint.
Creates a parametric CenterLinePoint from an Edge
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
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
m_icon = "/WF_centerLinePoint.svg"
m_dialog = "/WF_UI_centerLinePoint.ui"
m_dialog_title = "Define number of parts and location(s)."
m_exception_msg = """
Unable to create Center Line Point(s) :
- Select one or several Line/Edge(s) and/or
- Select one Plane/Face to process all (4) Edges at once and/or
- Select one Object to process all Edges at once;

You can also select 2 points (in place of an Edge) !

and go to Parameter(s) Window in Task Panel!"""
m_result_msg = " : Mid Line Point(s) created !"
m_menu_text = "Point(s) = center(Line)"
m_accel = ""
m_tool_tip = """<b>Create Point(s)</b> at Center location of each selected Line(s).<br>
Cut each selected Line(s) in 2 (n) parts and<br>
create a (n-1) Point(s) along selected edge(s).<br>
The number (n) indicates how many parts to consider.<br>
<br>
- Select one or several Line/Edge(s)<br>
 (you can also select 2 points in place of one Line/Edge) and/or<br>
- Select one Plane/Face to process all (4) Edges and/or<br>
- Select one Object to process all Edges at once<br>
- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
###############
m_macro = "Macro CenterLinePoint"
m_location = "Single"
m_locations = ["Single", "All"]
m_numberLinePart = 2
m_indexPart = 1
###############


class CenterLinePointPanel:
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
        self.form.UI_CenterLinePoint_spin_numberLinePart.setValue(m_numberLinePart)
        self.form.UI_CenterLinePoint_spin_indexPart.setValue(m_indexPart)
        self.form.UI_CenterLinePoint_checkBox.setCheckState(QtCore.Qt.Unchecked)
        if m_location == "All":
            self.form.UI_CenterLinePoint_checkBox.setCheckState(QtCore.Qt.Checked)

    def accept(self):
        global m_location
        global m_numberLinePart
        global m_indexPart

        m_select = self.form.UI_CenterLinePoint_checkBox.isChecked()
        if m_select:
            m_location = "All"
        else:
            m_location = "Single"
        m_numberLinePart = self.form.UI_CenterLinePoint_spin_numberLinePart.value()
        m_indexPart = self.form.UI_CenterLinePoint_spin_indexPart.value()

        if WF.verbose():
            print_msg("m_numberLinePart = " + str(m_numberLinePart))
            print_msg("m_indexPart = " + str(m_indexPart))

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


def makeCenterLinePointFeature(group):
    """ Makes a CenterLinePoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "CenterLinePoint_P"
    m_part = "Part::FeaturePython"

    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        CenterLinePoint(m_obj)
        ViewProviderCenterLinePoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=m_macro)
        return None

    return m_obj


class CenterLinePoint(WF_Point):
    """ The CenterLinePoint feature object. """
    # this method is mandatory
    def __init__(self, selfobj):
        if m_debug:
            print("running CenterLinePoint.__init__ !")

        self.name = "CenterLinePoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our CenterLinePoint feature object.
        selfobj.addProperty("App::PropertyLinkSubGlobal",
                            "Edge",
                            self.name,
                            "Input edge")
        selfobj.addProperty("App::PropertyLinkSubGlobal",
                            "Point1",
                            self.name,
                            "Start point")
        selfobj.addProperty("App::PropertyLinkSubGlobal",
                            "Point2",
                            self.name,
                            "End point")

        m_tooltip = """The number indicates in how many Parts
each selected parent Lines(s) will be cut in.
Limits : (Min: 2, Max: 100).
"""
        selfobj.addProperty("App::PropertyInteger",
                            "NumberLinePart",
                            self.name,
                            m_tooltip).NumberLinePart = 2

        m_tooltip = """The location of the point :
1/2 means middle of the segment !
The number indicates at which part's end the point will be located.
- If the Number of parts is 2 and Point at part's end 1,
this means that the point will be located in the middle of the Line.
- If the Number of parts is 2 and Point at part's end 2,
this means that the point will be located in the end of the Line.

Negative value are allowed
Limits : [-1000:1000]
"""
        selfobj.addProperty("App::PropertyInteger",
                            "IndexPart",
                            self.name,
                            m_tooltip).IndexPart = 1

        selfobj.setEditorMode("Edge", 1)
        selfobj.setEditorMode("Point1", 1)
        selfobj.setEditorMode("Point2", 1)

        selfobj.Proxy = self

    def execute_2018(self, selfobj):
        if WF.verbose():
            m_msg = "Recompute Python CenterLinePoint feature (old manner)\n"
            App.Console.PrintMessage(m_msg)

        if 'Edge' not in selfobj.PropertiesList:
            return
        if 'IndexPart' not in selfobj.PropertiesList:
            return
        if 'NumberLinePart' not in selfobj.PropertiesList:
            return

        n = eval(selfobj.Edge[1][0].lstrip('Edge'))
        if WF.verbose():
            print_msg("n = " + str(n))

        try:
            Vector_point = alongLinePoint(selfobj.Edge[0].Shape.Edges[n - 1],
                                          selfobj.IndexPart,
                                          selfobj.NumberLinePart)

            point = Part.Point(Vector_point)
            selfobj.Shape = point.toShape()
            propertiesPoint(selfobj.Label)
            selfobj.X = float(Vector_point.x)
            selfobj.Y = float(Vector_point.y)
            selfobj.Z = float(Vector_point.z)
        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        if m_debug:
            print("running CenterLinePoint.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return
        # To be compatible with previous version 2018
        if 'parametric' in selfobj.PropertiesList:
            self.execute_2018(selfobj)

        if WF.verbose():
            m_msg = "Recompute Python CenterLinePoint feature\n"
            App.Console.PrintMessage(m_msg)

        m_PropertiesList = ['Edge',
                            'Point1',
                            'Point2',
                            'IndexPart',
                            'NumberLinePart'
                            ]
        for m_Property in m_PropertiesList:
            if m_Property not in selfobj.PropertiesList:
                return

        try:
            Vector_point = None
            if selfobj.Point1 is not None and selfobj.Point2 is not None:
                n1 = eval(selfobj.Point1[1][0].lstrip('Vertex'))
                n2 = eval(selfobj.Point2[1][0].lstrip('Vertex'))
                if m_debug:
                    print_msg(str(selfobj.Point1))
                    print_msg(str(selfobj.Point2))
                    print_msg("n1 = " + str(n1))
                    print_msg("n2 = " + str(n2))

                point1 = selfobj.Point1[0].Shape.Vertexes[n1 - 1].Point
                point2 = selfobj.Point2[0].Shape.Vertexes[n2 - 1].Point

                Vector_point = alongTwoPointsPoint(point1,
                                                   point2,
                                                   selfobj.IndexPart,
                                                   selfobj.NumberLinePart)
            elif selfobj.Edge is not None:
                n = eval(selfobj.Edge[1][0].lstrip('Edge'))
                if m_debug:
                    print_msg(str(selfobj.Edge))
                    print_msg("n = " + str(n))
                    print_msg(str(selfobj.Edge[0].Shape.Edges))

                if len(selfobj.Edge[0].Shape.Edges) == 0:
                    return
                Vector_point = alongLinePoint(selfobj.Edge[0].Shape.Edges[n - 1],
                                              selfobj.IndexPart,
                                              selfobj.NumberLinePart)
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
            print("running CenterLinePoint.onChanged !")

        WF_Point.onChanged(self, selfobj, prop)

        if prop == "Parametric":
            if 'Parametric' in selfobj.PropertiesList:
                if selfobj.Parametric == 'Not':
                    selfobj.setEditorMode("NumberLinePart", 1)
                    selfobj.setEditorMode("IndexPart", 1)
                else:
                    selfobj.setEditorMode("NumberLinePart", 0)
                    selfobj.setEditorMode("IndexPart", 0)
            propertiesPoint(selfobj.Label, self.color)

        if prop == "IndexPart":
            selfobj.Proxy.execute(selfobj)

        if prop == 'NumberLinePart':
            if selfobj.NumberLinePart <= 1:
                selfobj.NumberLinePart = 2
            elif selfobj.NumberLinePart > 100:
                selfobj.NumberLinePart = 100
            selfobj.Proxy.execute(selfobj)


class ViewProviderCenterLinePoint:
    global path_WF_icons
    icon = '/WF_centerLinePoint.svg'

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
        return (path_WF_icons + ViewProviderCenterLinePoint.icon)

    def setIcon(self, icon='/WF_centerLinePoint.svg'):
        ViewProviderCenterLinePoint.icon = icon


class CommandCenterLinePoint:
    """ Command to create CenterLinePoint feature object. """
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel': m_accel,
                'ToolTip': m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(CenterLinePointPanel())

        run()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("CenterLinePoint", CommandCenterLinePoint())


def run():
    m_sel, m_actDoc = getSel(WF.verbose())

    try:
        Number_of_Edges, Edge_List = m_sel.get_segmentsNames(
            getfrom=["Segments", "Curves", "Planes", "Objects"])
        if WF.verbose():
            print_msg("Number_of_Edges = " + str(Number_of_Edges))
            print_msg("Edge_List = " + str(Edge_List))

        Number_of_Vertexes, Vertex_List = m_sel.get_pointsNames(
            getfrom=["Points", "Curves", "Objects"])
        if WF.verbose():
            print_msg("Number_of_Vertexes = " + str(Number_of_Vertexes))
            print_msg("Vertex_List = " + str(Vertex_List))

        if Number_of_Edges == 0 and Number_of_Vertexes == 0:
            raise Exception(m_exception_msg)
        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set001"
            m_group = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            # From Edges
            # Create a sub group if needed
            if Number_of_Edges > 1 or m_location != "Single":
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=m_macro)
                    printError_msg(m_error_msg)

            if WF.verbose():
                print_msg("Group = " + str(m_group.Label))

            for i in range(Number_of_Edges):
                edge = Edge_List[i]

                if WF.verbose():
                    print_msg("Location = " + str(m_location))

                if m_location == "Single":
                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj = makeCenterLinePointFeature(m_group)
                    selfobj.Edge = edge
                    selfobj.Point1 = None
                    selfobj.Point2 = None
                    selfobj.NumberLinePart = m_numberLinePart
                    selfobj.IndexPart = m_indexPart
                    selfobj.Proxy.execute(selfobj)
                else:
                    for m_iPart in range(m_numberLinePart + 1):
                        App.ActiveDocument.openTransaction(m_macro)
                        selfobj = makeCenterLinePointFeature(m_group)
                        selfobj.Edge = edge
                        selfobj.Point1 = None
                        selfobj.Point2 = None
                        selfobj.NumberLinePart = m_numberLinePart
                        selfobj.IndexPart = m_iPart
                        selfobj.Proxy.execute(selfobj)
                        if str(selfobj.Parametric) == 'Interactive':
                            selfobj.Parametric = 'Dynamic'
                            selfobj.touch()
                            selfobj.Parametric = 'Interactive'
                        if str(selfobj.Parametric) == 'Not':
                            selfobj.Parametric = 'Dynamic'
                            selfobj.touch()
                            selfobj.Parametric = 'Not'

            # From Vertexes
            if Number_of_Vertexes > 2:
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=m_macro)
                    printError_msg(m_error_msg)

            # Even number of vertexes
            if (Number_of_Vertexes % 2 == 0):
                if WF.verbose():
                    print_msg("Even number of points")

                if Number_of_Vertexes == 2:
                    vertex1 = Vertex_List[0]
                    vertex2 = Vertex_List[1]

                    if WF.verbose():
                        print_msg("vertex1 = " + str(vertex1))
                        print_msg("vertex2 = " + str(vertex2))

                    if m_location == "Single":
                        App.ActiveDocument.openTransaction(m_macro)
                        selfobj = makeCenterLinePointFeature(m_group)
                        selfobj.Edge = None
                        selfobj.Point1 = vertex1
                        selfobj.Point2 = vertex2
                        selfobj.NumberLinePart = m_numberLinePart
                        selfobj.IndexPart = m_indexPart
                        selfobj.Proxy.execute(selfobj)
                    else:
                        for m_iPart in range(m_numberLinePart + 1):
                            App.ActiveDocument.openTransaction(m_macro)
                            selfobj = makeCenterLinePointFeature(m_group)
                            selfobj.Edge = None
                            selfobj.Point1 = vertex1
                            selfobj.Point2 = vertex2
                            selfobj.NumberLinePart = m_numberLinePart
                            selfobj.IndexPart = m_iPart
                            selfobj.Proxy.execute(selfobj)
                else:
                    for i in range(0, Number_of_Vertexes - 2, 2):
                        vertex1 = Vertex_List[i]
                        vertex2 = Vertex_List[i + 1]

                        if WF.verbose():
                            print_msg("vertex1 = " + str(vertex1))
                            print_msg("vertex2 = " + str(vertex2))

                        if m_location == "Single":
                            App.ActiveDocument.openTransaction(m_macro)
                            selfobj = makeCenterLinePointFeature(m_group)
                            selfobj.Edge = None
                            selfobj.Point1 = vertex1
                            selfobj.Point2 = vertex2
                            selfobj.NumberLinePart = m_numberLinePart
                            selfobj.IndexPart = m_indexPart
                            selfobj.Proxy.execute(selfobj)
                        else:
                            for m_iPart in range(m_numberLinePart + 1):
                                App.ActiveDocument.openTransaction(m_macro)
                                selfobj = makeCenterLinePointFeature(m_group)
                                selfobj.Edge = None
                                selfobj.Point1 = vertex1
                                selfobj.Point2 = vertex2
                                selfobj.NumberLinePart = m_numberLinePart
                                selfobj.IndexPart = m_iPart
                                selfobj.Proxy.execute(selfobj)
            # Odd number of vertexes
            else:
                if WF.verbose():
                    print_msg("Odd number of points")
                for i in range(Number_of_Vertexes - 1):
                    vertex1 = Vertex_List[i]
                    vertex2 = Vertex_List[i + 1]

                    if WF.verbose():
                        print_msg("vertex1 = " + str(vertex1))
                        print_msg("vertex2 = " + str(vertex2))

                    if m_location == "Single":
                        App.ActiveDocument.openTransaction(m_macro)
                        selfobj = makeCenterLinePointFeature(m_group)
                        selfobj.Edge = None
                        selfobj.Point1 = vertex1
                        selfobj.Point2 = vertex2
                        selfobj.NumberLinePart = m_numberLinePart
                        selfobj.IndexPart = m_indexPart
                        selfobj.Proxy.execute(selfobj)
                    else:
                        for m_iPart in range(m_numberLinePart + 1):
                            App.ActiveDocument.openTransaction(m_macro)
                            selfobj = makeCenterLinePointFeature(m_group)
                            selfobj.Edge = None
                            selfobj.Point1 = vertex1
                            selfobj.Point2 = vertex2
                            selfobj.NumberLinePart = m_numberLinePart
                            selfobj.IndexPart = m_iPart
                            selfobj.Proxy.execute(selfobj)

        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

        App.ActiveDocument.commitTransaction()

    except Exception as err:
        printError_msg(err.args[0], title=m_macro)


if __name__ == '__main__':
    run()
