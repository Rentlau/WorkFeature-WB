# -*- coding: utf-8 -*-
"""
***************************************************************************
*   FreeCAD Work Features / version parametric 2017                       *
*   Copyright (c) 2017 <rentlau_64>                                       *
*   Code rewrite by <rentlau_64> from Work Features macro:                *
*   https://github.com/Rentlau/WorkFeature                                *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the COPYING and COPYING.LESSER text files.             *
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
import FreeCAD as App
if App.GuiUp:
    import FreeCADGui as Gui
import Part
from WF_print import print_msg
import WF_geometry as geom

def getSel(debug=0):

    m_actDoc = App.activeDocument()
    if m_actDoc == None:
        message = "No Active document selected !"
        return (None, message)
    if not m_actDoc.Name:
        message = "No Active document.name selected !"
        return (None, message) 
       
    m_selEx  = Gui.Selection.getSelectionEx(m_actDoc.Name)                    
    m_sel    = Selection(m_selEx)
 
    if m_sel == None :
        print_msg("Unable to create a Selection Object !") 
        return None
    
    if debug != 0:
        print_msg("m_actDoc      = " + str(m_actDoc))
        print_msg("m_actDoc.Name = " + str(m_actDoc.Name))
        print_msg("m_selEx       = " + str(m_selEx))         
        print_msg("m_sel         ... " + str(m_sel))
        
    return m_sel, m_actDoc

def parseSel(selectionObject):
    res = []
    for obj in selectionObject:
        if obj.HasSubObjects:
            i = 0
            for subobj in obj.SubObjects:
                if issubclass(type(subobj),Part.Edge):
                    res.append([obj.Object,obj.SubElementNames[i]])
                i += 1
        else:
            i = 0
            for e in obj.Object.Shape.Edges:
                n = "Edge"+str(i)
                res.append([obj.Object,n])
                i += 1
    return res


class Selection():

    def __init__(self, Gui_Selection):
        """ Create a Selection Object

        *Gui_Selection* : selected object from GUI.
    
        EXAMPLE :
        m_activeDoc = App.activeDocument()
        if m_activeDoc == None:
            message = "No Active document selected !"
            return (None, message)
        if not m_activeDoc.Name:
            message = "No Active document.name selected !"
            return (None, message) 
        
        m_selEx = Gui.Selection.getSelectionEx(m_activeDoc.Name)
        m_sel = Selection(m_selEx)
        
        Number_of_Edges, Edge_List = m_sel.get_segments(getfrom=["Points","Segments","Curves","Planes","Objects"])
                 
        """
        self.__numberOfEntities = 0
        self.__numberOfVertexes = 0
        self.__numberOfEdges = 0
        self.__numberOfWires = 0
        self.__numberOfFaces = 0
        self.__numberOfObjects = 0
        self.__numberOfImages = 0
        self.__selectedVertices = []
        self.__selectedEdges = []
        self.__selectedEdgesWithLabel = []
        self.__selectedWires = []
        self.__selectedFaces = []
        self.__selectedObjects = []
        self.__selectedImages = []

        self.__selEx = None
        if Gui_Selection == None:
            message = "No Selection from Active document passed !"
            return (None, message)
        self.__selEx = Gui_Selection

        self.initialize()
         
    def storeShapeType(self, Object):
        if Object.ShapeType == "Vertex":
            self.__selectedVertices.append(Object)
            return True
        if Object.ShapeType == "Edge":
            self.__selectedEdges.append(Object)
            return True
        if Object.ShapeType == "Wire":
            self.__selectedWires.append(Object)
            return True  
        if Object.ShapeType == "Face":
            self.__selectedFaces.append(Object)
            return True
        return False

    def initialize(self):
        self.__numberOfEntities = len (self.__selEx)
        if self.__numberOfEntities < 1:
            return
        
        for m_Sel_i_Object in self.__selEx:
            if not m_Sel_i_Object.HasSubObjects:
                if hasattr(m_Sel_i_Object, 'Object'):                   
                    
                    m_Object = m_Sel_i_Object.Object
                    if hasattr(m_Object, 'ShapeType'):
                        self.storeShapeType(m_Object)
                    if hasattr(m_Object, 'Shape'):
                        self.__selectedObjects.append(m_Object)
                    if hasattr(m_Object, 'ImageFile'):
                        self.__selectedImages.append(m_Object)
                    
            else:
                for m_Object in m_Sel_i_Object.SubObjects:
                    
                    if hasattr(m_Object, 'ShapeType'):
                        self.storeShapeType(m_Object)
                    if hasattr(m_Object, 'Shape'):
                        self.__selectedObjects.append(m_Object)
                    if hasattr(m_Object, 'ImageFile'):
                        self.__selectedImages.append(m_Object)
                                    
        self.__numberOfVertexes  = len(self.__selectedVertices)
        self.__numberOfEdges     = len(self.__selectedEdges)
        self.__numberOfWires     = len(self.__selectedWires)
        self.__numberOfFaces     = len(self.__selectedFaces)
        self.__numberOfObjects   = len(self.__selectedObjects)
        self.__numberOfImages    = len(self.__selectedImages)
        
        message = "Initialization done !"
        return message
      
     
    def __getNumberOfEntities(self):
        return self.__numberOfEntities    
    
    def __setNumberOfEntities(self, val):
        self.__numberOfEntities = val
           
    numberOfEntities = property(__getNumberOfEntities, __setNumberOfEntities)
         
    def __getNumberOfPoints(self):
        return self.__numberOfVertexes
     
    def __setNumberOfPoints(self, val):
        self.__numberOfVertexes = val
           
    numberOfPoints = property(__getNumberOfPoints, __setNumberOfPoints) 
    
    def __getNumberOfSegments(self):
        return self.__numberOfEdges
     
    def __setNumberOfSegments(self, val):
        self.__numberOfEdges = val
           
    numberOfSegments = property(__getNumberOfSegments, __setNumberOfSegments) 
    
    def __getNumberOfCurves(self):
        return self.__numberOfWires
     
    def __setNumberOfCurves(self, val):
        self.__numberOfWires = val
           
    numberOfCurves = property(__getNumberOfCurves, __setNumberOfCurves) 
    
    def __getNumberOfPlanes(self):
        return self.__numberOfFaces
     
    def __setNumberOfPlanes(self, val):
        self.__numberOfFaces = val
           
    numberOfPlanes = property(__getNumberOfPlanes, __setNumberOfPlanes) 
    
    def __getNumberOfObjects(self):
        return self.__numberOfObjects
     
    def __setNumberOfObjects(self, val):
        self.__numberOfObjects = val
           
    numberOfObjects = property(__getNumberOfObjects, __setNumberOfObjects)
    
        
    def __getNumberOfImages(self):
        return self.__numberOfImages
     
    def __setNumberOfImages(self, val):
        self.__numberOfImages = val
           
    numberOfImages = property(__getNumberOfImages, __setNumberOfImages)
    
    def __str__(self):
        message  = "\nGui_Selection        : " + str(self.__selEx)
        message += "\nNumber Of Images     : " + str(self.__numberOfImages)
        message += "\nNumber Of Objects    : " + str(self.__numberOfObjects)
        message += "\nNumber Of Planes     : " + str(self.__numberOfFaces)
        message += "\nNumber Of Curves     : " + str(self.__numberOfWires)
        message += "\nNumber Of Segments   : " + str(self.__numberOfEdges)
        message += "\nNumber Of Points     : " + str(self.__numberOfVertexes)
        message += "\nNumber Of Entities   : " + str(self.__numberOfEntities)
        return (message)
    
    
    def get_pointsNames(self, getfrom=["Points","Curves","Objects"]):
        """
        return a list of [obj.Object,"Vertex"+str(i)]
        """
        if self.numberOfEntities == 0 :
            return (0, None)
        
        def find(aVertex,inObject):
            if hasattr(inObject, 'Vertexes'):
                m_i = 0
                for e in inObject.Vertexes:
                    # We return the index + 1  of the vertex in the vertexes list when point match 
                    if geom.isEqualVectors(e.Point, aVertex.Point, tolerance=1e-12):
                            # Needs to add 1 as for Edge1 corresponds to first 0 index in the list
                            return (m_i + 1)
                    m_i += 1 
            return None

        Selected_Entities = []
        Selected_Entities1 = []
        Selected_Entities2 = []

        for m_obj in self.__selEx:
            m_shape = m_obj.Object.Shape
            print "m_shape = " + str(m_shape)
            print "type(m_shape) = " + str(type(m_shape))

            print "m_obj.HasSubObjects = " + str(m_obj.HasSubObjects)
            if m_obj.HasSubObjects:                
                m_i = 0
                for m_subobj in m_obj.SubObjects:

                    if issubclass(type(m_subobj),Part.Face) and "Planes" in getfrom :
                        m_i = 0
                        for m_v in m_subobj.Vertexes:
                            m_i_in_list = find(m_v,m_obj.Object.Shape)
                            Selected_Entities.append([m_obj.Object,"Vertex"+str(m_i_in_list)])
                            m_i += 1
                        #m_i = 0
                                           
                    if issubclass(type(m_subobj),Part.Vertex):
                        Selected_Entities.append([m_obj.Object,m_obj.SubElementNames[m_i]])
                        m_i += 1
            else:
                m_i = 0
                if issubclass(type(m_shape),Part.Vertex) and "Points" in getfrom :
                    if hasattr(m_shape, 'Vertexes'):
                        for m_v in m_shape.Vertexes:
                            Selected_Entities.append([m_obj.Object,"Vertex"+str(m_i)])
                            m_i += 1
                if issubclass(type(m_shape),Part.Wire) and "Curves" in getfrom :
                    if hasattr(m_shape, 'Vertexes'):
                        if self.__numberOfObjects== 2 :
                            if m_obj == self.__selEx[0]:
                                for m_v in m_shape.Vertexes:
                                    Selected_Entities1.append([m_obj.Object,"Vertex"+str(m_i)])
                                    m_i += 1
                            else:
                                for m_v in m_shape.Vertexes:
                                    Selected_Entities2.append([m_obj.Object,"Vertex"+str(m_i)])
                                    m_i += 1    
                        else:                        
                            for m_v in m_shape.Vertexes:
                                Selected_Entities.append([m_obj.Object,"Vertex"+str(m_i)])
                                m_i += 1 
                if issubclass(type(m_shape),Part.Solid) and "Objects" in getfrom :
                    if hasattr(m_shape, 'Vertexes'):
                        for m_v in m_shape.Vertexes:
                            Selected_Entities.append([m_obj.Object,"Vertex"+str(m_i)])
                            m_i += 1    
                if issubclass(type(m_shape),Part.Face) and "Planes" in getfrom : 
                    if hasattr(m_shape, 'Vertexes'):
                        for m_v in m_shape.Vertexes:
                            Selected_Entities.append([m_obj.Object,"Vertex"+str(m_i)])
                            m_i += 1
                 
        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)
        if len(Selected_Entities1) != 0:
            e = zip(Selected_Entities1,Selected_Entities2)
            Selected_Entities = [i[0] for i in e]
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)
        
    def get_points(self, getfrom=["Points","Segments","Curves","Planes","Objects"]):
        """ Return all Points found in selection including the Points from objects as
        (Number of Points, list of Vertexes)
        Return None if no Point detected 
        """
        Selected_Entities = []
        
        if self.numberOfEntities == 0 :
            return None
        
        if self.numberOfPoints > 0 and "Points" in getfrom :
            for m_point in self.__selectedVertices:
                Selected_Entities.append(m_point)
                
        if self.numberOfSegments > 0 and "Segments" in getfrom :
            for m_edge in self.__selectedEdges:
                Selected_Entities.append(m_edge.Vertexes[0])
                Selected_Entities.append(m_edge.Vertexes[-1])
        # TOCOMPLETE
        if self.numberOfCurves > 0 and "Curves" in getfrom :
            pass
                
        if self.numberOfPlanes > 0 and "Planes" in getfrom :
            for m_face in self.__selectedFaces:
                m_edges_list = m_face.Edges
                for m_edge in m_edges_list:
                    Selected_Entities.append(m_edge.Vertexes[0])
                    Selected_Entities.append(m_edge.Vertexes[-1])
         
        if self.numberOfObjects  > 0 and "Objects" in getfrom :
            for m_object in self.__selectedObjects:
                for m_vertex in m_object.Shape.Vertexes:
                    Selected_Entities.append(m_vertex)  
        
        if len(Selected_Entities) != 0:                          
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)      
    
    def get_segmentsNames(self, getfrom=["Points","Segments","Curves","Planes","Objects"]):
        """
        return a list of [obj.Object,"Edge"+str(i)]
        """
        if self.numberOfEntities == 0 :
            return (0, None)
        
        def find(anEdge,inObject):
            if hasattr(inObject, 'Edges'):
                m_i = 0
                for e in inObject.Edges:
                    # We return the index + 1  of the edge in the edges list when extrema points match 
                    if geom.isEqualVectors(e.Vertexes[0].Point, anEdge.Vertexes[0].Point, tolerance=1e-12):
                        if geom.isEqualVectors(e.Vertexes[-1].Point, anEdge.Vertexes[-1].Point, tolerance=1e-12):
                            # Needs to add 1 as for Edge1 corresponds to first 0 index in the list
                            return (m_i + 1)
                    m_i += 1 
            return None

        Selected_Entities = []

        m_i = 0
        for m_obj in self.__selEx:
            m_shape = m_obj.Object.Shape

            if m_obj.HasSubObjects:
                m_i = 0
                for m_subobj in m_obj.SubObjects:

                    if issubclass(type(m_subobj),Part.Face) and "Planes" in getfrom :
                        m_i = 0
                        for m_e in m_subobj.Edges:
                            m_i_in_list = find(m_e,m_obj.Object.Shape)
                            Selected_Entities.append([m_obj.Object,"Edge"+str(m_i_in_list)])
                            m_i += 1
                        m_i = 0
                                           
                    if issubclass(type(m_subobj),Part.Edge):
                        Selected_Entities.append([m_obj.Object,m_obj.SubElementNames[m_i]])
                        m_i += 1
            else:
                m_i = 0
                if issubclass(type(m_shape),Part.Solid) and "Objects" in getfrom :
                    if hasattr(m_shape, 'Edges'):
                        for m_e in m_shape.Edges:
                            Selected_Entities.append([m_obj.Object,"Edge"+str(m_i)])
                            m_i += 1    
                if issubclass(type(m_shape),Part.Face) and "Planes" in getfrom : 
                    if hasattr(m_shape, 'Edges'):
                        for m_e in m_shape.Edges:
                            Selected_Entities.append([m_obj.Object,"Edge"+str(m_i)])
                            m_i += 1
                            
        if self.numberOfPoints >= 2 and "Points" in getfrom :
            for m_p1,m_p2 in zip(self.__selectedVertices, self.__selectedVertices[1:]):
                m_diff = m_p2.Point.sub(m_p1.Point)
                tolerance = 1e-10
                if abs(m_diff.x) <= tolerance and abs(m_diff.y) <= tolerance and abs(m_diff.z) <= tolerance:
                    continue 
                Selected_Entities.append([Part.makeLine(m_p2.Point, m_p1.Point),"Edge"+str(m_i)])
                m_i += 1        
    
                 
        if len(Selected_Entities) != 0:                          
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)           
    
    def get_segments(self, getfrom=["Points","Segments","Curves","Planes","Objects"]):   
        """ Return all Segments found in selection including the Segments from objects
        as (Number of Segments, list of Edges)
        In case of at least 2 points selected it will create a line from these 2 points
        Return None if no Segment detected      
        """
        Selected_Entities = []
               
        if self.numberOfEntities == 0 :
            return (0, None)
        
        if self.numberOfPoints >= 2 and "Points" in getfrom :
            for m_p1,m_p2 in zip(self.__selectedVertices, self.__selectedVertices[1:]):
                m_diff = m_p2.Point.sub(m_p1.Point)
                tolerance = 1e-10
                if abs(m_diff.x) <= tolerance and abs(m_diff.y) <= tolerance and abs(m_diff.z) <= tolerance:
                    continue 
                Selected_Entities.append(Part.makeLine(m_p2.Point, m_p1.Point))        
                
        if self.numberOfSegments > 0 and "Segments" in getfrom :
            for m_edge in self.__selectedEdges:
                Selected_Entities.append(m_edge)
        # TOCOMPLETE
        if self.numberOfCurves > 0 and "Curves" in getfrom :
            for m_wire in self.__selectedWires:
                Selected_Entities.append(m_wire)
                
        if self.numberOfPlanes > 0 and "Planes" in getfrom :
            for m_face in self.__selectedFaces:
                m_edges_list = m_face.Edges
                for m_edge in m_edges_list:
                    Selected_Entities.append(m_edge)
         
        if self.numberOfObjects  > 0 and "Objects" in getfrom :
            for m_object in self.__selectedObjects:
                for m_edge in m_object.Shape.Edges:
                    Selected_Entities.append(m_edge) 
        
        if len(Selected_Entities) != 0:                          
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)  
    
    
    def get_curves(self, getfrom=["Points","Segments","Curves","Planes","Objects"]):
        Selected_Entities = []
                       
        if self.numberOfEntities == 0 :
            return None        
        
        if self.numberOfCurves > 0 and "Curves" in getfrom :
            for m_wire in self.__selectedWires:
                Selected_Entities.append(m_wire)
                
        if self.numberOfPlanes > 0 and "Planes" in getfrom :
            for m_face in self.__selectedFaces:
                m_wires_list = m_face.Wires
                for m_wire in m_wires_list:
                    Selected_Entities.append(m_wire)
         
        if self.numberOfObjects  > 0 and "Objects" in getfrom :
            for m_object in self.__selectedObjects:
                for m_wire in m_object.Shape.Wires:
                    Selected_Entities.append(m_wire) 
        
        if len(Selected_Entities) != 0:                          
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)   
    
    
    def get_planes(self, getfrom=["Points","Segments","Curves","Planes","Objects"]):
        Selected_Entities = []
                       
        if self.numberOfEntities == 0 :
            return None 
          
        # TOCOMPLETE
#         if self.numberOfPoints >= 3 and "Points" in getfrom :
#             import Part
#             for m_p1,m_p2 in zip(self.__selectedVertices, self.__selectedVertices[1:]):
#                 m_diff = m_p2.Point.sub(m_p1.Point)
#                 tolerance = 1e-10
#                 if abs(m_diff.x) <= tolerance and abs(m_diff.y) <= tolerance and abs(m_diff.z) <= tolerance:
#                     continue 
#                 Selected_Entities.append(Part.makeLine(m_p2.Point, m_p1.Point))         
#         
#         # TOCOMPLETE        
#         if self.numberOfSegments >= 2 and "Segments" in getfrom :
#             import Part
#             for m_l1,m_l2 in zip(self.__selectedEdges, self.__selectedEdges[1:]):
#             for m_edge in self.__selectedEdges
#                 Selected_Entities.append(m_edge) 
                
                                      
        if self.numberOfPlanes > 0 and "Planes" in getfrom :
            for m_face in self.__selectedFaces:
                Selected_Entities.append(m_face)
         
        if self.numberOfObjects  > 0 and "Objects" in getfrom :
            for m_object in self.__selectedObjects:
                for m_face in m_object.Shape.Faces:
                    Selected_Entities.append(m_face) 
        
        if len(Selected_Entities) != 0:                          
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)   
    
        
    def get_objects(self):
        Selected_Entities = []
        pass
  
  
    def get_primer_selected_entities(self, selection_type):
        Selected_Entities = selection_type
        if len(Selected_Entities) != 0:                          
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)  
    
     
    def get_primerPoints(self):
        return self.get_primer_selected_entities(self.__selectedVertices)
    
        
    def get_primerSegments(self):
        return self.get_primer_selected_entities(self.__selectedEdges)
    
    
    def get_primerCurves(self):
        return self.get_primer_selected_entities(self.__selectedWires)
    
    
    def get_primerPlanes(self):
        return self.get_primer_selected_entities(self.__selectedFaces)
    
    
    def get_primerObjects(self):
        return self.get_primer_selected_entities(self.__selectedObjects)
    
      
    def get_primerImages(self):
        return self.get_primer_selected_entities(self.__selectedImages)

if __name__ == '__main__': 
    pass
    
