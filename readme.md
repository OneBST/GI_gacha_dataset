# 提要

**持续收集原神抽卡记录中**

可以使用抽卡记录导出工具导出抽卡记录的json，将json文件发送至**onebst@foxmail.com**，我会在清除个人信息后将文件提交到此处。以下两种导出工具任选其一即可。

[一种抽卡记录导出工具](https://github.com/sunfkny/genshin-gacha-export) from sunfkny [使用方法演示视频](https://www.bilibili.com/video/BV1tr4y1K7Ea/)

[另一种electron版的抽卡记录导出工具](https://github.com/biuuu/genshin-gacha-export/releases) from lvlvl

目前数据集中有195917条抽卡记录



## 数据使用说明

你可以以个人身份自由的使用本项目数据用于抽卡机制研究，你可以自由的修改和发布我的分析代码（虽然我这代码还不如重新写一次）

但是**一定不要将抽卡数据集发布整合到别的平台上**，若如此，以后有人去使用多个来源的抽卡数据可能会遇到严重的数据重复问题。请让想要获得抽卡数据朋友来GitHub下载，或注明数据来自本项目。

在使用本数据集得出任何结论时，请自问过程是否严谨，结论是否可信。不应当发布显然不正确的抽卡模型或是不正确且会造成不良影响的模型，如造成不良影响，数据集整理者和提供数据的玩家不负任何责任。

通过一段时间的研究，我基本整理出了原神抽卡的所有机制：

[原神抽卡全机制总结](https://www.bilibili.com/read/cv10468091)

[分析抽卡机制的一些工具](https://www.bilibili.com/read/cv10152872)



## 数据格式说明

dataset_02文件夹中文件从0001开始顺序编号

每个文件夹内包含一个账号的抽卡记录

> 
> - gacha100.csv  记录初行者推荐祈愿抽卡数据
> - gacha200.csv  记录常驻祈愿抽卡数据
> - gacha301.csv  记录角色活动祈愿数据
> - gacha302.csv  记录武器活动祈愿数据
> 

csv文件内数据记录格式如下
| 抽卡时间 | 名称 | 类别 | 星级 |
| :------: | :----: | :----: | :----: |
| YYYY-MM-DD HH:MM:SS | 物品全名 | 角色/武器 | 3/4/5 |



## 推荐数据处理方式

**计算综合概率估计值时采用无偏估计量**

使用物品出现总次数/每次最后一次抽到研究星级物品时的抽数作为估计量

请不要使用物品出现总次数/总抽数，这对于原神这样的抽卡有保底的情况下并不是官方公布综合概率的无偏估计，会使得估计概率偏低

举个例子，如果数据中所有账号都只在常驻祈愿中抽10次，那么大量数据下统计得到的五星频率应该是0.6%，而不是1.6%。统计五星时应取最后一次抽到五星物品时的抽数作为总抽数，同理也应这样应用于四星

**对于每个账号，去除抽取到的前几个五星/四星**

收集数据时要求抽卡数据提供者标明自己是否有刷过初始五星号等，意用于去除玩家行为带来的偏差

后来发现很多提供者并未标注，并且及时不刷初始号，一开始就抽到了五星的玩家更容易留下来继续游戏，造成偏差

而对于玩了一会已经有一定数量五星的玩家，能不能再抽到五星对其是否继续玩的影响变得更低了

因此可以去除每个账号抽到的前N个五星，N的个数可以据情况选取，可以获得偏差更低的数据

同理也可以应用于四星的统计

**精细研究四星概率时略去总抽数过少的数据**

总抽数过少时，很难出现已经抽了九次没四星，然后抽到第十次出了五星这类情况，会导致四星的出率偏高

使用抽数较多的数据可以更精细的研究四星的概率

**谨慎处理武器池**

武器池的数据量比较小，做任何判断时都应该谨慎。若草草下了结论，造成了严重的影响，下结论的人是有责任的。



## 分析工具说明

DataAnalysis.py用于分析csv抽卡文件，这段代码还在重写中，**会非常的难用，仅供参考**，运行后会输出参考统计量并画出分布图，分布图中理论值是我根据实际数据、部分游戏文件推理建立的概率增长模型。

DistributionMatrix.py用于在四星五星耦合的情况下分析设计模型的抽卡概率和分布，是计算抽卡模型的综合概率与期望的大杀器

