import lx, lxu, traceback
from lxifc import UIValueHints, Visitor
from operator import ior

class MeshEditorClass():
    def __init__(self, args = None, mesh_edit_flags = []):
        self.args = args
        self.mesh_edit_flags = mesh_edit_flags
        self.mesh = None
        self.mesh_svc = None
        self.polygon_accessor = None
        self.edge_accessor = None
        self.meshmap_accessor = None
        self.point_accessor = None

    def mesh_edit_action(self):
        return None

    def mesh_read_action(self):
        return None

    def do_mesh_edit(self):
        return self.mesh_edit()

    def do_mesh_read(self):
        return self.mesh_edit(True)

    def mesh_edit(self, read_only=False):
        """Adapted from James O'Hare's excellent code: https://gist.github.com/Farfarer/31148a78f392a831239d9b018b90330c"""

        if read_only:
            scan_allocate = lx.symbol.f_LAYERSCAN_ACTIVE | lx.symbol.f_LAYERSCAN_MARKPOLYS
        if not read_only:
            scan_allocate = lx.symbol.f_LAYERSCAN_EDIT

        layer_svc = lx.service.Layer ()
        layer_scan = lx.object.LayerScan (layer_svc.ScanAllocate (scan_allocate))

        self.mesh_svc = lx.service.Mesh ()

        if not layer_scan.test ():
            return

        for n in xrange (layer_scan.Count ()):
            if read_only:
                self.mesh = lx.object.Mesh (layer_scan.MeshBase(n))
            if not read_only:
                self.mesh = lx.object.Mesh (layer_scan.MeshEdit(n))

            if not self.mesh.test ():
                continue

            polygon_count = self.mesh.PolygonCount ()
            if polygon_count == 0:
                continue

            self.polygon_accessor = lx.object.Polygon (self.mesh.PolygonAccessor ())
            if not self.polygon_accessor.test ():
                continue

            self.edge_accessor = lx.object.Edge (self.mesh.EdgeAccessor ())
            if not self.edge_accessor.test ():
                continue

            self.point_accessor = lx.object.Point (self.mesh.PointAccessor ())
            if not self.point_accessor.test ():
                continue

            self.meshmap_accessor = lx.object.MeshMap (self.mesh.MeshMapAccessor ())
            if not self.meshmap_accessor.test ():
                continue

            try:
                if read_only:
                    self.mesh_read_action()
                if not read_only:
                    self.mesh_edit_action()
            except:
                lx.out(traceback.print_exc())
                break

            if self.mesh_edit_flags and not read_only:
                layer_scan.SetMeshChange (n, reduce(ior, self.mesh_edit_flags))

        layer_scan.Apply ()

    def get_active_polys_by_island(self):
        mark_mode_checked = self.mesh_svc.ModeCompose ('user0', None)
        mark_mode_unchecked = self.mesh_svc.ModeCompose (None, 'user0')

        visClear = SetMarksClass (self.polygon_accessor, mark_mode_unchecked)
        self.polygon_accessor.Enumerate (mark_mode_checked, visClear, 0)

        visIslands = PolysByIslandClass (self.polygon_accessor, self.point_accessor, mark_mode_checked)
        self.polygon_accessor.Enumerate (mark_mode_unchecked, visIslands, 0)

        return visIslands.islands

    def get_active_polys(self):
        mark_mode_selected = self.mesh_svc.ModeCompose (lx.symbol.sMARK_SELECT, None)
        mark_mode_valid = self.mesh_svc.ModeCompose (None, 'hide lock')

        visitor = PolysClass (self.polygon_accessor, self.edge_accessor, mark_mode_valid)
        self.polygon_accessor.Enumerate (mark_mode_selected, visitor, 0)

        return visitor.getPolyIDs()

    def get_selected_polys_by_island(self):
        mark_mode_toCheck = self.mesh_svc.ModeCompose (lx.symbol.sMARK_SELECT, lx.symbol.sMARK_USER_0)
        mark_mode_valid = self.mesh_svc.ModeCompose (None, ' '.join ((lx.symbol.sMARK_USER_0, lx.symbol.sMARK_HIDE, lx.symbol.sMARK_LOCK)))
        mark_mode_checked = self.mesh_svc.ModeCompose (lx.symbol.sMARK_USER_0, None)
        mark_mode_clearChecked = self.mesh_svc.ModeCompose (None, lx.symbol.sMARK_USER_0)

        # Wipe any existing user0 marks on the polygons, just so they don't interfere with our marks.
        visClear = SetMarksClass (self.polygon_accessor, mark_mode_clearChecked)
        self.polygon_accessor.Enumerate (mark_mode_checked, visClear, 0)

        visitor = PolysByConnectedClass (self.polygon_accessor, self.edge_accessor, mark_mode_valid, mark_mode_checked)
        self.polygon_accessor.Enumerate (mark_mode_toCheck, visitor, 0)

        return visitor.getIslands()

    def get_selected_polys_by_flood(self, i_POLYTAG = lx.symbol.i_POLYTAG_MATERIAL):
        mark_mode_selected = self.mesh_svc.ModeCompose (lx.symbol.sMARK_SELECT, None)
        mark_mode_valid = self.mesh_svc.ModeCompose (None, 'hide lock')

        visitor = PolysByTagFloodClass (self.polygon_accessor, self.edge_accessor, mark_mode_valid, i_POLYTAG)
        self.polygon_accessor.Enumerate (mark_mode_selected, visitor, 0)

        return visitor.getPolyIDs()

    def get_selected_polys(self):
        mark_mode = self.mesh_svc.ModeCompose (lx.symbol.sMARK_SELECT, 'hide lock')
        selectedPolygons = set()
        polyCount = self.mesh.PolygonCount ()

        for p in xrange(polyCount):
            self.polygon_accessor.SelectByIndex(p)
            if self.polygon_accessor.TestMarks (mark_mode):
                selectedPolygons.add (self.polygon_accessor.ID())

        return selectedPolygons

class SetMarksClass(Visitor):
    def __init__(self, acc, mark):
        self.acc = acc
        self.mark = mark

    def vis_Evaluate(self):
        self.acc.SetMarks(self.mark)

class PolysClass (Visitor):
    def __init__ (self, polygon, edge, mark_mode_valid):
        self.polygon = polygon
        self.edge = edge
        self.mark_mode_valid = mark_mode_valid

        self.polygonIDs = set ()

    def reset (self):
        self.polygonIDs = set ()

    def getPolyIDs (self):
        return self.polygonIDs

    def vis_Evaluate (self):
        self.polygonIDs.add(self.polygon.ID())

class PolysByConnectedClass (Visitor):
    def __init__ (self, polygon, edge, mark_mode_valid, mark_mode_checked):
        self.polygon = polygon
        self.edge = edge
        self.mark_mode_valid = mark_mode_valid
        self.mark_mode_checked = mark_mode_checked

        self.polygonIDs = None
        self.islands = []

    def reset (self):
        self.islands = []
        self.polygonIDs = None

    def getPolyIDs (self):
        if not self.polygonIDs:
            self.polygonIDs = set ()
            for island in self.islands:
                self.polygonIDs |= set(island)
        return self.polygonIDs

    def getIslands(self):
        return self.islands

    def vis_Evaluate (self):
        inner_list = set ()
        outer_list = set ()

        this_polygon_ID = self.polygon.ID ()

        outer_list.add (this_polygon_ID)

        while len(outer_list) > 0:
            polygon_ID = outer_list.pop ()

            self.polygon.Select (polygon_ID)
            inner_list.add (polygon_ID)
            self.polygon.SetMarks (self.mark_mode_checked)

            num_points = self.polygon.VertexCount ()
            polygon_points = [self.polygon.VertexByIndex (p) for p in xrange (num_points)]

            for p in xrange (num_points):
                self.edge.SelectEndpoints (polygon_points[p], polygon_points[(p+1)%num_points])
                for e in xrange (self.edge.PolygonCount ()):
                    edge_polygon_ID = self.edge.PolygonByIndex (e)
                    if edge_polygon_ID != polygon_ID and edge_polygon_ID not in inner_list and edge_polygon_ID not in outer_list:
                        self.polygon.Select (edge_polygon_ID)
                        if self.polygon.TestMarks (self.mark_mode_valid):
                            outer_list.add (edge_polygon_ID)

        self.islands.append (tuple(inner_list))

class PolysByTagFloodClass (Visitor):
    def __init__ (self, polygon, edge, mark_mode_valid, i_POLYTAG):
        self.polygon = polygon
        self.edge = edge
        self.mark_mode_valid = mark_mode_valid

        self.polygonIDs = set ()

        self.tag = lx.object.StringTag ()
        self.tag.set (self.polygon)

        self.i_POLYTAG = i_POLYTAG
        self.tagValues = None

    def reset (self):
        self.polygonIDs = set ()

    def getPolyIDs (self):
        return self.polygonIDs

    def vis_Evaluate (self):
        inner_list = set ()
        outer_list = set ()

        this_polygon_ID = self.polygon.ID ()

        if self.tagValues == None:
            tagValues = self.tag.Get (self.i_POLYTAG)
        else:
            tagValues = self.tagValues

        if not tagValues:
            tagValues = []

        if not isinstance(tagValues, list):
            tagValues = tagValues.split(";")

        if this_polygon_ID not in outer_list:
            outer_list.add (this_polygon_ID)

            while len(outer_list) > 0:
                polygon_ID = outer_list.pop ()

                self.polygon.Select (polygon_ID)
                inner_list.add (polygon_ID)

                num_points = self.polygon.VertexCount ()
                polygon_points = [self.polygon.VertexByIndex (p) for p in xrange (num_points)]

                for p in xrange (num_points):
                    self.edge.SelectEndpoints (polygon_points[p], polygon_points[(p+1)%num_points])
                    if self.edge.test ():
                        for e in xrange (self.edge.PolygonCount ()):
                            edge_polygon_ID = self.edge.PolygonByIndex (e)
                            if edge_polygon_ID != polygon_ID:
                                if edge_polygon_ID not in outer_list and edge_polygon_ID not in inner_list:
                                    self.polygon.Select (edge_polygon_ID)

                                    tagString = self.tag.Get (self.i_POLYTAG)
                                    if not tagString:
                                        tagString = ''

                                    if self.polygon.TestMarks (self.mark_mode_valid) and (set(tagString.split(";")).intersection(set(tagValues))):
                                        outer_list.add (edge_polygon_ID)

        self.polygonIDs.update (inner_list)

class PolysByIslandClass (Visitor):
    def __init__ (self, polygon, point, mark):
        self.polygon = polygon
        self.point = point
        self.mark = mark
        self.islands = []

    def vis_Evaluate (self):
        inner = set ()
        outer = set ()

        outer.add (self.polygon.ID ())

        while len(outer) > 0:
            polygon_ID = outer.pop ()

            self.polygon.Select (polygon_ID)
            self.polygon.SetMarks (self.mark)
            inner.add (polygon_ID)

            num_points = self.polygon.VertexCount ()
            for v in xrange (num_points):
                self.point.Select (self.polygon.VertexByIndex (v))
                num_polys = self.point.PolygonCount ()
                for p in xrange (num_polys):
                    vert_polygon_ID = self.point.PolygonByIndex (p)
                    if vert_polygon_ID not in inner:
                        outer.add (vert_polygon_ID)
        self.islands.append (inner)
