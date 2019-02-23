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
import WF
from WF_Objects_base import WF_Point
if App.GuiUp:
    import FreeCADGui as Gui

__title__= "Macro ExtremaLinePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro ExtremaLinePoint.
Creates a parametric ExtremaLinePoint from an Edge
'''
###############
m_debug = False
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
m_icon = "/WF_extremaLinePoint.svg"
m_icons = ["/WF_startLinePoint.svg",
           "/WF_endLinePoint.svg",
           "/WF_extremaLinePoint.svg"]
m_dialog = "/WF_UI_extremaLinePoint.ui"
m_dialog_title = "Define location(s)."
m_exception_msg = """
Unable to create Extrema Line Point(s) :
- Select one or several Line/Edge(s) and/or
- Select one Plane/Face to process all (4) Edges and/or
- Select one Object to process all Edges at once !

Go to Parameter(s) Window in Task Panel!"""
m_result_msg = " : Extrema Line Point(s) created !"
m_menu_text = "Point(s) = Extrema(Line) "
m_accel = ""
m_tool_tip = """<b>Create Point(s)</b> at Start and End location<br>
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
m_macro = "Macro ExtremaLinePoint"
m_location = "Both ends"
m_locationList = ["Begin", "End", "Both ends"]
###############


class ExtremaLinePointPanel:
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(path_WF_ui + m_dialog)
        self.form.setWindowTitle(m_dialog_title)

        self.form.UI_ExtremaLinePoint_comboBox.setCurrentIndex(self.form.UI_ExtremaLinePoint_comboBox.findText(m_location))

    def accept(self):
        global m_location
        m_location = self.form.UI_ExtremaLinePoint_comboBox.currentText()

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


def makeExtremaLinePointFeature(group):
    """ Makes a ExtremaLinePoint" parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "ExtremaLinePoint_P"
    m_part = "Part::FeaturePython"

    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        ExtremaLinePoint(m_obj)
        ViewProviderExtremaLinePoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=m_macro)
        return None

    return m_obj


class ExtremaLinePoint(WF_Point):
    """ The ExtremaLinePoint feature object. """
    # this method is mandatory
    def __init__(self, selfobj):
        if m_debug:
            print("running ExtremaLinePoint.__init__ !")

        self.name = "ExtremaLinePoint"
        WF_Point.__init__(self, selfobj, self.name)
        # Add some custom properties to our CenterLinePoint feature object.
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
        if (sys.version_info > (3, 0)):
            # Python 3 code in this block
            selfobj.At = [v.encode('utf8').decode('utf-8') for v in m_locationList]
            selfobj.At = 'Both ends'.encode('utf8').decode('utf-8')
        else:
            # Python 2 code in this block
            selfobj.At = [v.encode('utf8') for v in m_locationList]
            selfobj.At = 'Both ends'.encode('utf8')

        selfobj.setEditorMode("Edge", 1)

        selfobj.Proxy = self

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        if m_debug:
            print("running ExtremaLinePoint.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        if WF.verbose():
            m_msg = "Recompute Python ExtremaLinePoint feature\n"
            App.Console.PrintMessage(m_msg)

        m_PropertiesList = ['Edge',
                            'At',
                            ]
        for m_Property in m_PropertiesList:
            if m_Property not in selfobj.PropertiesList:
                return

        try:
            Vector_point = None
            n = eval(selfobj.Edge[1][0].lstrip('Edge'))
            if m_debug:
                print_msg(str(selfobj.Edge))
                print_msg("n = " + str(n))
                print_msg(str(selfobj.Edge[0].Shape.Edges))

            if len(selfobj.Edge[0].Shape.Edges) == 0:
                    return

            if selfobj.At == "Begin":
                Vector_point = selfobj.Edge[0].Shape.Edges[n - 1].Vertexes[0].Point
            else:
                Vector_point = selfobj.Edge[0].Shape.Edges[n - 1].Vertexes[-1].Point

            if Vector_point is not None:
                point = Part.Point(Vector_point)
                selfobj.Shape = point.toShape()
                propertiesPoint(selfobj.Label, self.color)
                selfobj.X = float(Vector_point.x)
                selfobj.Y = float(Vector_point.y)
                selfobj.Z = float(Vector_point.z)
                # To be compatible with previous version 2018
                if 'Parametric' in selfobj.PropertiesList:
                    self.created = True
        except Exception as err:
            printError_msg(err.args[0], title=m_macro)

    def onChanged(self, selfobj, prop):
        if WF.verbose() != 0:
            App.Console.PrintMessage("Change property: " + str(prop) + "\n")

        if m_debug:
            print("running CenterLinePoint.onChanged !")

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
    global path_WF_icons
    icon = "/WF_extremaLinePoint.svg"

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
        return (path_WF_icons + ViewProviderExtremaLinePoint.icon)

    def setIcon(self, icon='/WF_extremaLinePoint.svg'):
        ViewProviderExtremaLinePoint.icon = icon


class CommandExtremaLinePoint:
    """ Command to create ExtremaLinePoint feature object. """
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel': m_accel,
                'ToolTip': m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            if len(Gui.Selection.getSelectionEx(m_actDoc.Name)) == 0:
                Gui.Control.showDialog(ExtremaLinePointPanel())

        run()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("ExtremaLinePoint", CommandExtremaLinePoint())


def run():
    m_sel, m_actDoc = getSel(WF.verbose())

    try:
        Number_of_Edges, Edge_List = m_sel.get_segmentsNames(
            getfrom=["Segments",
                     "Curves",
                     "Planes",
                     "Objects"])
        if WF.verbose():
            print_msg("Number_of_Edges = " + str(Number_of_Edges))
            print_msg("Edge_List = " + str(Edge_List))

        if Number_of_Edges == 0:
            raise Exception(m_exception_msg)
        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set001"
            m_group = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            # Create a sub group if needed
            if Number_of_Edges > 1 or m_location == "Both ends":
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_actDoc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=m_macro)
                    printError_msg(m_error_msg)

            if WF.verbose():
                print_msg("Group = " + str(m_group.Label))

            for i in range(Number_of_Edges):
                edge = Edge_List[i]

                if WF.verbose():
                    print_msg("Location = " + str(m_location))

                if m_location in ["Begin", "Both ends"]:
                    App.ActiveDocument.openTransaction(m_macro)
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
                if m_location in ["End", "Both ends"]:
                    App.ActiveDocument.openTransaction(m_macro)
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
            printError_msg(err.args[0], title=m_macro)

        App.ActiveDocument.commitTransaction()

    except Exception as err:
        printError_msg(err.args[0], title=m_macro)


if __name__ == '__main__':
    run()
