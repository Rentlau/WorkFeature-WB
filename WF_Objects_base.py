# -*- coding: utf-8 -*-
"""
***************************************************************************
*   FreeCAD Work Feature workbench                                        *
*                                                                         *
*   Copyright (c) 2017 <rentlau_64>                                       *
*   Code rewrite by <rentlau_64> from Work Features macro:                *
*   https://github.com/Rentlau/WorkFeature                                *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *  
*   http://www.freecadweb.org                                             *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the COPYING and COPYING.LESSER text files.             *
*   http://en.wikipedia.org/wiki/LGPL                                     *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA or see <http://www.gnu.org/licenses/>                             *
***************************************************************************
"""
__title__="Object WF_Point"
__author__ = "Rentlau_64"
__brief__ = '''

'''
import FreeCAD as App
import WF

class WF_Object():
    """ Abstract class of Work Feature Object.
    
    """
    def __init__(self, selfobj):
        if self.__class__ is WF_Object:
            raise Exception("Creation not allowed, MUST derive this class first")
        else:
            self.initiate(selfobj)
            
    def initiate(self, selfobj):
        #selfobj.addProperty("App::PropertyEnumeration","Parametric","CenterLinePoint","Parametric Definition").Parametric=["Not Parametric","Semi Parametric","Full Parametric"]

        selfobj.addProperty("App::PropertyEnumeration", 'parametric', 'Parametric',
                            """Choose the parametric behavior of the Feature<br>
                            regarding parent changes.<br>
                            No : for Static (no update)<br>
                            Interactive : Update only when user asks for<br>
                            Dynamic : Update each time parent changes
                            """)
        selfobj.parametric = [ v.encode('utf8') for v in ['No','Interactive','Dynamic'] ]
        selfobj.parametric = 'Dynamic'.encode('utf8')
        selfobj.parametric = WF.parametric()

    # this method is mandatory   
    def execute(self,selfobj):
        pass
    
    def onChanged(self, selfobj, prop):
        if prop == "parametric":
            selfobj.Proxy.execute(selfobj)
            if WF.verbose() != 0:
                App.Console.PrintMessage("New parametric : " + str(selfobj.parametric) + "\n")    

class WF_Point(WF_Object):
    """ The Point WF object. """
    # this method is mandatory
    def __init__(self, selfobj, name):
        WF_Object.__init__(self, selfobj)
        
        """ Add some custom properties to our Point WF object. """
        selfobj.addProperty("App::PropertyFloat","X",name,"X of the point").X=1.0
        selfobj.addProperty("App::PropertyFloat","Y",name,"Y of the point").Y=1.0
        selfobj.addProperty("App::PropertyFloat","Z",name,"Z of the point").Z=1.0
        
        # 0 -- default mode, read and write
        # 1 -- read-only
        # 2 -- hidden 
        selfobj.setEditorMode("X", 1) 
        selfobj.setEditorMode("Y", 1) 
        selfobj.setEditorMode("Z", 1)
    
    # this method is mandatory   
    def execute(self,selfobj):
        pass
        
    def onChanged(self, selfobj, prop): 
        WF_Object.onChanged(self, selfobj, prop)  
