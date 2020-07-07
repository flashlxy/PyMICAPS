## PyMICAPS（原名：MicapsDataDraw）更新到 Python3.7 python2.7 版见分支 v2.2-py2.7-20191119

#### 一个超级实用生产图片工具，用 matplotlib 和 basemap 绘制 micaps 数据

    利用配置文件config.xml定制参数，结合micaps具体数据，

    可实现多种 micaps 数据类型的单独绘制或叠加绘制（in the future）

    并自动输出相应图像到指定文件。

###### Author：Xianyao Liu | Version：3.0.20191120 | E-mail：flashlxy@qq.com | Language：Python3.7

## 更新日志

    2019-11-20 升级到python3.7

    2019-11-19 准备升级到python3.7

    2018-07-09 更改工程名称为PyMicaps

    2018-03-25 修复一个扩大多边形区域类PolygonEx.py中的bug

    2018-03-21 修复一个在无投影下绘制shp文件的bug

    2017-04-19 裁切区对流线和风矢也有效，修复1个自定义绘图区的BUG

    2017-04-18 修复在投影下绘制第11类数据当纬度步长为负数时出不了图的BUG

    2017-04-15 修复等值线标注在裁切区外还显示的BUG，

               增加一种快捷包含shp文件中所有闭合区域作为裁切区的配置参数。

    2017-04-14 增加Micaps第17类数据的绘制。

    2017-04-13 增加Micaps第11类数据的绘制，修复数个小BUG，优化配置文件逻辑。

               统一边界txt文件的格式为：

               经度 纬度 经度 纬度 经度 纬度 ......

               或

               经度 纬度
               经度 纬度
               经度 纬度
               ......

## 主要功能

#### 1、支持 Micaps 第 3、4、11、17 类数据的绘制

    目前实现了某类数据的单独绘制，多类数据叠加在不久的将来实现。

#### 2、支持多种投影

    sall：无投影，lcc:兰波托投影，mill，ortho，stere：极射赤面投影，

    npstere：北半球极射赤面投影,

    hammer，kav7，merc：麦卡托投影，gnom, cyl：等经纬度投影。

#### 3、支持底图叠加

    用一个或多个shp格式或者定制的txt文件叠加到底图。

#### 4、支持任意区域完美白化

    用shp或者定制的txt文件所形成的单个或多个闭合区域切图（也叫白化），轻松实现分省绘图。

#### 5、支持灵活配置色标

    可以自己定义色标，同时支持

[NCL 色标](http://www.ncl.ucar.edu/Document/Graphics/color_table_gallery.shtml)

#### 6、高度可定制化

    包括但不限于绘图区域、标题内容、样式、位置；色标选择、位置、放置方式；

    色版图、等值线、标注、格点着色的显隐等都实现了高度自定义。

## 程序运行

    python main.py config.xml

## 项目参考的代码及的用到的一些库

#### 代码[完美白化](http://bbs.06climate.com/forum.php?mod=viewthread&tid=42437)

    气象家园帖子作者的片段代码

#### 第三方库[nclcmaps](http://bbs.06climate.com/forum.php?mod=viewthread&tid=43521)

    作者的一个支持NCL colorbar的python库。

    matplotlib==3.0.3
    安装方法：
    conda安装 conda install matplotlib==3.0.3
    pip安装 pip install matplotlib==3.0.3

    basemap

    numpy

    natgrid
    安装包见.\lib\natgrid-0.2.1-cp37-cp37m-win_amd64.whl
    安装方法：
    pip install natgrid-0.2.1-cp37-cp37m-win_amd64.whl

    scipy

    sympy

    pyshp=1.2.10

    nclcmaps
    安装包见.\lib\nclcmaps-master.zip
    安装方法：解压后在当前目录运行python setup.py install

    cchardet

    欢迎大家star和fork，一并感谢2位作者！

## 示例数据结合适当配置文件输出的图片

    Micaps第三类数据-等经纬度投影：

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/xz.png)

    Micaps第11类数据 等经纬度和兰波托投影、自定义区域、中国区作为裁切区(流线风场也有效)

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/10.png)

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/11.png)

    Micaps第11类数据-等经纬度投影：

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/9.png)

    Micaps第11类数据-ortho投影：

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/7.png)

    Micaps第四类数据ortho投影：

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/3.png)

    Micaps第四类 数据无投影：

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/2.png)

    Micaps第四类 数据Lambert投影：

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/1.png)

    Micaps第三类数据-等经纬度投影：

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/4.png)

    Micaps第三类数据-Lambert投影：

![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/lcc.png)
