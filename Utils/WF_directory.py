# -*- coding: utf-8 -*-
import FreeCAD as App

from WF_print import printError_msg, print_msg
import WF


def addObjectToGrp(obj,
                   grp,
                   info=0):
    """ Adds an object 'obj' to the group 'grp'
    """
    grp.addObject(obj)
    if info != 0:
        m_msg = "Object " + str(obj.Label)
        m_msg += " added to Group : " + str(grp.Label)
        print_msg(m_msg)


def rmObjectFromGrp(obj,
                    grp,
                    info=0):
    """ Removes an object 'obj' from the group 'grp'
    """
    grp.removeObject(obj)
    if info != 0:
        m_msg = "Object " + str(obj.Label)
        m_msg += " removed from Group : " + str(grp.Label)
        print_msg(m_msg)


def createFolders(folder=None):
    """ Create WorkFeatures Parametric folders if needed.
    """
    m_main_dir = "WorkFeatures"
    if not(App.ActiveDocument.getObject(m_main_dir)):
        try:
            App.ActiveDocument.addObject("App::DocumentObjectGroup",
                                         m_main_dir)
        except Exception as err:
            printError_msg(err.args[0], title="createFolders")
            m_msg = "Could not Create '" + str(m_main_dir) + "' Objects Group!"
            printError_msg(m_msg)

    m_list_dirs = ['Origin_P',
                   'WorkPoints_P',
                   'WorkAxis_P',
                   'WorkPlanes_P',
                   'WorkCircles_P',
                   'WorkArcs_P',
                   'WorkBoxes_P',
                   'WorkWires_P',
                   'WorkImages_P',
                   'WorkObjects_P',
                   'Rot_Trans_P']

    m_group = None
    for m_dir in m_list_dirs:
        if folder == m_dir:
            m_group = App.ActiveDocument.getObject(m_main_dir).getObject(str(m_dir))
            if not(m_group):
                try:
                    m_group = App.ActiveDocument.getObject(m_main_dir).newObject("App::DocumentObjectGroup", str(m_dir))
                except Exception as err:
                    printError_msg(err.args[0], title="createFolders")
                    m_msg = "Could not Create '" + str(m_dir)
                    m_msg += "' Objects Group!"
                    printError_msg(m_msg)

    if WF.verbose():
        print_msg("Group = " + str(m_group.Label))

    return m_group


def createSubGroup(m_actDoc,
                   main_dir,
                   sub_dir,
                   error_msg):
    try:
        m_ob_dir = App.ActiveDocument.getObject(str(main_dir))
        m_ob = m_ob_dir.newObject("App::DocumentObjectGroup",
                                  str(sub_dir))
        m_group = m_actDoc.getObject(str(m_ob.Label))
    except Exception as err:
        printError_msg(err.args[0], title="createSubGroup")
        printError_msg(error_msg)

    if WF.verbose():
        print_msg("Group = " + str(m_group.Label))

    return m_group
