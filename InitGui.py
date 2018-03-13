# -*- coding: utf-8 -*-
# FreeCAD init script of the Work Features module
"""
***************************************************************************
*   FreeCAD Work Feature workbench                                        *
*                                                                         *
*   Copyright (c) 2017 <rentlau_64>                                       *
*   Code rewrite by <rentlau_64> from Work Features macro:                *
*   https://github.com/Rentlau/WorkFeature                                *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *  
*   http://www.freecadweb.org                                             *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the COPYING and COPYING.LESSER text files.             *
*   http://en.wikipedia.org/wiki/LGPL                                     *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA or see <http://www.gnu.org/licenses/>                             *
***************************************************************************
"""
__title__  = "WorkFeature  workbench"
__author__ = "Rentlau_64"
__url__    = "https://github.com/Rentlau/WorkFeature-WB.git"
###############
m_debug = False
###############

import os, sys
import WF

global WF_Release
WF_Release = "2018_03_13"

# get the path of the Release python script 
path_WF = os.path.dirname(WF.__file__)

path_WF_icons     = os.path.join(path_WF, 'Resources', 'Icons')
path_WF_utils     = os.path.join(path_WF, 'Utils')
path_WF_resources = os.path.join(path_WF, 'Resources')
path_WF_ui        = os.path.join(path_WF, 'Resources', 'Ui')

if not sys.path.__contains__(str(path_WF_utils)):
    sys.path.append(str(path_WF_utils))
    sys.path.append(str(path_WF_ui))
    
if m_debug:
    print "DEBUG : path_WF           is " +  str(path_WF)
    print "DEBUG : path_WF_icons     is " +  str(path_WF_icons)
    print "DEBUG : path_WF_utils     is " +  str(path_WF_utils)
    print "DEBUG : path_WF_resources is " +  str(path_WF_resources)
    print "DEBUG : path_WF_ui        is " +  str(path_WF_ui)     

import FreeCAD
import FreeCADGui

class WorkFeatureWorkbench ( Workbench ):
    "WorkFeature workbench object"
    global path_WF_icons
    global path_WF_ui
    
    def __init__(self):
        self.__class__.Icon = path_WF_icons + "/WF_wf16x16.svg"
        self.__class__.MenuText = "WorkFeature"
        self.__class__.ToolTip  = "WorkFeature workbench (allowing parametric objects)"
     
    def Initialize(self):
        import WF
        try:
            import WF_centerLinePoint        
            import WF_extremaLinePoint
            import WF_centerCirclePoint
            import WF_centerFacePoint
            
            import WF_twoPointsLine
            
            import WF_linePointPlane
            import WF_perpendicularLinePointPlane
        except ImportError:
            FreeCAD.Console.PrintWarning("Error: One of WF_ module not found, WorkFeature workbench will be disabled.\n")
        except:
            FreeCAD.Console.PrintWarning("Error: Unknown error while trying to load one of WF_ module !\n")
        
        # Set menu and commands for Points   
        self.Point_menu = ["Work Feature","Points"] 
        self.Point_commands_list = ["CenterLinePoint", 
                                    "ExtremaLinePoint",
                                    "CenterCirclePoint",
                                    "CenterFacePoint", 
                                    ]
        self.appendCommandbar("Points" , self.Point_commands_list)
        self.appendMenu(self.Point_menu, self.Point_commands_list)
        self.appendToolbar("WF Points" , self.Point_commands_list)
        
        # Set menu and commands for Lines   
        self.m_Line_menu = ["Work Feature","Lines"]
        self.m_Line_commands_list = ["TwoPointsLine", 
                                ]
        self.appendCommandbar("Lines"   , self.m_Line_commands_list)
        self.appendMenu(self.m_Line_menu, self.m_Line_commands_list)          
        self.appendToolbar("WF Lines"   , self.m_Line_commands_list)

        # Set menu and commands for Planes   
        self.m_Line_menu = ["Work Feature","Planes"]
        self.m_Line_commands_list = ["LinePointPlane",
                                     "PerpendicularLinePointPlane", 
                                ]
        self.appendCommandbar("Planes"   , self.m_Line_commands_list)
        self.appendMenu(self.m_Line_menu, self.m_Line_commands_list)          
        self.appendToolbar("WF Planes"   , self.m_Line_commands_list)
#         m_submenu = ['WorkFeature.pdf']
# 
#         self.appendMenu(["Work Feature", "Help"], m_submenu)
        
        FreeCADGui.addIconPath(path_WF_icons)
        FreeCADGui.addResourcePath(path_WF_icons)
        FreeCADGui.addPreferencePage(path_WF_ui + "/WorkFeature_prefs.ui","Work Feature" )
        
        WF.set_release(WF_Release)
        Log ('Loading WorkFeature workbench...done\n')

    def Activated(self):
        # do something here if needed...
        Msg ("WorkFeature workbench loaded\n")

    def Deactivated(self):
        # do something here if needed...
        Msg ("WorkFeature workbench Deactivated\n")
     
    def ContextMenu(self, recipient):
        if (recipient == "View"):
            self.appendContextMenu("Points",self.Point_list)
#             if (FreeCAD.activeDraftCommand == None):
#                 if (FreeCADGui.Selection.getSelection()):
#                     self.appendContextMenu("Draft",self.cmdList+self.modList)
#                     self.appendContextMenu("Utilities",self.treecmdList)
#                 else:
#                     self.appendContextMenu("Draft",self.cmdList)
#             else:
#                 if (FreeCAD.activeDraftCommand.featureName == "Line"):
#                     self.appendContextMenu("",self.lineList)
#         else:
#             if (FreeCADGui.Selection.getSelection()):
#                 self.appendContextMenu("Utilities",self.treecmdList)   
         
    def GetClassName(self):
        return "Gui::PythonWorkbench"
 
FreeCADGui.addWorkbench(WorkFeatureWorkbench)

if __name__ == '__main__':
    pass
