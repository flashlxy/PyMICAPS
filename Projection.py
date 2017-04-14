# -*- coding: utf-8 -*-
#     投影类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406
from __future__ import print_function
from __future__ import print_function

import sys

from mpl_toolkits.basemap import Basemap

from Main import parseInt

reload(sys)
sys.setdefaultencoding('utf-8')

# matplotlib.use('Agg')
from pylab import *
import matplotlib.pyplot as plt


class Projection:
    def __init__(self, root):
        leaf = root.find("Projection")
        if leaf is None:
            self.name = 'sall'
        self.name = self.leaf_to_string(leaf, 'Name', 'sall')
        self.lon_0 = self.leaf_to_float(leaf, 'Lon_0')
        self.lat_0 = self.leaf_to_float(leaf, 'Lat_0')
        self.lat_ts = self.leaf_to_float(leaf, 'Lat_ts')
        self.boundinglat = self.leaf_to_float(leaf, 'BoundingLat')
        self.llcrnrlat = self.leaf_to_float(leaf, 'LlcrnrLat')
        self.llcrnrlon = self.leaf_to_float(leaf, 'LlcrnrLon')
        self.urcrnrlat = self.leaf_to_float(leaf, 'UrcrnrLat')
        self.urcrnrlon = self.leaf_to_float(leaf, 'UrcrnrLon')

        if self.lon_0 is None or self.lat_0 is None:
            self.lon_0 = None
            self.lat_0 = None
        if self.llcrnrlat is None or self.llcrnrlon is None or self.urcrnrlat is None or self.urcrnrlon is None:
            self.llcrnrlat = None
            self.llcrnrlon = None
            self.urcrnrlat = None
            self.urcrnrlon = None

        self.coastlines = self.leaf_to_bool(leaf=leaf, code='Coastlines')
        self.countries = self.leaf_to_bool(leaf=leaf, code='Countries')

        subleaf = leaf.find('Lsmask')
        if subleaf is None:
            self.lsmask = {'visible': False, 'land_color': '#BF9E30', 'ocean_color': '#689CD2'}
        else:
            self.lsmask = {'visible': self.leaf_to_bool(leaf=subleaf, code='Visible'),
                           'land_color': self.leaf_to_string(subleaf, 'Land_color', '#BF9E30'),
                           'ocean_color': self.leaf_to_string(subleaf, 'Ocean_color', '#689CD2')
                           }
        self.axis = Projection.leaf_to_string(leaf=leaf, code='Axis', defvalue='off')
        self.axisthick = self.leaf_to_float(leaf, 'AxisThick', 1.)
        self.axisfmt = Projection.leaf_to_list(leaf=leaf, code='AxisFmt', defvalue=['%d°E', '%d°N'])
        self.latlabels = Projection.leaf_to_list(leaf=leaf, code='LatLabels', defvalue=[0, 0, 0, 0])
        self.lonlabels = Projection.leaf_to_list(leaf=leaf, code='LonLabels', defvalue=[0, 0, 0, 0])

    @staticmethod
    def ValidExtents(extents):
        for extent in extents:
            if extent is None:
                return False
        return True

    @staticmethod
    def GetProjection(products):
        """
        根据获得产品参数获得投影后的画布对象
        :param products: 产品参数
        :return: 画布对象
        """

        xmax = products.picture.extents.xmax
        xmin = products.picture.extents.xmin
        ymax = products.picture.extents.ymax
        ymin = products.picture.extents.ymin
        lon_0 = xmin + (xmax - xmin) / 2
        lat_0 = ymin + (ymax - ymin) / 2

        projection = products.map.projection
        pjname = projection.name

        if Projection.ValidExtents((projection.lon_0, projection.lon_0)):
            lon_0 = projection.lon_0
            lat_0 = projection.lat_0

        if Projection.ValidExtents(
                (projection.llcrnrlat, projection.llcrnrlat, projection.urcrnrlat, projection.urcrnrlon)):
            xmax = projection.urcrnrlon
            xmin = projection.llcrnrlon
            ymax = projection.urcrnrlat
            ymin = projection.llcrnrlat

        lat_ts = projection.lat_ts
        if lat_ts is None:
            lat_ts = lat_0

        boundinglat = projection.boundinglat
        if boundinglat is None:
            boundinglat = 0

        if pjname == 'sall':
            m = plt
        elif pjname == 'cyl':
            m = Basemap(projection='cyl', llcrnrlat=ymin, urcrnrlat=ymax, llcrnrlon=xmin, urcrnrlon=xmax,
                        lon_0=lon_0, lat_0=lat_0)
        elif pjname == 'mill':
            m = Basemap(projection='mill', llcrnrlon=xmin, llcrnrlat=ymin, urcrnrlon=xmax, urcrnrlat=ymax)
        elif pjname == 'gnom':
            m = Basemap(projection='gnom', llcrnrlon=xmin, llcrnrlat=ymin, urcrnrlon=xmax, urcrnrlat=ymax,
                        lat_0=lat_0, lon_0=lon_0)
        elif pjname == 'ortho':
            m = Basemap(projection='ortho', lat_0=lat_0, lon_0=lon_0, resolution='l')
        elif pjname == 'hammer':
            m = Basemap(projection='hammer', lon_0=lon_0)
        elif pjname == 'kav7':
            m = Basemap(projection='kav7', lon_0=lon_0, resolution=None)
        elif pjname == 'merc':
            ymin = ymin if ymin >= -80 else -80
            ymax = ymax if ymax <= 80 else 80
            lat_ts = lat_ts if lat_ts < 90 else 80.
            m = Basemap(llcrnrlon=xmin, llcrnrlat=ymin, urcrnrlon=xmax, urcrnrlat=ymax,
                        rsphere=(6378137.00, 6356752.3142),
                        resolution='l', projection='merc',
                        lat_0=lat_0, lon_0=lon_0, lat_ts=lat_ts)
        elif pjname == 'lcc':
            # lat_1=lat_0, lat_2=60, lat_0=lat_0, lon_0=lon_0 width=12000000, height=9000000,
            # lon_0 = 120.
            # lat_0 = 90.
            # ymin = 5.13
            # ymax = 53.51
            # xmin = 85.86
            # xmax = 174.69
            m = Basemap(projection='lcc',
                        # width=w, height=h,
                        llcrnrlon=xmin, llcrnrlat=ymin, urcrnrlon=xmax, urcrnrlat=ymax,
                        rsphere=(6378137.00, 6356752.3142),
                        resolution='l',
                        area_thresh=1000.,
                        lat_2=60, lat_1=30, lon_0=lon_0, lat_0=lat_0)
        elif pjname == 'stere':
            # lon_0 = 116.
            # lat_0 = 90.
            # ymin = 5.13
            # ymax = 53.51
            # xmin = 85.86
            # xmax = 174.69
            m = Basemap(projection='stere', lon_0=lon_0, lat_0=lat_0, lat_ts=lat_ts,
                        llcrnrlat=ymin, urcrnrlat=ymax,
                        llcrnrlon=xmin, urcrnrlon=xmax,
                        # boundinglat=ymin,
                        # width=w, height=h,
                        rsphere=6371200., resolution='l', area_thresh=10000
                        )
        elif pjname == 'npstere':
            m = Basemap(projection='npstere',
                        lon_0=lon_0, lat_0=lat_0,
                        lat_ts=lat_ts, boundinglat=boundinglat,
                        # llcrnrlat=ymin, urcrnrlat=ymax,
                        # llcrnrlon=xmin, urcrnrlon=xmax,
                        # width=12000000, height=8000000,
                        rsphere=6371200., area_thresh=10000)
        else:
            m = plt
        return m

    @staticmethod
    def leaf_to_float(leaf, code, defvalue=None):
        #
        try:
            tpos = leaf.find(code)
            if tpos is None or tpos.text.strip() == '':
                return defvalue
            else:
                return float(tpos.text.strip())
        except:
            return defvalue

    @staticmethod
    def leaf_to_string(leaf, code, defvalue=None):
        #
        try:
            tpos = leaf.find(code)
            if tpos is None or tpos.text.strip() == '':
                return defvalue
            else:
                return tpos.text.strip()
        except Exception as err:
            return defvalue

    @staticmethod
    def leaf_to_bool(leaf, code, defvalue=False, ok='ON'):
        try:
            tpos = leaf.find(code)
            if tpos is None or tpos.text.strip() == '':
                return defvalue
            else:
                return str.upper(tpos.text.strip()) == ok
        except Exception as err:
            return defvalue

    @staticmethod
    def leaf_to_int(leaf, code, defvalue=None):
        #
        try:
            tpos = leaf.find(code)
            if tpos is None or tpos.text.strip() == '':
                return defvalue
            else:
                return parseInt(tpos.text.strip())
        except Exception as err:
            return defvalue

    @staticmethod
    def leaf_to_list(leaf, code, defvalue=None):
        #
        try:
            tpos = leaf.find(code)
            if tpos is None or tpos.text.strip() == '':
                return defvalue
            else:
                labels = eval('[{0}]'.format(tpos.text.strip()))
                return labels
        except Exception as err:
            return defvalue
