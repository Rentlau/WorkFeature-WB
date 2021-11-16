# -*- coding: utf-8 -*-
import os.path
from WF_config import PATH_WF_ICONS
import FreeCAD as App
from WF_gui import raiseComboView
if App.GuiUp:
    import FreeCADGui as Gui


class Command:
    """ Command to create WF  object. """

    def __init__(self,
                 icon_file,
                 menu_test,
                 accel,
                 tool_tip,
                 panel,
                 command
                 ):
        self.icon = icon_file
        self.menu_text = menu_test
        self.accel = accel
        self.tool_tip = tool_tip
        self.panel = panel
        self.run = command
        self.active = False

    def GetResources(self):
        return {'Pixmap': os.path.join(PATH_WF_ICONS, self.icon),
                'MenuText': self.menu_text,
                'Accel': self.accel,
                'ToolTip': self.tool_tip}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            if len(Gui.Selection.getSelectionEx(m_act_doc.Name)) == 0:
                try:
                    Gui.Control.showDialog(self.panel())
                    raiseComboView()
                except Exception as err:
                    App.Console.PrintError(
                        "ERROR: Not able to launch a QT dialog !\n")
        self.run()

    def IsActive(self):
        if App.ActiveDocument:
            self.active = True
        else:
            self.active = False
        return self.active
