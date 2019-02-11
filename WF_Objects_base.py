# -*- coding: utf-8 -*-
"""
***************************************************************************
*   This file is part of Work Feature workbench                           *
*                                                                         *
*   Copyright (c) 2017-2019 <rentlau_64>                                  *
*   https://github.com/Rentlau/WorkFeature-WB                             *
*                                                                         *
*   Code rewrite by <rentlau_64> from Work Features macro:                *
*   https://github.com/Rentlau/WorkFeature                                *
*                                                                         *
*   This workbench is a supplement to the FreeCAD CAx development system. *
*   http://www.freecadweb.org                                             *
*                                                                         *
*   This workbench is free software; you can redistribute it and/or modify*
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation, either version 3 of the License, or     *
*   (at your option) any later version.                                   *
*   for detail see the LICENSE text file or:                              *
*   https://www.gnu.org/licenses/gpl-3.0.html                             *
*                                                                         *
*   This workbench is distributed in the hope that it will be useful,     *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this workbench;                                    *
*   If not, see <https://www.gnu.org/licenses/>                           *
***************************************************************************
"""

import sys
import FreeCAD as App
import WF

__title__ = "Object WF_Point"
__author__ = "Rentlau_64"
__url__ = "https://github.com/Rentlau/WorkFeature-WB.git"
__brief__ = '''

'''
###############
m_debug = True
###############

WF_ParametricList = ['Not', 'Interactive', 'Dynamic']
WF_PLIST = WF_ParametricList
WF_ColorList = [(0.45, 0.30, 0.00), (0.70, 0.47, 0.00), (1.00, 0.67, 0.00)]
WF_CLIST = WF_ColorList


class WF_Object():
    """ Abstract class of Work Feature Object.
    """
    def __init__(self, selfobj):
        if m_debug:
            print("running WF_Object.__init__ !")
        if self.__class__ is WF_Object:
            m_msg = "Creation not allowed, MUST derive this class first !"
            raise Exception(m_msg)
        else:
            self.initiate(selfobj)

    def initiate(self, selfobj):
        if m_debug:
            print("running WF_Object.initiate !")
        self.name = "Parametric"
        self.created = False
        m_tooltip = """Choose the parametric behavior of the Feature
regarding parent changes.
  Not : For Static behavior (no update when original parent(s) change)
  Interactive : Update only when user asks for
  Dynamic : Update each time parent changes
"""
        selfobj.addProperty("App::PropertyEnumeration",
                            'Parametric',
                            self.name,
                            m_tooltip)

        selfobj.Parametric = [v.encode('utf8') for v in WF_ParametricList]
        selfobj.Parametric = 'Dynamic'.encode('utf8')
        selfobj.Parametric = WF.parametric()
        # obj.setEditorMode("MyPropertyName", mode)
        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden
        selfobj.setEditorMode("Parametric", 0)
        self.color = WF_CLIST[WF_PLIST.index(selfobj.Parametric)]

    # this method is mandatory
    def execute(self, selfobj):
        if m_debug:
            print("running WF_Object.execute !")
        pass

    def onChanged(self, selfobj, prop):
        if m_debug:
            print("running WF_Object.onChanged !")

        # To be compatible with previous version 2018
        if 'parametric' in selfobj.PropertiesList:
            selfobj.setEditorMode("parametric", 1)

        # App.Console.PrintMessage(str(sys._getframe().f_code.co_name))
        if prop == "Parametric":
            self.color = WF_CLIST[WF_PLIST.index(selfobj.Parametric)]
            selfobj.Proxy.execute(selfobj)
            if WF.verbose() != 0:
                m_msg = "New parametric : " + str(selfobj.Parametric) + "\n"
                App.Console.PrintMessage(m_msg)
                m_msg = "New color : " + str(self.color) + "\n"
                App.Console.PrintMessage(m_msg)


class WF_Point(WF_Object):
    """ The Point WF object. """
    # this method is mandatory
    def __init__(self, selfobj, name):
        if m_debug:
            print("running WF_Point.__init__ !")
        WF_Object.__init__(self, selfobj)
        # Add some custom properties to our Point WF object.
        selfobj.addProperty("App::PropertyFloat",
                            "X",
                            name,
                            "X of the point").X = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Y",
                            name,
                            "Y of the point").Y = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Z",
                            name,
                            "Z of the point").Z = 1.0

        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden
        selfobj.setEditorMode("X", 1)
        selfobj.setEditorMode("Y", 1)
        selfobj.setEditorMode("Z", 1)

    # this method is mandatory
    def execute(self, selfobj):
        if m_debug:
            print("running WF_Point.execute !")
        pass

    def onChanged(self, selfobj, prop):
        if m_debug:
            print("running WF_Point.onChanged !")
        WF_Object.onChanged(self, selfobj, prop)


class WF_Line(WF_Object):
    """ The Line WF object. """
    # this method is mandatory
    def __init__(self, selfobj, name):
        if m_debug:
            print("running WF_Line.__init__ !")
        WF_Object.__init__(self, selfobj)
        # Add some custom properties to our Line WF object.
        selfobj.addProperty("App::PropertyFloat",
                            "Point1_X",
                            name,
                            "X of the start point").Point1_X = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point1_Y",
                            name,
                            "Y of the start point").Point1_Y = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point1_Z",
                            name,
                            "Z of the start point").Point1_Z = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point2_X",
                            name,
                            "X of the end point").Point2_X = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point2_Y",
                            name,
                            "Y of the end point").Point2_Y = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point2_Z",
                            name,
                            "Z of the end point").Point2_Z = 1.0

        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden
        selfobj.setEditorMode("Point1_X", 1)
        selfobj.setEditorMode("Point1_Y", 1)
        selfobj.setEditorMode("Point1_Z", 1)
        selfobj.setEditorMode("Point2_X", 1)
        selfobj.setEditorMode("Point2_Y", 1)
        selfobj.setEditorMode("Point2_Z", 1)

    # this method is mandatory
    def execute(self, selfobj):
        if m_debug:
            print("running WF_Line.execute !")
        pass

    def onChanged(self, selfobj, prop):
        if m_debug:
            print("running WF_Line.onChanged !")
        WF_Object.onChanged(self, selfobj, prop)


class WF_Plane(WF_Object):
    """ The Plane WF object. """
    # this method is mandatory
    def __init__(self, selfobj, name):
        if m_debug:
            print("running WF_Plane.__init__ !")
        WF_Object.__init__(self, selfobj)
        # Add some custom properties to our Line WF object.
        selfobj.addProperty("App::PropertyFloat",
                            "Point1_X",
                            name,
                            "X of the start point").Point1_X = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point1_Y",
                            name,
                            "Y of the start point").Point1_Y = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point1_Z",
                            name,
                            "Z of the start point").Point1_Z = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point2_X",
                            name,
                            "X of the end point").Point2_X = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point2_Y",
                            name,
                            "Y of the end point").Point2_Y = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point2_Z",
                            name,
                            "Z of the end point").Point2_Z = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point3_X",
                            name,
                            "X of the end point").Point3_X = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point3_Y",
                            name,
                            "Y of the end point").Point3_Y = 1.0
        selfobj.addProperty("App::PropertyFloat",
                            "Point3_Z",
                            name,
                            "Z of the end point").Point3_Z = 1.0
        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden
        selfobj.setEditorMode("Point1_X", 1)
        selfobj.setEditorMode("Point1_Y", 1)
        selfobj.setEditorMode("Point1_Z", 1)
        selfobj.setEditorMode("Point2_X", 1)
        selfobj.setEditorMode("Point2_Y", 1)
        selfobj.setEditorMode("Point2_Z", 1)
        selfobj.setEditorMode("Point3_X", 1)
        selfobj.setEditorMode("Point3_Y", 1)
        selfobj.setEditorMode("Point3_Z", 1)

    # this method is mandatory
    def execute(self, selfobj):
        if m_debug:
            print("running WF_Plane.execute !")
        pass

    def onChanged(self, selfobj, prop):
        WF_Object.onChanged(self, selfobj, prop)

class WF_Plane2(WF_Point, WF_Line):
    """ The Plane WF object. """
    # this method is mandatory
    def __init__(self, selfobj, name):
        if m_debug:
            print("running WF_Plane.__init__ !")
        WF_Point.__init__(self, selfobj)
        WF_Line.__init__(self, selfobj)
        # Add some custom properties to our Plane WF object.

    # this method is mandatory
    def execute(self, selfobj):
        if m_debug:
            print("running WF_Plane.execute !")
        pass

    def onChanged(self, selfobj, prop):
        WF_Object.onChanged(self, selfobj, prop)
