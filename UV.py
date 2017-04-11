# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-11
#     Copyright:  ©江西省气象台 2017
#     Version:    2.0.20170411
from __future__ import print_function

from Projection import Projection


class UV:
    def __init__(self, root):
        leaf = root.find("UV")
        if leaf is None:
            return

        self.stream = Projection.leaf_to_bool(leaf, 'Stream', False)
        self.density = Projection.leaf_to_list(leaf, 'Density', [1, 1])
        self.color = Projection.leaf_to_string(leaf, 'Color', 'k')
        self.onspeed = Projection.leaf_to_bool(leaf, 'OnSpeed', False)
        self.oncolor = Projection.leaf_to_bool(leaf, 'OnColor', False)
        self.linewidth = Projection.leaf_to_float(leaf, 'LineWidth', 1.)
        self.scale = Projection.leaf_to_int(leaf, 'Scale', 700)
        self.markscalelength = Projection.leaf_to_float(leaf, 'MarkScaleLength', 12.)

        self.barbs = Projection.leaf_to_bool(leaf, 'Barbs', False)
        self.length = Projection.leaf_to_int(leaf, 'Length', 1)

