# -*- coding: utf-8 -*-
import os
import inspect
import FreeCAD as App
from PySide import QtCore, QtGui
import WF

ERROR_MSG_NOT_YET = "Not yet Developed !"


class TimerMessageBox(QtGui.QMessageBox):
    def __init__(self, msg, timeout=15, parent=None):
        super(TimerMessageBox, self).__init__(parent)
        # self.setWindowTitle("wait")
        self.time_to_wait = timeout
        self.msg = msg
        m_msg = self.msg + "\n\n" + " (closing automatically in {0} secondes.)".format(timeout)
        self.setText(m_msg)
        self.setStandardButtons(QtGui.QMessageBox.Close)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

    def changeContent(self):
        self.time_to_wait -= 1
        m_msg = self.msg + "\n\n" + " (closing automatically in {0} secondes.)".format(self.time_to_wait)
        self.setText(m_msg)
        if self.time_to_wait <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


def gui_errorDialogWithTimer(msg, title=None, timeout=15):
    """ Create a QMessageBox dialog with timer for error messages.
    """
    m_script = os.path.basename(os.path.realpath(__file__))
    diag = TimerMessageBox(msg, timeout=timeout, parent=None)
    diag.setWindowModality(QtCore.Qt.ApplicationModal)
    diag.setWindowTitle('Error in ' + str(m_script))
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
        App.Console.PrintError("\nERROR: Not able to launch a QT dialog !")
        App.Console.PrintError(err.args[0])
        raise Exception


def printError_msg(message, title=None):
    """ Print a ERROR message on console.
    """
    m_msg = str(inspect.stack()[1][3]) + " : " + str(message)
    App.Console.PrintError(m_msg + "\n")
    try:
        gui_errorDialog(m_msg, title)
    except Exception as err:
        App.Console.PrintError("\nERROR: Not able to launch a QT dialog !")
        App.Console.PrintError(err.args[0])
        raise Exception


def printError_msgWithTimer(message, title=None):
    """ Print a ERROR message on console.
    """
    m_msg = str(inspect.stack()[1][3]) + " : " + str(message)
    App.Console.PrintError(m_msg + "\n")
    # recover timeout value from preferences
    timeout = WF.timeout()
    if timeout == 0:
        return
    try:
        gui_errorDialogWithTimer(m_msg, title, timeout)
    except Exception as err:
        App.Console.PrintError("\nERROR: Not able to launch a QT dialog !")
        App.Console.PrintError(err.args[0])
        raise Exception


def print_not_yet():
    """ Print for on going dev.
    """
    printError_msg(ERROR_MSG_NOT_YET)
