# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406
import os
from xml.etree import ElementTree

from datetime import datetime

import re
from matplotlib.path import Path
from matplotlib.transforms import Bbox

import maskout
from HeadDesc import HeadDesc
from Main import parseInt
from Micaps3Data import Micaps3Data
from Micaps4Data import Micaps4Data
from Projection import Projection


class Products:
    """
    画图参数的封装类
    用法：

    """

    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
        if not os.path.exists(self.xmlfile):
            return
        try:
            tree = ElementTree.parse(self.xmlfile)
            root = tree.getroot()

            products = root.getchildren()
            p = products[0]

            # M1：站点数据，M4：第4类格点数据，M11：第11类UV数据
            self.odatatype = Projection.leaf_to_string(p, "OriginalDataType")

            # 原始数据文件路径
            self.ofile = Projection.leaf_to_string(p, "OriginalFile")
            if self.odatatype == 'M4':
                self.micapsdata = Micaps4Data(self.ofile)
            elif self.odatatype == 'M3':
                self.micapsdata = Micaps3Data(self.ofile)
            else:
                return
            # 地图投影
            self.projection = Projection(p)

            # 地图边界文件路径，仅用于绘制边界
            mapborders = p.find("MapBorders").getchildren()
            self.mapborders = []
            for border in mapborders:
                mapfile = Projection.leaf_to_string(border, "File")
                filetype = str.upper(Projection.leaf_to_string(border, "Type", 'shp'))
                polygonswitch = str.upper(Projection.leaf_to_string(border, "Polygon", 'on'))

                mbdict = {
                    'file': mapfile,
                    'filetype': filetype,
                    'path': self.readPolygon(mapfile) if filetype != 'SHP' else None,
                    'polygon': polygonswitch,
                    'draw': Projection.leaf_to_bool(border, "Draw", False),
                    'linewidth': Projection.leaf_to_float(border, "LineWidth", 1),
                    'linecolor': Projection.leaf_to_string(border, "LineColor", 'k')
                }
                self.mapborders.append(mbdict)

            # 裁剪边界文件路径，用于对色斑图进行裁剪
            cutborders = p.find("CutBorders").getchildren()
            self.cutborders = []
            for border in cutborders:
                filehead = Projection.leaf_to_string(border, "File")
                filetype = Projection.leaf_to_string(border, "Type", 'shp')
                code = Projection.leaf_to_list(border, "Code", [360000])
                drawswitch = str.upper(Projection.leaf_to_string(border, "Draw", 'off'))
                linecolor = Projection.leaf_to_string(border, "LineColor", 'k') if drawswitch == 'ON' else 'none'
                mbdict = {
                    'path': self.getPath(filehead=filehead, code=code, filetype=filetype),
                    'draw': drawswitch,
                    'using': Projection.leaf_to_bool(border, "Using", True),
                    'linewidth': Projection.leaf_to_float(border, "LineWidth", 1),
                    'linecolor': linecolor
                }
                self.cutborders.append(mbdict)

            # 生成的图片宽度
            self.width = Projection.leaf_to_float(p, "PicWidth", 10)

            # 生成的图片高度
            self.height = Projection.leaf_to_float(p, "PicHeight", 10)

            # dpi
            self.dpi = Projection.leaf_to_int(p, "Dpi", 72)

            # 高宽比
            self.widthshrink = Projection.leaf_to_float(p, "WidthShrink", 1.0)

            # 绘图区外延
            self.margin = Projection.leaf_to_float(p, "Margin", 0.0)

            # 绘图区内边距
            self.pad = Projection.leaf_to_float(p, "Pad", 0.0)

            # 绘图区域
            extents = p.find("Extents").text.strip()
            if extents is None or extents == '':
                if len(self.cutborders) < 1 or self.cutborders[0]['path'] is None:
                    self.extents = None
                else:
                    jxextend = self.cutborders[0]['path'].get_extents()
                    delta = self.margin
                    xmax = jxextend.xmax + delta
                    xmin = jxextend.xmin - delta
                    ymax = jxextend.ymax + delta
                    ymin = jxextend.ymin - delta
                    self.extents = Bbox.from_extents(xmin, ymin, xmax, ymax)
            else:
                self.extents = Projection.leaf_to_list(p, "Extents", None)

            # 画布透明度
            self.opacity = Projection.leaf_to_float(p, 'Opacity', 1)
            if self.opacity < 0 or self.opacity > 1:
                self.opacity = 1

            # 生成的图片文件存放路径
            self.picfile = Projection.leaf_to_string(p, 'PicFile', 'mytest.png')
            Products.checkFilename(self.picfile)

            # 图例图片文件路径，图例叠加到产品图上的位置，为空表示自行生成图例
            legend_pic = p.find("LegendPic").text
            self.islegendpic = False
            self.legendpic = ''
            self.legendpos = [0, 0]
            self.legendopacity = 1
            if not (legend_pic is None or legend_pic.strip() == ''):
                self.islegendpic = True
                legend_pics = legend_pic.strip().split(',')
                if 1 == len(legend_pics):
                    self.legendpic = legend_pics[0].strip()
                elif 4 == len(legend_pics):
                    self.legendpic = legend_pics[0].strip()
                    self.legendpos = [float(legend_pics[1].strip()), float(legend_pics[2].strip())]
                    self.legendopacity = float(legend_pics[3].strip())
                else:
                    self.legendpic = legend_pics[0].strip()

            # 是否取MICAPS数据本身的图例值
            self.micapslegendvalue = Projection.leaf_to_bool(p, "MicapsLegendValue", True, 'TRUE')

            # 第三类数据等值线步长
            self.step = Projection.leaf_to_float(p, 'Step', 2.)

            # NCL colorbar 的别名
            self.micapslegendcolor = Projection.leaf_to_string(p, 'MicapsLegendColor', 'ncl_default')

            # 图例等级值
            self.legendvalue = Projection.leaf_to_list(p, "LegendValue", None)

            # 图例颜色值
            self.legendcolor = Projection.leaf_to_list(p, "LegendColor", None)

            # 图例放置方式
            self.orientation = Projection.leaf_to_string(p, 'Orientation', 'vertical')

            # 图例离边框位置
            self.anchor = Projection.leaf_to_list(p, "Anchor", [0, 0])

            # 图例收缩系数
            self.shrink = Projection.leaf_to_float(p, "Shrink", 1)

            self.fraction = Projection.leaf_to_float(p, 'Fraction', 0.15)

            # 是否按Micaps数据的标题写产品描述
            self.mtitleposition = Projection.leaf_to_list(p, "MTitlePosition", None)

            # 经纬方向上的插值格点数
            self.grid = Projection.leaf_to_list(p, "Grid", [195, 216])
            if len(self.grid) != 2:
                self.grid = [195, 216]
            else:
                self.grid = [parseInt(str(g)) for g in self.grid]

            # 等值线参数
            # self.contourvisible = Projection.leaf_to_bool(p, "ContourVisible", False, 'TRUE')
            contourleaf = p.find("Contour")
            if contourleaf is None:
                self.contour = {'visible': False, 'linewidth': 1.0, 'linecolor': 'k', 'colorline': False}
            else:
                self.contour = {
                                'visible': Projection.leaf_to_bool(contourleaf, "Visible", False, 'TRUE'),
                                'linewidth': Projection.leaf_to_float(contourleaf, 'LineWidth', 1.0),
                                'linecolor': Projection.leaf_to_string(contourleaf, 'LineColor', 'k'),
                                'colorline': Projection.leaf_to_bool(contourleaf, "ColorLine", False, 'TRUE')
                               }

            # 是否显示色斑图
            self.contourfvisible = Projection.leaf_to_bool(p, "ContourfVisible", False, 'TRUE')

            # 等值线标注参数
            # self.contourlabelvisible = Projection.leaf_to_bool(p, "ContourLabelVisible", False, 'TRUE')
            leaf = p.find("ContourLabel")
            if leaf is None:
                self.contourlabel = {'visible': False, 'fmt': '%1.0f', 'fontsize': 12, 'fontcolor': 'k'}
            else:
                self.contourlabel = {
                    'visible': Projection.leaf_to_bool(leaf, "Visible", False, 'TRUE'),
                    'fmt': Projection.leaf_to_string(leaf, 'Fmt', '%1.0f'),
                    'fontsize': Projection.leaf_to_float(leaf, 'FontSize', 12),
                    'fontcolor': Projection.leaf_to_string(leaf, 'FontColor', 'k')
                }

            # 产品图片文字描述（可能多个）
            descs = p.find("Descs").getchildren()
            self.descs = []
            for desc in descs:
                txt = Projection.leaf_to_string(desc, 'Text', u'测试数据')
                pos = Projection.leaf_to_list(desc, "Position", [113.2, 30.5])
                fonts = desc.find("Font").text.strip().split(',')
                font = {'family': 'monospace', 'weight': 'bold', 'fontsize': 12, 'color': 'k'}
                if len(fonts) == 4:
                    font['fontsize'] = parseInt(fonts[0].strip())
                    font['family'] = fonts[1]
                    font['weight'] = fonts[2]
                    font['color'] = fonts[3]
                self.descs.append(HeadDesc(txt, pos, font))
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(self.xmlfile, err, datetime.now()))
            return None

    @staticmethod
    def getPath(filehead, code, filetype):
        """
        根据文件类型获取path对象
        :param filehead: 文件名
        :param code: 闭合区域行政区号-对shp文件有效
        :param filetype: 文件类型
        :return: path对象的一个实例
        """
        if filetype == 'shp':
            path = maskout.getPathFromShp(filehead, code)
        else:
            path = Products.readPath(filehead)
        return path

    @staticmethod
    def checkFilename(filepath):
        """
        创建数据文件夹
        :param filepath: 文件路径
        :return: 
        """

        path = os.path.dirname(filepath)
        if not os.path.isdir(path):
            os.makedirs(path)

    @staticmethod
    def readPath(filename):
        """
        从类似第9类micaps数据中获取path
        :param filename: 数据文件全名
        :return: path对象的一个实例
        """
        try:
            file_object = open(filename)
            all_the_text = file_object.read()
            file_object.close()
            poses = all_the_text.split()
            lon = [float(p) for p in poses[13::2]]
            lat = [float(p) for p in poses[14::2]]
            path = Path(zip(lon, lat))
            return path
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(filename, err, datetime.now()))
            return None

    @staticmethod
    def readPolygon(filename):
        """
        从特定格式的文件中获取path
        :param filename: 特定的数据文件全名
        :return: path对象的一个实例
        """
        try:
            file_object = open(filename)
            all_the_text = file_object.read()
            file_object.close()
            poses = re.split('[,]+|[\s]+', all_the_text)
            lon = [float(p) for p in poses[0::2]]
            lat = [float(p) for p in poses[1::2]]
            path = Path(zip(lon, lat))
            return path
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(filename, err, datetime.now()))
            return None
