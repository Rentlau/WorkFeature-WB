# -*- coding: utf-8 -*-
from PySide import QtCore, QtGui
import os
import FreeCAD as App

def gui_infoDialog(msg, title=None):
    """ Create a simple QMessageBox dialog for info messages.
    """
    # The first argument indicates the icon used:
    # one of QtGui.QMessageBox.{NoIcon,Information,Warning Critical,Question}
    diag = QtGui.QMessageBox(QtGui.QMessageBox.Information,'Info :', msg)
    diag.setWindowModality(QtCore.Qt.ApplicationModal)
    if title != None:
        diag.setWindowTitle(str(title)) 
    diag.exec_()

def gui_errorDialog(msg, title=None):
    """ Create a simple QMessageBox dialog for error messages.
    """
    m_script = os.path.basename(os.path.realpath(__file__))
    # The first argument indicates the icon used:
    # one of QtGui.QMessageBox.{NoIcon,Information,Warning Critical,Question}
    diag = QtGui.QMessageBox(QtGui.QMessageBox.Warning,'Error in ' +
           str(m_script), msg)
    diag.setWindowModality(QtCore.Qt.ApplicationModal)
    if title != None:
        diag.setWindowTitle(str(title)) 
    diag.exec_()
    
def print_msg(message):
    """ Print a message on console.
    """
    App.Console.PrintMessage( message + "\n")
    
def printInfo_msg(message, title=None):
    """ Print a message on console.
    """
    App.Console.PrintMessage( message + "\n")
    try :
        gui_infoDialog(message, title)
    except:
        App.Console.PrintError("\nERROR : Not able to launch a QT dialog !" )
        raise(Exception(message)) 

def printError_msg(message, title=None):
    """ Print a ERROR message on console.
    """
    App.Console.PrintError( message + "\n")
    try :
        gui_errorDialog(message, title)
    except:
        App.Console.PrintError("\nERROR : Not able to launch a QT dialog !" )
        raise(Exception(message))