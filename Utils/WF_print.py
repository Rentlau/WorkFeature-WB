# -*- coding: utf-8 -*-
import os
import inspect
import FreeCAD as App
from PySide import QtCore, QtGui

error_msg_not_yet = "Not yet Developped !"


def gui_infoDialog(msg, title=None):
    """ Create a simple QMessageBox dialog for info messages.
    """
    # The first argument indicates the icon used:
    # one of QtGui.QMessageBox.{NoIcon,Information,Warning Critical,Question}
    diag = QtGui.QMessageBox(QtGui.QMessageBox.Information,
                             'Info :',
                             msg)
    diag.setWindowModality(QtCore.Qt.ApplicationModal)
    if title is not None:
        diag.setWindowTitle(str(title))
    diag.exec_()


def gui_errorDialog(msg, title=None):
    """ Create a simple QMessageBox dialog for error messages.
    """
    m_script = os.path.basename(os.path.realpath(__file__))
    # The first argument indicates the icon used:
    # one of QtGui.QMessageBox.{NoIcon,Information,Warning Critical,Question}
    diag = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                             'Error in ' + str(m_script),
                             msg)
    diag.setWindowModality(QtCore.Qt.ApplicationModal)
    if title is not None:
        diag.setWindowTitle(str(title))
    diag.exec_()


def print_msg(message):
    """ Print a message on console.
    """
    App.Console.PrintMessage(message + "\n")


def printInfo_msg(message, title=None):
    """ Print a message on console.
    """
    m_msg = message
    App.Console.PrintMessage(m_msg + "\n")
    try:
        gui_infoDialog(m_msg, title)
    except Exception as err:
        App.Console.PrintError("\nERROR : Not able to launch a QT dialog !")
        App.Console.PrintError(err.message)
        raise Exception


def printError_msg(message, title=None):
    """ Print a ERROR message on console.
    """
    m_msg = str(inspect.stack()[1][3]) + " : " + str(message)
    App.Console.PrintError(m_msg + "\n")
    try:
        gui_errorDialog(m_msg, title)
    except Exception as err:
        App.Console.PrintError("\nERROR : Not able to launch a QT dialog !")
        App.Console.PrintError(err.message)
        raise Exception


def print_not_yet():
    printError_msg(error_msg_not_yet)
