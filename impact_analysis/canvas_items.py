from qgis.gui import *
from qgis.core import QgsGeometry, QgsWkbTypes
from PyQt5 import QtGui

class CanvasItems(object):
    """
    Helper class for administrations of Rubberband and Vertex markers
    """
   
    def __init__(self, canvas, color, style, width, icon, size):
        self.markers = []
        self.canvas = canvas
        self.color = color
        self.style = style
        self.width = width
        self.icon = icon
        self.size = size

    def setMarkerGeom(self, geom):
        self.clearMarkerGeom()
        self._setMarkerGeom(geom)

    def setMarkerGeomBuffer(self, geom, buffer):
        self.clearMarkerGeom()
        geomb = geom.buffer(buffer,12)
        self._setMarkerGeom(geomb)

    def _setMarkerGeom(self, geom):
        if geom.isMultipart():
            geometries = self._extractAsSingle(geom)
            for g in geometries:
                self._setMarkerGeom(g)
        else:
            if geom.wkbType() == QgsWkbTypes.Point:
                m = self._setPointMarker(geom)
#            elif geom.wkbType() in (QgsWkbTypes.LineString, QgsWkbTypes.Polygon):
            else:
                m = self._setRubberBandMarker(geom)
            self.markers.append( m )

    def _setPointMarker(self, pointgeom):
        m = QgsVertexMarker(self.canvas)
        m.setColor(QtGui.QColor(self.color))
        m.setIconType(self.icon)
        m.setPenWidth(self.width)
        m.setIconSize(self.size)
        m.setCenter(pointgeom.asPoint())
        return m

    def _setRubberBandMarker(self, geom):
        m = QgsRubberBand(self.canvas, False)  # not polygon
        if geom.wkbType() == QgsWkbTypes.LineString:
            linegeom = geom
#        elif geom.wkbType() == QgsWkbTypes.Polygon:
        else:
            linegeom = QgsGeometry.fromPolylineXY(geom.asPolygon()[0])
        m.setToGeometry(linegeom, None)
        m.setColor(QtGui.QColor(self.color))
        m.setLineStyle(self.style)
        m.setWidth(self.width)
        return m

    def _extractAsSingle(self, geom):
        multiGeom = QgsGeometry()
        geometries = []
        if geom.type() == QgsWkbTypes.Point:
            if geom.isMultipart():
                multiGeom = geom.asMultiPoint()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPointXY(i))
            else:
                geometries.append(geom)
        elif geom.type() == QgsWkbTypes.LineString:
            if geom.isMultipart():
                multiGeom = geom.asMultiPolyline()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPolyline(i))
            else:
                geometries.append(geom)
        elif geom.type() == QgsWkbTypes.Polygon:
            if geom.isMultipart():
                multiGeom = geom.asMultiPolygon()
                for i in multiGeom:
                    geometries.append(QgsGeometry().fromPolygon(i))
            else:
                geometries.append(geom)
        return geometries

    def clearMarkerGeom(self):
        if self.markers:
            for m in self.markers:
                self.canvas.scene().removeItem(m)
        self.markers = []
        