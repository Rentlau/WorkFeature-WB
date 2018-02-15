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
__title__  = "WorkFeature  workbench"
__author__ = "Rentlau_64"
__url__    = "https://github.com/Rentlau/WorkFeature-WB.git"
import sys
import os.path

import FreeCAD
from PySide import QtCore, QtGui

# get the path of the current python script 
path_WF = os.path.dirname(__file__)

path_WF_icons     = os.path.join(path_WF, 'Resources', 'Icons')
path_WF_utils     = os.path.join(path_WF, 'Utils')
path_WF_resources = os.path.join(path_WF, 'Resources')
path_WF_ui        = os.path.join(path_WF, 'Resources', 'Ui')

if not sys.path.__contains__(str(path_WF_utils)):
    sys.path.append(str(path_WF_utils))
    sys.path.append(str(path_WF_ui))
    
# try:
#     from WF_selection import Selection
#     from WF_print import printError_msg, print_msg
#     
#     from WF_geometry import *
#     #from WF_utils import *
# 
# except:
#     print "ERROR: cannot load WF modules !!"
#     sys.exit(1)

# def gui_infoDialog(msg):
#     """ Create a simple QMessageBox dialog for info messages.
#     """
#     # The first argument indicates the icon used:
#     # one of QtGui.QMessageBox.{NoIcon,Information,Warning Critical,Question}
#     diag = QtGui.QMessageBox(QtGui.QMessageBox.Information,'Info :', msg)
#     diag.setWindowModality(QtCore.Qt.ApplicationModal)
#     diag.exec_()
#     
# def gui_errorDialog(msg):
#     """ Create a simple QMessageBox dialog for error messages.
#     """
#     m_script = os.path.basename(os.path.realpath(__file__))
#     # The first argument indicates the icon used:
#     # one of QtGui.QMessageBox.{NoIcon,Information,Warning Critical,Question}
#     diag = QtGui.QMessageBox(QtGui.QMessageBox.Warning,'Error in ' +
#       str(m_script), msg)
#     diag.setWindowModality(QtCore.Qt.ApplicationModal)
#     diag.exec_()
#     
# def print_msg(message):
#     """ Print a message on console.
#     """
#     print message
#     FreeCAD.Console.PrintMessage( message + "\n")
#     
# def print_gui_msg(message):
#     """ Print a message on console.
#     """
#     print message
#     FreeCAD.Console.PrintMessage( message + "\n")
#     try :
#         gui_infoDialog(message)
#     except:
#         FreeCAD.Console.PrintError("\nERROR : Not able to launch a QT dialog !" )
#         raise(Exception(message))

def typecheck (args_and_types, name="?"):
    """ Checks arguments types.
    
    typecheck([arg1,type),(arg2,type),...])
    """
    for v,t in args_and_types:
        if not isinstance (v,t):
            w = "typecheck[" + str(name) + "]: "
            w += str(v) + " is not " + str(t) + "\n"
            FreeCAD.Console.PrintWarning(w)
            raise TypeError("WF." + str(name))

def getParamType(param):
#     if param in ["dimsymbol","dimPrecision","dimorientation","precision","defaultWP",
#                  "snapRange","gridEvery","linewidth","UiMode","modconstrain","modsnap",
#                  "maxSnapEdges","modalt","HatchPatternResolution","snapStyle",
#                  "dimstyle","gridSize"]:
#         return "int"
#     elif param in ["constructiongroupname","textfont","patternFile","template",
#                    "snapModes","FontFile","ClonePrefix"]:
#         return "string"
#     elif param in ["textheight","tolerance","gridSpacing","arrowsize","extlines","dimspacing"]:
#         return "float"
#     elif param in ["selectBaseObjects","alwaysSnap","grid","fillmode","saveonexit","maxSnap",
#                    "SvgLinesBlack","dxfStdSize","showSnapBar","hideSnapBar","alwaysShowGrid",
#                    "renderPolylineWidth","showPlaneTracker","UsePartPrimitives","DiscretizeEllipses",
#                    "showUnit"]:
#         return "bool"
#     elif param in ["color","constructioncolor","snapcolor"]:
#         return "unsigned"
    if param in ["verbose",]:
        return "bool"
    elif param in ["release",]:
        return "string"
    elif param in ["parametric",]:
        return "int"
    else:
        return None
    
def getParam(param,default=None):
    """ Returns a WorkFeature parameter value from the current config.
    """
    p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/WF")
    t = getParamType(param)
    #print("getting param ",param, " of type ",t, " default: ",str(default))
    if t == "int":
        if default == None:
            default = 0
        return p.GetInt(param,default)
    elif t == "string":
        if default == None:
            default = ""
        return p.GetString(param,default)
    elif t == "float":
        if default == None:
            default = 0
        return p.GetFloat(param,default)
    elif t == "bool":
        if default == None:
            default = False
        return p.GetBool(param,default)
    elif t == "unsigned":
        if default == None:
            default = 0
        return p.GetUnsigned(param,default)
    else:
        return None
    
def setParam(param,value):
    """ Sets a WorkFeature parameter value with the given value.
    """
    p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/WF")
    t = getParamType(param)
    if   t == "int":      p.SetInt(param,value)
    elif t == "string":   p.SetString(param,value)
    elif t == "float":    p.SetFloat(param,value)
    elif t == "bool":     p.SetBool(param,value)
    elif t == "unsigned": p.SetUnsigned(param,value)

def verbose():
    """ Returns the verbose value from WF user settings
    """
    return getParam("verbose",False)

def release():
    """ Returns the release value from WF user settings
    """
    return getParam("release",None)

def set_release(value):    
    """ Sets the release value to WF user settings
    """
    setParam("release",value)
    
def parametric():
    """ Returns the parametric index from WF user settings
    
    m_parametric = ['No','Interactive','Dynamic']  
    """    
    return getParam("parametric",None)

def set_parametric(value):    
    """ Sets the parametric index to WF user settings
    """
    setParam("parametric",value)
    
    
