# -*- coding: utf-8 -*-
""" To set the config of different resources.
"""
import os

# get the path of the current python script
PATH_WF = os.path.dirname(__file__)

global PATH_WF_ICONS
global PATH_WF_UTILS
global PATH_WF_RESOURCES
global PATH_WF_UI

PATH_WF_ICONS = os.path.join(PATH_WF, 'Resources', 'Icons')
PATH_WF_UTILS = os.path.join(PATH_WF, 'Utils')
PATH_WF_RESOURCES = os.path.join(PATH_WF, 'Resources')
PATH_WF_UI = os.path.join(PATH_WF, 'Resources', 'Ui')

# print("PATH_WF_ICONS = " + str(PATH_WF_ICONS))
# print("PATH_WF_UTILS = " + str(PATH_WF_UTILS))
# print("PATH_WF_RESOURCES = " + str(PATH_WF_RESOURCES))
# print("PATH_WF_UI = " + str(PATH_WF_UI))
