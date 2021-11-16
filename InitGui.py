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

# FreeCAD init script of the Work Features module
import os
import sys
import WF
import FreeCAD as App
import FreeCADGui as Gui
from _version import __version__

__title__ = "WorkFeature  workbench"
__author__ = "Rentlau_64"
__url__ = "https://github.com/Rentlau/WorkFeature-WB.git"
###############
M_DEBUG = False
###############
global WF_Release
WF_Release = __version__

# get the path of the current python script
PATH_WF = os.path.dirname(WF.__file__)

global PATH_WF_ICONS
global PATH_WF_UTILS
global PATH_WF_RESOURCES
global PATH_WF_UI

PATH_WF_ICONS = os.path.join(PATH_WF, 'Resources', 'Icons')
PATH_WF_UTILS = os.path.join(PATH_WF, 'Utils')
PATH_WF_RESOURCES = os.path.join(PATH_WF, 'Resources')
PATH_WF_UI = os.path.join(PATH_WF, 'Resources', 'Ui')

if not sys.path.__contains__(str(PATH_WF_UTILS)):
    sys.path.append(str(PATH_WF_UTILS))
    sys.path.append(str(PATH_WF_UI))

if M_DEBUG:
    print("DEBUG : PATH_WF           is " + str(PATH_WF))
    print("DEBUG : PATH_WF_ICONS     is " + str(PATH_WF_ICONS))
    print("DEBUG : PATH_WF_UTILS     is " + str(PATH_WF_UTILS))
    print("DEBUG : PATH_WF_RESOURCES is " + str(PATH_WF_RESOURCES))
    print("DEBUG : PATH_WF_UI        is " + str(PATH_WF_UI))


class WorkFeatureWorkbench(Workbench):
    """ WorkFeature workbench object
    """
    global PATH_WF_ICONS
    global PATH_WF_UI
    global M_DEBUG

    def __init__(self):
        self.__class__.Icon = os.path.join(PATH_WF_ICONS, "WF_wf16x16.svg")
        self.__class__.MenuText = "WorkFeature"
        m_tooltip = "WorkFeature workbench (allowing parametric objects)"
        self.__class__.ToolTip = m_tooltip
        self.General_menu = None
        self.General_commands_list = None
        self.Point_menu = None
        self.Point_commands_list = None
        self.m_Line_menu = None
        self.m_Line_commands_list = None
        self.m_Plane_menu = None
        self.m_Plane_commands_list = None

    def Initialize(self):
        """ Run at start of FreeCAD.
        """
        import WF
        try:
            import WF_general
            import WF_centerLinePoint
            import WF_extremaLinePoint
            import WF_alongLinePoint
            import WF_nPointsPoint
            # import WF_centerCirclePoint
            import WF_centerFacePoint
            import WF_projectedPoint
            # import WF_pointFacePoint
            # import WF_lineFacePoint

            import WF_twoPointsLine
            import WF_nPointsLine

            import WF_threePointsPlane
            import WF_linePointPlane
            # import WF_perpendicularLinePointPlane
        except ImportError:
            m_error = "Error: One of WF_ module not found,"
            m_error += "WorkFeature workbench will be disabled.\n"
            App.Console.PrintWarning(m_error)
            m_error = "Error: Unknown error while trying"
            m_error += "to load one of WF_ module !\n"
            App.Console.PrintWarning(m_error)

        # Set menu and commands for Points
        self.General_menu = ["Work Feature",
                             "General"]
        self.General_commands_list = ["ShowHideDynamic",
                                      "ShowHideInteractive",
                                      "ShowHideNo",
                                      "Refresh",
                                      ]
        self.appendCommandbar("General", self.General_commands_list)
        self.appendMenu(self.General_menu, self.General_commands_list)
        self.appendToolbar("WF General", self.General_commands_list)

        # Set menu and commands for Points
        self.Point_menu = ["Work Feature",
                           "Points"]
        self.Point_commands_list = ["CenterLinePoint",  # done but to test
                                    "ExtremaLinePoint",  # done but to test
                                    "AlongLinePoint",  # done but to test
                                    "NPointsPoint",  # done but to test
                                    # "CenterCirclePoint",
                                    "CenterFacePoint",
                                    # "PointFacePoint",
                                    # "LineFacePoint",
                                    "ProjectedPoint"
                                    ]
        self.appendCommandbar("Points", self.Point_commands_list)
        self.appendMenu(self.Point_menu, self.Point_commands_list)
        self.appendToolbar("WF Points", self.Point_commands_list)

        # Set menu and commands for Lines
        self.m_Line_menu = ["Work Feature",
                            "Lines"]
        self.m_Line_commands_list = ["TwoPointsLine",  # done but to test
                                     "NPointsLine",  # done but to test
                                     ]
        self.appendCommandbar("Lines", self.m_Line_commands_list)
        self.appendMenu(self.m_Line_menu, self.m_Line_commands_list)
        self.appendToolbar("WF Lines", self.m_Line_commands_list)

        # Set menu and commands for Planes
        self.m_Plane_menu = ["Work Feature",
                             "Planes"]
        self.m_Plane_commands_list = ["ThreePointsPlane",   # done but to test
                                      "LinePointPlane",  # done but to test
                                      # "PerpendicularLinePointPlane",
                                      ]
        self.appendCommandbar("Planes", self.m_Plane_commands_list)
        self.appendMenu(self.m_Plane_menu, self.m_Plane_commands_list)
        self.appendToolbar("WF Planes", self.m_Plane_commands_list)

        # m_submenu = ['WorkFeature.pdf']
        # self.appendMenu(["Work Feature", "Help"], m_submenu)

        Gui.addIconPath(PATH_WF_ICONS)
        Gui.addResourcePath(PATH_WF_ICONS)
        Gui.addPreferencePage(PATH_WF_UI + "/WorkFeature_prefs.ui",
                              "Work Feature")

        WF.set_release(WF_Release)
        Log('Loading WorkFeature workbench...done\n')
        if M_DEBUG:
            print("DEBUG : WF_Release is " + str(WF_Release))

    def Activated(self):
        """ Run when the workbench is activated.
        """
        # do something here if needed...
        m_msg = "WorkFeature workbench loaded !"
        App.Console.PrintMessage(m_msg + "\n")
        m_msg = "WorkFeature Release is : {0:s}".format(str(WF_Release))
        App.Console.PrintMessage(m_msg + "\n")

    def Deactivated(self):
        """ Run when the workbench is deactivated.
        """
        # do something here if needed...
        m_msg = "WorkFeature workbench Deactivated !"
        App.Console.PrintMessage(m_msg + "\n")

    def ContextMenu(self, recipient):
        """ Define contextual menu.
        """
        if (recipient == "View"):
            self.appendContextMenu("Points", self.Point_list)
#             if (App.activeDraftCommand == None):
#                 if (Gui.Selection.getSelection()):
#                     self.appendContextMenu("Draft",self.cmdList+self.modList)
#                     self.appendContextMenu("Utilities",self.treecmdList)
#                 else:
#                     self.appendContextMenu("Draft",self.cmdList)
#             else:
#                 if (App.activeDraftCommand.featureName == "Line"):
#                     self.appendContextMenu("",self.lineList)
#         else:
#             if (Gui.Selection.getSelection()):
#                 self.appendContextMenu("Utilities",self.treecmdList)

    def GetClassName(self):
        """ Return the class name.
        """
        return "Gui::PythonWorkbench"


Gui.addWorkbench(WorkFeatureWorkbench)

if __name__ == '__main__':
    pass
