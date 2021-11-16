# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
***************************************************************************
Create Point(s) at Center location of each selected Line/Edge(s) .

Cut each selected Line/Edge(s) in 2 (n) Parts and
create a (n-1) Point(s) along selected Line/Edge(s).

Number of Parts : n (2 by default)
The number (n) indicates in how many Parts each selected parent Line/Edge(s)
will be cut in.
Limits : (Min: 2, Max: 100).

Point's location:
If check box checked then points will be created at each ends of Parts.
Even at extrema!
Ie : if Number of Parts is 3 then 5 points will be created!

Part's end number
The number indicates at which part's end the point will be located.
- If the Number of parts is 2 and Point at part's end 1,
this means that the point will be located in the middle of the Line.
1/2 means middle of the segment !
- If the Number of parts is 2 and Point at part's end 2,
this means that the point will be located in the end of the Line.
 Limits : [-1000:1000]. Negative value are allowed.

 check box and Part's end number are exclusive!

How to
- Select one or several Line/Edge(s)
 (you can also select 2 points in place of one Line/Edge) and/or
- Select one Plane/Face to process all (4) Edges and/or
- Select one Object to process all Edges at once
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

__title__ = "Macro_CenterLinePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro CenterLinePoint.
Creates a parametric CenterLinePoint from an Edge
'''
###############
M_DEBUG = False
###############
if not sys.path.__contains__(str(PATH_WF_UTILS)):
    sys.path.append(str(PATH_WF_UTILS))
    sys.path.append(str(PATH_WF_UI))

try:
    from WF_selection import getSel
    from WF_print import printError_msg, print_msg, printError_msgWithTimer
    from WF_directory import createFolders, addObjectToGrp, createSubGroup
    from WF_geometry import isEqualVectors, alongTwoPointsPoint, alongLinePoint, propertiesPoint
    from WF_command import Command
except ImportError:
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME = "WF_centerLinePoint.svg"
M_DIALOG = "WF_UI_centerLinePoint.ui"
M_DIALOG_TITLE = "Define number of parts and location(s)."
M_EXCEPTION_MSG = """
Unable to create Center Line Point(s) :
- Select one or several Line/Edge(s) and/or
- Select one Plane/Face to process all (4) Edges at once and/or
- Select one Object to process all Edges at once;

You can also select 2 points (in place of an Edge) !

and go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG = " : Mid Line Point(s) created !"
M_MENU_TEXT = "Point(s) = center(Line)"
M_ACCEL = ""
M_TOOL_TIP = """<b>Create Point(s)</b> at Center location of each selected Line(s).<br>
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
M_MACRO = "Macro CenterLinePoint"
M_LOCATION = "Single"
M_LOCATIONS = ["Single", "All"]
M_NUMBERLINEPART = 2
M_INDEXPART = 1
###############


def setLocation(location):
    """ Set location of the point.

    Parameters
    -------
    *location* : (String, Mandatory)
            either "Single" or "All"
            "either" for creation of one point only.
            "all" for creation all points at end of all parts.
    """
    global M_LOCATION
    if location in M_LOCATIONS:
        M_LOCATION = location
    else:
        raise Exception(
            "Not valid 'location' option : must be either 'Single' or 'All'")


def getLocation():
    """ Get location of the point.

    Return
    -------
    either "Single" or "All"

    """
    return M_LOCATION


def setNumberLinePart(number_line_part):
    """ Set number of parts to consider.

    Cut each selected Line(s) in 2 (n) parts
    The number (n) indicates how many parts to consider.
    Parameters
    -------
    *number_line_part* : (Positive Integer, Mandatory)
            must be greater than 1
    """
    global M_NUMBERLINEPART
    if int(number_line_part) > 1:
        M_NUMBERLINEPART = int(number_line_part)


def getNumberLinePart():
    """ Get number of parts.

    Return
    -------
    A positive Integer greater than 1.
    """
    return M_NUMBERLINEPART


def setIndexPart(index_part):
    """ Set index of the point along the parts.

    Parameters
    -------
    *index_part* : (Integer, Mandatory)
            index where put the point
            if location == "Single"
    """
    global M_INDEXPART
    M_INDEXPART = int(index_part)


def getIndexPart():
    """ Get index of the point along the parts.

    Return
    -------
    An integer.
    """
    return M_INDEXPART


class CenterLinePointPanel:
    """ The CenterLinePointPanel (GUI).
    """

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)

        self.form.UI_CenterLinePoint_spin_numberLinePart.setValue(
            M_NUMBERLINEPART)
        self.form.UI_CenterLinePoint_spin_indexPart.setValue(M_INDEXPART)
        self.form.UI_CenterLinePoint_checkBox.setCheckState(
            QtCore.Qt.Unchecked)
        if M_LOCATION == "All":
            self.form.UI_CenterLinePoint_checkBox.setCheckState(
                QtCore.Qt.Checked)

    def accept(self):
        """ Run when click on OK button.
        """
        global M_LOCATION
        global M_NUMBERLINEPART
        global M_INDEXPART

        m_select = self.form.UI_CenterLinePoint_checkBox.isChecked()
        if m_select:
            M_LOCATION = "All"
        else:
            M_LOCATION = "Single"
        M_NUMBERLINEPART = self.form.UI_CenterLinePoint_spin_numberLinePart.value()
        M_INDEXPART = self.form.UI_CenterLinePoint_spin_indexPart.value()

        if WF.verbose():
            print_msg("M_NUMBERLINEPART = " + str(M_NUMBERLINEPART))
            print_msg("M_INDEXPART = " + str(M_INDEXPART))
            print_msg("M_LOCATION = " + str(M_LOCATION))

        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if Gui.Selection.getSelectionEx(m_act_doc.Name):
                center_line_point_command()
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


def makeCenterLinePointFeature(group):
    """ Makes a CenterLinePoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "CenterLinePoint_P"
    m_part = "Part::FeaturePython"

    if group is None:
        return None
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        CenterLinePoint(m_obj)
        ViewProviderCenterLinePoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj


class CenterLinePoint(WF_Point):
    """ The CenterLinePoint feature object.
    """

    def __init__(self, selfobj):
        if M_DEBUG:
            print("running CenterLinePoint.__init__ !")

        self.name = "CenterLinePoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our feature object.
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
        """ Doing a old recomputation.
        """
        if M_DEBUG:
            print("Recompute Python CenterLinePoint feature (old manner)\n")

        if 'Edge' not in selfobj.PropertiesList:
            return
        if 'IndexPart' not in selfobj.PropertiesList:
            return
        if 'NumberLinePart' not in selfobj.PropertiesList:
            return

#         n = eval(selfobj.Edge[1][0].lstrip('Edge'))
        m_int = re.sub('[^0-9]', '', selfobj.Edge[1][0])
        n = int(m_int)
        if WF.verbose():
            print_msg("n = " + str(n))

        try:
            vector_point = alongLinePoint(selfobj.Edge[0].Shape.Edges[n - 1],
                                          selfobj.IndexPart,
                                          selfobj.NumberLinePart)

            point = Part.Point(vector_point)
            selfobj.Shape = point.toShape()
            propertiesPoint(selfobj.Label)
            selfobj.X = float(vector_point.x)
            selfobj.Y = float(vector_point.y)
            selfobj.Z = float(vector_point.z)
        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

    # this method is mandatory

    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        m_properties_list = ['Edge',
                             'Point1',
                             'Point2',
                             'IndexPart',
                             'NumberLinePart'
                             ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        if M_DEBUG:
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

        try:
            vector_point = None
            if selfobj.Point1 is not None and selfobj.Point2 is not None:
                # n1 = eval(selfobj.Point1[1][0].lstrip('Vertex'))
                # n2 = eval(selfobj.Point2[1][0].lstrip('Vertex'))
                m_n1 = re.sub('[^0-9]', '', selfobj.Point1[1][0])
                m_n2 = re.sub('[^0-9]', '', selfobj.Point2[1][0])
                m_n1 = int(m_n1)
                m_n2 = int(m_n2)
                if M_DEBUG:
                    print_msg(str(selfobj.Point1))
                    print_msg(str(selfobj.Point2))
                    print_msg("m_n1 = " + str(m_n1))
                    print_msg("m_n2 = " + str(m_n2))

                point1 = selfobj.Point1[0].Shape.Vertexes[m_n1 - 1].Point
                point2 = selfobj.Point2[0].Shape.Vertexes[m_n2 - 1].Point

                vector_point = alongTwoPointsPoint(point1,
                                                   point2,
                                                   selfobj.IndexPart,
                                                   selfobj.NumberLinePart)
            elif selfobj.Edge is not None:
                m_n = re.sub('[^0-9]', '', selfobj.Edge[1][0])
                m_n = int(m_n)
                if M_DEBUG:
                    print_msg(str(selfobj.Edge))
                    print_msg("m_n = " + str(m_n))

                if not selfobj.Edge[0].Shape.Edges:
                    return

                vector_point = alongLinePoint(selfobj.Edge[0].Shape.Edges[m_n - 1],
                                              selfobj.IndexPart,
                                              selfobj.NumberLinePart)
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
        return os.path.join(PATH_WF_ICONS, self.icon)

    def setIcon(self, icon=M_ICON_NAME):
        self.icon = icon


def buildFromEdge(macro, group, edge, number_line_part, index_part):
    """ Build a CenterLinePoint feature object using an edge.
    """
    if WF.verbose():
        print_msg("edge = " + str(edge))
    App.ActiveDocument.openTransaction(macro)
    selfobj = makeCenterLinePointFeature(group)
    selfobj.Edge = edge
    selfobj.Point1 = None
    selfobj.Point2 = None
    selfobj.NumberLinePart = number_line_part
    selfobj.IndexPart = index_part
    selfobj.Proxy.execute(selfobj)

    WF.touch(selfobj)


def buildFromPoints(macro, group, vertexes, number_line_part, index_part):
    """ Build a CenterLinePoint feature object using two points.
    """
    vertex1 = vertexes[0]
    vertex2 = vertexes[1]
    if WF.verbose():
        print_msg("vertex1 = " + str(vertex1))
        print_msg("vertex2 = " + str(vertex2))
    App.ActiveDocument.openTransaction(macro)
    selfobj = makeCenterLinePointFeature(group)
    selfobj.Edge = None
    selfobj.Point1 = vertex1
    selfobj.Point2 = vertex2
    selfobj.NumberLinePart = number_line_part
    selfobj.IndexPart = index_part
    selfobj.Proxy.execute(selfobj)
    WF.touch(selfobj)


def center_line_point_command():
    """ This command use the selected object(s) to try to build a
    CenterLinePoint feature object.
    """
    m_sel, m_act_doc = getSel(WF.verbose())

    edges_from = ["Segments", "Curves", "Planes", "Shells", "Objects"]
    points_from = ["Points"]
    try:
        number_of_edges, edge_list = m_sel.get_segmentsWithNames(
            get_from=edges_from)
        # number_of_edges, edge_list = m_sel.get_segmentsWithIndex(getfrom=edges_from)

        if number_of_edges == 0:
            # Try to get Edges from points
            number_of_vertexes, vertex_list = m_sel.get_pointsWithNames(
                get_from=points_from)

        if number_of_edges == 0 and number_of_vertexes < 2:
            raise Exception(M_EXCEPTION_MSG)

        try:
            if WF.verbose():
                print_msg("Location = " + str(M_LOCATION))

            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set000"
            m_group = createFolders(str(m_main_dir))

            # From Edges
            if number_of_edges != 0:
                # Create a sub group if needed
                if number_of_edges > 1 or M_LOCATION != "Single":
                    m_group = createSubGroup(m_act_doc, m_main_dir, m_sub_dir)

                for i in range(number_of_edges):
                    m_edge = edge_list[i]

                    # Check if first point and last point of edge is not the
                    # same
                    vector_a = m_edge[0].Shape.Edges[0].Vertexes[0].Point
                    vector_b = m_edge[0].Shape.Edges[0].Vertexes[-1].Point
                    if isEqualVectors(vector_a, vector_b):
                        continue

                    if M_LOCATION == "Single":
                        buildFromEdge(M_MACRO,
                                      m_group,
                                      m_edge, M_NUMBERLINEPART, M_INDEXPART)
                    else:
                        for m_i_part in range(M_NUMBERLINEPART + 1):
                            buildFromEdge(M_MACRO,
                                          m_group,
                                          m_edge, M_NUMBERLINEPART, m_i_part)

            # From Vertexes
            else:
                if number_of_vertexes > 2:
                    m_group = createSubGroup(m_act_doc, m_main_dir, m_sub_dir)

                # Even number of vertexes
                if number_of_vertexes % 2 == 0:
                    if WF.verbose():
                        print_msg("Even number of points")

                    if number_of_vertexes == 2:
                        vertex1 = vertex_list[0]
                        vertex2 = vertex_list[1]

    #                     point1 = vertex1[0].Shape.Vertexes[0].Point
    #                     point2 = vertex2[0].Shape.Vertexes[0].Point
    #                     if isEqualVectors(point1, point2):
    #                         return

                        if M_LOCATION == "Single":
                            buildFromPoints(M_MACRO,
                                            m_group,
                                            (vertex1, vertex2),
                                            M_NUMBERLINEPART, M_INDEXPART)
                        else:
                            for m_i_part in range(M_NUMBERLINEPART + 1):
                                buildFromPoints(M_MACRO,
                                                m_group,
                                                (vertex1, vertex2),
                                                M_NUMBERLINEPART, m_i_part)
                    else:
                        for i in range(0, number_of_vertexes - 2, 2):
                            vertex1 = vertex_list[i]
                            vertex2 = vertex_list[i + 1]

    #                         point1 = vertex1[0].Shape.Vertexes[0].Point
    #                         point2 = vertex2[0].Shape.Vertexes[0].Point
    #                         if isEqualVectors(point1, point2):
    #                             continue

                            if M_LOCATION == "Single":
                                buildFromPoints(M_MACRO,
                                                m_group,
                                                (vertex1, vertex2),
                                                M_NUMBERLINEPART, M_INDEXPART)
                            else:
                                for m_i_part in range(M_NUMBERLINEPART + 1):
                                    buildFromPoints(M_MACRO,
                                                    m_group,
                                                    (vertex1, vertex2),
                                                    M_NUMBERLINEPART, m_i_part)
                # Odd number of vertexes
                else:
                    if WF.verbose():
                        print_msg("Odd number of points")
                    for i in range(number_of_vertexes - 1):
                        vertex1 = vertex_list[i]
                        vertex2 = vertex_list[i + 1]

                        if M_LOCATION == "Single":
                            buildFromPoints(M_MACRO,
                                            m_group,
                                            (vertex1, vertex2),
                                            M_NUMBERLINEPART, M_INDEXPART)
                        else:
                            for m_i_part in range(M_NUMBERLINEPART + 1):
                                buildFromPoints(M_MACRO,
                                                m_group,
                                                (vertex1, vertex2),
                                                M_NUMBERLINEPART, m_i_part)

        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

    except Exception as err:
        printError_msgWithTimer(err.args[0], title=M_MACRO)

    App.ActiveDocument.commitTransaction()
    App.activeDocument().recompute()


if App.GuiUp:
    Gui.addCommand("CenterLinePoint", Command(M_ICON_NAME,
                                              M_MENU_TEXT,
                                              M_ACCEL,
                                              M_TOOL_TIP,
                                              CenterLinePointPanel,
                                              center_line_point_command))


if __name__ == '__main__':
    center_line_point_command()
