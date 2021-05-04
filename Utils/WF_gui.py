# -*- coding: utf-8 -*-
from PySide import QtGui
import FreeCAD as App
if App.GuiUp:
    import FreeCADGui as Gui


def raiseComboView():
    """ Raise up the Combo View of FreeCAD Gui
    """
    mw = Gui.getMainWindow()
    dws = mw.findChildren(QtGui.QDockWidget)
    # objectName may be :
    # "Report view"
    # "Tree view"
    # "Property view"
    # "Selection view"
    # "Combo View"
    # "Python console"
    # "draftToolbar"
    for i in dws:
        if i.objectName() == "Combo View":
            dw = i
            break
    # va = dw.toggleViewAction()
    # va.setChecked(True)        # True or False
    dw.raise_()
    dw.setVisible(True)        # True or False
