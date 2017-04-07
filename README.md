# MicapsDataDraw
用matplotlib和basemap绘制micaps数据
利用basemap绘制micaps数据，利用配置文件config.xml定制参数。
主要功能：
1、支持Micaps第3和第4类数据的绘制
2、支持多种投影
3、支持用shp或者定制的txt文件 所形成的单个或多个闭合区域切图，也就是所谓的白化。
4、程序运行 python main.py config.xml
5、本程序用到了气象家园http://bbs.06climate.com/forum.php?mod=viewthread&tid=42437作者的片段代码、以及http://bbs.06climate.com/forum.php?mod=viewthread&tid=43521作者的一个支持NCL colorbar的python库。
