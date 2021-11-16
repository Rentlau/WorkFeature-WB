# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
*   https://github.com/Rentlau/WorkFeature-WB                             *
***************************************************************************
Create Point(s) along Line(s) at a defined distance of Reference
Point(s)/Line(s) intersection.

The reference Point is the projection of the selected Point(s) onto the
first selected Line.
Or the reference Point is the projection of Line(s) two ends onto the first
selected Line.

Define the Distance along the line from the Reference Point(s)/Line( )
intersection.
Negative values will revert the direction.
A null distance gives you the projection of point(s) onto the first
selected Line.

How to
The First selected Line/Edge(s) is  where to attach new Points.
and Second define one or several Reference Point(s).
3 cases:
Selection of : One Edge and One or several Point(s).
Selection of : One Edge and One or several Edge(s).
Selection of : Several couple (Edge,Point) with same number of Edges and
Points
- Then Click on the icon
"""

import sys
import os.path
import re
import FreeCAD as App
import Part
from PySide import QtCore
from WF_config import PATH_WF_ICONS, PATH_WF_UTILS, PATH_WF_UI
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
M_DEBUG = True
###############
if not sys.path.__contains__(str(PATH_WF_UTILS)):
    sys.path.append(str(PATH_WF_UTILS))
    sys.path.append(str(PATH_WF_UI))

try:
    from WF_selection import getSel
    from WF_print import printError_msg, print_msg, printError_msgWithTimer
    from WF_directory import createFolders, addObjectToGrp, createSubGroup
    from WF_geometry import isEqualVectors, intersectPerpendicularLine, propertiesPoint
    from WF_utils import *
    from WF_command import Command
except ImportError:
    print("ERROR: cannot load WF modules !")
    sys.exit(1)


###############
M_ICON_NAME = "WF_alongLinePoint.svg"
M_DIALOG = "WF_UI_alongLinePoint.ui"
M_DIALOG_TITLE = "Define distance"
M_EXCEPTION_MSG = """
Unable to create Point along a Line :
The First selected Line/Edge(s) is  where to attach new Points.
and Second define one or several Reference Point(s).

3 cases:
Selection of : One Edge and One or several Point(s).
Selection of : One Edge and One or several Edge(s).
Selection of : Several Edges and Points with same number of Edges and Points

and go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG = " : Point along a Line created !"
M_MENU_TEXT = "Point(s) = along(Line, Point)"
M_ACCEL = ""
M_TOOL_TIP = """<b>Create Point(s)</b> along Line(s) at a defined<br>
 distance of Reference Point(s)/Line(s) intersection.<br>
The reference Point is the projection of the selected Point(s)<br>
 onto the first selected Line.<br>
Or the reference Point is the projection of Line(s) two ends<br>
 onto the first selected Line.<br>
<br>
Define the Distance along the line from the <br>
Reference Point(s)/Line(s) intersection.<br>
Negative values will revert the direction.<br>
A null distance gives you the projection of point(s)<br>
onto the first selected Line.<br>
<br>
The First selected Line/Edge(s) is  where to attach new Points.<br>
and Second define one or several Reference Point(s).<br>
<br>
<b>3 cases:</b><br>
Selection of : One Edge and One or several Point(s).<br>
Selection of : One Edge and One or several Edge(s).<br>
Selection of : Several Edges and Points with same number of Edges and Points<br>
- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
###############
M_MACRO = "Macro AlongLinePoint"
M_DISTANCELINEPOINT = 10.0
###############


def setDistanceLinePoint(distance):
    """ Set distance along the line.

    Parameters
    -------
    *distance* : (String, Mandatory)
                Define the Distance along the line from the
                Reference Point(s)/Line(s) intersection.
                Negative values will revert the direction.
                A null distance gives you the projection of point(s)
                onto the first selected Line.
    """
    global M_DISTANCELINEPOINT
    M_DISTANCELINEPOINT = float(distance)


def getDistanceLinePoint():
    """ Get distance along the line.

    Return
    -------
    float value

    """
    return M_DISTANCELINEPOINT


class AlongLinePointPanel:
    """ The AlongLinePointPanel (GUI).
    """

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)

        self.form.UI_Distance.setText(str(M_DISTANCELINEPOINT))

    def accept(self):
        """ Run when click on OK button.
        """
        global M_DISTANCELINEPOINT

        M_DISTANCELINEPOINT = float(self.form.UI_Distance.text())

        if WF.verbose():
            print_msg("M_DISTANCELINEPOINT = " + str(M_DISTANCELINEPOINT))

        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if Gui.Selection.getSelectionEx(m_act_doc.Name):
                along_line_point_command()
        return True

    def reject(self):
        """ Run when click on CANCEL button.
        """
        Gui.Control.closeDialog()
        return False

    def shouldShow(self):
        """ Must show when nothing selected.
        """
        return len(Gui.Selection.getSelectionEx(
            App.activeDocument().Name)) == 0


def makeAlongLinePointFeature(group):
    """ Makes a AlongLinePoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "AlongLinePoint_P"
    m_part = "Part::FeaturePython"

    if group is None:
        return None
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        AlongLinePoint(m_obj)
        ViewProviderAlongLinePoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj


class AlongLinePoint(WF_Point):
    """ The AlongLinePoint feature object.
    """

    def __init__(self, selfobj):
        if M_DEBUG:
            print("running AlongLinePoint.__init__ !")

        self.name = "AlongLinePoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our AlongLinePoint feature object.
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
Or the reference Point is the projection of Line(s) closest end
onto the first selected Line."""
        selfobj.addProperty("App::PropertyFloat",
                            "Distance",
                            self.name,
                            m_tooltip).Distance = M_DISTANCELINEPOINT

        selfobj.setEditorMode("AlongEdge", 1)
        selfobj.setEditorMode("Point", 1)
        selfobj.setEditorMode("Edge", 1)

        selfobj.Proxy = self

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        m_properties_list = ["Distance",
                             'AlongEdge',
                             'Edge',
                             'Point'
                             ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        if M_DEBUG:
            print("running AlongLinePoint.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        if selfobj.AlongEdge is None:
            return

        if selfobj.Edge is None and selfobj.Point is None:
            return

        try:
            vector_point = None
            m_distance = selfobj.Distance

            # m_n1 = eval(selfobj.AlongEdge[1][0].lstrip('Edge'))
            m_n1 = re.sub('[^0-9]', '', selfobj.AlongEdge[1][0])
            m_n1 = int(m_n1)

            if selfobj.Edge is not None:
                # m_n2 = eval(selfobj.Edge[1][0].lstrip('Edge'))
                m_n2 = re.sub('[^0-9]', '', selfobj.Edge[1][0])
                m_n2 = int(m_n2)
            else:
                if selfobj.Point != selfobj.AlongEdge:
                    # m_n3 = eval(selfobj.Point[1][0].lstrip('Vertex'))
                    m_n3 = re.sub('[^0-9]', '', selfobj.Point[1][0])
                else:
                    # m_n3 = eval(selfobj.Point[1][0].lstrip('Edge'))
                    m_n3 = re.sub('[^0-9]', '', selfobj.Point[1][0])
                m_n3 = int(m_n3)

            if M_DEBUG:
                print_msg("m_n1 = " + str(m_n1))
                if selfobj.Edge is not None:
                    print_msg("m_n2 = " + str(m_n2))
                else:
                    print_msg("m_n3 = " + str(m_n3))
                print_msg("m_distance = " + str(m_distance))

            m_alongedge = selfobj.AlongEdge[0].Shape.Edges[m_n1 - 1]
            if selfobj.Edge is not None:
                m_edge = selfobj.Edge[0].Shape.Edges[m_n2 - 1]
            else:
                m_point = selfobj.Point[0].Shape.Vertexes[m_n3 - 1].Point

            vector_a = m_alongedge.valueAt(0.0)
            vector_b = m_alongedge.valueAt(m_alongedge.Length)

            if isEqualVectors(vector_a, vector_b):
                return

            if selfobj.Edge is not None:
                m_dist = m_alongedge.distToShape(m_edge)
                vector_c = m_dist[1][0][0]
            else:
                vector_c = m_point

            # Calculate intersection Point
            vector_t, _, _ = intersectPerpendicularLine(vector_a,
                                                        vector_b,
                                                        vector_c,)
            if M_DEBUG:
                print_msg("m_alongedge = " + str(m_alongedge))
                if selfobj.Edge is not None:
                    print_msg("m_edge = " + str(m_edge))
                else:
                    print_msg("m_point = " + str(m_point))
                print_msg("vector_a = " + str(vector_a))
                print_msg("vector_b = " + str(vector_b))
                print_msg("vector_c = " + str(vector_c))
                print_msg("vector_t = " + str(vector_t))

            vector_translate = (vector_b - vector_a)
            if m_distance != 0.0:
                vector_translate = vector_translate.normalize() * m_distance
                vector_point = vector_t + vector_translate
            else:
                vector_point = vector_t

            if vector_point is not None:
                point = Part.Point(vector_point)
                selfobj.Shape = point.toShape()
                propertiesPoint(selfobj.Label, self.color)
                selfobj.X = float(vector_point.x)
                selfobj.Y = float(vector_point.y)
                selfobj.Z = float(vector_point.z)
                # To be compatible with previous version 2018
                if 'Parametric' in selfobj.PropertiesList:
                    self.created = True
        except AttributeError as err:
            print("AttributeError" + str(err))
        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

    def onChanged(self, selfobj, prop):
        """ Run when a proterty change.
        """
        if M_DEBUG:
            print("running CenterLinePoint.onChanged !")
            print("Change property : " + str(prop))

        WF_Point.onChanged(self, selfobj, prop)

        if prop == "Parametric":
            if 'Parametric' in selfobj.PropertiesList:
                if selfobj.Parametric == 'Not':
                    selfobj.setEditorMode("Distance", 1)
                else:
                    selfobj.setEditorMode("Distance", 0)
            propertiesPoint(selfobj.Label, self.color)

        if prop == "Distance":
            selfobj.Proxy.execute(selfobj)


class ViewProviderAlongLinePoint:
    global PATH_WF_ICONS
    icon = M_ICON_NAME

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
        return os.path.join(PATH_WF_ICONS + self.icon)

    def setIcon(self, icon=M_ICON_NAME):
        self.icon = icon


def buildFromTwoPoints(vertex1, vertex2, index, object1, group):
    if WF.verbose():
        App.Console.PrintMessage("running aLP.buildFromTwoPoints !")
    try:
        if M_DEBUG:
            print_msg("\nvertex1 = " + str(vertex1))
            print_msg("vertex2 = " + str(vertex2))

        vector_a = vertex1
        vector_b = vertex2
        m_distance = vector_b.sub(vector_a).Length / 2
        m_distance = index * (vector_b.sub(vector_a).Length / 1)
        if M_DEBUG:
            print_msg("vector_a = " + str(vector_a))
            print_msg("vector_b = " + str(vector_b))
            print_msg("m_distance = " + str(m_distance))

        vector_c = vector_a.add(
            vector_b.sub(vector_a).normalize().multiply(m_distance))
        if M_DEBUG:
            print_msg("vector_c = " + str(vector_c))

        L1 = Part.LineSegment(vector_b, vector_c)
        edge = Part.Edge(L1)

#         App.ActiveDocument.openTransaction("Macro AlongLinePoint")
#         selfobj = makeAlongLinePointFeature(group)
#         selfobj.AlongEdge = edge [object1, "Vertex1"]
#         selfobj.Point = vector_c
#         selfobj.Edge = None
#         selfobj.Distance = m_distance
#         selfobj.Proxy.execute(selfobj)
    except Exception as err:
        printError_msg(err.args[0], title="Macro AlongLinePoint")


def buildFromEdgeAndPoint(macro, group, edge, point, distance):
    """ Build a AlongLinePoint feature object using an edge.
    and a point.
    """
    if WF.verbose():
        print_msg("edge = " + str(edge))
        print_msg("point = " + str(point))

    App.ActiveDocument.openTransaction(macro)
    selfobj = makeAlongLinePointFeature(group)
    selfobj.AlongEdge = edge
    selfobj.Point = point
    selfobj.Edge = None
    selfobj.Distance = distance
    selfobj.Proxy.execute(selfobj)


def buildFromEdges(macro, group, edge, other_edge, distance):
    """ Build a AlongLinePoint feature object using an edge.
    and an other edge if any.
    """
    if WF.verbose():
        print_msg("edge = " + str(edge))
        print_msg("other_edge = " + str(other_edge))

    App.ActiveDocument.openTransaction(macro)
    selfobj = makeAlongLinePointFeature(group)
    selfobj.AlongEdge = edge
    selfobj.Point = None
    selfobj.Edge = other_edge
    selfobj.Distance = distance
    selfobj.Proxy.execute(selfobj)

    WF.touch(selfobj)


def along_line_point_command():
    """ This command use the selected object(s) to try to build a
    AlongLinePoint feature object.
    """
    m_sel, m_act_doc = getSel(WF.verbose())

    edges_from = ["Segments", "Curves"]
    points_from = ["Points"]
    try:
        if m_sel.numberOfEntities == 1:
            number_of_edges, edge_list = m_sel.get_segmentsWithNames(
                get_from=edges_from)
        else:
            number_of_edges, edge_list = m_sel.get_segmentsWithNames(
                get_from=edges_from)

        number_of_vertexes, vertex_list = m_sel.get_pointsWithNames(
            get_from=points_from)

        if number_of_edges == 0:
            raise Exception(M_EXCEPTION_MSG)
        else:
            if number_of_edges == 1 and number_of_vertexes == 0:
                raise Exception(M_EXCEPTION_MSG)

        m_main_dir = "WorkPoints_P"
        m_sub_dir = "Set000"
        m_group = createFolders(str(m_main_dir))

        m_distance = getDistanceLinePoint()

        # Selection of : One Edge and One or several Point(s)
        if number_of_edges == 1 and number_of_vertexes > 0:
            try:
                # Create a sub group if needed
                if number_of_vertexes > 1:
                    m_group = createSubGroup(m_act_doc, m_main_dir, m_sub_dir)

                edge = edge_list[0]
                for j in range(number_of_vertexes):
                    point = vertex_list[j]
                    buildFromEdgeAndPoint(M_MACRO,
                                          m_group,
                                          edge, point, m_distance)

            except Exception as err:
                printError_msg(err.args[0], title=M_MACRO)

        # Selection of : One Edge and One or several Edge(s)
        elif number_of_edges > 1 and number_of_vertexes == 0:
            try:
                # Create a sub group if needed
                if number_of_edges > 2:
                    m_group = createSubGroup(m_act_doc, m_main_dir, m_sub_dir)

                edge = edge_list[0]
                for other_edge in edge_list[1:]:
                    buildFromEdges(M_MACRO,
                                   m_group,
                                   edge, other_edge, m_distance)

            except Exception as err:
                printError_msg(err.args[0], title=M_MACRO)

        # Selection of : several Edges and Points with
        # same number of Edges and Points
        elif number_of_edges > 1 and number_of_vertexes == number_of_edges:
            try:
                # Create a sub group if needed
                m_group = createSubGroup(m_act_doc, m_main_dir, m_sub_dir)

                for edge, point in zip(edge_list, vertex_list):
                    buildFromEdgeAndPoint(M_MACRO,
                                          m_group,
                                          edge, point, m_distance)

            except Exception as err:
                printError_msg(err.args[0], title=M_MACRO)

        else:
            printError_msg("Bad selection !", title=M_MACRO)

    except Exception as err:
        printError_msgWithTimer(err.args[0], title=M_MACRO)

    App.ActiveDocument.commitTransaction()
    App.activeDocument().recompute()


if App.GuiUp:
    Gui.addCommand("AlongLinePoint", Command(M_ICON_NAME,
                                             M_MENU_TEXT,
                                             M_ACCEL,
                                             M_TOOL_TIP,
                                             AlongLinePointPanel,
                                             along_line_point_command))
if __name__ == '__main__':
    along_line_point_command()
