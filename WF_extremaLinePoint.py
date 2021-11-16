# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *                        *
***************************************************************************
Create Point(s) at Start and End location of each selected Line(s).
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

__title__ = "Macro ExtremaLinePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro ExtremaLinePoint.
Creates a parametric ExtremaLinePoint from an Edge
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
    from WF_directory import createFolders, addObjectToGrp
    from WF_geometry import propertiesPoint
    from WF_command import Command
except ImportError:
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME = "WF_extremaLinePoint.svg"
M_ICON_NAMES = ["WF_startLinePoint.svg",
                "WF_endLinePoint.svg",
                "WF_extremaLinePoint.svg"]
M_DIALOG = "WF_UI_extremaLinePoint.ui"
M_DIALOG_TITLE = "Define location(s)."
M_EXCEPTION_MSG = """
Unable to create Extrema Line Point(s) :
- Select one or several Line/Edge(s) and/or
- Select one Plane/Face to process all (4) Edges and/or
- Select one Object to process all Edges at once !

Go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG = " : Extrema Line Point(s) created !"
M_MENU_TEXT = "Point(s) = Extrema(Line) "
M_ACCEL = ""
M_TOOL_TIP = """<b>Create Point(s)</b> at Start and End location<br>
of each selected Line(s).<br>
<br>
- Select one or several Line/Edge(s) and/or<br>
- Select one Plane/Face to process all (4) Edges and/or<br>
- Select one Object to process all Edges at once<br>
- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window and<br>
 - a Parameter(s) Window in Task Panel!</i>
"""
###############
M_MACRO = "Macro ExtremaLinePoint"
M_LOCATION = "Both ends"
M_LOCATIONS = ["Begin",
               "End",
               # "Both ends"
               ]
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


def getLocation():
    """ Get location of the point.

    Return
    -------
    either "Single" or "All"

    """
    return M_LOCATION


class ExtremaLinePointPanel:
    """ The ExtremaLinePointPanel (GUI).
    """

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)

        self.form.UI_ExtremaLinePoint_comboBox.setCurrentIndex(
            self.form.UI_ExtremaLinePoint_comboBox.findText(M_LOCATION))

    def accept(self):
        """ Run when click on OK button.
        """
        global M_LOCATION
        M_LOCATION = self.form.UI_ExtremaLinePoint_comboBox.currentText()

        if WF.verbose():
            print_msg("M_LOCATION = " + str(M_LOCATION))

        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if Gui.Selection.getSelectionEx(m_act_doc.Name):
                extrema_line_point_command()
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


def makeExtremaLinePointFeature(group):
    """ Makes a ExtremaLinePoint" parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "ExtremaLinePoint_P"
    m_part = "Part::FeaturePython"

    if group is None:
        return None
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        ExtremaLinePoint(m_obj)
        ViewProviderExtremaLinePoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj


class ExtremaLinePoint(WF_Point):
    """ The ExtremaLinePoint feature object. """
    # this method is mandatory

    def __init__(self, selfobj):
        if M_DEBUG:
            print("running ExtremaLinePoint.__init__ !")

        self.name = "ExtremaLinePoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our feature object.
        selfobj.addProperty("App::PropertyLinkSub",
                            "Edge",
                            self.name,
                            "Input edge")
        m_tooltip = """Indicates where is located the Point
relative to the parent Line.
        """
        selfobj.addProperty("App::PropertyEnumeration",
                            "At",
                            self.name,
                            m_tooltip)
        if sys.version_info > (3, 0):
            # Python 3 code in this block
            selfobj.At = [v.encode('utf8').decode('utf-8')
                          for v in M_LOCATIONS]
            selfobj.At = 'Begin'.encode('utf8').decode('utf-8')
        else:
            # Python 2 code in this block
            selfobj.At = [v.encode('utf8') for v in M_LOCATIONS]
            selfobj.At = 'Begin'.encode('utf8')

        selfobj.setEditorMode("Edge", 1)

        selfobj.Proxy = self

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        m_properties_list = ['Edge',
                             'At',
                             ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        if M_DEBUG:
            print("running ExtremaLinePoint.execute !")

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
            m_n = re.sub('[^0-9]', '', selfobj.Edge[1][0])
            m_n = int(m_n)
            if M_DEBUG:
                print_msg(str(selfobj.Edge))
                print_msg("m_n = " + str(m_n))

            if not selfobj.Edge[0].Shape.Edges:
                return

            if selfobj.At == "Begin":
                vector_point = selfobj.Edge[0].Shape.Edges[m_n -
                                                           1].Vertexes[0].Point
            else:
                vector_point = selfobj.Edge[0].Shape.Edges[m_n -
                                                           1].Vertexes[-1].Point

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
                    selfobj.setEditorMode("At", 1)
                else:
                    selfobj.setEditorMode("At", 0)
            propertiesPoint(selfobj.Label, self.color)

        if prop == "At":
            selfobj.Proxy.execute(selfobj)


class ViewProviderExtremaLinePoint:
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


def extrema_line_point_command():
    """ This command use the selected object(s) to try to build a
    ExtremaLinePoint feature object.
    """
    m_sel, m_act_doc = getSel(WF.verbose())

    edges_from = ["Segments", "Curves", "Planes", "Shells", "Objects"]
    try:
        number_of_edges, edge_list = m_sel.get_segmentsWithNames(
            get_from=edges_from)

        if number_of_edges == 0:
            raise Exception(M_EXCEPTION_MSG)

        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set000"
            m_group = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            if WF.verbose():
                print_msg("Location = " + str(M_LOCATION))

            # Create a sub group if needed
            if number_of_edges > 1 or M_LOCATION == "Both ends":
                try:
                    m_ob = App.ActiveDocument.getObject(
                        str(m_main_dir)).newObject(
                        "App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_act_doc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=M_MACRO)
                    printError_msg(m_error_msg)

            if WF.verbose():
                print_msg("Group = " + str(m_group.Label))

            for i in range(number_of_edges):
                edge = edge_list[i]

                if M_LOCATION in ["Begin", "Both ends"]:
                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj1 = makeExtremaLinePointFeature(m_group)
                    selfobj1.Edge = edge
                    selfobj1.At = "Begin"
                    selfobj1.Proxy.execute(selfobj1)
                    if str(selfobj1.Parametric) == 'Interactive':
                        selfobj1.Parametric = 'Dynamic'
                        selfobj1.touch()
                        selfobj1.Parametric = 'Interactive'
                    if str(selfobj1.Parametric) == 'Not':
                        selfobj1.Parametric = 'Dynamic'
                        selfobj1.touch()
                        selfobj1.Parametric = 'Not'
                if M_LOCATION in ["End", "Both ends"]:
                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj2 = makeExtremaLinePointFeature(m_group)
                    selfobj2.Edge = edge
                    selfobj2.At = "End"
                    selfobj2.Proxy.execute(selfobj2)
                    if str(selfobj2.Parametric) == 'Interactive':
                        selfobj2.Parametric = 'Dynamic'
                        selfobj2.touch()
                        selfobj2.Parametric = 'Interactive'
                    if str(selfobj2.Parametric) == 'Not':
                        selfobj2.Parametric = 'Dynamic'
                        selfobj2.touch()
                        selfobj2.Parametric = 'Not'

        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

    except Exception as err:
        printError_msgWithTimer(err.args[0], title=M_MACRO)

    App.ActiveDocument.commitTransaction()
    App.activeDocument().recompute()


if App.GuiUp:
    Gui.addCommand("ExtremaLinePoint", Command(M_ICON_NAME,
                                               M_MENU_TEXT,
                                               M_ACCEL,
                                               M_TOOL_TIP,
                                               ExtremaLinePointPanel,
                                               extrema_line_point_command))

if __name__ == '__main__':
    extrema_line_point_command()
