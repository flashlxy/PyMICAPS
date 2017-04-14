# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406
from __future__ import print_function
from __future__ import print_function

from Main import parseInt
from Projection import Projection


class Contour:
    def __init__(self, root):
        p = root.find("Contour")

        # 是否用彩色圆点标注格点或站点
        self.scatter = Projection.leaf_to_bool(p, 'Scatter', False)
        # 圆点的透明度
        self.alpha = Projection.leaf_to_float(p, 'Alpha', 1)
        #  圆点半径 default is 10
        self.radius = Projection.leaf_to_float(p, 'Radius', 10)

        # 第三类数据等值线步长
        self.step = Projection.leaf_to_float(p, 'Step', 2.)

        # 经纬方向上的插值格点数
        self.grid = Projection.leaf_to_list(p, "Grid", [195, 216])
        if len(self.grid) != 2:
            self.grid = [195, 216]
        else:
            self.grid = [parseInt(str(g)) for g in self.grid]

        # 等值线参数
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
        leaf = p.find("ContourLabel")
        if leaf is None:
            self.contourlabel = {'visible': False, 'fmt': '%1.0f',
                                 'fontsize': 12, 'fontcolor': 'k', 'inlinespacing': 2}
        else:
            self.contourlabel = {
                'visible': Projection.leaf_to_bool(leaf, "Visible", False, 'TRUE'),
                'fmt': Projection.leaf_to_string(leaf, 'Fmt', '%1.0f'),
                'fontsize': Projection.leaf_to_float(leaf, 'FontSize', 12),
                'fontcolor': Projection.leaf_to_string(leaf, 'FontColor', 'k'),
                'inlinespacing': Projection.leaf_to_float(leaf, 'InlineSpacing', 2)
            }

