# -*- coding: utf-8 -*-
#
#     Author:     Liu xianyao
#     Email:      flashlxy@qq.com
#     Update:     2017-04-06
#     Copyright:  ©江西省气象台 2017
#     Version:    1.1.20170406
from __future__ import print_function
from Micaps11Data import Micaps11Data
from Micaps3Data import Micaps3Data
from Micaps4Data import Micaps4Data
from Projection import Projection


class File:
    def __init__(self, root):
        leaf = root.find("File")
        if leaf is None:
            return
        self.type = Projection.leaf_to_string(leaf, "Type", "M4")
        self.filename = Projection.leaf_to_string(leaf, "FileName", "M4")
        if self.type == "M4":
            self.micapsdata = Micaps4Data(self.filename)
        elif self.type == "M3":
            self.micapsdata = Micaps3Data(self.filename)
        elif self.type == "M11":
            self.micapsdata = Micaps11Data(self.filename)
        else:
            return
