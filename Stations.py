# -*- coding: utf-8 -*-
#     站点类
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-14
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170414
from __future__ import print_function
from Micaps17Data import Micaps17Data
from Projection import Projection


class Stations:
    def __init__(self, root):
        leaf = root.find("Stations")

        self.file = Projection.leaf_to_string(leaf, "File")
        self.visible = Projection.leaf_to_bool(leaf, "Visible", False)
        self.markstyle = Projection.leaf_to_list(leaf, "MarkStyle", ["o", "full"])
        self.color = Projection.leaf_to_string(leaf, "Color", "k")
        self.edgecolors = Projection.leaf_to_string(leaf, "EdgeColors", "k")

        self.alpha = Projection.leaf_to_float(leaf, "Alpha", 1.0)
        self.radius = Projection.leaf_to_float(leaf, "Radius", 5)
        self.font = Projection.leaf_to_list(leaf, "Font", [18, "myyh.ttc", "bold", "k"])
        self.detax = Projection.leaf_to_float(leaf, "Detax", 0.03)
        self.micapsdata = Micaps17Data(self.file)
