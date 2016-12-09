# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
'''
This module provides methods to export layers so they can be used as valid data
for uploading to GeoServer.
'''
from builtins import str

import os

from qgis.PyQt.QtCore import QSettings
from qgis.core import (QgsMapLayer,
                       QgsVectorLayer,
                       QgsVectorFileWriter,
                       QgsRasterFileWriter
                      )
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from geoserverexplorer.qgistools import utils

def exportVectorLayer(layer):
    '''accepts a QgsVectorLayer or a string with a filepath'''
    settings = QSettings()
    systemEncoding = settings.value( "/UI/encoding", "System" )
    if isinstance(layer, QgsMapLayer):
        filename = str(layer.source())
        destFilename = str(layer.name())
    else:
        filename = str(layer)
        destFilename = str(os.path.splitext(os.path.basename(filename))[0])
    if (not filename.lower().endswith("shp")):
        if not isinstance(layer, QgsMapLayer):
            layer = QgsVectorLayer(filename, "layer", "ogr")
            if not layer.isValid() or layer.type() != QgsMapLayer.VectorLayer:
                raise Exception ("Error reading file {} or it is not a valid vector layer file".format(filename))
        output = utils.tempFilenameInTempFolder(destFilename + ".shp")
        provider = layer.dataProvider()
        writer = QgsVectorFileWriter(output, systemEncoding, layer.pendingFields(), provider.geometryType(), layer.crs() )
        for feat in layer.getFeatures():
            writer.addFeature(feat)
        del writer
        iface.messageBar().pushMessage("Warning", "Layer had to be exported to shapefile for importing. Data might be lost.",
                                              level = QgsMessageBar.WARNING,
                                              duration = 5)
        return output
    else:
        return filename


def exportRasterLayer(layer):
    if (not str(layer.source()).lower().endswith("tif") ):
        filename = str(layer.name())
        output = utils.tempFilenameInTempFolder(filename + ".tif")
        writer = QgsRasterFileWriter(output)
        writer.setOutputFormat("GTiff");
        writer.writeRaster(layer.pipe(), layer.width(), layer.height(), layer.extent(), layer.crs())
        del writer
        return output
    else:
        return str(layer.source())
