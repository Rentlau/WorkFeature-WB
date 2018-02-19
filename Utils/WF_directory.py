# -*- coding: utf-8 -*-
import FreeCAD as App

from WF_print import printError_msg, print_msg

def addObjectToGrp(obj,grp,info=0):
    """ Add an object to the group
    """
    m_obj = obj
    m_grp = grp
    m_grp.addObject(m_obj) # adds object to the group
    if info != 0:
        print_msg("Object " + str(m_obj.Label) + " added to Group : " + str(m_grp.Label))

def createFolders(folder=None):
    """ Create WorkFeatures Parametric folders if needed.
    """
    m_main_dir = "WorkFeatures"
    if not(App.ActiveDocument.getObject(m_main_dir)):   
        try:
            App.ActiveDocument.addObject("App::DocumentObjectGroup",m_main_dir)    
        except:
            printError_msg("Could not Create '" + str(m_main_dir) +"' Objects Group!")
            
    m_list_dirs = ['Origin_P','WorkPoints_P','WorkAxis_P','WorkPlanes_P',\
                   'WorkCircles_P','WorkArcs_P','WorkBoxes_P',\
                   'WorkWires_P','WorkImages_P','WorkObjects_P','Rot_Trans_P']
    
    m_group = None
    for m_dir in m_list_dirs:     
        if folder == m_dir:
            m_group = App.ActiveDocument.getObject(m_main_dir).getObject(str(m_dir))
            if not(m_group):
                try:
                    m_group = App.ActiveDocument.getObject(m_main_dir).newObject("App::DocumentObjectGroup", str(m_dir))
                except:
                    printError_msg("Could not Create '"+ str(m_dir) +"' Objects Group!")
    return m_group