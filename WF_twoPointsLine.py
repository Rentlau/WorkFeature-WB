# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
***************************************************************************
Create Line(s) from at least two selected Points.

A line will be created in between the selected Points.

Extension :  (0 by default)
Distance for the extensions on extrema.
Positive values will enlarge the Axis.
Negative values will start to shrink it (then reverse when middle reached).

Process consecutive Points as Pair:
If check box NOT checked:
    If 4 consecutive Points are selected then 3 Lines will be created.
If check box checked:
    If 4 consecutive Points are selected then only 2 Lines will be created.

NB
You can also select in general Preference menu : Close polyline option

How to
- Select two or more Points
- Then Click on the icon
"""
import sys
import re
import FreeCAD as App
import Part
from PySide import QtCore
from WF_config import PATH_WF_ICONS, PATH_WF_UTILS, PATH_WF_UI
import WF
from WF_Objects_base import WF_Line

if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro TwoPointsLine"
__author__ = "Rentlau_64"
__brief__ = '''
Macro TwoPointsLine.
Creates a parametric TwoPointsLine from two points
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
    from WF_geometry import isEqualVectors, coordVectorPoint, propertiesLine
    from WF_command import Command
except ImportError:
    print("ERROR: cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME = "WF_twoPointsLine.svg"
M_DIALOG = "WF_UI_twoPointsLine.ui"
M_DIALOG_TITLE = "Define extension."
M_EXCEPTION_MSG = """
Unable to create Line(s) from 2 Points :
- Select two or several Points !

Go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG = " : Line(s) from 2 Points created !"
M_MENU_TEXT = "Line(s) = (Point, Point)"
M_ACCEL = ""
M_TOOL_TIP = """<b>Create Line(s)</b> from at least two selected Points.<br>
<br>
- Select two or more Points<br>
- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
###############
M_MACRO = "Macro TwoPointsLine"
M_LINE_EXT = 0.0
M_BYPAIR = False
###############


def setLineExtension(ext):
    """ Set Extension of the line outside the two points.

    Parameters
    -------
    *ext*       : (Float, Mandatory)
                Distance for the extensions on extrema.
                Positive values will enlarge the Axis.
                Negative values will start to shrink it (then reverse when middle reached).
    """
    global M_LINE_EXT
    M_LINE_EXT = float(ext)


def getExtension():
    """ Get Extension of the line outside the two points.

    Return
    -------
    A Float.
    """
    return M_LINE_EXT


def setProcessByPair(flag):
    """ Set if Process consecutive Points as Pair.

    Parameters
    -------
    *flag*      : (Boolean, mandatory)
                If False:
                If 4 consecutive Points are selected then 3 Lines will be created.
                If True:
                If 4 consecutive Points are selected then only 2 Lines will be created.
    """
    global M_BYPAIR
    M_BYPAIR = flag


def isProcessByPair():
    """ Get if Process consecutive Points as Pair.

    Return
    -------
    A Boolean
    """
    return M_BYPAIR


class TwoPointsLinePanel:
    """ The TwoPointsLinePanel (GUI).
    """

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)
        self.form.UI_Line_extension.setText(str(M_LINE_EXT))
        self.form.UI_Point_by_Pair_checkBox.setCheckState(
            QtCore.Qt.Unchecked)
        if M_BYPAIR:
            self.form.UI_Point_by_Pair_checkBox.setCheckState(
                QtCore.Qt.Checked)

    def accept(self):
        """ Run when click on OK button.
        """
        global M_LINE_EXT
        global M_BYPAIR

        M_LINE_EXT = float(self.form.UI_Line_extension.text())
        M_BYPAIR = self.form.UI_Point_by_Pair_checkBox.isChecked()

        if WF.verbose():
            print_msg("M_LINE_EXT = " + str(M_LINE_EXT))
            print_msg("M_BYPAIR = " + str(M_BYPAIR))

        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if Gui.Selection.getSelectionEx(m_act_doc.Name):
                two_points_line_command()
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


def makeTwoPointsLineFeatureFromList(selectionset, group):
    """ Makes a TwoPointsLine parametric feature object from a selection set.
    into the given Group
    Returns the new object.
    """
    m_name = "TwoPointsLine_P"
    m_part = "Part::FeaturePython"

    if not isinstance(selectionset, list):
        selectionset = [selectionset]
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        TwoPointsLine(m_obj)
        ViewProviderTwoPointsLine(m_obj.ViewObject)
        m_obj.Proxy.addSubobjects(m_obj, selectionset)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj


def makeTwoPointsLineFeature(group):
    """ Makes a TwoPointsLine parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "TwoPointsLine_P"
    m_part = "Part::FeaturePython"

    if group is None:
        return None
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        TwoPointsLine(m_obj)
        ViewProviderTwoPointsLine(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj


class TwoPointsLine(WF_Line):
    """ The TwoPointsLine feature object. """
    # this method is mandatory

    def __init__(self, selfobj):
        if M_DEBUG:
            print("running TwoPointsLine.__init__ !")

        self.name = "TwoPointsLine"
        WF_Line.__init__(self, selfobj, self.name)
        # Add some custom properties to our TwoPointsLine feature object.
        selfobj.addProperty("App::PropertyLinkSub",
                            "Point1",
                            self.name,
                            "Start point")
        selfobj.addProperty("App::PropertyLinkSub",
                            "Point2",
                            self.name,
                            "End point")

        m_tooltip = """This is the amount of extension
on each part of the line.
Negative number allowed.
"""
        selfobj.addProperty("App::PropertyFloat",
                            "Extension",
                            self.name,
                            m_tooltip).Extension = M_LINE_EXT

        selfobj.setEditorMode("Point1", 1)
        selfobj.setEditorMode("Point2", 1)

        selfobj.Proxy = self

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        m_properties_list = ['Point1',
                             'Point2',
                             'Extension'
                             ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        if M_DEBUG:
            print("running TwoPointsLine.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        try:
            line = None
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

                if isEqualVectors(point1, point2):
                    m_msg = """Unable to create Line(s) from 2 Points :
                    Given Points are equals !
                    """
                    printError_msg(m_msg, title=M_MACRO)

                axis_dir = point2 - point1
                point_e1 = point2
                point_e2 = point1
                M_LINE_EXT = selfobj.Extension
                if M_LINE_EXT != 0.0:
                    point_e1 += axis_dir.normalize().multiply(M_LINE_EXT)
                    if M_LINE_EXT >= 0.0:
                        point_e2 -= axis_dir.normalize().multiply(M_LINE_EXT)
                    else:
                        point_e2 += axis_dir.normalize().multiply(M_LINE_EXT)

                line = Part.makeLine(coordVectorPoint(point_e2),
                                     coordVectorPoint(point_e1))

            if line is not None:
                selfobj.Shape = line
                propertiesLine(selfobj.Label, self.color)
                selfobj.Point1_X = float(point1.x)
                selfobj.Point1_Y = float(point1.y)
                selfobj.Point1_Z = float(point1.z)
                selfobj.Point2_X = float(point2.x)
                selfobj.Point2_Y = float(point2.y)
                selfobj.Point2_Z = float(point2.z)
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
            print("running TwoPointsLine.onChanged !")
            print("Change property : " + str(prop))

        WF_Line.onChanged(self, selfobj, prop)

        if prop == "Parametric":
            if 'Parametric' in selfobj.PropertiesList:
                if selfobj.Parametric == 'Not':
                    selfobj.setEditorMode("Extension", 1)
                else:
                    selfobj.setEditorMode("Extension", 0)
            propertiesLine(selfobj.Label, self.color)

        if prop == "Extension":
            selfobj.Proxy.execute(selfobj)

        if prop == "Point1":
            selfobj.Proxy.execute(selfobj)
        if prop == "Point2":
            selfobj.Proxy.execute(selfobj)

    def addSubobjects(self, selfobj, pointlinks):
        "adds pointlinks to this TwoPointsLine object"
        objs = selfobj.Points
        for o in pointlinks:
            if isinstance(o, tuple) or isinstance(o, list):
                if o[0].Name != selfobj.Name:
                    objs.append(tuple(o))
            else:
                for el in o.SubElementNames:
                    if "Point" in el:
                        if o.Object.Name != selfobj.Name:
                            objs.append((o.Object, el))
        selfobj.Points = objs
        selfobj.Proxy.execute(selfobj)
        # self.execute(selfobj)


class ViewProviderTwoPointsLine:
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


def buildFromOnePointAndOneObject(vertex1, object1, group):
    """ Build a TwoPointsLine feature object using one point and one object.
    """
    if WF.verbose():
        App.Console.PrintMessage(
            "running twoPL.buildFromOnePointAndOneObject !")
    try:
        if WF.verbose():
            print_msg("vertex1 = " + str(vertex1))
            print_msg("object1 = " + str(object1))

        App.ActiveDocument.openTransaction("Macro TwoPointsLine")
        selfobj = makeTwoPointsLineFeature(group)
        selfobj.Point1 = vertex1
        selfobj.Point2 = [object1, "Vertex1"]
        selfobj.Extension = 0.0
        selfobj.Proxy.execute(selfobj)
        try:
            Gui.ActiveDocument.getObject(selfobj.Label).DrawStyle = "Dotted"
        except Exception as err:
            printError_msg(err.args[0], title="Macro TwoPointsLine")
            print_msg("Not able to set DrawStyle !")
    except Exception as err:
        printError_msg(err.args[0], title="Macro TwoPointsLine")


def buildFromPoints(
        macro, group, vertex1, vertex2, line_ext):
    """ Build a TwoPointsLine feature object using two points.
    """

    if WF.verbose():
        print_msg("vertex1 = " + str(vertex1))
        print_msg("vertex2 = " + str(vertex2))

    App.ActiveDocument.openTransaction(macro)
    selfobj = makeTwoPointsLineFeature(group)
    selfobj.Point1 = vertex1
    selfobj.Point2 = vertex2
    selfobj.Extension = line_ext
    selfobj.Proxy.execute(selfobj)
    WF.touch(selfobj)


def two_points_line_command():
    """ This command use the selected object(s) to try to build a
    TwoPointsLine feature object.
    """
    m_sel, m_act_doc = getSel(WF.verbose())

    points_from = ["Points", "Curves", "Objects"]
    try:
        number_of_vertexes, vertex_list = m_sel.get_pointsWithNames(
            get_from=points_from)

        if number_of_vertexes < 2:
            raise Exception(M_EXCEPTION_MSG)

        try:
            m_main_dir = "WorkAxis_P"
            m_sub_dir = "Set000"
            m_group = createFolders(str(m_main_dir))

            # Create a sub group if needed
            if number_of_vertexes > 2:
                m_group = createSubGroup(m_act_doc, m_main_dir, m_sub_dir)

            # Case of only 2 points
            if number_of_vertexes == 2:
                if WF.verbose():
                    print_msg("Process only 2 points")
                vertex1 = vertex_list[0]
                vertex2 = vertex_list[1]

                buildFromPoints(M_MACRO,
                                m_group,
                                vertex1, vertex2, M_LINE_EXT)

            # Case of more than 2 points
            else:
                if M_BYPAIR:
                    if WF.verbose():
                        print_msg("Process points by pair")
                    # even
                    if (number_of_vertexes % 2 == 0):
                        if WF.verbose():
                            print_msg("Even number of points")
                        for i in range(0, number_of_vertexes - 1, 2):
                            vertex1 = vertex_list[i]
                            vertex2 = vertex_list[i + 1]

                            buildFromPoints(M_MACRO,
                                            m_group,
                                            vertex1, vertex2, M_LINE_EXT)
                    # odd
                    else:
                        if WF.verbose():
                            print_msg("Odd number of points")
                        for i in range(0, number_of_vertexes - 2, 2):
                            vertex1 = vertex_list[i]
                            vertex2 = vertex_list[i + 1]

                            buildFromPoints(M_MACRO,
                                            m_group,
                                            vertex1, vertex2, M_LINE_EXT)

                        if WF.closePolyline():
                            vertex1 = vertex_list[-1]
                            vertex2 = vertex_list[0]

                            buildFromPoints(M_MACRO,
                                            m_group,
                                            vertex1, vertex2, M_LINE_EXT)
                else:
                    if WF.verbose():
                        print_msg("Process points as list")
                    for i in range(number_of_vertexes - 1):
                        vertex1 = vertex_list[i]
                        vertex2 = vertex_list[i + 1]

                        buildFromPoints(M_MACRO,
                                        m_group,
                                        vertex1, vertex2, M_LINE_EXT)

                    if WF.closePolyline():
                        vertex1 = vertex_list[-1]
                        vertex2 = vertex_list[0]

                        buildFromPoints(M_MACRO,
                                        m_group,
                                        vertex1, vertex2, M_LINE_EXT)

        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

    except Exception as err:
        printError_msgWithTimer(err.args[0], title=M_MACRO)

    App.ActiveDocument.commitTransaction()
    App.activeDocument().recompute()


if App.GuiUp:
    Gui.addCommand("TwoPointsLine", Command(M_ICON_NAME,
                                            M_MENU_TEXT,
                                            M_ACCEL,
                                            M_TOOL_TIP,
                                            TwoPointsLinePanel,
                                            two_points_line_command))

if __name__ == '__main__':
    two_points_line_command()
