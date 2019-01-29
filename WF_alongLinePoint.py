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
from PySide import QtGui,QtCore
import WF
from WF_Objects_base import WF_Point
if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro AlongLinePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro AlongLinePoint.
Creates a parametric AlongLinePoint from a Line and a Point
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
    # from WF_utils import *
except ImportError:
    print("ERROR: cannot load WF modules !")
    sys.exit(1)

###############
m_icon = "/WF_alongLinePoint.svg"
m_dialog = "/WF_UI_alongLinePoint.ui"
m_dialog_title = "Define distance"
m_exception_msg = """
Unable to create Point along a Line :
- Select first one Line/Edge where to attach the new point and
- Define one or several Reference Point(s) by either
    - Select one or several Line/Edge(s) and/or
    - Select one or several Point(s).

The reference Point is the projection of the selected Point(s)
onto the first selected Line.
Or the reference Point is the projection of Line(s)
onto the first selected Line.

and go to Parameter(s) Window in Task Panel!"""
m_result_msg = " : Point along a Line created !"
m_menu_text = "Point(s) = along(Line, Point)"
m_accel = ""
m_tool_tip = """<b>Create Point(s)</b> along Line(s) at a defined<br>
 distance of intersection from selected Point(s)/Line(s).<br>
<br>
First<br>
- Select one Line/Edge where to attach the new point<br>
and Second define one or several Reference Point(s) by either<br>
- Select one or several Line/Edge(s) and/or<br>
- Select one or several Point(s)<br>
- Then Click on the button<br>
<br>
The reference Point is the projection of the selected Point(s)<br>
onto the first selected Line.<br>
Or the reference Point is the projection of Line(s)<br>
onto the first selected Line.<br>
<br>
Be aware that if second Points or Lines selected are not on the first<br>
Line, an intersection Point is calculated as reference by projection.<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
###############
m_macro = "Macro AlongLinePoint"
m_distanceLinePoint = 10.0
###############


class AlongLinePointPanel:
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
        self.form.UI_Distance.setText(str(m_distanceLinePoint))

    def accept(self):
        global m_distanceLinePoint

        m_distanceLinePoint = float(self.form.UI_Distance.text())

        if WF.verbose():
            print_msg("m_distanceLinePoint = " + str(m_distanceLinePoint))

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


def makeAlongLinePointFeature(group):
    """ Makes a AlongLinePoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "AlongLinePoint_P"
    m_part = "Part::FeaturePython"

    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        AlongLinePoint(m_obj)
        ViewProviderAlongLinePoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.message, title=m_macro)
        return None

    return m_obj


class AlongLinePoint(WF_Point):
    """ The AlongLinePoint feature object. """
    # this method is mandatory
    def __init__(self, selfobj):
        self.name = "AlongLinePoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our AlongLinePoint feature object.
#         selfobj.addProperty("App::PropertyLinkSub","AlongEdge",self.name,
#                             "Along edge")
#         selfobj.addProperty("App::PropertyLinkSub","Point",self.name,
#                             "point")
#         selfobj.addProperty("App::PropertyLinkSub","Edge",self.name,
#                             "edge")
        selfobj.addProperty("App::PropertyLinkSubGlobal",
                            "AlongEdge",
                            self.name,
                            "Along edge")
        selfobj.addProperty("App::PropertyLinkSubGlobal",
                            "Point",
                            self.name,
                            "point")
        selfobj.addProperty("App::PropertyLinkSubGlobal",
                            "Edge",
                            self.name,
                            "edge")

        m_tooltip = """Distance from the reference Point.
The reference Point is the projection of the selected Point(s)
onto the first selected Line.
Or the reference Point is the projection of Line(s)
onto the first selected Line."""
        selfobj.addProperty("App::PropertyFloat",
                            "Distance",
                            self.name,
                            m_tooltip).Distance = 10.0

        selfobj.setEditorMode("AlongEdge", 1)
        selfobj.setEditorMode("Point", 1)
        selfobj.setEditorMode("Edge", 1)

        selfobj.Proxy = self

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        if m_debug:
            print("running AlongLinePoint.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        if WF.verbose():
            m_msg = "Recompute Python AlongLinePoint feature\n"
            App.Console.PrintMessage(m_msg)

        m_PropertiesList = ['AlongEdge',
                            'Edge',
                            'Point'
                            ]
        for m_Property in m_PropertiesList:
            if m_Property not in selfobj.PropertiesList:
                return

        if selfobj.AlongEdge is None:
            return

        if selfobj.Edge is None and selfobj.Point is None:
            return

        if m_debug:
            print("selfobj.AlongEdge = " + str(selfobj.AlongEdge))
            print("selfobj.Edge = " + str(selfobj.Edge))
            print("selfobj.Point = " + str(selfobj.Point))

        n1 = eval(selfobj.AlongEdge[1][0].lstrip('Edge'))
        print("running AlongLinePoint.execute !")
        if selfobj.Edge is not None:
            n2 = eval(selfobj.Edge[1][0].lstrip('Edge'))
        else:
            if selfobj.Point != selfobj.AlongEdge:
                n3 = eval(selfobj.Point[1][0].lstrip('Vertex'))
            else:
                print(selfobj.Point[1][0].name())
                n3 = eval(selfobj.Point[1][0].lstrip('Edge'))

        print("running AlongLinePoint.execute !")
        m_distanceLinePoint = selfobj.Distance
        print("running AlongLinePoint.execute !")
        if WF.verbose():
            print_msg("n1 = " + str(n1))
            if selfobj.Edge is not None:
                print_msg("n2 = " + str(n2))
            else:
                print_msg("n3 = " + str(n3))
            print_msg("m_distanceLinePoint = " + str(m_distanceLinePoint))

        try:
            Vector_point = None
            m_alongedge = selfobj.AlongEdge[0].Shape.Edges[n1-1]
            if selfobj.Edge is not None:
                m_edge = selfobj.Edge[0].Shape.Edges[n2-1]
            else:
                m_point = selfobj.Point[0].Shape.Vertexes[n3-1].Point

            if WF.verbose():
                print_msg("m_alongedge = " + str(m_alongedge))
                if selfobj.Edge is not None:
                    print_msg("m_edge = " + str(m_edge))
                else:
                    print_msg("m_point = " + str(m_point))

            Vector_A = m_alongedge.valueAt(0.0)
            Vector_B = m_alongedge.valueAt(m_alongedge.Length)
            if WF.verbose():
                print_msg("Vector_A = " + str(Vector_A))
                print_msg("Vector_B = " + str(Vector_B))

            if isEqualVectors(Vector_A, Vector_B):
                return

            if selfobj.Edge is not None:
                m_dist = m_alongedge.distToShape(m_edge)
                Vector_C = m_dist[1][0][0]
            else:
                Vector_C = m_point

            if WF.verbose():
                print_msg("Vector_C = " + str(Vector_C))

            # Calculate intersection Point
            Vector_T, _, _ = intersectPerpendicularLine(Vector_A,
                                                        Vector_B,
                                                        Vector_C,)
            if WF.verbose():
                print_msg("Vector_T = " + str(Vector_T))

            Vector_Translate = (Vector_B - Vector_A)
            if m_distanceLinePoint != 0.0:
                Vector_Translate = Vector_Translate.normalize() * m_distanceLinePoint
                Vector_point = Vector_T + Vector_Translate
            else:
                Vector_point = Vector_T

            if Vector_point is not None:
                point = Part.Point(Vector_point)
                selfobj.Shape = point.toShape()
                propertiesPoint(selfobj.Label)
                selfobj.X = float(Vector_point.x)
                selfobj.Y = float(Vector_point.y)
                selfobj.Z = float(Vector_point.z)
                # To be compatible with previous version 2018
                if 'Parametric' in selfobj.PropertiesList:
                    self.created = True
        except Exception as err:
            printError_msg(err.message, title=m_macro)

    def onChanged(self, selfobj, prop):
        if m_debug:
            print("running AlongLinePoint.onChanged !")

        if WF.verbose():
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")

        WF_Point.onChanged(self, selfobj, prop)


class ViewProviderAlongLinePoint:
    global path_WF_icons
    icon = '/WF_alongLinePoint.svg'

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
        return (path_WF_icons + ViewProviderAlongLinePoint.icon)

    def setIcon(self, icon='/WF_alongLinePoint.svg'):
        ViewProviderAlongLinePoint.icon = icon


class CommandAlongLinePoint:
    """ Command to create AlongLinePoint feature object. """
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel': m_accel,
                'ToolTip': m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(AlongLinePointPanel())

        run()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("AlongLinePoint", CommandAlongLinePoint())


def run():
    m_sel, m_actDoc = getSel(WF.verbose())

    if WF.verbose():
        print_msg("m_sel = " + str(m_sel))

    def createSubGroup(main_dir,
                       sub_dir,
                       error_msg):
        try:
            m_ob_dir = App.ActiveDocument.getObject(main_dir)
            m_ob = m_ob_dir.newObject("App::DocumentObjectGroup",
                                      str(sub_dir))
            m_group = m_actDoc.getObject(str(m_ob.Label))
        except Exception as err:
            printError_msg(err.message, title=m_macro)
            printError_msg(error_msg)
        return m_group

    try:
        Number_of_Edges, Edge_List = m_sel.get_segmentsNames(
            getfrom=["Segments", "Curves"])
        if WF.verbose():
            print_msg("Number_of_Edges = " + str(Number_of_Edges))
            print_msg("Edge_List = " + str(Edge_List))

        Number_of_Vertexes, Vertex_List = m_sel.get_pointsNames(
            getfrom=["Points", "Segments", "Curves", "Objects"])
        if WF.verbose():
            print_msg("Number_of_Vertexes = " + str(Number_of_Vertexes))
            print_msg("Vertex_List = " + str(Vertex_List))

        if Number_of_Edges == 0:
            raise Exception(m_exception_msg)
        else:
            if Number_of_Edges == 1 and Number_of_Vertexes == 0:
                raise Exception(m_exception_msg)

        m_main_dir = "WorkPoints_P"
        m_sub_dir = "Set"
        m_group = createFolders(str(m_main_dir))
        m_error_msg = "Could not Create '"
        m_error_msg += str(m_sub_dir) + "' Objects Group!"

        # Selection of : One Edge and One or several Point(s)
        if Number_of_Edges == 1 and Number_of_Vertexes > 0:
            try:
                # Create a sub group if needed
                if Number_of_Vertexes > 1:
                    m_group = createSubGroup(m_main_dir,
                                             m_sub_dir,
                                             m_error_msg)

                if WF.verbose():
                    print_msg("Group = " + str(m_group.Label))

                edge = Edge_List[0]
                if WF.verbose():
                    print_msg("edge = " + str(edge))

                for j in range(Number_of_Vertexes):
                    point = Vertex_List[j]
                    if WF.verbose():
                        print_msg("point = " + str(point))

                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj = makeAlongLinePointFeature(m_group)
                    selfobj.AlongEdge = edge
                    selfobj.Point = point
                    selfobj.Edge = None
                    selfobj.Distance = m_distanceLinePoint
                    selfobj.Proxy.execute(selfobj)

            finally:
                App.ActiveDocument.commitTransaction()

        # Selection of : One Edge and One or several Edge(s)
        if Number_of_Edges > 1 and Number_of_Vertexes == 0:
            try:
                # Create a sub group if needed
                if Number_of_Edges > 2:
                    m_group = createSubGroup(m_main_dir,
                                             m_sub_dir,
                                             m_error_msg)

                if WF.verbose():
                    print_msg("Group = " + str(m_group.Label))

                edge = Edge_List[0]
                if WF.verbose():
                    print_msg("edge = " + str(edge))

                for other_edge in Edge_List[1:]:
                    if WF.verbose():
                        print_msg("other_edge = " + str(other_edge))

                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj = makeAlongLinePointFeature(m_group)
                    selfobj.AlongEdge = edge
                    selfobj.Point = None
                    selfobj.Edge = other_edge
                    selfobj.Distance = m_distanceLinePoint
                    selfobj.Proxy.execute(selfobj)

            finally:
                App.ActiveDocument.commitTransaction()

        # Selection of : same number of Edges and Points
        if Number_of_Edges > 1 and Number_of_Vertexes == Number_of_Edges:
            try:
                # Create a sub group if needed
                m_group = createSubGroup(m_main_dir,
                                         m_sub_dir,
                                         m_error_msg)

                if WF.verbose():
                    print_msg("Group = " + str(m_group.Label))

                for edge, point in zip(Edge_List, Vertex_List):
                    if WF.verbose():
                        print_msg("edge = " + str(edge))
                        print_msg("point = " + str(point))

                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj = makeAlongLinePointFeature(m_group)
                    selfobj.AlongEdge = edge
                    selfobj.Point = point
                    selfobj.Edge = None
                    selfobj.Distance = m_distanceLinePoint
                    selfobj.Proxy.execute(selfobj)

            finally:
                App.ActiveDocument.commitTransaction()
    except Exception as err:
        printError_msg(err.message, title=m_macro)


if __name__ == '__main__':
    run()
