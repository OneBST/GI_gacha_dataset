# Readme

**持续收集原神抽卡记录中**

可以使用抽卡记录导出工具导出抽卡记录的json，将json文件发送至**onebst@foxmail.com**，我会在清除个人信息后将文件提交到此处

[抽卡记录导出工具](https://github.com/sunfkny/genshin-gacha-export) from sunfkny [使用方法演示视频](https://www.bilibili.com/video/BV1tr4y1K7Ea/)



## 数据格式说明

dataset文件夹中文件从0001开始顺序编号

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

