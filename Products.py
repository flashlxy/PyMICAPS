# -*- coding: utf-8 -*-
#     Output:
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406

from __future__ import print_function
from __future__ import print_function

import sys

from mpl_toolkits.basemap import Basemap

import maskout
import shapefile

reload(sys)
sys.setdefaultencoding('utf-8')

import matplotlib

# matplotlib.use('Agg')
from matplotlib.font_manager import FontProperties
from pylab import *
from matplotlib._png import read_png
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.ticker import FormatStrFormatter
from matplotlib.transforms import Bbox
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import codecs
import os
import re
from datetime import datetime
from matplotlib import patches
from matplotlib.path import Path
from xml.etree import ElementTree
from itertools import takewhile
import numpy as np
import matplotlib.pyplot as plt
import time as ttime
import nclcmaps

matplotlib.rcParams["figure.subplot.top"] = 1
matplotlib.rcParams["figure.subplot.bottom"] = 0
matplotlib.rcParams["figure.subplot.left"] = 0
matplotlib.rcParams["figure.subplot.right"] = 1
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体 SimHei
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
matplotlib.rcParams["savefig.dpi"] = 72


def parseInt(s):
    """
    全局函数 字符串转整数
    :param s: 字符串
    :return: 整数
    """
    assert isinstance(s, basestring)
    return int(''.join(list(takewhile(lambda x: x.isdigit(), s)))) if s[0].isdigit() else None


class Micaps:
    def __init__(self, filename):
        self.filename = filename
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
        Micaps.UpdatePath(products.cutborders[0]['path'], projection)
        for area in products.mapborders:
            Micaps.UpdatePath(area['path'], projection)

    @staticmethod
    def UpdateXY(projection, x, y):
        return projection(x, y)

    @staticmethod
    def DrawBorders(m, products):
        """
        画县市边界
        :param m: 画布对象（plt或投影后的plt)
        :param products: 产品参数
        :return: 
        """
        try:
            for area in products.mapborders:
                if not area['draw']:
                    continue
                if area['filetype'] == 'SHP':  # shp文件
                    if m is plt:
                        Micaps.DrawShapeFile(area)
                    else:
                        m.readshapefile(area['file'].replace('.shp', ''),
                                        os.path.basename(area['file']),
                                        color=area['linecolor'])
                else:  # 文本文件 , 画之前 路径中的点已经被投影了
                    if area['path'] is None:
                        continue
                    if area['polygon'] == 'ON':
                        area_patch = patches.PathPatch(area['path'], linewidth=area['linewidth'], linestyle='solid',
                                                       facecolor='none', edgecolor=area['linecolor'])
                        plt.gca().add_patch(area_patch)
                    else:
                        x, y = zip(*area['path'].vertices)
                        m.plot(x, y, 'k-', linewidth=area['linewidth'], color=area['linecolor'])
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(products.xmlfile, err, datetime.now()))

    @staticmethod
    def DrawTitle(m, products, headtxt):
        if m is plt:
            if products.mtitleposition is None:
                for desc in products.descs:
                    fontfile = r"C:\WINDOWS\Fonts\{0}".format(desc.font['family'])
                    if not os.path.exists(fontfile):
                        font = FontProperties(size=desc.font['fontsize'], weight=desc.font['weight'])
                    else:
                        font = FontProperties(fname=fontfile, size=desc.font['fontsize'], weight=desc.font['weight'])
                    plt.text(desc.pos[0], desc.pos[1], desc.text,
                             # size=desc.font['fontsize'], weight=desc.font['weight'],
                             color=desc.font['color'],
                             fontdict=desc.font,
                             fontproperties=font,
                             rotation=0,
                             ha='left', va='top')
            else:
                if products.mtitleposition == [0, 0]:
                    plt.title(headtxt, fontdict={'fontsize': 14})
                else:
                    plt.text(products.mtitleposition[0], products.mtitleposition[1], headtxt,
                             size=14,
                             weight='bold',
                             # color='blue',
                             # fontdict=desc.font,
                             # fontproperties=font,
                             rotation=0,
                             ha='left', va='top')
        else:
            plt.title(headtxt)

    @staticmethod
    def DrawShapeFile(area):
        """
        在画布上绘制shp文件
        :param area: 包含shp文件名及线宽和线颜色的一个字典
        :return: 
        """
        try:
            shpfile = area['file']
            border_shape = shapefile.Reader(shpfile)
            border = border_shape.shapes()
            for b in border:
                border_points = b.points
                path_data = []
                count = 0
                for cell in border_points:
                    if count == 0:
                        trans = (Path.MOVETO, (cell[0], cell[1]))
                        path_data += [trans]
                        cell_end = cell
                    else:
                        trans = (Path.CURVE4, (cell[0], cell[1]))
                        path_data += [trans]
                trans = (Path.CLOSEPOLY, (cell_end[0], cell_end[1]))
                path_data += [trans]

                codes, verts = zip(*path_data)
                path = Path(verts, codes)
                x, y = zip(*path.vertices)
                plt.plot(x, y, 'k-', linewidth=area['linewidth'], color=area['linecolor'])
        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(area['file'], err, datetime.now()))

    def UpdateExtents(self, products):
        """
        更新产品参数的extents
        :param products: 产品参数对象
        :return: 
        """
        if products.extents is None:
            maxlon = max(self.endlon, self.beginlon)
            minlon = min(self.endlon, self.beginlon)
            maxlat = max(self.endlat, self.beginlat)
            minlat = min(self.endlat, self.beginlat)
            xmax = maxlon + products.margin if maxlon + products.margin <= 180 else 180
            xmin = minlon - products.margin if minlon - products.margin >= -180 else -180
            ymax = maxlat + products.margin if maxlat + products.margin <= 90 else 90
            ymin = minlat - products.margin if minlat - products.margin >= -90 else -90
            products.extents = Bbox.from_extents(xmin, ymin, xmax, ymax)

    def UpdateData(self, products):
        self.UpdateExtents(products)

    def Draw(self, products):
        """
        根据产品参数绘制图像
        :param products: 
        :return: 产品参数
        """
        # 图例的延展类型
        origin = 'lower'
        if self.title.find(u'降水') >= 0 or self.title.find(u'雨'):
            extend = 'max'
        else:
            extend = 'neither'

        # 更新绘图矩形区域
        # self.UpdateExtents(products)
        self.UpdateData(products)
        xmax = products.extents.xmax
        xmin = products.extents.xmin
        ymax = products.extents.ymax
        ymin = products.extents.ymin

        # 设置绘图画板的宽和高 单位：英寸
        h = products.height
        if products.projection.name == 'sall':  # 等经纬度投影时不用配置本身的宽度，直接根据宽高比得到
            w = h * np.math.fabs((xmax - xmin) / (ymax - ymin)) * products.widthshrink
        else:
            w = products.width

        # 创建画布
        fig = plt.figure(figsize=(w, h), dpi=products.dpi, facecolor="white")  # 必须在前面
        # ax = fig.add_subplot(111)
        # 设置绘图区域
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)

        # 背景透明
        fig.patch.set_alpha(products.opacity)

        # 坐标系统尽可能靠近绘图区边界
        fig.tight_layout(pad=products.pad)

        # 获得产品投影
        m = Projection.GetProjection(products)
        if m is not plt:
            # 用投影更新经纬度数据
            self.X, self.Y = Micaps.UpdateXY(m, self.X, self.Y)
            # 用投影更新产品参数中涉及经纬度的数据
            Micaps.Update(products, m)
            if products.projection.coastlines:
                m.drawcoastlines(linewidth=0.25)
            if products.projection.countries:
                m.drawcountries(linewidth=0.25)
            # draw parallels and meridians.
            if products.projection.axis == 'on':
                m.drawparallels(np.arange(-80., 81., 10.),
                                labels=products.projection.latlabels,
                                family='DejaVu Sans',
                                fontsize=10)
                m.drawmeridians(np.arange(-180., 181., 10.),
                                labels=products.projection.lonlabels,
                                family='DejaVu Sans',
                                fontsize=10)

            if products.projection.lsmask['visible']:
                m.drawlsmask(land_color=products.projection.lsmask['land_color'],
                             ocean_color=products.projection.lsmask['ocean_color'], resolution='l')

        else:
            # 坐标轴
            plt.axis(products.projection.axis)

            # 设置坐标轴刻度值显示格式
            if products.projection.axis == 'on':
                x_majorFormatter = FormatStrFormatter('%d°E')
                y_majorFormatter = FormatStrFormatter('%d°N')
                plt.gca().xaxis.set_major_formatter(x_majorFormatter)
                plt.gca().yaxis.set_major_formatter(y_majorFormatter)
                xaxis = plt.gca().xaxis
                for label in xaxis.get_ticklabels():
                    label.set_fontproperties('DejaVu Sans')
                    label.set_fontsize(10)
                yaxis = plt.gca().yaxis
                for label in yaxis.get_ticklabels():
                    label.set_fontproperties('DejaVu Sans')
                    label.set_fontsize(10)

        # 绘制裁切区域边界
        if products.cutborders[0]['path'] is not None:
            patch = patches.PathPatch(products.cutborders[0]['path'],
                                      linewidth=products.cutborders[0]['linewidth'],
                                      facecolor='none',
                                      edgecolor=products.cutborders[0]['linecolor'])
            plt.gca().add_patch(patch)

        # 绘制地图
        Micaps.DrawBorders(m, products)

        cmap = nclcmaps.cmaps(products.micapslegendcolor)  # cm.jet  temp_diff_18lev
        vmax = math.ceil(self.max)
        vmin = math.floor(self.min)
        levels = arange(vmin - self.distance, vmax + self.distance + 0.1, self.distance)

        if products.micapslegendvalue:
            level = levels
        else:
            level = products.legendvalue

        # 是否绘制等值线 ------ 等值线和标注是一体的
        if products.contour['visible']:

            matplotlib.rcParams['contour.negative_linestyle'] = 'dashed'
            if products.contour['colorline']:
                CS1 = m.contour(self.X, self.Y, self.Z, levels=level,
                                linewidths=products.contour['linewidth'])
            else:
                CS1 = m.contour(self.X, self.Y, self.Z, levels=level,
                                linewidths=products.contour['linewidth'], colors=products.contour['linecolor'])
            # 用区域边界裁切等值线图
            if not products.cutborders[0]['path'] is None:
                for collection in CS1.collections:
                    collection.set_clip_on(True)
                    collection.set_clip_path(patch)
            # 是否绘制等值线标注
            if products.contourlabel['visible']:
                plt.clabel(CS1, inline=1, fmt=products.contourlabel['fmt'],
                           fontsize=products.contourlabel['fontsize'],
                           colors=products.contourlabel['fontcolor'])

        # 是否绘制色斑图 ------ 色版图、图例、裁切是一体的
        if products.contourfvisible:
            # 绘制色斑图
            if products.micapslegendvalue:

                CS = m.contourf(self.X, self.Y, self.Z, cmap=cmap,
                                levels=levels,
                                extend=extend, orientation='vertical', origin=origin)
            else:

                CS = m.contourf(self.X, self.Y, self.Z,  # cax=axins,
                                levels=products.legendvalue, colors=products.legendcolor,
                                extend=extend, orientation='vertical', origin=origin)

            # 用区域边界裁切色斑图
            if products.cutborders[0]['path'] is not None and products.cutborders[0]['using']:
                for collection in CS.collections:
                    collection.set_clip_on(True)
                    collection.set_clip_path(patch)

            if m is plt:
                # 插入一个新坐标系 以使图例在绘图区内部显示
                ax2 = plt.gca()
                axins = inset_axes(ax2, width="100%", height="100%", loc=1, borderpad=0)
                axins.axis('off')
                axins.margins(0, 0)
                axins.xaxis.set_ticks_position('bottom')
                axins.yaxis.set_ticks_position('left')
                axins.set_xlim(xmin, xmax)
                axins.set_ylim(ymin, ymax)

                # 画图例
                if products.islegendpic:
                    # 插入图片
                    arr_lena = read_png(products.legendpic)
                    image_box = OffsetImage(arr_lena, zoom=products.legendopacity)
                    ab = AnnotationBbox(image_box, products.legendpos, frameon=False)
                    plt.gca().add_artist(ab)
                else:
                    ticks = fmt = None
                    CB = plt.colorbar(CS, cmap='RdBu', anchor=products.anchor, shrink=products.shrink, ticks=ticks,
                                      # fraction=products.fraction,
                                      drawedges=not products.micapslegendvalue,
                                      filled=False,
                                      spacing='uniform',
                                      use_gridspec=False,
                                      orientation=products.orientation,
                                      # extendfrac='auto',
                                      format=fmt)
            else:

                cb = m.colorbar(CS, location=products.projection.location, size=products.projection.size,
                                pad=products.projection.pad)

        # 绘制描述文本
        Micaps.DrawTitle(m, products, self.title)

        # 存图
        fig.savefig(products.picfile, format='png', transparent=False)
        print(products.picfile + u'存图成功!')
        if ISDEBUG:
            plt.show()


class Micaps4Data(Micaps):
    def __init__(self, filename):
        self.filename = filename
        self.ReadFromFile()

    def ReadFromFile(self):
        """
        读micaps第4类数据文件到内存
        :return: 
        """
        try:
            file_object = codecs.open(self.filename, mode='r', encoding='GBK')
            all_the_text = file_object.read().strip()
            file_object.close()
            contents = re.split('[\s]+', all_the_text)
            if len(contents) < 23:
                return
            self.dataflag = contents[0].strip()
            self.style = contents[1].strip()
            self.title = contents[2].strip()
            self.yy = int(contents[3].strip())
            self.mm = int(contents[4].strip())
            self.dd = int(contents[5].strip())
            self.hh = int(contents[6].strip())
            self.forehh = int(contents[7].strip())
            self.level = contents[8].strip()

            self.deltalon = float(contents[9].strip())
            self.deltalat = float(contents[10].strip())
            self.beginlon = float(contents[11].strip())
            self.endlon = float(contents[12].strip())
            self.beginlat = float(contents[13].strip())
            self.endlat = float(contents[14].strip())

            self.sumlon = int(contents[15].strip())
            self.sumlat = int(contents[16].strip())
            self.distance = float(contents[17].strip())
            self.min = float(contents[18].strip())
            self.max = float(contents[19].strip())
            self.def1 = contents[20].strip()
            self.def2 = contents[21].strip()

            x = np.arange(self.beginlon, self.endlon + self.deltalon, self.deltalon)
            y = np.arange(self.beginlat, self.endlat + self.deltalat, self.deltalat)
            self.X, self.Y = np.meshgrid(x, y)

            if self.dataflag == 'diamond' and self.style == '4':
                begin = 22
                self.Z = np.zeros((self.sumlat, self.sumlon))

                for i in range(self.sumlon):
                    for j in range(self.sumlat):
                        self.Z[j, i] = float(contents[begin + j * self.sumlon + i])

        except Exception as err:
            print(u'【{0}】{1}-{2}'.format(self.filename, err, datetime.now()))

    @staticmethod
    def Write(filename, fdate, edate, flon, elon, flat, elat, xjj, yjj, nx, ny, zi):
        """
        把数据写入 micaps 第四类数据文件
        :param filename: 写入文件
        :param fdate: 起始日期
        :param edate: 结束日期
        :param flon: 起始经度
        :param elon: 结束经度
        :param flat: 起始纬度
        :param elat: 结束纬度
        :param xjj: 经度方向的步长
        :param yjj: 纬度方向的步长
        :param nx: 经度方向上的点数
        :param ny: 纬度方向上的点数
        :param zi: z值数组
        :return: 
        """
        content = 'diamond 4 ' + fdate + '-' + edate + '客观分析网格雨量 '
        content += fdate[0:4] + ' ' + fdate[4:6] + ' ' + fdate[6:8] + ' ' + fdate[8:10] + ' 000 999 '
        content += ' '.join([xjj, yjj, flon, elon, flat, elat, nx, ny, '10.0', '0', str(zi.max()), '0', '0']) + '\n'
        for a in zi.tolist():
            content += ' '.join([Products.FToS(b) for b in a]) + '\n'
        fp = open(filename, 'w')
        fp.write(content)
        fp.close()

    @staticmethod
    def FToS(lat):
        """
        实数转字符串
        :param lat: 实数
        :return: 转换后的字符串
        """
        if lat is None:
            s = '0'
        else:
            s = '%.2f' % lat
        return s


class HeadDesc:
    """
    标题描述类
    """

    def __init__(self, txt, pos, font):
        self.text = txt
        self.pos = pos
        self.font = font
        # fontdict={'family': 'monospace', 'color': 'blue'}


class Projection:
    def __init__(self, root):
        leaf = root.find("Projection")
        if leaf is None:
            self.name = 'sall'
        self.name = self.leaf_to_string(leaf, 'name', 'sall')
        self.lon_0 = self.leaf_to_float(leaf, 'lon_0')
        self.lat_0 = self.leaf_to_float(leaf, 'lat_0')
        self.lat_ts = self.leaf_to_float(leaf, 'lat_ts')
        self.boundinglat = self.leaf_to_float(leaf, 'boundinglat')
        self.llcrnrlat = self.leaf_to_float(leaf, 'llcrnrlat')
        self.llcrnrlon = self.leaf_to_float(leaf, 'llcrnrlon')
        self.urcrnrlat = self.leaf_to_float(leaf, 'urcrnrlat')
        self.urcrnrlon = self.leaf_to_float(leaf, 'urcrnrlon')

        if self.lon_0 is None or self.lat_0 is None:
            self.lon_0 = None
            self.lat_0 = None
        if self.llcrnrlat is None or self.llcrnrlon is None or self.urcrnrlat is None or self.urcrnrlon is None:
            self.llcrnrlat = None
            self.llcrnrlon = None
            self.urcrnrlat = None
            self.urcrnrlon = None

        self.coastlines = self.leaf_to_bool(leaf=leaf, code='coastlines')
        self.countries = self.leaf_to_bool(leaf=leaf, code='countries')

        subleaf = leaf.find('lsmask')
        if subleaf is None:
            self.lsmask = {'visible': False, 'land_color': '#BF9E30', 'ocean_color': '#689CD2'}
        else:
            self.lsmask = {'visible': self.leaf_to_bool(leaf=subleaf, code='visible'),
                           'land_color': self.leaf_to_string(subleaf, 'land_color', '#BF9E30'),
                           'ocean_color': self.leaf_to_string(subleaf, 'ocean_color', '#689CD2')
                           }

        self.axis = self.leaf_to_string(leaf=leaf, code='axis', defvalue='off')
        self.latlabels = self.leaf_to_list(leaf=leaf, code='latlabels', defvalue=[0, 0, 0, 0])
        self.lonlabels = self.leaf_to_list(leaf=leaf, code='lonlabels', defvalue=[0, 0, 0, 0])
        self.size = self.leaf_to_string(leaf=leaf, code='size', defvalue='5%')
        self.pad = self.leaf_to_string(leaf=leaf, code='pad', defvalue='2%')
        self.location = self.leaf_to_string(leaf=leaf, code='location', defvalue='right')

    @staticmethod
    def GetProjection(products):
        """
        根据获得产品参数获得投影后的画布对象
        :param products: 产品参数
        :return: 画布对象
        """

        xmax = products.extents.xmax
        xmin = products.extents.xmin
        ymax = products.extents.ymax
        ymin = products.extents.ymin
        lon_0 = xmin + (xmax - xmin) / 2
        lat_0 = ymin + (ymax - ymin) / 2

        projection = products.projection
        pjname = projection.name

        if projection.lat_0 is not None:
            lon_0 = projection.lon_0
            lat_0 = projection.lat_0

        if projection.llcrnrlat is not None:
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


if __name__ == '__main__':
    ISDEBUG = True
    if ISDEBUG:
        xml = r'config.xml'
    else:
        if len(sys.argv) < 2:
            print(u'参数不够，至少需要一个xml文件名参数')
            sys.exit()
        xml = sys.argv[1]

    start = ttime.clock()

    paras = Products(xml)
    if paras is not None:
        paras.micapsdata.Draw(paras)

    print('Micaps data contour and save picture seconds:', ttime.clock() - start)
