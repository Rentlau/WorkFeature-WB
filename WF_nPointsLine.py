# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
***************************************************************************
Create a "best fit" Line from a set of Points using
Singular Value Decomposition (SVD).

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
from PySide import QtCore
from FreeCAD import Base
from WF_config import PATH_WF_ICONS, PATH_WF_UTILS, PATH_WF_UI
import WF
from WF_Objects_base import WF_Line

if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro_NPointsLine"
__author__ = "Rentlau_64"
__brief__ = '''
Macro NPointsLine.
Creates a parametric NPointsLine from a list of Points
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
    from WF_geometry import coordVectorPoint, propertiesLine
    from WF_utils import linkSubList_convertToOldStyle
    from WF_command import Command
except ImportError:
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME = "WF_nPointsLine.svg"
M_DIALOG = "WF_UI_nPointsLine.ui"
M_DIALOG_TITLE = ""
M_EXCEPTION_MSG = """
Unable to create a Line :
- Select several Points(s) and/or
- Select several Line/Edge(s) to process 2 ends points and/or
- Select one or several Plane/Face(s) to process all Points at once and/or
- Select one or several Object(s) to process all Points at once;

and go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG = " : N Points Lines created!"
M_MENU_TEXT = "Line = SVD(Points)"
M_ACCEL = ""
M_TOOL_TIP = """<b>Create a "best fit" Line</b> from a set of Points using Singular Value Decomposition (SVD).<br>

<br>
- Select several Points(s) and/or<br>
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
M_MACRO = "Macro NPointsLine"
M_SVD_FLAG = False
###############


def setSvd(flag):
    """ Set SVD flag to generate all 3 vectors from SVD decomposition.

    Parameters
    -------
    *flag*      : (Boolean, mandatory)
                If False:
                Generate only main vector.
                If True:
                Generate all 3 vectors from SVD decomposition
    """
    global M_SVD_FLAG
    M_SVD_FLAG = flag


def isSvd():
    """ Get SVD flag.

    Return
    -------
    A Boolean
    """
    return M_SVD_FLAG


class NPointsLinePanel:
    """ The NPointsLinePanel (GUI).
    """

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)
        self.form.UI_nPointsLine_checkBox.setCheckState(
            QtCore.Qt.Unchecked)
        if M_SVD_FLAG:
            self.form.UI_nPointsLine_checkBox.setCheckState(
                QtCore.Qt.Checked)

    def accept(self):
        """ Run when click on OK button.
        """
        global M_SVD_FLAG

        M_SVD_FLAG = self.form.UI_nPointsLine_checkBox.isChecked()

        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if Gui.Selection.getSelectionEx(m_act_doc.Name):
                n_points_line_command()
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


def makeNPointsLineFeature(group):
    """ Makes a NPointsLine parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "NPointsLine_P"
    m_part = "Part::FeaturePython"

    if group is None:
        return None
    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        m_inst = NPointsLine(m_obj)
        ViewProviderNPointsLine(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj, m_inst


class NPointsLine(WF_Line):
    """ The NPointsLine feature object.
    """

    def __init__(self, selfobj):
        if M_DEBUG:
            print("running NPointsLine.__init__ !")

        self.name = "NPointsLine"
        WF_Line.__init__(self, selfobj, self.name)
        # Add some custom properties to our feature object.
        selfobj.addProperty("App::PropertyLinkSubList",
                            "Points",
                            self.name,
                            "List of Points")
        selfobj.Points = []
        selfobj.setEditorMode("Points", 1)

        m_tooltip = """This is the Vector index
of the Singular Value Decomposition (SVD).
1, 2 or 3 are allowed.
"""
        selfobj.addProperty("App::PropertyEnumeration",
                            "VectorIndex",
                            self.name,
                            m_tooltip)
        if (sys.version_info > (3, 0)):
            # Python 3 code in this block
            selfobj.VectorIndex = [v.encode('utf8').decode(
                'utf-8') for v in ['1', '2', '3']]
            selfobj.VectorIndex = '1'.encode('utf8').decode('utf-8')
        else:
            # Python 2 code in this block
            selfobj.VectorIndex = [v.encode('utf8') for v in ['1', '2', '3']]
            selfobj.VectorIndex = '1'.encode('utf8')
        selfobj.Proxy = self
        # save the object in the class, to store or retrieve specific data from it
        # from within the class
        # self.Object = selfobj

    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        m_properties_list = ['Points',
                             "VectorIndex",
                             ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        if M_DEBUG:
            print("running NPointsLine.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        try:
            import numpy as np
        except ImportError:
            m_msg = "You MUST install numpy to use this function !"
            printError_msg(m_msg, title=M_MACRO)

        try:
            line = None
            m_points = []
            m_x = []
            m_y = []
            m_z = []
            if selfobj.Points is not None:
                for p in linkSubList_convertToOldStyle(selfobj.Points):
                    # n = eval(p[1].lstrip('Vertex'))
                    m_n = re.sub('[^0-9]', '', p[1])
                    m_n = int(m_n)
                    if M_DEBUG:
                        print("p " + str(p))
                        print_msg("m_n = " + str(m_n))

                    m_point = p[0].Shape.Vertexes[m_n - 1].Point
                    m_points.append(m_point)
                    m_x.append(m_point.x)
                    m_y.append(m_point.y)
                    m_z.append(m_point.z)

                m_np_x = np.asfarray(m_x)
                m_np_y = np.asfarray(m_y)
                m_np_z = np.asfarray(m_z)
                if M_DEBUG:
                    print_msg(" m_np_x=" + str(m_np_x))
                    print_msg(" m_np_y=" + str(m_np_y))
                    print_msg(" m_np_z=" + str(m_np_z))

                m_data = np.concatenate((m_np_x[:, np.newaxis],
                                         m_np_y[:, np.newaxis],
                                         m_np_z[:, np.newaxis]),
                                        axis=1)
                if M_DEBUG:
                    print_msg(" m_data=" + str(m_data))

                # Calculate the mean of the points, i.e. the 'center' of the
                # cloud
                m_data_mean = m_data.mean(axis=0)
                axis_eo = Base.Vector(
                    m_data_mean[0], m_data_mean[1], m_data_mean[2])

                # Do an SVD on the mean-centered data.
                m_uu, m_dd, m_vv = np.linalg.svd(m_data - m_data_mean)
                if M_DEBUG:
                    print_msg(" m_uu=" + str(m_uu))
                    print_msg(" m_dd=" + str(m_dd))
                    print_msg(" m_vv=" + str(m_vv))

                # Now vv[0] contains the first principal component, i.e. the direction
                # vector of the 'best fit' line in the least squares sense.
                axis_dir = Base.Vector(m_vv[0][0], m_vv[0][1], m_vv[0][2])
                point1 = axis_eo - axis_dir.normalize().multiply(m_dd[0] / 2.)

                if selfobj.VectorIndex == '1':
                    point2 = axis_eo + \
                        axis_dir.normalize().multiply(m_dd[0] / 2.)

                if selfobj.VectorIndex == '2':
                    axis_dir = Base.Vector(m_vv[1][0], m_vv[1][1], m_vv[1][2])
                    point1 = axis_eo - \
                        axis_dir.normalize().multiply(m_dd[0] / 2.)
                    point2 = axis_eo + \
                        axis_dir.normalize().multiply(m_dd[1] / 2.)
                    # point2 = axis_eo + axis_dir

                if selfobj.VectorIndex == '3':
                    axis_dir = Base.Vector(m_vv[2][0], m_vv[2][1], m_vv[2][2])
                    point1 = axis_eo - \
                        axis_dir.normalize().multiply(m_dd[0] / 2.)
                    point2 = axis_eo + \
                        axis_dir.normalize().multiply(m_dd[2] / 2.)
                    # point2 = axis_eo + axis_dir

                line = Part.makeLine(coordVectorPoint(point1),
                                     coordVectorPoint(point2))
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
            print("running NPointsLine.onChanged !")
            print("Change property : " + str(prop))

        WF_Line.onChanged(self, selfobj, prop)

        if prop == "Parametric":
            if 'Parametric' in selfobj.PropertiesList:
                if selfobj.Parametric == 'Not':
                    pass
                else:
                    pass
            propertiesLine(selfobj.Label, self.color)

        if prop == "Points":
            selfobj.Proxy.execute(selfobj)

    def addSubobjects(self, selfobj, points_list=[]):
        """ Adds pointlinks to this NPointsLine object
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


class ViewProviderNPointsLine:
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


def n_points_line_command():
    """ This command use the selected object(s) to try to build a
    NPointsLine feature object.
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
            if M_SVD_FLAG:
                m_group = createSubGroup(m_act_doc, m_main_dir, m_sub_dir)

            points = []
            # Case of only 2 points
            if number_of_vertexes == 2:
                if WF.verbose():
                    print_msg("Process only 2 points")
                vertex1 = vertex_list[0]
                vertex2 = vertex_list[1]
                points.append(vertex1)
                points.append(vertex2)

                if WF.verbose():
                    print_msg("vertex1 = " + str(vertex1))
                    print_msg("vertex2 = " + str(vertex2))

                App.ActiveDocument.openTransaction(M_MACRO)
                selfobj, m_inst = makeNPointsLineFeature(m_group)
                m_inst.addSubobjects(selfobj, points)
                selfobj.VectorIndex = '1'
                selfobj.Proxy.execute(selfobj)

                if M_SVD_FLAG:
                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj, m_inst = makeNPointsLineFeature(m_group)
                    m_inst.addSubobjects(selfobj, points)
                    selfobj.VectorIndex = '2'
                    selfobj.Proxy.execute(selfobj)

                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj, m_inst = makeNPointsLineFeature(m_group)
                    m_inst.addSubobjects(selfobj, points)
                    selfobj.VectorIndex = '3'
                    selfobj.Proxy.execute(selfobj)
            # Case of more than 2 points
            else:
                if WF.verbose():
                    print_msg("Process more than 2 points")
                for i in range(number_of_vertexes):
                    vertex = vertex_list[i]
                    points.append(vertex)
                    if WF.verbose():
                        print_msg("vertex = " + str(vertex))

                App.ActiveDocument.openTransaction(M_MACRO)
                selfobj, m_inst = makeNPointsLineFeature(m_group)
                m_inst.addSubobjects(selfobj, points)
                selfobj.VectorIndex = '1'
                selfobj.Proxy.execute(selfobj)

                if M_SVD_FLAG:
                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj, m_inst = makeNPointsLineFeature(m_group)
                    m_inst.addSubobjects(selfobj, points)
                    selfobj.VectorIndex = '2'
                    selfobj.Proxy.execute(selfobj)

                    App.ActiveDocument.openTransaction(M_MACRO)
                    selfobj, m_inst = makeNPointsLineFeature(m_group)
                    m_inst.addSubobjects(selfobj, points)
                    selfobj.VectorIndex = '3'
                    selfobj.Proxy.execute(selfobj)

        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

    except Exception as err:
        printError_msgWithTimer(err.args[0], title=M_MACRO)

    App.ActiveDocument.commitTransaction()
    App.activeDocument().recompute()


if App.GuiUp:
    Gui.addCommand("NPointsLine", Command(M_ICON_NAME,
                                          M_MENU_TEXT,
                                          M_ACCEL,
                                          M_TOOL_TIP,
                                          NPointsLinePanel,
                                          n_points_line_command))

if __name__ == '__main__':
    n_points_line_command()
