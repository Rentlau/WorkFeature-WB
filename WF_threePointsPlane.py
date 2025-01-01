# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
***************************************************************************
Create Plane from three selected Points.

Extension :  (100 by default)
Width and Length of the plane in current units.

- Select three Points only
- Then Click on the Button/Icon
"""
import sys
import os.path
import re
import FreeCAD as App
import Part
from PySide import QtCore
from WF_config import PATH_WF_ICONS, PATH_WF_UTILS, PATH_WF_UI
import WF
from WF_Objects_base import WF_Plane

if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro ThreePointsPlane"
__author__ = "Rentlau_64"
__brief__ = '''
Macro ThreePointsPlane.
Creates a parametric ThreePointsPlane from 3 points
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
    from WF_geometry import isEqualVectors, isColinearVectors, minMaxVectorsLimits, meanVectorsPoint, propertiesPlane
    from WF_command import Command
except ImportError:
    print("ERROR: cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME = "WF_threePointsPlane.svg"
M_DIALOG = "WF_UI_threePointsPlane.ui"
M_DIALOG_TITLE = "Define extension of the plane."
M_EXCEPTION_MSG = """
Unable to create Plane from 3 Points :
- Select three separated Points !

Go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG = " : Plane from 3 Points created !"
M_MENU_TEXT = "Plane = (3 Points)"
M_ACCEL = ""
M_TOOL_TIP = """<b>Create Plane</b> from three selected Points.<br>
<br>
Extension :  (100 by default)<br>
Width and Length of the plane in current units.<br>
<br>
<br>
- Select three Points only<br>
- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
###############
M_MACRO = "Macro ThreePointsPlane"
M_PLANE_EXT = 100.0
###############


def setPlaneExtension(ext):
    """ Set Extension of the plane.

    Parameters
    -------
    *ext*       : (Float, Mandatory)
                Distance for the extensions.
    """
    global M_PLANE_EXT
    M_PLANE_EXT = float(ext)


def getExtension():
    """ Get Extension of plane.

    Return
    -------
    A Float.
    """
    return M_PLANE_EXT


class ThreePointsPlanePanel:
    """ The ThreePointsPlanePanel (GUI).
    """

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)
        self.form.UI_Plane_extension.setText(str(M_PLANE_EXT))

    def accept(self):
        """ Run when click on OK button.
        """
        global M_PLANE_EXT
        M_PLANE_EXT = float(self.form.UI_Plane_extension.text())

        if WF.verbose():
            print_msg("M_PLANE_EXT = " + str(M_PLANE_EXT))

        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if Gui.Selection.getSelectionEx(m_act_doc.Name):
                three_points_plane_command()
        return True

    def reject(self):
        """ Run when click on CANCEL button.
        """
        Gui.Control.closeDialog()
        return False

    def shouldShow(self):
        """ Must show when nothing selected.
        """
        return (len(Gui.Selection.getSelectionEx(
            App.activeDocument().Name)) == 0)


def makeThreePointsPlaneFeature(group):
    """ Makes a ThreePointsPlane parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "ThreePointsPlane_P"
    m_part = "Part::FeaturePython"

    if group is None:
        return None
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        ThreePointsPlane(m_obj)
        ViewProviderThreePointsPlane(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj


class ThreePointsPlane(WF_Plane):
    """ The ThreePointsPlane feature object.
    """

    def __init__(self, selfobj):
        if M_DEBUG:
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

        m_tooltip = """Width and Length of the plane in current units."""
        selfobj.addProperty("App::PropertyFloat",
                            "Extension",
                            self.name,
                            m_tooltip).Extension = M_PLANE_EXT
        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden
        selfobj.setEditorMode("Point1", 1)
        selfobj.setEditorMode("Point2", 1)
        selfobj.setEditorMode("Point3", 1)

        selfobj.Proxy = self

    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        m_properties_list = ['Point1',
                             'Point2',
                             'Point3'
                             ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        if M_DEBUG:
            print("running ThreePointsPlane.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        try:
            plane = None
            if selfobj.Point1 is not None and selfobj.Point2 is not None and selfobj.Point3 is not None:
                # n1 = eval(selfobj.Point1[1][0].lstrip('Vertex'))
                # n2 = eval(selfobj.Point2[1][0].lstrip('Vertex'))
                # n3 = eval(selfobj.Point3[1][0].lstrip('Vertex'))
                m_n1 = re.sub('[^0-9]', '', selfobj.Point1[1][0])
                m_n2 = re.sub('[^0-9]', '', selfobj.Point2[1][0])
                m_n3 = re.sub('[^0-9]', '', selfobj.Point3[1][0])
                m_n1 = int(m_n1)
                m_n2 = int(m_n2)
                m_n3 = int(m_n3)
                if M_DEBUG:
                    print_msg(str(selfobj.Point1))
                    print_msg(str(selfobj.Point2))
                    print_msg(str(selfobj.Point3))
                    print_msg("m_n1 = " + str(m_n1))
                    print_msg("m_n2 = " + str(m_n2))
                    print_msg("m_n3 = " + str(m_n3))

                points = []
                point_a = selfobj.Point1[0].Shape.Vertexes[m_n1 - 1].Point
                point_b = selfobj.Point2[0].Shape.Vertexes[m_n2 - 1].Point
                point_c = selfobj.Point3[0].Shape.Vertexes[m_n3 - 1].Point

                if isEqualVectors(point_a, point_b):
                    m_msg = """Unable to create Plane from 2 equals Points :
                    Points 1 and 2 are equals !
                    """
                    printError_msg(m_msg, title=M_MACRO)
                    return

                if isEqualVectors(point_a, point_c):
                    m_msg = """Unable to create Plane from 2 equals Points :
                    Points 1 an 3 are equals !
                    """
                    printError_msg(m_msg, title=M_MACRO)
                    return

                if isEqualVectors(point_b, point_c):
                    m_msg = """Unable to create Plane from 2 equals Points :
                    Points 2 an 3 are equals !
                    """
                    printError_msg(m_msg, title=M_MACRO)
                    return

                if isColinearVectors(point_a, point_b, point_c):
                    printError_msg(M_EXCEPTION_MSG, title=M_MACRO)
                    return

                points.append(point_a)
                points.append(point_b)
                points.append(point_c)

                vector_center = meanVectorsPoint(points)

                vector21 = point_b - point_a
                vector31 = point_c - point_a
                plane_point = vector_center
                plane_normal = vector21.cross(vector31)

                edge_length = selfobj.Extension
                plane = Part.makePlane(edge_length,
                                       edge_length,
                                       plane_point,
                                       plane_normal)
                plane_center = plane.CenterOfMass
                plane_translate = plane_point - plane_center
                plane.translate(plane_translate)

#                 plane = Part.Plane(point_a, point_b, point_c)
#                 .toShape()
            if plane is not None:
                selfobj.Shape = plane
                propertiesPlane(selfobj.Label, self.color)
                selfobj.Point1_X = float(point_a.x)
                selfobj.Point1_Y = float(point_a.y)
                selfobj.Point1_Z = float(point_a.z)
                selfobj.Point2_X = float(point_b.x)
                selfobj.Point2_Y = float(point_b.y)
                selfobj.Point2_Z = float(point_b.z)
                selfobj.Point3_X = float(point_c.x)
                selfobj.Point3_Y = float(point_c.y)
                selfobj.Point3_Z = float(point_c.z)
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
            print("running ThreePointsPlane.onChanged !")
            print("Change property : " + str(prop))

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


def buildFromThreePoints(macro, group, vertexes, extension):
    """ Build a ThreePointsPlane feature object using three points.
    """
    vertex1 = vertexes[0]
    vertex2 = vertexes[1]
    vertex3 = vertexes[2]
    if WF.verbose():
        print_msg("vertex1 = " + str(vertex1))
        print_msg("vertex2 = " + str(vertex2))
        print_msg("vertex3 = " + str(vertex3))

    App.ActiveDocument.openTransaction(macro)
    selfobj = makeThreePointsPlaneFeature(group)
    selfobj.Point1 = vertex1
    selfobj.Point2 = vertex2
    selfobj.Point3 = vertex3
    selfobj.Extension = extension
    selfobj.Proxy.execute(selfobj)
    WF.touch(selfobj)


def three_points_plane_command():
    """ This command use the selected object(s) to try to build a
    ThreePointsPlane feature object.
    """
    m_sel, m_act_doc = getSel(WF.verbose())

    points_from = ["Points", "Curves", "Objects"]
    try:
        number_of_vertexes, vertex_list = m_sel.get_pointsWithNames(
            get_from=points_from)

        if number_of_vertexes < 3:
            raise Exception(M_EXCEPTION_MSG)

        try:
            m_main_dir = "WorkPlanes_P"
            m_sub_dir = "Set000"
            m_group = createFolders(str(m_main_dir))

            # Create a sub group if needed
            if number_of_vertexes > 6:
                m_group = createSubGroup(m_act_doc, m_main_dir, m_sub_dir)

            # Case of only 3 points
            if number_of_vertexes == 3:
                buildFromThreePoints(
                    M_MACRO, m_group, vertex_list, M_PLANE_EXT)
            else:
                raise Exception(M_EXCEPTION_MSG)

        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

    except Exception as err:
        printError_msgWithTimer(err.args[0], title=M_MACRO)

    App.ActiveDocument.commitTransaction()
    App.activeDocument().recompute()


if App.GuiUp:
    Gui.addCommand("ThreePointsPlane", Command(M_ICON_NAME,
                                               M_MENU_TEXT,
                                               M_ACCEL,
                                               M_TOOL_TIP,
                                               ThreePointsPlanePanel,
                                               three_points_plane_command))

if __name__ == '__main__':
    three_points_plane_command()
