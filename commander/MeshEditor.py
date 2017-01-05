import lx, lxu, traceback
from lxifc import UIValueHints, Visitor
from operator import ior

class MeshEditorClass:
    def __init__(self, args=None, mesh_edit_flags=None):
        self.args = args
        self.mesh_edit_flags = mesh_edit_flags
        if self.mesh_edit_flags == None:
            self.mesh_edit_flags = []
        self.mesh_svc = None
        self.mesh = None
        self.mark_mode_checked = None
        self.mark_mode_unchecked = None
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
        """Adapted from James O'Hare's excellent code:
        https://gist.github.com/Farfarer/31148a78f392a831239d9b018b90330c"""

        if read_only:
            scan_allocate = lx.symbol.f_LAYERSCAN_ACTIVE | lx.symbol.f_LAYERSCAN_MARKPOLYS
        else:
            scan_allocate = lx.symbol.f_LAYERSCAN_EDIT

        layer_svc = lx.service.Layer()
        layer_scan = lx.object.LayerScan(layer_svc.ScanAllocate(scan_allocate))

        if not layer_scan.test():
            return

        self.mesh_svc = lx.service.Mesh()
        self.mark_mode_checked = self.mesh_svc.ModeCompose('user0', None)
        self.mark_mode_unchecked = self.mesh_svc.ModeCompose(None, 'user0')

        for n in xrange(layer_scan.Count()):
            if read_only:
                self.mesh = lx.object.Mesh(layer_scan.MeshBase(n))
            if not read_only:
                self.mesh = lx.object.Mesh(layer_scan.MeshEdit(n))

            if not self.mesh.test():
                continue

            polygon_count = self.mesh.PolygonCount()
            if polygon_count == 0:
                continue

            self.polygon_accessor = lx.object.Polygon(self.mesh.PolygonAccessor())
            if not self.polygon_accessor.test():
                continue

            self.edge_accessor = lx.object.Edge(self.mesh.EdgeAccessor())
            if not self.edge_accessor.test():
                continue

            self.point_accessor = lx.object.Point(self.mesh.PointAccessor())
            if not self.point_accessor.test():
                continue

            self.meshmap_accessor = lx.object.MeshMap(self.mesh.MeshMapAccessor())
            if not self.meshmap_accessor.test():
                continue

            visClear = SetMarksClass(self.polygon_accessor, self.mark_mode_unchecked)
            self.polygon_accessor.Enumerate(self.mark_mode_checked, visClear, 0)

            if read_only:
                self.mesh_read_action()
            if not read_only:
                self.mesh_edit_action()

            if self.mesh_edit_flags and not read_only:
                layer_scan.SetMeshChange(n, reduce(ior, self.mesh_edit_flags))

        layer_scan.Apply()

    def get_polys_by_island(self):
        visIslands = PolysByIslandClass(self.polygon_accessor, self.point_accessor, self.mark_mode_checked)
        self.polygon_accessor.Enumerate(self.mark_mode_unchecked, visIslands, 0)

        return visIslands.islands

    def get_polys_by_selected(self):
        mark_mode = self.mesh_svc.ModeCompose(lx.symbol.sMARK_SELECT, 'hide lock')

        selectedPolygons = set()

        polyCount = self.mesh.PolygonCount()
        for p in xrange(polyCount):
            self.polygon_accessor.SelectByIndex(p)
            if self.polygon_accessor.TestMarks(mark_mode):
                selectedPolygons.add(self.polygon_accessor.ID())

        return selectedPolygons


class SetMarksClass(Visitor):
    def __init__(self, acc, mark):
        self.acc = acc
        self.mark = mark

    def vis_Evaluate(self):
        self.acc.SetMarks(self.mark)


class PolysByIslandClass(Visitor):
    def __init__(self, polygon, point, mark):
        self.polygon = polygon
        self.point = point
        self.mark = mark
        self.islands = []

    def vis_Evaluate(self):
        inner = set()
        outer = set()

        outer.add(self.polygon.ID())

        while len(outer) > 0:
            polygon_ID = outer.pop()

            self.polygon.Select(polygon_ID)
            self.polygon.SetMarks(self.mark)
            inner.add(polygon_ID)

            num_points = self.polygon.VertexCount()
            for v in xrange(num_points):
                self.point.Select(self.polygon.VertexByIndex(v))
                num_polys = self.point.PolygonCount()
                for p in xrange(num_polys):
                    vert_polygon_ID = self.point.PolygonByIndex(p)
                    if vert_polygon_ID not in inner:
                        outer.add(vert_polygon_ID)
        self.islands.append(inner)
