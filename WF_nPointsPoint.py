# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
***************************************************************************
Create a Point at MEAN location of all selected  Points.

How to
- Select several Points and/or
- Select several Line/Edge(s) to process 2 ends points and/or
- Select one or several Plane/Face(s) to process all Points at once and/or
- Select one or several Object(s) to process all Points at once;
- Then Click on the icon
"""
import sys
import os.path
import re
import FreeCAD as App
import Part
from PySide import QtGui, QtCore
from WF_config import PATH_WF_ICONS, PATH_WF_UTILS, PATH_WF_UI
import WF
from WF_Objects_base import WF_Point

if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro_NPointsPoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro NPointsPoint.
Creates a parametric NPointsPoint from a list of Points
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
    from WF_geometry import meanVectorsPoint, propertiesPoint
    from WF_utils import linkSubList_convertToOldStyle
    from WF_command import Command
except ImportError:
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME = "WF_nPointsPoint.svg"
M_DIALOG = "WF_UI_nPointsPoint.ui"
M_DIALOG_TITLE = ""
M_EXCEPTION_MSG = """
Unable to create a Mean Point :
- Select several Points(s) and/or
- Select several Line/Edge(s) to process 2 ends points and/or
- Select one or several Plane/Face(s) to process all Points at once and/or
- Select one or several Object(s) to process all Points at once;

and go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG = " : N Points Point created !"
M_MENU_TEXT = "Point = center(Points)"
M_ACCEL = ""
M_TOOL_TIP = """<b>Create a Point</b> at MEAN location of all selected points.<br>

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
M_MACRO = "Macro NPointsPoint"
###############


class NPointsPointPanel:
    """ The NPointsLinePanel (GUI).
    """

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)

    def accept(self):
        """ Run when click on OK button.
        """
        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if Gui.Selection.getSelectionEx(m_act_doc.Name):
                n_points_point_comand()
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


def makeNPointsPointFeature(group):
    """ Makes a NPointsPoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "NPointsPoint_P"
    m_part = "Part::FeaturePython"

    if group is None:
        return None
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        m_inst = NPointsPoint(m_obj)
        ViewProviderNPointsPoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj, m_inst


class NPointsPoint(WF_Point):
    """ The NPointsPoint feature object.
    """

    def __init__(self, selfobj):
        if M_DEBUG:
            print("running NPointsPoint.__init__ !")

        self.name = "NPointsPoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our feature object.
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

    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        m_properties_list = ['Points',
                             ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        if M_DEBUG:
            print("running NPointsPoint.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        try:
            vector_point = None
            if selfobj.Points is not None:
                m_points = []
                for p in linkSubList_convertToOldStyle(selfobj.Points):
                    # n = eval(p[1].lstrip('Vertex'))
                    m_n = re.sub('[^0-9]', '', p[1])
                    m_n = int(m_n)
                    if M_DEBUG:
                        print("p " + str(p))
                        print_msg("m_n = " + str(m_n))

                    m_points.append(p[0].Shape.Vertexes[m_n - 1].Point)

            vector_point = meanVectorsPoint(m_points)

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
            print("running NPointsPoint.onChanged !")
            print("Change property : " + str(prop))

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
        """ Add pointlinks to this TwoPointsLine object
        """
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


def buildFromPoints(macro, group, vertexes):
    """ Build a NPointsPoint feature object using a list of points.
    """
    if WF.verbose():
        print_msg("vertexes = " + str(vertexes))
    App.ActiveDocument.openTransaction(macro)
    selfobj, m_inst = makeNPointsPointFeature(group)
    m_inst.addSubobjects(selfobj, vertexes)
    selfobj.Proxy.execute(selfobj)
    WF.touch(selfobj)


def n_points_point_comand():
    m_sel, _ = getSel(WF.verbose())

    points_from = ["Points", "Curves", "Planes", "Shells", "Objects"]
    try:
        number_of_vertexes, vertex_list = m_sel.get_pointsWithNames(
            get_from=points_from)

        if number_of_vertexes < 2:
            raise Exception(M_EXCEPTION_MSG)

        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set001"
            m_group = createFolders(str(m_main_dir))

            points = []
            # Case of only 2 points
            if number_of_vertexes == 2:
                if WF.verbose():
                    print_msg("Process only 2 points")
                vertex1 = vertex_list[0]
                vertex2 = vertex_list[1]
                points.append(vertex1)
                points.append(vertex2)

                buildFromPoints(M_MACRO, m_group, points)

            # Case of more than 2 points
            else:
                if WF.verbose():
                    print_msg("Process more than 2 points")
                for i in range(number_of_vertexes):
                    vertex1 = vertex_list[i]
                    points.append(vertex1)

                buildFromPoints(M_MACRO, m_group, points)

        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

    except Exception as err:
        printError_msgWithTimer(err.args[0], title=M_MACRO)

    App.ActiveDocument.commitTransaction()
    App.activeDocument().recompute()


if App.GuiUp:
    Gui.addCommand("NPointsPoint", Command(M_ICON_NAME,
                                           M_MENU_TEXT,
                                           M_ACCEL,
                                           M_TOOL_TIP,
                                           NPointsPointPanel,
                                           n_points_point_comand))

if __name__ == '__main__':
    n_points_point_comand()
