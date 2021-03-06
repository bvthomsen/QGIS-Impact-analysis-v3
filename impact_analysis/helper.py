# -*- coding: utf-8 -*-
from PyQt5.QtCore import QCoreApplication, QSettings, QVariant, Qt
from PyQt5.QtWidgets import QTreeWidgetItem
from qgis.core  import QgsMessageLog, Qgis, QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry, QgsLayerTreeGroup, QgsWkbTypes, QgsField, QgsFeatureRequest
from qgis.utils import iface
from json import load, loads
from inspect import currentframe
from os import path

trClassName= ''

def hLog (mess,tab):

    QgsMessageLog.logMessage(mess,tab, Qgis.Info)


def trInit(message):

    global trClassName
    trClassName = message

# noinspection PyMethodMayBeStatic
def tr(message):

    global trClassName
    return QCoreApplication.translate(trClassName, message)


def hInfo (mess1,mess2,duration):

    iface.messageBar().pushMessage (mess1,mess2, Qgis.Info, duration)

def hWarning (mess1,mess2,duration):

    iface.messageBar().pushMessage (mess1,mess2, Qgis.Warning, duration)

def hCritical (mess1,mess2,duration):

    iface.messageBar().pushMessage (mess1,mess2, Qgis.Critical,duration)

def xStr(s):

    return '' if s is None else str(s)


def readConfig():

    data = None
    s = QSettings()

    hLog(__package__,currentframe().f_code.co_name)
    filename =  s.value(__package__ + '/settings','Path to the settings json file',type=str)
    s.setValue(__package__ + '/settings', filename)

    if filename != 'Path to the settings json file':
        try:
            with open(filename) as file:
                data = load(file)
                data['path'] = path.dirname(path.abspath(filename))
        except:
            hCritical (tr('Read configuration error; configuration failed'),tr('Settings json-file is missing or in error: ') + filename, 10)
    else:
        hCritical (tr('Read configuration error; configuration failed'),tr('Set the path to the settings json-file using menu "Settings" -> "Options" -> "Advanced" -> "impact_analysis" -> "Settings"'), 20)

    return data

def addMemoryLayer2tree (type, epsg, name, style, tree, tb):

    epsg = epsg.upper().replace('EPSG:','')

    vl = QgsVectorLayer(wkbtype2str(type)+"?crs=epsg:"+epsg, name , "memory")
    vl.dataProvider().addAttributes([QgsField("id",  QVariant.Int)])
    vl.updateFields()

    if tb:
        n = tree.insertLayer(0,vl)
    else:
        n = tree.addLayer(vl)

    QgsProject.instance().addMapLayer(vl, False)
    hLog(style,currentframe().f_code.co_name)
    vl.loadNamedStyle(style)
    vl.triggerRepaint()

    return vl

def addMemoryLayer2treeNG (name , attr, tree, tb):

    vl = QgsVectorLayer('none', name , "memory")
    vl.dataProvider().addAttributes(attr)
    vl.updateFields()

    if tb:
        n = tree.insertLayer(0,vl)
    else:
        n = tree.addLayer(vl)

    QgsProject.instance().addMapLayer(vl, False)

    return vl

def layerCrs (layer):
    return int (layer.dataProvider().crs().authid()[5:])

def crs2int (crs):
    return int (crs.upper().replace('EPSG:',''))

def removeGroup(groupName):

    # Find conflict group if exists and remove it
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(groupName)
    if group is not None:
        root.removeChildNode(group)

def removeGroupLayer(groupName,layer):

    # Find group if exists

    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(groupName)
    if group is not None:
        # Find layer if exists
        ln = group.findLayer (layer)
        if layer is not None:
            group.removeChildNode(ln)

def clearGroupLayer(groupName,layer):

    # Find group if exists
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(groupName)
    if group is not None:
        ln = group.findLayer (layer)
        if ln is not None:
            ln.layer().dataProvider.truncate()
            return ln

    return None


def cnvobj2obj (gobj,epsg_in,epsg_out):

    if epsg_in == epsg_out:
        return gobj

    else:
        crsSrc = QgsCoordinateReferenceSystem(epsg_in)
        crsDest = QgsCoordinateReferenceSystem(epsg_out)
        xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        i = gobj.transform(xform)
        return gobj

def cnvobj2wkt (gobj,epsg_in,epsg_out):

    return cnvobj2obj(gobj,epsg_in,epsg_out).asWkt()

def cnvwkt2obj (wkt,epsg_in,epsg_out):

    return cnvobj2obj(QgsGeometry.fromWkt(wkt),epsg_in,epsg_out)

def cnvwkt2wkt (wkt,epsg_in,epsg_out):

    return cnvobj2wkt(QgsGeometry.fromWkt(wkt),epsg_in,epsg_out)

def wkbtype2simple (type):

    my_WkbType = {0:'pnt', 1:'pnt', 2:'lin', 3:'pol', 4:'pnt', 5:'lin', 6:'pol'}
    return my_WkbType[type]

def wkbtype2str (type):

    my_WkbType = {0:'Unknown', 1:'Point', 2:'LineString', 3:'Polygon', 4:'MultiPoint', 5:'MultiLineString', 6:'MultiPolygon', 100:'NoGeometry'}
    return my_WkbType[type]

def fillResultTree (tree, layer, lid, jvar, rc, u1c, u2c):

    # Unfold json
    jDict = loads(jvar)
    res = jDict[rc]
    url1 = jDict[u1c]
    url2 = jDict[u2c]

    # Create parent
    parent = QTreeWidgetItem(tree)
    parent.setText(0,tr(u'{} ({} overlaps)').format(layer.name(),layer.featureCount()))
    parent.setText(1,str(lid))
    parent.setText(2,str(layer.name()))
    parent.setText(3,str(layer.featureCount()))
    parent.setFlags( Qt.ItemIsEnabled| Qt.ItemIsUserCheckable | Qt.ItemIsTristate ) #parent.flags() |
    parent.setCheckState(0, Qt.Checked)

    # Iterate through layer sorted by resColumn ascending
    res = jDict[rc]
    for f in layer.getFeatures(QgsFeatureRequest().addOrderBy(res,True)):

        # Create new item
        child = QTreeWidgetItem(parent)
        child.setText(0,str(f[res]))
        child.setText(1,str(f.id()))
        child.setText(2,str(f[url1]) if url1 != '' else '')
        child.setText(3,str(f[url2]) if url2 != '' else '')
        child.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled| Qt.ItemIsTristate | Qt.ItemIsUserCheckable )
        child.setCheckState(0, Qt.Checked)

def is_http_url(s):
    return re.match('https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})(?:/[\w&%?#-]{1,300})?',s)

