# -*- coding: utf-8 -*-
import re
import FreeCAD as App
import Part
import WF
from WF_print import print_msg
import WF_geometry as geom
if App.GuiUp:
    import FreeCADGui as Gui

###############
M_DEBUG = True
###############


def getSel(verbose=0):
    """ Create and return A Selection Object
    and the active FreeCAD document.

    Return:
    -------
    (sel, doc) when success
    (None, message) when error

    Parameters
    -------
    *verbose*   : (Integer , Optional, default=0)
                if == 1 force the verbose mode.

    Examples
    -------
    >>> import WF_selection as sel
    >>> # Open a document in FreeCAD
    >>> m_in_file_name = u"/home/.../01.FCStd"
    >>> m_doc = App.open(m_in_file_name)
    >>> # Clear selection
    >>> Gui.Selection.clearSelection()
    >>> # You can use this to add your element to FreeCAD's selection :
    >>> Gui.Selection.addSelection(m_doc.Line001)
    >>> # Recover the selection Object m_sel
    >>> m_sel, m_act_doc = sel.getSel(verbose=0)
    """
    global M_DEBUG

    M_DEBUG = False
    if verbose:
        M_DEBUG = True

    m_doc = App.activeDocument()
    if m_doc is None:
        message = "No Active document selected !"
        return (None, message)
    if not m_doc.Name:
        message = "No Active document.name selected !"
        return (None, message)

    if M_DEBUG:
        print("Document      = " + str(m_doc))
        print("Document.Name = " + str(m_doc.Name))
        printObjectStructure()

    m_selEx = Gui.Selection.getSelectionEx(m_doc.Name)
    m_sel = Selection(m_selEx)

    if m_sel is None:
        message = "Unable to create a Selection Object !"
        print_msg(message)
        return (None, message)

    if M_DEBUG:
        print(str(m_sel))

    return m_sel, m_doc


def printObjectStructure():
    m_act_doc = App.activeDocument()
    print(str(m_act_doc.Name))

    m_selEx = Gui.Selection.getSelectionEx(m_act_doc.Name)

    for m_sel in m_selEx:
        print("|__" + str(m_sel.ObjectName) +
              " (type: " + str(m_sel.Object.Shape.ShapeType) + ")")

        if m_sel.HasSubObjects:
            for m_sub_obj_name, m_sub_obj in zip(
                    m_sel.SubElementNames, m_sel.SubObjects):
                print("   |__" + str(m_sub_obj_name) +
                      " (type: " + str(m_sub_obj.ShapeType) + ")")
        else:
            pass


def addSubItem(Sel, m_parent, m_name, m_i):
    Sel.append([m_parent, m_name])
    m_i += 1
    return m_i


def selection_debug(m_parent, m_name, m_i, m_type):
    m_shape = m_parent.Shape
    if WF.verbose():
        print_msg("   m_obj.Object = " + str(m_parent))
        print_msg("   m_obj.SubElementNames = " + str(m_name))
        print_msg("   m_obj.Object.Shape = " + str(m_shape))
        print_msg("   type(m_obj.Object.Shape) = " + str(m_type))
        print_msg("   m_i = " + str(m_i))


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

        number_of_edges, edge_list = m_sel.get_segments(
           getfrom=["Points","Segments","Curves","Planes","Objects"])

        """
        self.__numberOfEntities = 0
        self.__numberOfVertexes = 0
        self.__numberOfEdges = 0
        self.__numberOfWires = 0
        self.__numberOfFaces = 0
        self.__numberOfShells = 0
        self.__numberOfObjects = 0
        self.__numberOfImages = 0

        self.__selectedVertices = []
        self.__selectedVerticesNames = []
        self.__selectedEdges = []
        self.__selectedEdgesNames = []
        self.__selectedWires = []
        self.__selectedWiresNames = []
        self.__selectedFaces = []
        self.__selectedFacesNames = []
        self.__selectedShells = []
        self.__selectedShellsNames = []
        self.__selectedObjects = []
        self.__selectedObjectsNames = []
        self.__selectedImages = []
        self.__selectedImagesNames = []

        self.__selEx = Gui_Selection

        self.initialize()

    def storeShapeType(self, Parent, ObjectShape, Name=None, index=0):
        m_shape = ObjectShape
        if M_DEBUG:
            print("  Object.Shape = " + str(m_shape))

        if m_shape == "Vertex":
            self.__selectedVertices.append(Parent)
            self.__selectedVerticesNames.append("Vertex" + str(index))
            return True
        if m_shape == "Edge":
            self.__selectedEdges.append(Parent)
            self.__selectedEdgesNames.append("Edge" + str(index))
            return True
        if m_shape == "Wire":
            self.__selectedWires.append(Parent)
            self.__selectedWiresNames.append("Wire" + str(index))
            return True
        if m_shape == "Face":
            self.__selectedFaces.append(Parent)
            self.__selectedFacesNames.append("Face" + str(index))
            return True
        if m_shape == "Shell":
            self.__selectedShells.append(Parent)
            self.__selectedShellsNames.append("Shell" + str(index))
            return True
            # TO DO insert Object type
        print("Unknown ShapeType !")
        return False

    def initialize(self):
        if self.__selEx is None:
            message = "No Selection from Active document passed !"
            print_msg(message)
            return message

        if len(self.__selEx) < 1:
            message = "No Entity selected !"
            print_msg(message)
            return message

        for m_obj in self.__selEx:
            if not m_obj.HasSubObjects:
                if M_DEBUG:
                    print("NO SubObjects !")
                if hasattr(m_obj, 'Object'):
                    m_parent = m_obj.Object
                    m_object = m_obj.Object
                    m_name = m_obj.Object.Name
#                     if hasattr(m_object, 'ShapeType'):
#                         self.storeShapeType(m_object, m_name)
                    if hasattr(m_object, 'Shape'):
                        self.storeShapeType(
                            m_parent, m_object.Shape.ShapeType, m_name)
#                     if hasattr(m_object, 'ImageFile'):
#                         self.__selectedImages.append(m_object)
            else:
                if M_DEBUG:
                    print("SOME SubObjects !")
                m_parent = m_obj.Object
                m_parent_name = m_obj.ObjectName
                for m_name, m_object in zip(
                        m_obj.SubElementNames, m_obj.SubObjects):
                    m_index = re.sub('[^0-9]', '', m_name)
                    index = int(m_index)
                    m_composite_name = str(m_parent_name) + "." + str(m_name)
                    if hasattr(m_object, 'ShapeType'):
                        self.storeShapeType(
                            m_parent, m_object.ShapeType, m_composite_name, index)
#                     if hasattr(m_object, 'Shape'):
#                         self.storeShapeType(m_object, m_composite_name)
#                     if hasattr(m_object, 'ImageFile'):
#                         self.__selectedImages.append(m_object)

        self.__numberOfVertexes = len(self.__selectedVertices)
        self.__numberOfEdges = len(self.__selectedEdges)
        self.__numberOfWires = len(self.__selectedWires)
        self.__numberOfFaces = len(self.__selectedFaces)
        self.__numberOfShells = len(self.__selectedShells)
        self.__numberOfObjects = len(self.__selectedObjects)
        self.__numberOfImages = len(self.__selectedImages)
        self.__numberOfEntities = self.__numberOfVertexes + \
            self.__numberOfEdges + self.__numberOfWires + self.__numberOfFaces + \
            self.__numberOfShells + \
            self.__numberOfObjects + self.__numberOfImages

        message = "Selection.initialize done !"
        if M_DEBUG:
            print_msg(message)
        return

    def removeItem(self, m_id):
        if M_DEBUG:
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

    numberOfSegments = property(
        __getNumberOfSegments,
        __setNumberOfSegments)

    def __getSelectedEdges(self):
        return self.__selectedEdges

    def __setSelectedEdges(self, val):
        self.__selectedEdges = val

    selectedEdges = property(
        __getSelectedEdges,
        __setSelectedEdges)

    def __getSelectedEdgesNames(self):
        return self.__selectedEdgesNames

    def __setSelectedEdgesNames(self, val):
        self.__selectedEdgesNames = val

    selectedEdgesNames = property(
        __getSelectedEdgesNames,
        __setSelectedEdgesNames)

    def __getNumberOfCurves(self):
        return self.__numberOfWires

    def __setNumberOfCurves(self, val):
        self.__numberOfWires = val

    numberOfCurves = property(
        __getNumberOfCurves,
        __setNumberOfCurves)

    def __getNumberOfPlanes(self):
        return self.__numberOfFaces

    def __setNumberOfPlanes(self, val):
        self.__numberOfFaces = val

    numberOfPlanes = property(
        __getNumberOfPlanes,
        __setNumberOfPlanes)

    def __getSelectedPlanes(self):
        return self.__selectedFaces

    def __setSelectedPlanes(self, val):
        self.__selectedFaces = val

    selectedPlanes = property(
        __getSelectedPlanes,
        __setSelectedPlanes)

    def __getSelectedPlanesNames(self):
        return self.__selectedFacesNames

    def __setSelectedPlanesNames(self, val):
        self.__selectedFacesNames = val

    selectedPlanesNames = property(
        __getSelectedPlanesNames,
        __setSelectedPlanesNames)

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
        message = "\nGui_Selection        = " + str(self.__selEx)
        message += "\nNumber Of Images     = " + str(self.__numberOfImages)
        message += " " + str(self.__selectedImages)
        message += " " + str(self.__selectedImagesNames)
        message += "\nNumber Of Objects    = " + str(self.__numberOfObjects)
        message += " " + str(self.__selectedObjects)
        message += " " + str(self.__selectedObjectsNames)
        message += "\nNumber Of Shells     = " + str(self.__numberOfShells)
        message += " " + str(self.__selectedShells)
        message += " " + str(self.__selectedShellsNames)
        message += "\nNumber Of Planes     = " + str(self.__numberOfFaces)
        message += " " + str(self.__selectedFaces)
        message += " " + str(self.__selectedFacesNames)
        message += "\nNumber Of Curves     = " + \
            str(self.__numberOfWires)
        message += " " + str(self.__selectedWires)
        message += " " + str(self.__selectedWiresNames)
        message += "\nNumber Of Segments   = " + \
            str(self.__numberOfEdges)
        message += " " + str(self.__selectedEdges)
        message += " " + str(self.__selectedEdgesNames)
        message += "\nNumber Of Points     = " + \
            str(self.__numberOfVertexes)
        message += " " + str(self.__selectedVertices)
        message += " " + str(self.__selectedVerticesNames)
        message += "\nNumber Of Entities   = " + \
            str(self.__numberOfEntities)
        return (message)

    def get_vertexesFromPlane(self, subObj, selObject, SelEntities):
        # Object of type Plane
        m_i = 0
        for m_v in subObj.Vertexes:
            m_i_in_list = find(m_v, selObject.Shape)
            SelEntities.append([selObject,
                                "Vertex" + str(m_i_in_list)])
            m_i += 1

        # Managing Vertexes
        # Managing Edges
        # Managing Wires
        # Managing Faces
        # Managing Solids
        # Managing Compounds

    def get_pointsWithNames(self,
                            get_from=["Points"]
                            ):
        """ Return all Points found in Selection object.
        depending of 'getFrom' parameter.

        Return
        -------
        A tuple : (Number, Selected_Points)
        Selected_Pointss as a list of [obj.Object, Name]

        (0, None) if no Point detected

        Parameters
        -------
        *get_from* : (List of string, Optional, default=["Points"]
                    A list of object to look into.
                    can be :
                    "Points"
                    "Segments", "Curves",
                    "Planes", "Objects", "Sets"

        Examples
        -------
        """
        if M_DEBUG:
            print("\nrunning Selection.get_pointsWithNames !")
            print("get_from=" + str(get_from))
        if self.numberOfEntities == 0:
            return (0, None)

        m_sel_items = []

        # Managing Vertexes
        if self.__numberOfVertexes != 0 and "Points" in get_from:
            for m_v, m_l in zip(self.__selectedVertices,
                                self.__selectedVerticesNames):
                m_sel_items.append([m_v, m_l])
        # Managing Edges
        if self.__numberOfEdges != 0 and "Segments" in get_from:
            for m_f, m_l in zip(self.__selectedEdges,
                                self.__selectedEdgesNames):
                if hasattr(m_f.Shape, 'Vertexes'):
                    for index, m_e in enumerate(m_f.Shape.Vertexes, 0):
                        m_sel_items.append([m_f, "Vertex" + str(index)])
        # Managing Wires
        # Managing Faces
        if self.__numberOfFaces != 0 and "Planes" in get_from:
            for m_f, m_l in zip(self.__selectedFaces,
                                self.__selectedFacesNames):
                if hasattr(m_f.Shape, 'Vertexes'):
                    for index, m_e in enumerate(m_f.Shape.Vertexes, 0):
                        m_sel_items.append([m_f, "Vertex" + str(index)])
        # Managing Shells
        # Managing Solids
        # Managing Compounds

        if WF.verbose():
            print_msg("number_of_vertexes = " + str(len(m_sel_items)))
            print_msg("vertex_list = " + str(m_sel_items))

        if len(m_sel_items) != 0:
            return (len(m_sel_items), m_sel_items)

        return (0, None)

    def get_segmentsWithNames(self,
                              get_from=["Segments"]
                              ):
        """ Return all Segments found in Selection object.

        Return
        ----------
        A tuple : (Number, Selected_Segments)
        Selected_Segments as a list of [obj.Object, Name]

        (0, None) if no Segment detected

        Parameters
        -------
        *get_from* : (List of string, Optional, default=["Segments"]
                    A list of object to look into.
                    can be :
                    "Segments", "Curves",
                    "Planes",  "Shells",
                    "Objects", "Sets"

        Examples
        -------
        """
        if M_DEBUG:
            print("\nrunning Selection.get_segmentsWithNames !")
            print("get_from=" + str(get_from))
        if self.numberOfEntities == 0:
            return (0, None)

        m_sel_items = []

        # Managing Vertexes : Not valid
        # Managing Edges
        if self.__numberOfEdges != 0 and "Segments" in get_from:
            for m_e, m_l in zip(self.__selectedEdges,
                                self.__selectedEdgesNames):
                m_sel_items.append([m_e, m_l])

        # Managing Wires
        if self.__numberOfWires != 0 and "Curves" in get_from:
            for m_f, m_l in zip(self.__selectedWires,
                                self.__selectedWiresNames):
                if hasattr(m_f.Shape, 'Edges'):
                    for index, m_e in enumerate(m_f.Shape.Edges, 0):
                        m_sel_items.append([m_f, "Edge" + str(index)])

        # Managing Faces
        if self.__numberOfFaces != 0 and "Planes" in get_from:
            for m_f, m_l in zip(self.__selectedFaces,
                                self.__selectedFacesNames):
                if hasattr(m_f.Shape, 'Edges'):
                    for index, m_e in enumerate(m_f.Shape.Edges, 0):
                        m_sel_items.append([m_f, "Edge" + str(index)])
#                 if not m_f.HasSubObjects:
#                     if hasattr(m_f.Shape, 'Edges'):
#                         for index, m_e in enumerate(m_f.Shape.Edges, 0):
#                             m_sel_items.append([m_f, "Edge" + str(index)])
#                 else:
#                     m_index = re.sub('[^0-9]', '', m_l)
#                     if hasattr(m_f.SubObjects[m_index - 1], 'Edges'):
#                         for index, m_e in enumerate(
#                                 m_f.SubObjects[m_index - 1].Edges, 0):
#                             m_sel_items.append(
#                                 [m_f.SubObjects[m_index - 1], "Edge" + str(index)])
        # Managing Shells
        if self.__numberOfShells != 0 and "Shells" in get_from:
            for m_f, m_l in zip(self.__selectedShells,
                                self.__selectedShellsNames):
                print(m_f)
                if hasattr(m_f.Shape, 'Edges'):
                    for index, m_e in enumerate(m_f.Shape.Edges, 0):
                        m_sel_items.append([m_f, "Edge" + str(index)])
        # Managing Solids
        # Managing Compounds

        if WF.verbose():
            print_msg("number_of_edges = " + str(len(m_sel_items)))
            print_msg("edge_list = " + str(m_sel_items))

        if len(m_sel_items) != 0:
            return (len(m_sel_items), m_sel_items)

        return (0, None)

    def get_curvesWithNames(self):
        pass

    def get_planesWithNames(self):
        pass

    def get_shellsWithNames(self):
        pass

    def get_objectsWithNames(self):
        pass

    def get_setsWithNames(self):
        pass

    def get_curvesNames(
            self, getfrom=["Points", "Segments", "Curves", "Planes", "Objects"]):
        """
        return a list of [obj.Object,"Curve"+str(i)]
        """
        M_DEBUG = True
        if M_DEBUG:
            print("self.numberOfEntities = " + str(self.numberOfEntities))
        if self.numberOfEntities == 0:
            return (0, None)

        Selected_Entities = []

        for m_obj in self.__selEx:
            m_shape = m_obj.Object.Shape
            if M_DEBUG:
                print("m_shape = " + str(m_shape))
                print("type(m_shape) = " + str(type(m_shape)))

            if m_obj.HasSubObjects:
                if M_DEBUG:
                    print("m_obj.HasSubObjects")
                m_i = 0
                for m_subobj in m_obj.SubObjects:
                    if M_DEBUG:
                        print("m_subobj = " + str(m_subobj))
                    if issubclass(type(m_subobj),
                                  Part.Edge) and "Segments" in getfrom:
                        Selected_Entities.append(
                            [m_obj.Object, m_obj.SubElementNames[m_i]])
                        m_i += 1
            else:
                if M_DEBUG:
                    print("NOT m_obj.HasSubObjects")
                m_i = 0

        if len(Selected_Entities) != 0:
            return (len(Selected_Entities), Selected_Entities)
        else:
            return (0, None)

    def get_planesNames(self, getfrom=["Planes", "Objects"]):
        """
        return a list of [obj.Object,"Face"+str(i)]
        """
        M_DEBUG = True
        if M_DEBUG:
            print("self.numberOfEntities = " + str(self.numberOfEntities))
        if self.numberOfEntities == 0:
            return (0, None)

        Selected_Entities = []

        for m_obj in self.__selEx:
            m_shape = m_obj.Object.Shape
            if M_DEBUG:
                print("m_shape = " + str(m_shape))
                print("type(m_shape) = " + str(type(m_shape)))

            if m_obj.HasSubObjects:
                if M_DEBUG:
                    print("m_obj.HasSubObjects")
                m_i = 0

                for m_subobj in m_obj.SubObjects:
                    if M_DEBUG:
                        print("m_subobj = " + str(m_subobj))

                    if issubclass(type(m_subobj), Part.Face):
                        Selected_Entities.append(
                            [m_obj.Object, m_obj.SubElementNames[m_i]])
                        m_i += 1
            else:
                if M_DEBUG:
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
