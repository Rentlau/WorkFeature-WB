# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
***************************************************************************
Create projected point(s) on the chosen (main) Plane(s).

Projected Plane(s):
You can either select one or several of the MAIN plane(s) : XY, XZ, YZ

Options:
You can choose to generated projection dashed lines.
You can choose to generate several symmetrical point(s).

How to
- Select one or several Points and/or
- Select several Line/Edge(s) to process 2 ends points
- Then Click on the icon
"""
import sys
import os.path
import re
import FreeCAD as App
import Part
from FreeCAD import Base
from PySide import QtCore
from WF_config import PATH_WF_ICONS, PATH_WF_UTILS, PATH_WF_UI
import WF
from WF_Objects_base import WF_Point
from WF_Objects_base import WF_Line
import WF_twoPointsLine as twoPL
import WF_alongLinePoint as aLP

if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro_ProjectedPoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro ProjectedPoint.
Creates a parametric ProjectedPoint from a list of Points
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
    from WF_geometry import *
    from WF_command import Command
except ImportError:
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME = "WF_projectedPoint.svg"
M_DIALOG = "WF_UI_projectedPoint.ui"
M_DIALOG_TITLE = ""
M_EXCEPTION_MSG = """
Unable to create a Projected Point(s) :
 - Select one or several Points(s) and/or
 - Select one or several Line/Edge(s) to process 2 ends points

and go to Parameter(s) Window in Task Panel!"""
# - Select one or several Plane/Face(s) to process all Points at once and/or
# - Select one or several Object(s) to process all Points at once;
M_RESULT_MSG = " : Projected Point(s) created !"
M_MENU_TEXT = "Point = projected(Points)"
M_ACCEL = ""
M_TOOL_TIP = """<b>Create projected point(s)</b> on chosen or main Planes.<br>

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
M_MACRO = "Macro ProjectedPoint"
M_SEL_PLANE = "XY plane"
M_SEL_MULTI = ["XY, YZ planes",
               "XY, XZ planes",
               "YZ, XZ planes",
               "XY, YZ, XZ planes"
               # "Already Selected planes",
               ]
M_SEL_PLANE_LIST = ["Defined plane",
                    "XY plane",
                    "YZ plane",
                    "XZ plane",
                    # "XY, YZ planes",
                    # "XY, XZ planes",
                    # "YZ, XZ planes",
                    # "XY, YZ, XZ planes"
                    # "Already Selected planes",
                    ]
M_PROJ_LINE = False
M_GROUP = None
M_NUMBER_SYM_POINTS = 0
###############


def setSelectedPlane(selected_plane):
    """ Set projection plane of the point.

    Parameters
    -------
    *selected_plane* : (String, Mandatory)
            either "XY plane", "YZ plane" or "XZ plane".
    """
    global M_SEL_PLANE
    if selected_plane in M_SEL_PLANE_LIST:
        M_SEL_PLANE = selected_plane
    else:
        raise Exception(
            "Not valid 'selected_plane' option : must be either 'XY plane', 'YZ plane' or 'XZ plane'")


def getSelectedPlane():
    """ Get projection plane  of the point.

    Return
    -------
    either "XY plane", "YZ plane" or "XZ plane".

    """
    return M_SEL_PLANE


def setProjectionLine(flag):
    """ Set if projection line from point to plane is generated.

    Parameters
    -------
    *flag*      : (Boolean, mandatory)

    """
    global M_PROJ_LINE
    M_PROJ_LINE = flag


def isProjectionLine():
    """ Get if projection line from point to plane is generated.

    Return
    -------
    A Boolean
    """
    return M_PROJ_LINE


def setNumberSymmetrics(number_of_symmetric):
    """ Set the number of symmetric points to generate.

    Parameters
    -------
    *number_of_symmetric* : (Integer, Mandatory)
    """
    global M_NUMBER_SYM_POINTS
    M_NUMBER_SYM_POINTS = int(number_of_symmetric)


def getNumberSymmetrics():
    """ Get the number of symmetric points.

    Return
    -------
    An integer.
    """
    return M_NUMBER_SYM_POINTS


class ProjectedPointPanel:
    """ The ProjectedPointPanel (GUI).
    """

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)
        self.form.UI_ProjectePoint_comboBox.setCurrentIndex(
            self.form.UI_ProjectePoint_comboBox.findText(M_SEL_PLANE))
        self.form.UI_ProjectePoint_checkBox.setCheckState(QtCore.Qt.Unchecked)
        if M_PROJ_LINE:
            self.form.UI_ProjectePoint_checkBox.setCheckState(
                QtCore.Qt.Checked)

        self.form.UI_ProjectePoint_spin_numberSymPoint.setValue(
            M_NUMBER_SYM_POINTS)

    def accept(self):
        """ Run when click on OK button.
        """
        global M_SEL_PLANE
        global M_PROJ_LINE
        global M_NUMBER_SYM_POINTS
        M_SEL_PLANE = self.form.UI_ProjectePoint_comboBox.currentText()
        M_PROJ_LINE = self.form.UI_ProjectePoint_checkBox.isChecked()
        M_NUMBER_SYM_POINTS = self.form.UI_ProjectePoint_spin_numberSymPoint.value()

        if WF.verbose():
            print_msg("M_SEL_PLANE = " + str(M_SEL_PLANE))
            print_msg("M_PROJ_LINE = " + str(M_PROJ_LINE))
            print_msg("M_NUMBER_SYM_POINTS = " + str(M_NUMBER_SYM_POINTS))

        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if Gui.Selection.getSelectionEx(m_act_doc.Name):
                projected_point_command()
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


def makeProjectedPointFeature(group):
    """ Makes a ProjectedPoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "ProjectedPoint_P"
    m_part = "Part::FeaturePython"

    if group is None:
        return None
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        ProjectedPoint(m_obj)
        ViewProviderProjectedPoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj


class ProjectedPoint(WF_Point):
    """ The ProjectedPoint feature object.
    """

    def __init__(self, selfobj):
        if M_DEBUG:
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
            selfobj.At = [v.encode('utf8').decode('utf-8')
                          for v in M_SEL_PLANE_LIST]
            selfobj.At = 'XY plane'.encode('utf8').decode('utf-8')
        else:
            # Python 2 code in this block
            selfobj.At = [v.encode('utf8') for v in M_SEL_PLANE_LIST]
            selfobj.At = 'XY plane'.encode('utf8')

        selfobj.setEditorMode("Point", 1)
        selfobj.setEditorMode("Plane", 1)

        selfobj.Proxy = self

    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        m_properties_list = ['Point',
                             "Plane",
                             "At",
                             # "Show",
                             ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        if M_DEBUG:
            print("running ProjectedPoint.execute !")

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
            if selfobj.Point is not None:
                # n = eval(selfobj.Point[1][0].lstrip('Vertex'))
                m_n = re.sub('[^0-9]', '', selfobj.Point1[1][0])
                m_n = int(m_n)
                if M_DEBUG:
                    print_msg(str(selfobj.Point1))
                    print_msg("m_n = " + str(m_n))

                point1 = selfobj.Point[0].Shape.Vertexes[m_n - 1].Point
                x = point1.x
                y = point1.y
                z = point1.z

                if selfobj.Plane is None:
                    # No selected plane so projection on one of MAIN planes
                    if selfobj.At == "XY plane":
                        vector_point = Base.Vector(x, y, 0.0)
                    elif selfobj.At == "YZ plane":
                        vector_point = Base.Vector(0.0, y, z)
                    elif selfobj.At == "XZ plane":
                        vector_point = Base.Vector(x, 0.0, z)
                    else:
                        printError_msg(
                            "Not valid plane option!", title=M_MACRO)
                else:
                    # A selected plane
                    pass
#                     p=App.Vector(1,1,1)
#                     p.projectToPlane(App.Vector(0,0,0),App.Vector(1,0,1))
# projectToPlane parameters are (point on plane,normal direction)

            if vector_point is not None:
                point = Part.Point(vector_point)
                selfobj.Shape = point.toShape()
                propertiesPoint(selfobj.Label, self.color)
                selfobj.X = float(vector_point.x)
                selfobj.Y = float(vector_point.y)
                selfobj.Z = float(vector_point.z)

                if M_DEBUG:
                    print("M_PROJ_LINE = " + str(M_PROJ_LINE))
                    print("M_NUMBER_SYM_POINTS = " + str(M_NUMBER_SYM_POINTS))

                if M_PROJ_LINE and not self.created:
                    point_1 = selfobj.Point
                    object_1 = selfobj
                    twoPL.buildFromOnePointAndOneObject(point_1,
                                                        object_1,
                                                        M_GROUP)

                if M_NUMBER_SYM_POINTS > 0 and not self.created:
                    for m_i in range(M_NUMBER_SYM_POINTS):
                        index = m_i + 2
                        aLP.buildFromTwoPoints(point1,
                                               vector_point,
                                               index,
                                               object_1,
                                               M_GROUP)

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
            print("running ProjectedPoint.onChanged !")
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
        if M_DEBUG:
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
        return os.path.join(PATH_WF_ICONS, self.icon)

    def setIcon(self, icon=M_ICON_NAME):
        self.icon = icon


class CommandProjectedPoint:
    """ Command to create ProjectedPoint feature object. """

    def GetResources(self):
        return {'Pixmap': os.path.join(PATH_WF_ICONS, M_ICON_NAME),
                'MenuText': M_MENU_TEXT,
                'Accel': M_ACCEL,
                'ToolTip': M_TOOL_TIP}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if len(Gui.Selection.getSelectionEx(m_act_doc.Name)) == 0:
                Gui.Control.showDialog(ProjectedPointPanel())

        projected_point_command()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("ProjectedPoint", CommandProjectedPoint())


def projected_point_command():
    global M_GROUP
    m_sel, m_act_doc = getSel(WF.verbose())

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
        number_of_vertexes, vertex_list = m_sel.get_pointsNames(
            getfrom=["Points",
                     "Segments",
                     "Curves",
                     "Planes",
                     "Objects"
                     ])
        if WF.verbose():
            print_msg("number_of_vertexes = " + str(number_of_vertexes))
            print_msg("vertex_list = " + str(vertex_list))

        if number_of_vertexes < 1:
            raise Exception(M_EXCEPTION_MSG)

        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set001"
            M_GROUP = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            # Create a sub group if needed
            if number_of_vertexes > 1 or M_SEL_PLANE in M_SEL_MULTI or M_PROJ_LINE:
                try:
                    m_ob = App.ActiveDocument.getObject(
                        str(m_main_dir)).newObject(
                        "App::DocumentObjectGroup", str(m_sub_dir))
                    M_GROUP = m_act_doc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=M_MACRO)
                    printError_msg(m_error_msg)

            if WF.verbose():
                print_msg("Group = " + str(M_GROUP.Label))

            for point in vertex_list:
                if WF.verbose():
                    print_msg("Selected plane" + str(M_SEL_PLANE))

                # Possible selections
                # "XY plane",
                # "YZ plane",
                # "XZ plane",
                # "XY, YZ planes",
                # "XY, XZ planes",
                # "YZ, XZ planes",
                # "XY, YZ, XZ planes"
                # "Already Selected planes",

                if M_SEL_PLANE in ["XY plane",
                                   "XY, YZ planes",
                                   "XY, XZ planes",
                                   "XY, YZ, XZ planes"]:
                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj = makeProjectedPointFeature(M_GROUP)
                    selfobj.Point = point
                    selfobj.At = "XY plane"
                    selfobj.Proxy.execute(selfobj)
                    WF.touch(selfobj)

                if M_SEL_PLANE in ["YZ plane",
                                   "XY, YZ planes",
                                   "YZ, XZ planes",
                                   "XY, YZ, XZ planes"]:
                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj = makeProjectedPointFeature(M_GROUP)
                    selfobj.Point = point
                    selfobj.At = "YZ plane"
                    selfobj.Proxy.execute(selfobj)
                    WF.touch(selfobj)
                if M_SEL_PLANE in ["XZ plane",
                                   "XY, XZ planes",
                                   "YZ, XZ planes",
                                   "XY, YZ, XZ planes"]:
                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj = makeProjectedPointFeature(M_GROUP)
                    selfobj.Point = point
                    selfobj.At = "XZ plane"
                    selfobj.Proxy.execute(selfobj)
                    WF.touch(selfobj)
        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

        App.ActiveDocument.commitTransaction()

    except Exception as err:
        printError_msg(err.args[0], title=M_MACRO)


if __name__ == '__main__':
    projected_point_command()
