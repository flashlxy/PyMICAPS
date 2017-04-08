# MicapsDataDraw 

## 用matplotlib和basemap绘制micaps数据

利用配置文件config.xml定制参数，结合micaps具体数据，可实现一种或多种类型（in the future）的micaps数据的叠加绘制并自动输出相应图像到指定文件。

## 主要功能：

### 1、支持Micaps第3和第4类数据的绘制

### 2、支持多种投影

sall：无投影，lcc:兰波托投影，mill，ortho，stere：极射赤面投影，

npstere：北半球极射赤面投影, 

hammer，kav7，merc：麦卡托投影，gnom, cyl：等经纬度投影

### 3、支持用shp或者定制的txt文件 所形成的单个或多个闭合区域切图，也就是所谓的白化。

### 4、程序运行 

       python main.py config.xml

### 5、本项目参考的代码及的用到的一些库

   气象家园帖子
 
   http://bbs.06climate.com/forum.php?mod=viewthread&tid=42437
   
   作者的片段代码
   
   以及
   
   http://bbs.06climate.com/forum.php?mod=viewthread&tid=43521
   
   作者的一个支持NCL colorbar的python库。
   
   欢迎大家star和fork，一并感谢2位作者！
   
## 以下是利用示例数据结合适当配置文件输出的图片
   
   Micaps第四类数据ortho投影：
   
   ![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/3.png)
   
   Micaps第四类 数据无投影：
   
   ![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/2.png)
   
   Micaps第四类 数据Lambert投影：
   
   ![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/1.png)
   
   Micaps第三类数据-等经纬度投影：
   
   ![](https://github.com/flashlxy/MicapsDataDraw/raw/master/images/4.png)
   
##### ![](https://github.com/flashlxy/MicapsDataDraw/raw/master/jxlogo.png) 
   
   
   
