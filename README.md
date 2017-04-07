# MicapsDataDraw

## 用matplotlib和basemap绘制micaps数据

利用配置文件config.xml定制参数。

## 主要功能：

### 1、支持Micaps第3和第4类数据的绘制

### 2、支持多种投影

sall：无投影，lcc:兰波托投影，mill，ortho，stere：极射赤面投影，

npstere：北半球极射赤面投影, 

hammer，kav7，merc：麦卡托投影，gnom, cyl：等经纬度投影

### 3、支持用shp或者定制的txt文件 所形成的单个或多个闭合区域切图，也就是所谓的白化。

### 4、程序运行 python main.py config.xml

### 5、本程序用到了气象家园帖子
 
   http://bbs.06climate.com/forum.php?mod=viewthread&tid=42437
   
   作者的片段代码
   
   以及
   
   http://bbs.06climate.com/forum.php?mod=viewthread&tid=43521
   
   作者的一个支持NCL colorbar的python库。
   
   欢迎大家star和fork，一并感谢2位作者！
   
## 以下是利用示例数据结合适当配置文件输出的图片
   
   Micaps第四类数据ortho投影：
   ![](http://bbs.06climate.com/forum.php?mod=attachment&aid=NjM2MjF8ZDBjNGQ0OTR8MTQ5MTU2ODk4MnwxNTU5Mnw1MTk0NA%3D%3D&noupdate=yes)  
   
   Micaps第四类 数据无投影：
   ![](http://bbs.06climate.com/forum.php?mod=attachment&aid=NjM2MjJ8ZGNmMjY3OTR8MTQ5MTU2ODk4MnwxNTU5Mnw1MTk0NA%3D%3D&noupdate=yes)
   
   Micaps第四类 数据Lambert投影：
   ![](http://bbs.06climate.com/forum.php?mod=attachment&aid=NjM2MjN8ZDQxM2RhYzZ8MTQ5MTU2ODk4MnwxNTU5Mnw1MTk0NA%3D%3D&noupdate=yes)
   
   Micaps第三类数据-等经纬度投影：
   ![](http://bbs.06climate.com/forum.php?mod=attachment&aid=NjM2MjR8YzY3NGE3NTl8MTQ5MTU2ODk4MnwxNTU5Mnw1MTk0NA%3D%3D&noupdate=yes)
   
