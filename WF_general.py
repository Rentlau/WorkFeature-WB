# -*- coding: utf-8 -*-
import sys
import os.path
import FreeCAD as App
from PySide import QtGui, QtCore
import WF
if App.GuiUp:
    import FreeCADGui as Gui

__title__ = "Macro xxxx"
__author__ = "Rentlau_64"
__brief__ = '''

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
    from WF_selection import Selection
    from WF_print import printError_msg, print_msg
except ImportError:
    print("ERROR: cannot load WF modules !")
    sys.exit(1)

###############
M_ICON_NAME_refresh = "WF_refresh.svg"
M_DIALOG_refresh = ""
M_DIALOG_TITLE_refresh = ""
M_EXCEPTION_MSG_refresh = """
Unable to Update parametric Objects !
"""
M_RESULT_MSG_refresh = ""
M_MENU_TEXT_refresh = "Update parametric Objects"
M_ACCEL_refresh = ""
M_TOOL_TIP_refresh = """Click to force the update
of all Interactive parametric Objects !
"""


class Refresh():
    # this method is mandatory
    def __init__(self):
        self.name = "Update"


class ViewProviderRefresh:
    global PATH_WF_ICONS
    icon = M_ICON_NAME_refresh

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

    def setIcon(self, icon=M_ICON_NAME_refresh):
        self.icon = icon


class CommandRefresh:
    def GetResources(self):
        return {'Pixmap': os.path.join(PATH_WF_ICONS, M_ICON_NAME_refresh),
                'MenuText': M_MENU_TEXT_refresh,
                'Accel': M_ACCEL_refresh,
                'ToolTip': M_TOOL_TIP_refresh}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_act_doc.Name)
            if len(m_selEx) != 0 and WF.verbose():
                print_msg(str(m_selEx))
            run_refresh()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


###############
M_ICON_NAME_showhidedynamic = "WF_showHideDynamic.svg"
M_DIALOG_showhidedynamic = ""
M_DIALOG_TITLE_showhidedynamic = ""
M_EXCEPTION_MSG_showhidedynamic = """
Unable to Hide/Show Dynamic parametric Objects !
"""
M_RESULT_MSG_showhidedynamic = ""
M_MENU_TEXT_showhidedynamic = "Hide/Show Dynamic parametric Objects"
M_ACCEL_showhidedynamic = ""
M_TOOL_TIP_showhidedynamic = """Click to Hide/Show all Dynamic
parametric Objects !
"""


class ShowHideDynamic():
    # this method is mandatory
    def __init__(self):
        self.name = "ShowHideDynamic"


class ViewProviderShowHideDynamic:
    global PATH_WF_ICONS
    icon = M_ICON_NAME_showhidedynamic

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

    def setIcon(self, icon=M_ICON_NAME_showhidedynamic):
        self.icon = icon


class CommandShowHideDynamic:
    def GetResources(self):
        return {'Pixmap': os.path.join(PATH_WF_ICONS, M_ICON_NAME_showhidedynamic),
                'MenuText': M_MENU_TEXT_showhidedynamic,
                'Accel': M_ACCEL_showhidedynamic,
                'ToolTip': M_TOOL_TIP_showhidedynamic}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_act_doc.Name)
            if len(m_selEx) != 0 and WF.verbose():
                print_msg(str(m_selEx))
            run_showhide('Dynamic')

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


###############
M_ICON_NAME_showhideinteractive = "WF_showHideInteractive.svg"
M_DIALOG_showhideinteractive = ""
M_DIALOG_TITLE_showhideinteractive = ""
M_EXCEPTION_MSG_showhideinteractive = """
Unable to Hide/Show Interactive parametric Objects !
"""
M_RESULT_MSG_showhideinteractive = ""
M_MENU_TEXT_showhideinteractive = "Hide/Show Interactive parametric Objects"
M_ACCEL_showhideinteractive = ""
M_TOOL_TIP_showhideinteractive = """Click to Hide/Show all Interactive
parametric Objects !
"""


class ShowHideInteractive():
    # this method is mandatory
    def __init__(self):
        self.name = "ShowHideInteractive"


class ViewProviderShowHideInteractive:
    global PATH_WF_ICONS
    icon = M_ICON_NAME_showhideinteractive

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

    def setIcon(self, icon=M_ICON_NAME_showhideinteractive):
        self.icon = icon


class CommandShowHideInteractive:
    def GetResources(self):
        return {'Pixmap': os.path.join(PATH_WF_ICONS, M_ICON_NAME_showhideinteractive),
                'MenuText': M_MENU_TEXT_showhideinteractive,
                'Accel': M_ACCEL_showhideinteractive,
                'ToolTip': M_TOOL_TIP_showhideinteractive}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_act_doc.Name)
            if len(m_selEx) != 0 and WF.verbose():
                print_msg(str(m_selEx))
            run_showhide('Interactive')

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


###############
M_ICON_NAME_showhideno = "WF_showHideNot.svg"
M_DIALOG_showhideno = ""
M_DIALOG_TITLE_showhideno = ""
M_EXCEPTION_MSG_showhideno = """
Unable to Hide/Show Interactive parametric Objects !
"""
M_RESULT_MSG_showhideno = ""
M_MENU_TEXT_showhideno = "Hide/Show Interactive parametric Objects"
M_ACCEL_showhideno = ""
M_TOOL_TIP_showhideno = """Click to Hide/Show all Not
parametric Objects !
"""


class ShowHideNo():
    # this method is mandatory
    def __init__(self):
        self.name = "ShowHideNo"


class ViewProviderShowHideNo:
    global PATH_WF_ICONS
    icon = M_ICON_NAME_showhideno

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

    def setIcon(self, icon=M_ICON_NAME_showhideno):
        self.icon = icon


class CommandShowHideNot:
    def GetResources(self):
        return {'Pixmap': os.path.join(PATH_WF_ICONS, M_ICON_NAME_showhideno),
                'MenuText': M_MENU_TEXT_showhideno,
                'Accel': M_ACCEL_showhideno,
                'ToolTip': M_TOOL_TIP_showhideno}

    def Activated(self):
        m_act_doc = App.activeDocument()
        if m_act_doc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_act_doc.Name)
            if len(m_selEx) != 0 and WF.verbose():
                print_msg(str(m_selEx))
            run_showhide('Not')

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


if App.GuiUp:
    Gui.addCommand("ShowHideDynamic", CommandShowHideDynamic())
    Gui.addCommand("ShowHideInteractive", CommandShowHideInteractive())
    Gui.addCommand("ShowHideNo", CommandShowHideNot())
    Gui.addCommand("Refresh", CommandRefresh())


def run_refresh():
    for obj in App.ActiveDocument.Objects:
        # print str(obj.Name)
        # print obj.PropertiesList
        if "Parametric" in obj.PropertiesList:
            if WF.verbose():
                print(str(obj.Name))
                print(str(obj.Parametric))
            if str(obj.Parametric) == 'Interactive':
                obj.Parametric = 'Dynamic'
                obj.touch()
                obj.Parametric = 'Interactive'

    if WF.verbose():
        print_msg("Update done !")


def run_showhide(parametric='Dynamic'):
    for obj in App.ActiveDocument.Objects:
        # print str(obj.Name)
        # print obj.PropertiesList
        if "Parametric" in obj.PropertiesList:
            if WF.verbose():
                print(str(obj.Name))
                print(str(obj.Parametric))
            if str(obj.Parametric) == parametric:
                obj.ViewObject.Visibility = not obj.ViewObject.Visibility

    if WF.verbose():
        print_msg("Show/Hide done !")


if __name__ == '__main__':
    run_refresh()
