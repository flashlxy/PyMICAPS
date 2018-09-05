# -*- coding: utf-8 -*-
#     MicapsData基类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-11
#     Copyright:  ©江西省气象台 2017
#     Version:    2.0.20170411
from __future__ import print_function

import codecs
import sys

import chardet
from matplotlib.font_manager import FontProperties
from matplotlib.markers import MarkerStyle

import MicapsFile
from Map import Map
from Picture import Picture

reload(sys)
sys.setdefaultencoding('utf-8')

# matplotlib.use('Agg')
from pylab import *
from matplotlib.transforms import Bbox
import os
import numpy as np
import matplotlib.pyplot as plt
import nclcmaps

matplotlib.rcParams["figure.subplot.top"] = 1
matplotlib.rcParams["figure.subplot.bottom"] = 0
matplotlib.rcParams["figure.subplot.left"] = 0
matplotlib.rcParams["figure.subplot.right"] = 1
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体 SimHei
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
matplotlib.rcParams["savefig.dpi"] = 72


class Micaps:
    def __init__(self, filename, encoding='utf-8', **kwargs):
        self.filename = filename
        self.encoding = encoding
        self.dataflag = None
        self.style = None
        self.title = None
        self.yy = None
        self.mm = None
        self.dd = None
        self.hh = None
        self.forehh = None
        self.level = None
        self.deltalon = None
        self.deltalat = None
        self.beginlon = None
        self.endlon = None
        self.beginlat = None
        self.endlat = None
        self.beginlon = None
        self.endlon = None
        self.sumlon = None
        self.sumlat = None
        self.distance = None
        self.min = None
        self.max = None
        self.def1 = None
        self.def2 = None
        self.X = None
        self.Y = None
        self.Z = None
        self.outPath = os.path.dirname(os.path.abspath(__file__))

        self.SetCheckSize(self.filename, **kwargs)
        self.SetEncoding()
        pass

    def SetCheckSize(self, filename, **kwargs):
        if 'check_bytes' in kwargs.keys():
            self.check_bytes = kwargs['check_bytes']
        else:
            if os.path.isfile(filename):
                self.check_bytes = os.path.getsize(self.filename)
            else:
                self.check_bytes = 1024

    def SetEncoding(self):
        if os.path.isfile(self.filename):
            # bytes = min(32, os.path.getsize(self.filename))
            # raw = open(self.filename, 'rb').read(bytes)
            # result = chardet.detect(raw)
            # self.encoding = result['encoding']

            bytes = min(self.check_bytes, os.path.getsize(self.filename))
            # bytes = os.path.getsize(self.filename)
            if bytes == 0: return
            raw = open(self.filename, 'rb').read(bytes)

            if raw.startswith(codecs.BOM_UTF8):
                self.encoding = 'utf-8-sig'
            else:
                result = chardet.detect(raw)
                if result['encoding'] is not None:
                    self.encoding = result['encoding']

    @staticmethod
    def UpdatePath(path, projection):
        """
        根据投影对象更新path
        :param path: 路径对象
        :param projection: 投影类型
        :return: 
        """
        if path is None:
            return
        for point in path.vertices:
            point[0], point[1] = projection(point[0], point[1])

    @staticmethod
    def Update(products, projection):
        """
        根据投影类型和更新产品对象中的path对象
        :param products: 产品参数
        :param projection: 投影类型
        :return: 
        """

        Micaps.UpdatePath(products.map.clipborders[0].path, projection)

        for area in products.map.borders:
            if area.path is not None:
                Micaps.UpdatePath(area.path, projection)

    @staticmethod
    def UpdateXY(projection, x, y):
        return projection(x, y)

    @staticmethod
    def StandardPinLegendValue(pin):
        distance = pin[2]
        minvalue = math.floor(pin[0] / distance) * distance
        maxvalue = math.ceil(pin[1] / distance) * distance
        return minvalue, maxvalue, distance

    def UpdateExtents(self, products):
        """
        更新产品参数的extents
        :param products: 产品参数对象
        :return: 
        """
        if products.picture.extents is None:
            maxlon = max(self.endlon, self.beginlon)
            minlon = min(self.endlon, self.beginlon)
            maxlat = max(self.endlat, self.beginlat)
            minlat = min(self.endlat, self.beginlat)
            margin = products.picture.margin
            xmax = maxlon + margin[2] if maxlon + margin[2] <= 180 else 180
            xmin = minlon - margin[0] if minlon - margin[0] >= -180 else -180
            ymax = maxlat + margin[1] if maxlat + margin[1] <= 90 else 90
            ymin = minlat - margin[3] if minlat - margin[3] >= -90 else -90
            products.picture.extents = Bbox.from_extents(xmin, ymin, xmax, ymax)
        else:
            extents = products.picture.extents
            if isinstance(extents, list):
                products.picture.extents = Bbox.from_extents(extents[0], extents[1],
                                                             extents[2], extents[3])

    def UpdatePinLegendValue(self, micapsfile):
        pin = micapsfile.legend.pinlegendvalue
        if pin is not None:
            self.min, self.max, self.distance = self.StandardPinLegendValue(pin)

    def UpdateData(self, products, micapsfile):
        """
        要被重载的函数，用来更新产品中的一系列参数
        :param micapsfile: 产品中包含的一个micapsfile
        :param products:产品参数 
        :return: 
        """
        return

    def GetExtend(self):
        if self.title.find(u'降水') >= 0 or self.title.find(u'雨') >= 0:
            extend = 'max'
        else:
            extend = 'neither'
        return extend

    def DrawUV(self, m, micapsfile, clipborder, patch):
        return

    def DrawCommon(self, products, debug=True):
        # 图例的延展类型
        # extend = self.GetExtend()
        # 更新绘图矩形区域
        # self.UpdateExtents(products)
        micapsfile = products.micapsfiles[0]

    def Clip(self, clipborder, fig, patch):
        if clipborder.path is not None and clipborder.using:
            for ax in fig.axes:
                if not isinstance(ax, Axes):
                    # from matplotlib.patches import FancyArrowPatch
                    artists = ax.get_children()
                    for artist in artists:
                        # if isinstance(artist, FancyArrowPatch):
                        artist.set_clip_path(patch)

    def Draw(self, products, micapsfile, debug=True):
        """
        根据产品参数绘制图像
        :param micapsfile: 指定绘制产品中包含的一个micapsfile
        :param debug: 调试状态
        :param products: 产品参数 
        :return: 
        """
        self.UpdateData(products, micapsfile)
        extents = products.picture.extents
        xmax = extents.xmax
        xmin = extents.xmin
        ymax = extents.ymax
        ymin = extents.ymin

        # 设置绘图画板的宽和高 单位：英寸
        h = products.picture.height
        if products.map.projection.name == 'sall':  # 等经纬度投影时不用配置本身的宽度，直接根据宽高比得到
            w = h * np.math.fabs((xmax - xmin) / (ymax - ymin)) * products.picture.widthshrink
        else:
            w = products.picture.width

        # 创建画布
        fig = plt.figure(figsize=(w, h), dpi=products.picture.dpi, facecolor="white")  # 必须在前面
        ax = fig.add_subplot(111)
        ax.spines['bottom'].set_linewidth(products.map.projection.axisthick)
        ax.spines['left'].set_linewidth(products.map.projection.axisthick)
        ax.spines['right'].set_linewidth(products.map.projection.axisthick)
        ax.spines['top'].set_linewidth(products.map.projection.axisthick)
        # 设置绘图区域
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)

        # 背景透明
        fig.patch.set_alpha(products.picture.opacity)

        # 坐标系统尽可能靠近绘图区边界
        fig.tight_layout(pad=products.picture.pad)

        clipborder = products.map.clipborders[0]

        # 获得产品投影
        from Projection import Projection
        m = Projection.GetProjection(products)

        if m is not plt:
            # 用投影更新经纬度数据
            self.X, self.Y = Micaps.UpdateXY(m, self.X, self.Y)
            # 用投影更新产品参数中涉及经纬度的数据
            Micaps.Update(products, m)
            # 画世界底图
            Map.DrawWorld(products, m)

        # 绘制裁切区域边界
        patch = Map.DrawClipBorders(products.map.clipborders)

        # draw parallels and meridians.
        Map.DrawGridLine(products, m)

        cmap = nclcmaps.cmaps(micapsfile.legend.micapslegendcolor)  # cm.jet  temp_diff_18lev
        vmax = math.ceil(self.max)
        vmin = math.floor(self.min)
        levels = arange(vmin - self.distance, vmax + self.distance + 0.1, self.distance)

        if micapsfile.legend.micapslegendvalue:
            level = levels
        else:
            level = micapsfile.legend.legendvalue

        # 绘制等值线 ------ 等值线和标注是一体的
        c = micapsfile.contour

        Map.DrawContourAndMark(contour=c, x=self.X, y=self.Y, z=self.Z,
                               level=level, clipborder=clipborder, patch=patch, m=m)

        cf = micapsfile.contour
        cbar = micapsfile.legend
        extend = micapsfile.legend.extend
        # 绘制色斑图 ------ 色版图、图例、裁切是一体的
        Map.DrawContourfAndLegend(contourf=cf, legend=cbar, clipborder=clipborder,
                                  patch=patch, cmap=cmap, levels=levels,
                                  extend=extend, extents=extents, x=self.X, y=self.Y, z=self.Z, m=m)

        # 绘制描述文本
        MicapsFile.MicapsFile.DrawTitle(m, micapsfile.title, self.title)

        self.DrawUV(m, micapsfile, clipborder, patch)

        # 绘制地图
        Map.DrawBorders(m, products)

        # 绘制散点
        if micapsfile.contour.scatter:
            if hasattr(self, 'x1'):
                m.scatter(self.x1, self.y1, s=micapsfile.contour.radius, c=self.z1,
                          alpha=micapsfile.contour.alpha,
                          edgecolors='b')
            else:
                m.scatter(self.X, self.Y, s=micapsfile.contour.radius, c=self.Z,
                          alpha=micapsfile.contour.alpha,
                          edgecolors='b')

        # 绘制站点
        stations = products.map.stations
        if stations.visible:
            # 'code': code, 'lon': lon, 'lat': lat, 'height': height,
            # 'iclass': iclass, 'infosum': infosum, 'name': info[0]
            # stations_tuple = tuple(stations.micapsdata.stations)
            # (code, lat, lon, height, iclass, infosum, info[0])
            # stations_array = np.array(stations.micapsdata.stations, dtype=[
            #     ('code', 'U'),
            #     ('lat', np.float32),
            #     ('lon', np.float32),
            #     ('height', np.float32),
            #     ('iclass', 'i'),
            #     ('infosum', 'i'),
            #     ('info', 'U')
            # ])

            # stations_array = [list(ele) for ele in zip(*stations.micapsdata.stations)]
            stations_array = zip(*stations.micapsdata.stations)
            # 画站点mark
            if m is not plt:
                stations_array[2], stations_array[1] = \
                    Micaps.UpdateXY(m, stations_array[2], stations_array[1])
            marker = MarkerStyle(stations.markstyle[0], stations.markstyle[1])
            m.scatter(stations_array[2], stations_array[1], marker=marker,
                      s=stations.radius, c=stations.color,
                      alpha=stations.alpha, edgecolors=stations.edgecolors)

            # 画站点文本

            fontfile = r"C:\WINDOWS\Fonts\{0}".format(stations.font[1])
            if not os.path.exists(fontfile):
                font = FontProperties(size=stations.font[0], weight=stations.font[2])
            else:
                font = FontProperties(fname=fontfile, size=stations.font[0], weight=stations.font[2])
            for sta in stations.micapsdata.stations:
                if m is not plt:
                    lon, lat = Micaps.UpdateXY(m, sta[2], sta[1])
                    lon1, lat1 = Micaps.UpdateXY(m, sta[2] + stations.detax, sta[1])
                    deta = lon1 - lon
                else:
                    lon, lat = sta[2], sta[1]
                    deta = stations.detax
                plt.text(lon + deta, lat, sta[6],
                         fontproperties=font, rotation=0,
                         color=stations.font[3], ha='left', va='center')

        # 接近收尾

        # self.Clip(clipborder, fig, patch)

        # 存图
        Picture.savePicture(fig, products.picture.picfile)

        print(products.picture.picfile + u'存图成功!')
        if debug:
            plt.show()

            # def GetColors(self, legend, z):
            #     if legend.micapslegendvalue:
            #         pass
            #     else:
            #         for i in range(len(z)):
            #             if z[i]
