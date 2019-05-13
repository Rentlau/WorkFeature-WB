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
from FreeCAD import Base
import WF
from WF_Objects_base import WF_Line
# from InitGui import m_debug
if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro_NPointsLine"
__author__ = "Rentlau_64"
__brief__ = '''
Macro NPointsLine.
Creates a parametric NPointsLine from a list of Points
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
except ImportError:
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
m_icon = "/WF_nPointsLine.svg"
m_dialog = "/WF_UI_nPointsLine.ui"
m_dialog_title = ""
m_exception_msg = """
Unable to create a Line :
- Select several Points(s) and/or
- Select several Line/Edge(s) to process 2 ends points and/or
- Select one or several Plane/Face(s) to process all Points at once and/or
- Select one or several Object(s) to process all Points at once;

and go to Parameter(s) Window in Task Panel!"""
m_result_msg = " : N Points Lines created!"
m_menu_text = "Line = SVD(Points)"
m_accel = ""
m_tool_tip = """<b>Create a "best fit" Line</b> from a set of Points using Singular Value Decomposition (SVD).<br>

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
m_macro = "Macro NPointsLine"
m_svd_flag = False
###############


def linkSubList_convertToOldStyle(references):
    """("input: [(obj1, (sub1, sub2)), (obj2, (sub1, sub2))]\n"
    "output: [(obj1, sub1), (obj1, sub2), (obj2, sub1), (obj2, sub2)]")"""
    result = []
    for tup in references:
        if type(tup[1]) is tuple or type(tup[1]) is list:
            for subname in tup[1]:
                result.append((tup[0], subname))
            if len(tup[1]) == 0:
                result.append((tup[0], ''))
        else:
            # old style references, no conversion required
            result.append(tup)
    return result


class NPointsLinePanel:
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)
        self.form.UI_nPointsLine_checkBox.setCheckState(QtCore.Qt.Unchecked)
        if m_svd_flag:
            self.form.UI_nPointsLine_checkBox.setCheckState(QtCore.Qt.Checked)

    def accept(self):
        global m_svd_flag

        m_svd_flag = self.form.UI_nPointsLine_checkBox.isChecked()

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


def makeNPointsLineFeature(group):
    """ Makes a NPointsLine parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "NPointsLine_P"
    m_part = "Part::FeaturePython"

    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        m_inst = NPointsLine(m_obj)
        ViewProviderNPointsLine(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=m_macro)
        return None

    return m_obj, m_inst


class NPointsLine(WF_Line):
    """ The NPointsLine feature object. """
    # this method is mandatory
    def __init__(self, selfobj):
        if m_debug:
            print("running NPointsLine.__init__ !")

        self.name = "NPointsLine"
        WF_Line.__init__(self, selfobj, self.name)

        # Add some custom properties to our NPointsLine feature object.
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
            selfobj.VectorIndex = [v.encode('utf8').decode('utf-8') for v in ['1', '2', '3']]
            selfobj.VectorIndex = '1'.encode('utf8').decode('utf-8')
        else:
            # Python 2 code in this block
            selfobj.VectorIndex = [v.encode('utf8') for v in ['1', '2', '3']]
            selfobj.VectorIndex = '1'.encode('utf8')
        selfobj.Proxy = self
        # save the object in the class, to store or retrieve specific data from it
        # from within the class
        # self.Object = selfobj

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        if m_debug:
            print("running NPointsLine.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        if WF.verbose():
            m_msg = "Recompute Python NPointsLine feature\n"
            App.Console.PrintMessage(m_msg)

        if m_debug:
            print("selfobj.PropertiesList = " + str(selfobj.PropertiesList))

        m_PropertiesList = ['Points',
                            "VectorIndex",
                            ]
        for m_Property in m_PropertiesList:
            if m_Property not in selfobj.PropertiesList:
                return

        try:
            import numpy as np
        except ImportError:
            m_msg = "You MUST install numpy to use this function !"
            printError_msg(m_msg, title=m_macro)

        try:
            Line = None
            if m_debug:
                print("selfobj.Points = " + str(selfobj.Points))

            m_points = []
            m_x = []
            m_y = []
            m_z = []
            if selfobj.Points is not None:
                for p in linkSubList_convertToOldStyle(selfobj.Points):
                    n = eval(p[1].lstrip('Vertex'))
                    if m_debug:
                        print("p " + str(p))
                        print_msg("n = " + str(n))
                    m_point = p[0].Shape.Vertexes[n - 1].Point
                    m_points.append(m_point)
                    m_x.append(m_point.x)
                    m_y.append(m_point.y)
                    m_z.append(m_point.z)

                m_np_x = np.asfarray(m_x)
                m_np_y = np.asfarray(m_y)
                m_np_z = np.asfarray(m_z)
                if m_debug:
                    print_msg(" m_np_x=" + str(m_np_x))
                    print_msg(" m_np_y=" + str(m_np_y))
                    print_msg(" m_np_z=" + str(m_np_z))

                m_data = np.concatenate((m_np_x[:, np.newaxis],
                                        m_np_y[:, np.newaxis],
                                        m_np_z[:, np.newaxis]),
                                        axis=1)
                if m_debug:
                    print_msg(" m_data=" + str(m_data))

                # Calculate the mean of the points, i.e. the 'center' of the cloud
                m_datamean = m_data.mean(axis=0)
                Axis_E0 = Base.Vector(m_datamean[0], m_datamean[1], m_datamean[2])

                # Do an SVD on the mean-centered data.
                m_uu, m_dd, m_vv = np.linalg.svd(m_data - m_datamean)
                if m_debug:
                    print_msg(" m_uu=" + str(m_uu))
                    print_msg(" m_dd=" + str(m_dd))
                    print_msg(" m_vv=" + str(m_vv))

                # Now vv[0] contains the first principal component, i.e. the direction
                # vector of the 'best fit' line in the least squares sense.
                Axis_dir = Base.Vector(m_vv[0][0], m_vv[0][1], m_vv[0][2])
                point1 = Axis_E0 - Axis_dir.normalize().multiply(m_dd[0] / 2.)

                if selfobj.VectorIndex == '1':
                    point2 = Axis_E0 + Axis_dir.normalize().multiply(m_dd[0] / 2.)

                if selfobj.VectorIndex == '2':
                    Axis_dir = Base.Vector(m_vv[1][0], m_vv[1][1], m_vv[1][2])
                    point1 = Axis_E0 - Axis_dir.normalize().multiply(m_dd[0] / 2.)
                    point2 = Axis_E0 + Axis_dir.normalize().multiply(m_dd[1] / 2.)
                    # point2 = Axis_E0 + Axis_dir

                if selfobj.VectorIndex == '3':
                    Axis_dir = Base.Vector(m_vv[2][0], m_vv[2][1], m_vv[2][2])
                    point1 = Axis_E0 - Axis_dir.normalize().multiply(m_dd[0] / 2.)
                    point2 = Axis_E0 + Axis_dir.normalize().multiply(m_dd[2] / 2.)
                    # point2 = Axis_E0 + Axis_dir

                Point_E1 = point2
                Point_E2 = point1

                Line = Part.makeLine(coordVectorPoint(Point_E2),
                                     coordVectorPoint(Point_E1))
            if Line is not None:
                selfobj.Shape = Line
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
        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

    def onChanged(self, selfobj, prop):
        if WF.verbose():
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")

        if m_debug:
            print("running NPointsLine.onChanged !")

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

#         if prop == 'VectorIndex':
#             if selfobj.VectorIndex <= 1:
#                 selfobj.VectorIndex = 1
#             if selfobj.VectorIndex >= 3:
#                 selfobj.VectorIndex = 3
#
#             selfobj.Proxy.execute(selfobj)

    def addSubobjects(self, selfobj, points_list=[]):
        "adds pointlinks to this TwoPointsLine object"
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
    global path_WF_icons
    icon = '/WF_nPointsLine.svg'

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
        return (path_WF_icons + ViewProviderNPointsLine.icon)

    def setIcon(self, icon='/WF_nPointsLine.svg'):
        ViewProviderNPointsLine.icon = icon


class CommandNPointsLine:
    """ Command to create NPointsLine feature object. """
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel': m_accel,
                'ToolTip': m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(NPointsLinePanel())

        run()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("NPointsLine", CommandNPointsLine())


def run():
    m_sel, m_actDoc = getSel(WF.verbose())

    try:
        Number_of_Vertexes, Vertex_List = m_sel.get_pointsNames(
            getfrom=["Points",
                     "Curves",
                     "Objects"])
        if WF.verbose():
            print_msg("Number_of_Vertexes = " + str(Number_of_Vertexes))
            print_msg("Vertex_List = " + str(Vertex_List))

        if Number_of_Vertexes < 2:
            raise Exception(m_exception_msg)

        try:
            m_main_dir = "WorkAxis_P"
            m_sub_dir = "Set001"
            m_group = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            # Create a sub group if needed
            if m_svd_flag:
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=m_macro)
                    printError_msg(m_error_msg)

            if WF.verbose():
                print_msg("Group = " + str(m_group.Label))

            points = []
            # Case of only 2 points
            if Number_of_Vertexes == 2:
                if WF.verbose():
                    print_msg("Process only 2 points")
                vertex1 = Vertex_List[0]
                vertex2 = Vertex_List[1]
                points.append(vertex1)
                points.append(vertex2)

                if WF.verbose():
                    print_msg("vertex1 = " + str(vertex1))
                    print_msg("vertex2 = " + str(vertex2))

                App.ActiveDocument.openTransaction(m_macro)
                selfobj, m_inst = makeNPointsLineFeature(m_group)
                if m_debug:
                    print("selfobj : " + str(selfobj))
                m_inst.addSubobjects(selfobj, points)
                selfobj.VectorIndex = '1'
                selfobj.Proxy.execute(selfobj)

                if m_svd_flag:
                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj, m_inst = makeNPointsLineFeature(m_group)
                    m_inst.addSubobjects(selfobj, points)
                    selfobj.VectorIndex = '2'
                    selfobj.Proxy.execute(selfobj)

                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj, m_inst = makeNPointsLineFeature(m_group)
                    m_inst.addSubobjects(selfobj, points)
                    selfobj.VectorIndex = '3'
                    selfobj.Proxy.execute(selfobj)
            # Case of more than 2 points
            else:
                if WF.verbose():
                    print_msg("Process more than 2 points")
                for i in range(Number_of_Vertexes):
                    vertex = Vertex_List[i]
                    points.append(vertex)
                    if WF.verbose():
                        print_msg("vertex = " + str(vertex))

                App.ActiveDocument.openTransaction(m_macro)
                selfobj, m_inst = makeNPointsLineFeature(m_group)
                if m_debug:
                    print("selfobj : " + str(selfobj))
                m_inst.addSubobjects(selfobj, points)
                selfobj.VectorIndex = '1'
                selfobj.Proxy.execute(selfobj)

                if m_svd_flag:
                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj, m_inst = makeNPointsLineFeature(m_group)
                    m_inst.addSubobjects(selfobj, points)
                    selfobj.VectorIndex = '2'
                    selfobj.Proxy.execute(selfobj)

                    App.ActiveDocument.openTransaction(m_macro)
                    selfobj, m_inst = makeNPointsLineFeature(m_group)
                    m_inst.addSubobjects(selfobj, points)
                    selfobj.VectorIndex = '3'
                    selfobj.Proxy.execute(selfobj)

        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

        App.ActiveDocument.commitTransaction()

    except Exception as err:
        printError_msg(err.args[0], title=m_macro)


if __name__ == '__main__':
    run()
