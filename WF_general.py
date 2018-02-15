# -*- coding: utf-8 -*-
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
__title__="Macro xxxx"
__author__ = "Rentlau_64"
__brief__ = '''

'''
import sys
import os.path
import FreeCAD as App
if App.GuiUp:
    import FreeCADGui as Gui
from PySide import QtGui,QtCore
import WF

# get the path of the current python script 
path_WF = os.path.dirname(__file__)
 
path_WF_icons     = os.path.join(path_WF, 'Resources', 'Icons')
path_WF_utils     = os.path.join(path_WF, 'Utils')
path_WF_resources = os.path.join(path_WF, 'Resources')
path_WF_ui        = os.path.join(path_WF, 'Resources', 'Ui')
 
if not sys.path.__contains__(str(path_WF_utils)):
    sys.path.append(str(path_WF_utils))
    sys.path.append(str(path_WF_ui))

try:
    from WF_selection import Selection
    from WF_print import printError_msg, print_msg
except:
    print "ERROR: cannot load WF modules !!"
    sys.exit(1)

###############
m_icon          = "/WF_interact.svg"
m_dialog        = ""
m_dialog_title  = ""
m_exception_msg = """Unable to Update parametric Objects !
"""
m_result_msg    = ""
m_menu_text     = "Update parametric Objects"
m_accel         = ""
m_tool_tip      = """Click to Interactive update parametric Objects
"""

class Update():
    """ The Update object. """
    # this method is mandatory
    def __init__(self):
        self.name = "Update"

class CommandUpdate:
    """ Command to create CenterLinePoint feature object. """
    def GetResources(self):
        return {'Pixmap'  : path_WF_icons + m_icon,
                'MenuText': m_menu_text,
                'Accel'   : m_accel,
                'ToolTip' : m_tool_tip}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
            if len(m_selEx) != 0:
                print_msg(str(m_selEx))
            run()
        
    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False

if App.GuiUp:
    Gui.addCommand("Update", CommandUpdate()) 

def run():
    if WF.verbose() != 0:
        print_msg("Update done !")

          
if __name__ == '__main__':
    run()        
        