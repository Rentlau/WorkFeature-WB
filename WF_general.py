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
m_debug = False
###############

# get the path of the current python script
path_WF = os.path.dirname(__file__)

path_WF_icons = os.path.join(path_WF, 'Resources', 'Icons')
path_WF_utils = os.path.join(path_WF, 'Utils')
path_WF_resources = os.path.join(path_WF, 'Resources')
path_WF_ui = os.path.join(path_WF, 'Resources', 'Ui')

if not sys.path.__contains__(str(path_WF_utils)):
    sys.path.append(str(path_WF_utils))
    sys.path.append(str(path_WF_ui))

try:
    from WF_selection import Selection
    from WF_print import printError_msg, print_msg
except ImportError:
    print("ERROR: cannot load WF modules !")
    sys.exit(1)

###############
m_icon_refresh = "/WF_refresh.svg"
m_dialog_refresh = ""
m_dialog_title_refresh = ""
m_exception_msg_refresh = """
Unable to Update parametric Objects !
"""
m_result_msg_refresh = ""
m_menu_text_refresh = "Update parametric Objects"
m_accel_refresh = ""
m_tool_tip_refresh = """Click to force  update
of all Interactive parametric Objects !
"""


class Refresh():
    # this method is mandatory
    def __init__(self):
        self.name = "Update"


class ViewProviderRefresh:
    global path_WF_icons
    icon = '/WF_refresh.svg'

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
        return (path_WF_icons + ViewProviderRefresh.icon)

    def setIcon(self, icon='/WF_refresh.svg'):
        ViewProviderRefresh.icon = icon


class CommandRefresh:
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon_refresh,
                'MenuText': m_menu_text_refresh,
                'Accel': m_accel_refresh,
                'ToolTip': m_tool_tip_refresh}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
            if len(m_selEx) != 0 and WF.verbose():
                print_msg(str(m_selEx))
            run_refresh()

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


###############
m_icon_showhidedynamic = "/WF_showHideDynamic.svg"
m_dialog_showhidedynamic = ""
m_dialog_title_showhidedynamic = ""
m_exception_msg_showhidedynamic = """
Unable to Hide/Show Dynamic parametric Objects !
"""
m_result_msg_showhidedynamic = ""
m_menu_text_showhidedynamic = "Hide/Show Dynamic parametric Objects"
m_accel_showhidedynamic = ""
m_tool_tip_showhidedynamic = """Click to Hide/Show all Dynamic
parametric Objects !
"""


class ShowHideDynamic():
    # this method is mandatory
    def __init__(self):
        self.name = "ShowHideDynamic"


class ViewProviderShowHideDynamic:
    global path_WF_icons
    icon = '/WF_showHideDynamic.svg'

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
        return (path_WF_icons + ViewProviderRefresh.icon)

    def setIcon(self, icon='/WF_showHideDynamic.svg'):
        ViewProviderRefresh.icon = icon


class CommandShowHideDynamic:
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon_showhidedynamic,
                'MenuText': m_menu_text_showhidedynamic,
                'Accel': m_accel_showhidedynamic,
                'ToolTip': m_tool_tip_showhidedynamic}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
            if len(m_selEx) != 0 and WF.verbose():
                print_msg(str(m_selEx))
            run_showhide('Dynamic')

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


###############
m_icon_showhideinteractive = "/WF_showHideInteractive.svg"
m_dialog_showhideinteractive = ""
m_dialog_title_showhideinteractive = ""
m_exception_msg_showhideinteractive = """
Unable to Hide/Show Interactive parametric Objects !
"""
m_result_msg_showhideinteractive = ""
m_menu_text_showhideinteractive = "Hide/Show Interactive parametric Objects"
m_accel_showhideinteractive = ""
m_tool_tip_showhideinteractive = """Click to Hide/Show all Interactive
parametric Objects !
"""


class ShowHideInteractive():
    # this method is mandatory
    def __init__(self):
        self.name = "ShowHideInteractive"


class ViewProviderShowHideInteractive:
    global path_WF_icons
    icon = '/WF_showHideInteractive.svg'

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
        return (path_WF_icons + ViewProviderRefresh.icon)

    def setIcon(self, icon='/WF_showHideInteractive.svg'):
        ViewProviderRefresh.icon = icon


class CommandShowHideInteractive:
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon_showhideinteractive,
                'MenuText': m_menu_text_showhideinteractive,
                'Accel': m_accel_showhideinteractive,
                'ToolTip': m_tool_tip_showhideinteractive}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
            if len(m_selEx) != 0 and WF.verbose():
                print_msg(str(m_selEx))
            run_showhide('Interactive')

    def IsActive(self):
        if App.ActiveDocument:
            return True
        else:
            return False


###############
m_icon_showhideno = "/WF_showHideNot.svg"
m_dialog_showhideno = ""
m_dialog_title_showhideno = ""
m_exception_msg_showhideno = """
Unable to Hide/Show Interactive parametric Objects !
"""
m_result_msg_showhideno = ""
m_menu_text_showhideno = "Hide/Show Interactive parametric Objects"
m_accel_showhideno = ""
m_tool_tip_showhideno = """Click to Hide/Show all Interactive
parametric Objects !
"""


class ShowHideNo():
    # this method is mandatory
    def __init__(self):
        self.name = "ShowHideNo"


class ViewProviderShowHideNo:
    global path_WF_icons
    icon = '/WF_showHideNo.svg'

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
        return (path_WF_icons + ViewProviderRefresh.icon)

    def setIcon(self, icon='/WF_showHideNo.svg'):
        ViewProviderRefresh.icon = icon


class CommandShowHideNot:
    def GetResources(self):
        return {'Pixmap': path_WF_icons + m_icon_showhideno,
                'MenuText': m_menu_text_showhideno,
                'Accel': m_accel_showhideno,
                'ToolTip': m_tool_tip_showhideno}

    def Activated(self):
        m_actDoc = App.activeDocument()
        if m_actDoc is not None:
            m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
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
