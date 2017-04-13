# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-11
#     Copyright:  ©江西省气象台 2017
#     Version:    2.0.20170411
from __future__ import print_function
from __future__ import print_function

from Projection import Projection


class Legend:
    def __init__(self, root):
        p = root.find("Legend")
        if p is None:
            print(u'没有图例节点')
            return
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

        # 图例的延展类型:neither,min,max default is neither
        self.extend = Projection.leaf_to_string(p, 'Extend', 'neither')

        # 是否取MICAPS数据本身的图例值
        self.micapslegendvalue = Projection.leaf_to_bool(p, "MicapsLegendValue", True, 'TRUE')

        # When micapslegendvalue is true, the setting is working.
        # if pin the legend values, [begin value, stop value, step] is working.default is None
        # else use the data self legend values
        self.pinlegendvalue = Projection.leaf_to_list(p, "PinLegendValue", None)
        self.valid(self.pinlegendvalue)

        # NCL colorbar 的别名
        self.micapslegendcolor = Projection.leaf_to_string(p, 'MicapsLegendColor', 'ncl_default')

        # 图例填充样式数组，一般和自定义的legend结合使用，如不够LegendValue数组的长度，则会用最后一个样式自动补齐
        self.hatches = Projection.leaf_to_list(p, "Hatches", [''])
        self.validhatches(self.hatches)
        # 图例等级值
        self.legendvalue = Projection.leaf_to_list(p, "LegendValue", None)

        # 图例颜色值
        self.legendcolor = Projection.leaf_to_list(p, "LegendColor", None)

        # ---------- 无投影时的图例配置 start --------
        # 图例放置方式
        self.orientation = Projection.leaf_to_string(p, 'Orientation', 'vertical')

        # 图例离边框位置
        self.anchor = Projection.leaf_to_list(p, "Anchor", [0, 0])

        # 图例收缩系数
        self.shrink = Projection.leaf_to_float(p, "Shrink", 1)

        self.fraction = Projection.leaf_to_float(p, 'Fraction', 0.15)

        # ---------- 有投影时的图例配置 start --------
        # 图例收缩系数
        self.size = Projection.leaf_to_string(leaf=p, code='Size', defvalue='5%')

        # 图例离边框位置
        self.pad = Projection.leaf_to_string(leaf=p, code='Pad', defvalue='2%')

        # 图例放置位置
        self.location = Projection.leaf_to_string(leaf=p, code='Location', defvalue='right')

    def valid(self, pin):
        if pin is not None and len(pin) == 3:
            if pin[1] < pin[0] or pin[2] < 0:
                self.pinlegendvalue = None
        else:
            self.pinlegendvalue = None

    def validhatches(self, hatches):
        hatches_list = ["", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]
        if hatches is not None:
            self.hatches = [a if a in hatches_list else '' for a in hatches]

