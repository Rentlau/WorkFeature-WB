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
# from InitGui import M_DEBUG
if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro CenterFacePoint"
__author__ = "Rentlau_64"
__brief__ = '''
Macro CenterFacePoint.
Creates a parametric CenterFacePoint from a  Plane
'''
###############
M_DEBUG = False
###############

# get the path of the current python script
path_WF = os.path.dirname(__file__)

PATH_WF_ICONS = os.path.join(path_WF, 'Resources', 'Icons')
PATH_WF_UTILS = os.path.join(path_WF, 'Utils')
path_WF_resources = os.path.join(path_WF, 'Resources')
PATH_WF_UI = os.path.join(path_WF, 'Resources', 'Ui')

if not sys.path.__contains__(str(PATH_WF_UTILS)):
    sys.path.append(str(PATH_WF_UTILS))
    sys.path.append(str(PATH_WF_UI))

try:
    from WF_selection import Selection, getSel
    from WF_print import printError_msg, print_msg
    from WF_directory import createFolders, addObjectToGrp
    from WF_geometry import *
except ImportError:
    print("ERROR: Cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME = "WF_centerFacePoint.svg"
M_DIALOG = "WF_UI_centerFacePoint.ui"
M_DIALOG_TITLE = "centerFacePoint Dialog"
M_EXCEPTION_MSG = """
Unable to create Center Face Point(s) :
- Select one or several Plane/Face(s) and/or
- Select one or several Object(s) to process all FAces at once;

and go to Parameter(s) Window in Task Panel!"""
M_RESULT_MSG = " : Center Face Point(s) created !"
M_MENU_TEXT = "Point = center(Plane)"
M_ACCEL = ""
M_TOOL_TIP = """<b>Create Point(s)</b> at Center of mass location
of each selected Face(s).<br>
<br>
- Select one or several Plane/Face(s) to process and/or<br>
- Select one or several Object(s) to process all Faces at once<br>
- Then Click on the Button/Icon<br>
<br>
<i>Click in view window without selection will popup<br>
 - a Warning Window !</i>
"""
###############
M_MACRO = "Macro CenterFacePoint"
###############


class CenterFacePointPanel:
    def __init__(self):
        self.form = Gui.PySideUic.loadUi(os.path.join(PATH_WF_UI, M_DIALOG))
        self.form.setWindowTitle(M_DIALOG_TITLE)

    def accept(self):
        Gui.Control.closeDialog()
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if len(Gui.Selection.getSelectionEx(m_act_doc.Name)) != 0:
                run()
        return True

    def reject(self):
        Gui.Control.closeDialog()
        return False

    def shouldShow(self):
        return (len(Gui.Selection.getSelectionEx(App.activeDocument().Name)) == 0)


def makeCenterFacePointFeature(group):
    """ Makes a CenterFacePoint parametric feature object.
    into the given Group
    Returns the new object.
    """
    m_name = "CenterFacePoint_P"
    m_part = "Part::FeaturePython"

    try:
        m_obj = App.ActiveDocument.addObject(str(m_part), str(m_name))
        if group is not None:
            addObjectToGrp(m_obj, group, info=1)
        CenterFacePoint(m_obj)
        ViewProviderCenterFacePoint(m_obj.ViewObject)
    except Exception as err:
        printError_msg("Not able to add an object to Model!")
        printError_msg(err.args[0], title=M_MACRO)
        return None

    return m_obj


class CenterFacePoint(WF_Point):
    """ The CenterFacePoint feature object. """
    # this method is mandatory
    def __init__(self, selfobj):
        if M_DEBUG:
            print("running CenterFacePoint.__init__ !")

        self.name = "CenterFacePoint"
        WF_Point.__init__(self, selfobj, self.name)
        """ Add some custom properties to our CenterFacePoint feature object. """
        selfobj.addProperty("App::PropertyLinkSub",
                            "Face",
                            self.name,
                            "Input face")

        selfobj.setEditorMode("Face", 1)
        selfobj.Proxy = self

    # this method is mandatory
    def execute(self, selfobj):
        """ Doing a recomputation.
        """
        if M_DEBUG:
            print("running CenterFacePoint.execute !")

        # To be compatible with previous version > 2019
        if 'Parametric' in selfobj.PropertiesList:
            # Create the object the first time regardless
            # the parametric behavior
            if selfobj.Parametric == 'Not' and self.created:
                return
            if selfobj.Parametric == 'Interactive' and self.created:
                return

        if WF.verbose():
            m_msg = "Recompute Python CenterFacePoint feature\n"
            App.Console.PrintMessage(m_msg)

        m_properties_list = ['Face',
                            ]
        for m_property in m_properties_list:
            if m_property not in selfobj.PropertiesList:
                return

        try:
            Vector_point = None
            if selfobj.Face is not None:
                n = eval(selfobj.Face[1][0].lstrip('Face'))
                if M_DEBUG:
                    print_msg(str(selfobj.Face))
                    print_msg("n = " + str(n))

                m_face = selfobj.Face[0].Shape.Faces[n - 1]

                if M_DEBUG:
                    print_msg("m_face = " + str(m_face))

                Vector_point = m_face.CenterOfMass

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
            printError_msg(err.args[0], title=M_MACRO)

    def onChanged(self, selfobj, prop):
        if WF.verbose():
            App.Console.PrintMessage("Change property : " + str(prop) + "\n")

        if M_DEBUG:
            print("running CenterFacePoint.onChanged !")

        WF_Point.onChanged(self, selfobj, prop)

        if prop == "Parametric":
            if 'Parametric' in selfobj.PropertiesList:
                if selfobj.Parametric == 'Not':
                    pass
                else:
                    pass
            propertiesPoint(selfobj.Label, self.color)


class ViewProviderCenterFacePoint:
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


class CommandCenterFacePoint:
    """ Command to create CenterFacePoint feature object. """
    def GetResources(self):
        return {'Pixmap': os.path.join(PATH_WF_ICONS, M_ICON_NAME),
                'MenuText': M_MENU_TEXT,
                'Accel': M_ACCEL,
                'ToolTip': M_TOOL_TIP}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if len(Gui.Selection.getSelectionEx(m_act_doc.Name)) == 0:
                Gui.Control.showDialog(CenterFacePointPanel())

        run()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("CenterFacePoint", CommandCenterFacePoint())


def run():
    m_sel, m_act_doc = getSel(WF.verbose())

    try:
        Number_of_Planes, Plane_List = m_sel.get_planesNames(
            getfrom=["Planes",
                     "Objects"])
        if WF.verbose():
            print_msg("Number_of_Planes = " + str(Number_of_Planes))
            print_msg("Plane_List = " + str(Plane_List))

        if Number_of_Planes == 0:
            raise Exception(M_EXCEPTION_MSG)
        try:
            m_main_dir = "WorkPoints_P"
            m_sub_dir = "Set001"
            m_group = createFolders(str(m_main_dir))
            m_error_msg = "Could not Create '"
            m_error_msg += str(m_sub_dir) + "' Objects Group!"

            # Create a sub group if needed
            if Number_of_Planes > 1:
                try:
                    m_ob = App.ActiveDocument.getObject(str(m_main_dir)).newObject("App::DocumentObjectGroup", str(m_sub_dir))
                    m_group = m_act_doc.getObject(str(m_ob.Label))
                except Exception as err:
                    printError_msg(err.args[0], title=M_MACRO)
                    printError_msg(m_error_msg)

            if WF.verbose():
                print_msg("Group = " + str(m_group.Label))

            for i in range(Number_of_Planes):
                plane = Plane_List[i]
                App.ActiveDocument.openTransaction(M_MACRO)
                selfobj = makeCenterFacePointFeature(m_group)
                selfobj.Face = plane
                selfobj.Proxy.execute(selfobj)

        except Exception as err:
            printError_msg(err.args[0], title=M_MACRO)

        App.ActiveDocument.commitTransaction()

    except Exception as err:
        printError_msg(err.args[0], title=M_MACRO)


if __name__ == '__main__':
    run()
