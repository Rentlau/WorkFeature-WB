# -*- coding: utf-8 -*-
import FreeCAD as App
import Part
import WF
from WF_print import print_msg
import WF_geometry as geom
if App.GuiUp:
    import FreeCADGui as Gui

###############
m_debug = True
###############


def getSel(verbose=0):
    m_actDoc = App.activeDocument()
    if m_actDoc is None:
        message = "No Active document selected !"
        return (None, message)
    if not m_actDoc.Name:
        message = "No Active document.name selected !"
        return (None, message)

    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)
    m_sel = Selection(m_selEx)

    if m_sel is None:
        message = "Unable to create a Selection Object !"
        print_msg(message)
        return (None, message)

    if verbose:
        print_msg("VERBOSE MODE :")
        print_msg("m_actDoc      = " + str(m_actDoc))
        print_msg("m_actDoc.Name = " + str(m_actDoc.Name))
        print_msg(str(m_sel))
        printObjectStructure()

    return m_sel, m_actDoc


def printObjectStructure():
    m_actDoc = App.activeDocument()
    print(str(m_actDoc.Name))

    m_selEx = Gui.Selection.getSelectionEx(m_actDoc.Name)

    for m_sel in m_selEx:
        print("|__" + str(m_sel.ObjectName))
        if m_sel.HasSubObjects:
            for m_obj_name in m_sel.SubElementNames:
                print("   |__" + str(m_obj_name))
        else:
            pass


class Selection():

    def __init__(self, Gui_Selection):
        """ Create a Selection Object

        *Gui_Selection* : selected object from GUI.

        EXAMPLE :
        m_activeDoc = App.activeDocument()
        if m_activeDoc is None:
            message = "No Active document selected !"
            return (None, message)
        if not m_activeDoc.Name:
            message = "No Active document.name selected !"
            return (None, message)

        m_selEx = Gui.Selection.getSelectionEx(m_activeDoc.Name)
        m_sel = Selection(m_selEx)

        Number_of_Edges, Edge_List = m_sel.get_segments(
           getfrom=["Points","Segments","Curves","Planes","Objects"])

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

        self.__selEx = Gui_Selection

        self.initialize()

    def storeShapeType(self, Object):
        if m_debug:
            print("Object.ShapeType = " + str(Object.ShapeType))

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

    def storeShape(self, Object):
        m_shape_type = type(Object.Shape)
        if m_debug:
            print("type(Object.Shape) = " + str(m_shape_type))

        if m_shape_type == Part.Vertex:
            self.__selectedVertices.append(Object.Shape)
            return True
        if m_shape_type == Part.Edge:
            self.__selectedEdges.append(Object.Shape)
            return True
        if m_shape_type == Part.Wire:
            self.__selectedWires.append(Object.Shape)
            return True
        if m_shape_type == Part.Face:
            self.__selectedFaces.append(Object.Shape)
            return True
        return False

    def initialize(self):
        if m_debug:
            print("running Selection.initialize !")

        if self.__selEx is None:
            message = "No Selection from Active document passed !"
            print_msg(message)
            return message

        self.__numberOfEntities = len(self.__selEx)
        if self.__numberOfEntities < 1:
            message = "No Entity selected !"
            print_msg(message)
            return message

        for m_Sel_i_Object in self.__selEx:
            if not m_Sel_i_Object.HasSubObjects:
                if m_debug:
                    print("NO SubObjects !")

                if hasattr(m_Sel_i_Object, 'Object'):
                    m_Object = m_Sel_i_Object.Object
                    if hasattr(m_Object, 'ShapeType'):
                        self.storeShapeType(m_Object)
                    if hasattr(m_Object, 'Shape'):
                        self.storeShape(m_Object)
                        # self.__selectedObjects.append(m_Object)
                    if hasattr(m_Object, 'ImageFile'):
                        self.__selectedImages.append(m_Object)
            else:
                if m_debug:
                    print("SOME SubObjects !")

                for m_Object in m_Sel_i_Object.SubObjects:
                    if hasattr(m_Object, 'ShapeType'):
                        self.storeShapeType(m_Object)
                    if hasattr(m_Object, 'Shape'):
                        self.storeShape(m_Object)
                        # self.__selectedObjects.append(m_Object)
                    if hasattr(m_Object, 'ImageFile'):
                        self.__selectedImages.append(m_Object)

        self.__numberOfVertexes = len(self.__selectedVertices)
        self.__numberOfEdges = len(self.__selectedEdges)
        self.__numberOfWires = len(self.__selectedWires)
        self.__numberOfFaces = len(self.__selectedFaces)
        self.__numberOfObjects = len(self.__selectedObjects)
        self.__numberOfImages = len(self.__selectedImages)

        message = "Initialization done !"
        if m_debug:
            print_msg(message)
        return message

    def removeItem(self, m_id):
        if m_debug:
            print("running Selection.removeItem !")

        self.__numberOfEntities = len(self.__selEx)
        if self.__numberOfEntities < 1:
            return

        for c, _ in enumerate(self.__selEx, 0):
            if c == m_id:
                del self.__selEx[id]
                break
        self.initialize()

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
        message = "\nGui_Selection        : " + str(self.__selEx)
        message += "\nNumber Of Images     : " + str(self.__numberOfImages)
        message += "\n" + str(self.__selectedImages)
        message += "\nNumber Of Objects    : " + str(self.__numberOfObjects)
        message += "\n" + str(self.__selectedObjects)
        message += "\nNumber Of Planes     : " + str(self.__numberOfFaces)
        message += "\n" + str(self.__selectedFaces)
        message += "\nNumber Of Curves     : " + str(self.__numberOfWires)
        message += "\n" + str(self.__selectedWires)
        message += "\nNumber Of Segments   : " + str(self.__numberOfEdges)
        message += "\n" + str(self.__selectedEdges)
        message += "\nNumber Of Points     : " + str(self.__numberOfVertexes)
        message += "\n" + str(self.__selectedVertices)
        message += "\nNumber Of Entities   : " + str(self.__numberOfEntities)
        return (message)

    def get_vertexesFromPlane(self, subObj, selObject, SelEntities):
        # Object of type Plane
        m_i = 0
        for m_v in subObj.Vertexes:
            m_i_in_list = find(m_v, selObject.Shape)
            SelEntities.append([selObject,
                                "Vertex" + str(m_i_in_list)])
            m_i += 1

    def get_pointsNames(self,
                        getfrom=["Points",
                                 "Segments",
                                 "Curves",
                                 "Objects"],
                        flag_remove=False,
                        ):
        """
        return a list of [obj.Object,"Vertex"+str(i)]
        """
        if m_debug:
            print("\nrunning Selection.get_pointsNames !")
            print("self.numberOfEntities = " + str(self.numberOfEntities))

        if self.numberOfEntities == 0:
            return (0, None)

        def find(aVertex, inObject):
            if hasattr(inObject, 'Vertexes'):
                m_i = 0
                for e in inObject.Vertexes:
                    # We return the index + 1  of the vertex in the vertexes
                    # list when point match
                    if geom.isEqualVectors(e.Point,
                                           aVertex.Point,
                                           tolerance=1e-12):
                        # Needs to add 1 as for Edge1 corresponds to first 0
                        # index in the list
                        return (m_i + 1)
                    m_i += 1
            return None

        Selected_Entities = []

        for m_id, m_obj in enumerate(self.__selEx, 0):
            if m_debug:
                print("   m_obj = " + str(m_obj))
                print("   m_obj.Object = " + str(m_obj.Object))
                print("   m_obj.Object.Shape = " + str(m_obj.Object.Shape))
                print("   type(m_obj.Object.Shape) = " + str(type(m_obj.Object.Shape)))
                print("   m_obj.HasSubObjects = " + str(m_obj.HasSubObjects))

            if m_obj.HasSubObjects:
                for m_obj_name, m_subobj in zip(m_obj.SubElementNames, m_obj.SubObjects):

                    if m_debug:
                        print("      m_obj_name = " + str(m_obj_name))
                        print("      m_subobj = " + str(m_subobj))
                        print("      type(m_subobj) = " + str(type(m_subobj)))

                    # Object of type Plane
                    if issubclass(type(m_subobj), Part.Face) and "Planes" in getfrom:
                        self.get_vertexesFromPlane(m_subobj, m_obj.Object, Selected_Entities)
                        m_i = 0
                        for m_v in m_subobj.Vertexes:
                            m_i_in_list = find(m_v, m_obj.Object.Shape)
                            Selected_Entities.append([m_obj.Object,
                                                      "Vertex" + str(m_i_in_list)])
                            m_i += 1

                    # Object of type Edge
                    if issubclass(type(m_subobj), Part.Edge) and "Segments" in getfrom:
                        m_i = 0
                        for m_v in m_subobj.Vertexes:
                            m_i_in_list = find(m_v, m_obj.Object.Shape)
                            Selected_Entities.append([m_obj.Object,
                                                      "Vertex" + str(m_i_in_list)])
                            m_i += 1

                    # Object of type Vertex
                    if issubclass(type(m_subobj), Part.Vertex):
                        Selected_Entities.append([m_obj.Object,
                                                  m_obj_name])

            else:
                m_shape = m_obj.Object.Shape

        if WF.verbose():
            print_msg("Number_of_Vertexes = " + str(len(Selected_Entities)))
            print_msg("Vertex_List = " + str(Selected_Entities))

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)

        return (0, None)

    def get_pointsNamesV0(self,
                          getfrom=["Points",
                                   "Segments",
                                   "Curves",
                                   "Objects"],
                          flag_remove=False,
                          ):
        """
        return a list of [obj.Object,"Vertex"+str(i)]
        """
        if m_debug:
            print("\nrunning Selection.get_pointsNames !")
            print("self.numberOfEntities = " + str(self.numberOfEntities))

        if self.numberOfEntities == 0:
            return (0, None)

        def find(aVertex, inObject):
            if hasattr(inObject, 'Vertexes'):
                m_i = 0
                for e in inObject.Vertexes:
                    # We return the index + 1  of the vertex in the vertexes
                    # list when point match
                    if geom.isEqualVectors(e.Point,
                                           aVertex.Point,
                                           tolerance=1e-12):
                        # Needs to add 1 as for Edge1 corresponds to first 0
                        # index in the list
                        return (m_i + 1)
                    m_i += 1
            return None

        Selected_Entities = []
        Selected_Entities1 = []
        Selected_Entities2 = []

        for m_id, m_obj in enumerate(self.__selEx, 0):
            m_shape = m_obj.Object.Shape
            if m_debug:
                print("m_obj = " + str(m_obj))
                print("m_shape = " + str(m_shape))
                print("type(m_shape) = " + str(type(m_shape)))
                print("m_obj.HasSubObjects = " + str(m_obj.HasSubObjects))

            if m_obj.HasSubObjects:
                m_i = 0
                for m_subobj in m_obj.SubObjects:
                    if m_debug:
                        print("m_subobj = " + str(m_subobj))
                        print("type(m_subobj) = " + str(type(m_subobj)))

                    # Object of type Plane
                    if issubclass(type(m_subobj), Part.Face) and "Planes" in getfrom:
                        m_i = 0
                        for m_v in m_subobj.Vertexes:
                            m_i_in_list = find(m_v, m_obj.Object.Shape)
                            Selected_Entities.append([m_obj.Object,
                                                      "Vertex" + str(m_i_in_list)])
                            m_i += 1

                        if flag_remove:
                            self.removeItem(m_id)
                    # Object of type Edge
                    elif issubclass(type(m_subobj), Part.Edge) and "Segments" in getfrom:
                        m_i = 0
                        for m_v in m_subobj.Vertexes:
                            m_i_in_list = find(m_v, m_obj.Object.Shape)
                            Selected_Entities.append([m_obj.Object,
                                                      "Vertex" + str(m_i_in_list)])
                            m_i += 1
                        if flag_remove:
                            self.removeItem(m_id)
                    # Object of type Vertex
                    elif issubclass(type(m_subobj), Part.Vertex):
                        m_i = 0
                        Selected_Entities.append([m_obj.Object,
                                                  m_obj.SubElementNames[m_i]])
                        m_i += 1
                        if flag_remove:
                            self.removeItem(m_id)
            else:
                m_i = 0

                if issubclass(type(m_shape), Part.Vertex) and "Points" in getfrom:
                    if hasattr(m_shape, 'Vertexes'):
                        for m_v in m_shape.Vertexes:
                            Selected_Entities.append([m_obj.Object,
                                                      "Vertex" + str(m_i)])
                            m_i += 1

                elif issubclass(type(m_shape), Part.Wire) and "Curves" or "Segments" in getfrom:
                    if hasattr(m_shape, 'Vertexes'):
                        if self.__numberOfObjects == 2:
                            if m_obj == self.__selEx[0]:
                                for m_v in m_shape.Vertexes:
                                    Selected_Entities1.append([m_obj.Object,
                                                               "Vertex" + str(m_i)])
                                    m_i += 1
                            else:
                                for m_v in m_shape.Vertexes:
                                    Selected_Entities2.append([m_obj.Object,
                                                               "Vertex" + str(m_i)])
                                    m_i += 1
                        else:
                            for m_v in m_shape.Vertexes:
                                Selected_Entities.append([m_obj.Object,
                                                          "Vertex" + str(m_i)])
                                m_i += 1

                elif issubclass(type(m_shape),
                                Part.Solid) and "Objects" in getfrom:
                    if hasattr(m_shape, 'Vertexes'):
                        for m_v in m_shape.Vertexes:
                            Selected_Entities.append([m_obj.Object,
                                                      "Vertex" + str(m_i)])
                            m_i += 1

                elif issubclass(type(m_shape),
                                Part.Face) and "Planes" in getfrom:
                    if hasattr(m_shape, 'Vertexes'):
                        for m_v in m_shape.Vertexes:
                            Selected_Entities.append([m_obj.Object,
                                                      "Vertex" + str(m_i)])
                            m_i += 1

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)
        if len(Selected_Entities1) != 0:
            e = list(zip(Selected_Entities1, Selected_Entities2))
            Selected_Entities = [i[0] for i in e]
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)

    def get_points(self, getfrom=["Points",
                                  "Segments",
                                  "Curves",
                                  "Planes",
                                  "Objects"]):
        """ Return all Points found in selection including the Points from objects as
        (Number of Points, list of Vertexes)
        Return None if no Point detected
        """
        Selected_Entities = []

        if self.numberOfEntities == 0:
            return None

        if self.numberOfPoints > 0 and "Points" in getfrom:
            for m_point in self.__selectedVertices:
                Selected_Entities.append(m_point)

        if self.numberOfSegments > 0 and "Segments" in getfrom:
            for m_edge in self.__selectedEdges:
                Selected_Entities.append(m_edge.Vertexes[0])
                Selected_Entities.append(m_edge.Vertexes[-1])
        # TOCOMPLETE
        if self.numberOfCurves > 0 and "Curves" in getfrom:
            pass

        if self.numberOfPlanes > 0 and "Planes" in getfrom:
            for m_face in self.__selectedFaces:
                m_edges_list = m_face.Edges
                for m_edge in m_edges_list:
                    Selected_Entities.append(m_edge.Vertexes[0])
                    Selected_Entities.append(m_edge.Vertexes[-1])

        if self.numberOfObjects > 0 and "Objects" in getfrom:
            for m_object in self.__selectedObjects:
                for m_vertex in m_object.Shape.Vertexes:
                    Selected_Entities.append(m_vertex)

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)

    def get_segmentsNames(self,
                          getfrom=["TwoPoints",
                                   "Segments",
                                   "Curves",
                                   "Planes",
                                   "Objects",
                                   "Sets"],
                          ):
        """ Return all Segments Name found in Selection object.

        Return
        ----------
        A tuple : (Number, Selected_Segments)
        Selected_Segments as a list of [obj.Object, "Edge"+str(i)]

        (0, None) if no Segment detected

        Parameters
        ----------
        *getfrom*     : (List, Optional, default)

        *flag_remove* : (Boolean, Optional, default=False)
                    Flag to force to remove the entity from
                    the Selection after dectection.
        """
        if m_debug:
            print("\nrunning Selection.get_segmentsNames !")
            print("self.numberOfEntities = " + str(self.numberOfEntities))

        if self.numberOfEntities == 0:
            return (0, None)

        def addSubEdge(Sel_Edges, m_parent, m_name, m_i):
            Sel_Edges.append([m_parent, m_name])
            m_i += 1
            return m_i

        def addEdge(Sel_Edges, m_parent, m_shape, m_i):
            if hasattr(m_shape, 'Edges'):
                for m_e in m_shape.Edges:
                    Sel_Edges.append([m_parent, "Edge" + str(m_i)])
                    m_i += 1
            return m_i

        def findEdge(anEdge, inObject):
            if hasattr(inObject, 'Edges'):
                m_i = 0
                for e in inObject.Edges:
                    # We return the index + 1  of the edge in the edges list
                    # when extrema points match
                    if geom.isEqualVectors(e.Vertexes[0].Point,
                                           anEdge.Vertexes[0].Point,
                                           tolerance=1e-12):
                        if geom.isEqualVectors(e.Vertexes[-1].Point,
                                               anEdge.Vertexes[-1].Point,
                                               tolerance=1e-12):
                            # Needs to add 1 as for Edge1 corresponds to
                            # first 0 index in the list
                            return (m_i + 1)
                    m_i += 1
            return None

        def addSubEdges(Sel_Edges, m_parent, m_name, m_shape, m_i):
            m_type = type(m_shape)
            if WF.verbose():
                print_msg("   m_obj.Object = " + str(m_parent))
                print_msg("   m_obj.SubElementNames = " + str(m_name))
                print_msg("   type(m_obj.Object.Shape) = " + str(m_type))
                print_msg("   m_obj.Object.Shape = " + str(m_shape))

            if issubclass(m_type, Part.Edge) and "Segments" in getfrom:
                m_i = addSubEdge(Sel_Edges, m_parent, m_name, m_i)
            elif issubclass(m_type, Part.Wire) and "Curves" in getfrom:
                m_i = addSubEdge(Sel_Edges, m_parent, m_name, m_i)
            elif issubclass(m_type, Part.Face) and "Planes" in getfrom:
                for m_e in m_subobj.Edges:
                    m_i_in_list = findEdge(m_e, m_obj.Object.Shape)
                    Sel_Edges.append([m_parent, "Edge" + str(m_i_in_list)])
                    m_i += 1
            elif issubclass(m_type, Part.Solid) and "Objects" in getfrom:
                m_i = addSubEdge(Sel_Edges, m_parent, m_name, m_i)
            elif issubclass(m_type, Part.Compound) and "Sets" in getfrom:
                m_i = addSubEdge(Sel_Edges, m_parent, m_name, m_i)

        def addEdges(Sel_Edges, m_parent, m_name, m_shape, m_i):
            m_type = type(m_shape)
            if WF.verbose():
                print_msg("   m_obj.Object = " + str(m_parent))
                print_msg("   m_obj.SubElementNames = " + str(m_name))
                print_msg("   type(m_obj.Object.Shape) = " + str(m_type))
                print_msg("   m_obj.Object.Shape = " + str(m_shape))

            if issubclass(m_type, Part.Edge) and "Segments" in getfrom:
                m_i = addEdge(Sel_Edges, m_parent, m_shape, m_i)
            elif issubclass(m_type, Part.Wire) and "Curves" in getfrom:
                m_i = addEdge(Sel_Edges, m_parent, m_shape, m_i)
            elif issubclass(m_type, Part.Face) and "Planes" in getfrom:
                m_i = addEdge(Sel_Edges, m_parent, m_shape, m_i)
            elif issubclass(m_type, Part.Solid) and "Objects" in getfrom:
                m_i = addEdge(Sel_Edges, m_parent, m_shape, m_i)
            elif issubclass(m_type, Part.Compound) and "Sets" in getfrom:
                m_i = addEdge(Sel_Edges, m_parent, m_shape, m_i)

        Sel_Edges = []
        m_j = 0
        for _, m_obj in enumerate(self.__selEx, 0):
            if hasattr(m_obj, 'HasSubObjects') and m_obj.HasSubObjects:
                m_i = 0
                if WF.verbose():
                    print_msg("SOME SubObjects !")
                for m_subobj in m_obj.SubObjects:
                    m_shape = m_subobj
                    m_parent = m_obj.Object
                    m_name = m_obj.SubElementNames[m_i]
                    m_i += 1
                    addSubEdges(Sel_Edges, m_parent, m_name, m_shape, m_i)
            else:
                if WF.verbose():
                    print_msg("NO SubObjects !")
                m_shape = m_obj.Object.Shape
                m_parent = m_obj.Object
                m_name = m_obj.Object.Name
                m_j += 1
                addEdges(Sel_Edges, m_parent, m_name, m_shape, m_j)

        if WF.verbose():
            print_msg("Number_of_Edges = " + str(len(Sel_Edges)))
            print_msg("Edge_List = " + str(Sel_Edges))

        if len(Sel_Edges) != 0:
            return (len(Sel_Edges), Sel_Edges)

        return (0, None)

    def get_segmentsNamesV0(self,
                            getfrom=["Points",
                                     "Segments",
                                     "Curves",
                                     "Planes",
                                     "Objects",
                                     "Sets"],
                            flag_remove=False,
                            ):
        """ Return all Segments Name found in Selection object.

        Return
        ----------
        A tuple : (Number, Selected_Segments)
        Selected_Segments as a list of [obj.Object, "Edge"+str(i)]

        (0, None) if no Segment detected

        Parameters
        ----------
        *getfrom*     : (List, Optional, default)

        *flag_remove* : (Boolean, Optional, default=False)
                    Flag to force to remove the entity from
                    the Selection after dectection.
        """
        if m_debug:
            print("\nrunning Selection.get_segmentsNames !")
            print("self.numberOfEntities = " + str(self.numberOfEntities))

        if self.numberOfEntities == 0:
            return (0, None)

        def addEdge(Selected_Entities, m_obj, m_i, m_shape):
            if hasattr(m_shape, 'Edges'):
                for m_e in m_shape.Edges:
                    Selected_Entities.append([m_obj.Object, "Edge" + str(m_i)])
                    m_i += 1
            return m_i

        def find(anEdge, inObject):
            if hasattr(inObject, 'Edges'):
                m_i = 0
                for e in inObject.Edges:
                    # We return the index + 1  of the edge in the edges list
                    # when extrema points match
                    if geom.isEqualVectors(e.Vertexes[0].Point,
                                           anEdge.Vertexes[0].Point,
                                           tolerance=1e-12):
                        if geom.isEqualVectors(e.Vertexes[-1].Point,
                                               anEdge.Vertexes[-1].Point,
                                               tolerance=1e-12):
                            # Needs to add 1 as for Edge1 corresponds to
                            # first 0 index in the list
                            return (m_i + 1)
                    m_i += 1
            return None

        Selected_Entities = []

        for m_id, m_obj in enumerate(self.__selEx, 0):
            if m_debug:
                print("   m_obj = " + str(m_obj))
                print("   m_obj.Object = " + str(m_obj.Object))
                print("   m_obj.Object.Shape = " + str(m_obj.Object.Shape))
                print("   type(m_obj.Object.Shape) = " + str(type(m_obj.Object.Shape)))
                print("   m_obj.HasSubObjects = " + str(m_obj.HasSubObjects))

            if m_obj.HasSubObjects:
                m_i = 0

                for m_subobj in m_obj.SubObjects:
                    if m_debug:
                        # print("      m_obj_name = " + str(m_obj_name))
                        print("      m_subobj = " + str(m_subobj))
                        print("      type(m_subobj) = " + str(type(m_subobj)))

                    # Object of type Plane
                    if issubclass(type(m_subobj),
                                  Part.Face) and "Planes" in getfrom:
                        m_i = 0
                        for m_e in m_subobj.Edges:
                            m_i_in_list = find(m_e, m_obj.Object.Shape)
                            Selected_Entities.append([m_obj.Object,
                                                      "Edge" + str(m_i_in_list)])
                            m_i += 1
                        m_i = 0
                        if flag_remove:
                            self.removeItem(m_id)

                    # Object of type Edge
                    if issubclass(type(m_subobj),
                                  Part.Edge):
                        Selected_Entities.append([m_obj.Object,
                                                  m_obj.SubElementNames[m_i]])
                        m_i += 1
                        if flag_remove:
                            self.removeItem(id)
            else:
                m_shape = m_obj.Object.Shape
                m_i = 0

                if issubclass(type(m_shape),
                              Part.Edge) and "Segments" in getfrom:
                    m_i = addEdge(Selected_Entities,
                                  m_obj, m_i,
                                  m_shape)

                elif issubclass(type(m_shape),
                                Part.Compound):
                    m_i = addEdge(Selected_Entities,
                                  m_obj, m_i,
                                  m_shape)

                elif issubclass(type(m_shape),
                                Part.Solid) and "Objects" in getfrom:
                    m_i = addEdge(Selected_Entities,
                                  m_obj, m_i,
                                  m_shape)

                elif issubclass(type(m_shape),
                                Part.Wire) and "Curves" in getfrom:
                    m_i = addEdge(Selected_Entities,
                                  m_obj, m_i,
                                  m_shape)

                elif issubclass(type(m_shape),
                                Part.Face) and "Planes" in getfrom:
                    m_i = addEdge(Selected_Entities,
                                  m_obj, m_i,
                                  m_shape)

        if WF.verbose():
            print_msg("Number_of_Edges = " + str(len(Selected_Entities)))
            print_msg("Edge_List = " + str(Selected_Entities))

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)

        return (0, None)

    def get_segments(self, getfrom=["Points",
                                    "Segments",
                                    "Curves",
                                    "Planes",
                                    "Objects"]):
        """ Return all Segments found in Selection including
        the Segments from objects
        as (Number of Segments, list of Edges)
        In case of at least 2 points selected it will create
        a line from these 2 points
        Return None if no Segment detected
        """
        Selected_Entities = []

        if self.numberOfEntities == 0:
            return (0, None)

        if self.numberOfPoints >= 2 and "Points" in getfrom:
            for m_p1, m_p2 in zip(self.__selectedVertices,
                                  self.__selectedVertices[1:]):
                m_diff = m_p2.Point.sub(m_p1.Point)
                tolerance = 1e-10
                if abs(m_diff.x) <= tolerance and abs(
                        m_diff.y) <= tolerance and abs(m_diff.z) <= tolerance:
                    continue
                Selected_Entities.append(Part.makeLine(m_p2.Point, m_p1.Point))

        if self.numberOfSegments > 0 and "Segments" in getfrom:
            for m_edge in self.__selectedEdges:
                Selected_Entities.append(m_edge)
        # TOCOMPLETE
        if self.numberOfCurves > 0 and "Curves" in getfrom:
            for m_wire in self.__selectedWires:
                Selected_Entities.append(m_wire)

        if self.numberOfPlanes > 0 and "Planes" in getfrom:
            for m_face in self.__selectedFaces:
                m_edges_list = m_face.Edges
                for m_edge in m_edges_list:
                    Selected_Entities.append(m_edge)

        if self.numberOfObjects > 0 and "Objects" in getfrom:
            for m_object in self.__selectedObjects:
                for m_edge in m_object.Shape.Edges:
                    Selected_Entities.append(m_edge)

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)

    def get_curvesNames(
            self, getfrom=["Points", "Segments", "Curves", "Planes", "Objects"]):
        """
        return a list of [obj.Object,"Curve"+str(i)]
        """
        m_debug = True
        if m_debug:
            print("self.numberOfEntities = " + str(self.numberOfEntities))
        if self.numberOfEntities == 0:
            return (0, None)

#         def find(aCurve,inObject):
#             if hasattr(inObject, 'Curves'):
#                 m_i = 0
#                 for e in inObject.Curves:
#                     # We return the index + 1  of the vertex in the vertexes list when point match
#                     if geom.isEqualVectors(e.Point, aVertex.Point, tolerance=1e-12):
#                         # Needs to add 1 as for Edge1 corresponds to first 0 index in the list
#                         return (m_i + 1)
#                     m_i += 1
#             return None

        Selected_Entities = []

        for m_obj in self.__selEx:
            m_shape = m_obj.Object.Shape
            if m_debug:
                print("m_shape = " + str(m_shape))
                print("type(m_shape) = " + str(type(m_shape)))

            if m_obj.HasSubObjects:
                if m_debug:
                    print("m_obj.HasSubObjects")
                m_i = 0
                for m_subobj in m_obj.SubObjects:
                    if m_debug:
                        print("m_subobj = " + str(m_subobj))
                    if issubclass(type(m_subobj),
                                  Part.Edge) and "Segments" in getfrom:
                        Selected_Entities.append(
                            [m_obj.Object, m_obj.SubElementNames[m_i]])
                        m_i += 1
            else:
                if m_debug:
                    print("NOT m_obj.HasSubObjects")
                m_i = 0

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)

    def get_curves(
            self, getfrom=["Points", "Segments", "Curves", "Planes", "Objects"]):
        Selected_Entities = []

        if self.numberOfEntities == 0:
            return None

        if self.numberOfCurves > 0 and "Curves" in getfrom:
            for m_wire in self.__selectedWires:
                Selected_Entities.append(m_wire)

        if self.numberOfPlanes > 0 and "Planes" in getfrom:
            for m_face in self.__selectedFaces:
                m_wires_list = m_face.Wires
                for m_wire in m_wires_list:
                    Selected_Entities.append(m_wire)

        if self.numberOfObjects > 0 and "Objects" in getfrom:
            for m_object in self.__selectedObjects:
                for m_wire in m_object.Shape.Wires:
                    Selected_Entities.append(m_wire)

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)

    def get_planesNames(self, getfrom=["Planes", "Objects"]):
        """
        return a list of [obj.Object,"Face"+str(i)]
        """
        m_debug = True
        if m_debug:
            print("self.numberOfEntities = " + str(self.numberOfEntities))
        if self.numberOfEntities == 0:
            return (0, None)

        Selected_Entities = []

        for m_obj in self.__selEx:
            m_shape = m_obj.Object.Shape
            if m_debug:
                print("m_shape = " + str(m_shape))
                print("type(m_shape) = " + str(type(m_shape)))

            if m_obj.HasSubObjects:
                if m_debug:
                    print("m_obj.HasSubObjects")
                m_i = 0

                for m_subobj in m_obj.SubObjects:
                    if m_debug:
                        print("m_subobj = " + str(m_subobj))

                    if issubclass(type(m_subobj), Part.Face):
                        Selected_Entities.append(
                            [m_obj.Object, m_obj.SubElementNames[m_i]])
                        m_i += 1
            else:
                if m_debug:
                    print("NOT m_obj.HasSubObjects")
                m_i = 0

                if issubclass(type(m_shape), Part.Face):
                    Selected_Entities.append([m_obj.Object, "Face" + str(m_i)])
                    m_i += 1

                elif issubclass(type(m_shape), Part.Compound):
                    if hasattr(m_shape, 'Faces'):
                        for m_e in m_shape.Faces:
                            Selected_Entities.append(
                                [m_obj.Object, "Face" + str(m_i)])
                            m_i += 1

                elif issubclass(type(m_shape),
                                Part.Solid) and "Objects" in getfrom:
                    if hasattr(m_shape, 'Faces'):
                        for m_e in m_shape.Faces:
                            Selected_Entities.append(
                                [m_obj.Object, "Face" + str(m_i)])
                            m_i += 1

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)

    def get_planes(
            self, getfrom=["Points", "Segments", "Curves", "Planes", "Objects"]):
        Selected_Entities = []

        if self.numberOfEntities == 0:
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

        if self.numberOfPlanes > 0 and "Planes" in getfrom:
            for m_face in self.__selectedFaces:
                Selected_Entities.append(m_face)

        if self.numberOfObjects > 0 and "Objects" in getfrom:
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
