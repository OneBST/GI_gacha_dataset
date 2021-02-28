import os
import pandas as pd
import numpy as np
import os.path as osp
import datetime
import tqdm
import math
from matplotlib import pyplot as plt


def weapon_filter(up_only, time, pool_number, name):  # 筛选武器活动祈愿
    # 单纯是否为UP监测模式 祈愿时间 祈愿池编号 物品名称
    t_formats = ['%Y-%m-%d %H:%M:%S']
    # 1     2     3    4     5      6     7             8
    # 温迪池 可莉池 公子池 钟离池 阿贝多池 甘雨池 魈池刻晴池前半   刻晴池后半胡桃池？
    start_times = ['2020-09-28 00:00:01',
                   '2020-10-20 18:00:00',
                   '2020-11-09 22:00:00',
                   '2020-12-01 18:00:00',
                   '2020-12-22 18:00:00',
                   '2021-01-12 18:00:00',
                   '2021-02-02 18:00:00',
                   '2021-02-23 18:00:00']
    end_times = ['2020-10-18 17:59:59',
                 '2020-11-09 17:59:59',
                 '2020-12-01 15:59:59',
                 '2020-12-22 14:59:59',
                 '2021-01-12 15:59:59',
                 '2021-02-02 14:59:59',
                 '2021-02-23 15:59:59',
                 '2021-03-16 14:59:59']
    up_characters = [['风鹰剑', '阿莫斯之弓', '笛剑', '钟剑', '流浪乐章', '绝弦', '西风长枪'],
                     ['四风原典', '狼的末路', '祭礼剑', '祭礼大剑', '祭礼残章', '祭礼弓', '匣里灭辰'],
                     ['天空之翼', '尘世之锁', '笛剑', '雨裁', '昭心', '弓藏', '西风长枪'],
                     ['贯虹之槊', '无工之剑', '匣里龙吟', '钟剑', '西风秘典', '西风猎弓', '匣里灭辰'],
                     ['斫峰之刃', '天空之卷', '西风剑', '西风大剑', '西风长枪', '祭礼残章', '绝弦'],
                     ['阿莫斯之弓', '天空之傲', '祭礼剑', '钟剑', '匣里灭辰', '昭心', '西风猎弓'],
                     ['磐岩结绿', '和璞鸢', '笛剑', '祭礼大剑', '弓藏', '昭心', '西风长枪'],
                     ['护摩之杖', '狼的末路', '千岩古剑', '千岩长枪', '匣里龙吟', '祭礼弓', '流浪乐章']]

    def get_time(text_time):
        w = None
        for t_format in t_formats:
            try:
                w = datetime.datetime.strptime(text_time, t_format)
            except Exception as _:
                continue
        return w

    if up_only:  # 仅判断是不是UP武器
        for j in range(len(start_times)):
            start_time = get_time(start_times[j])
            end_time = get_time(end_times[j])
            pull_time = get_time(time)
            if (pull_time >= start_time) and (pull_time <= end_time):
                if name in up_characters[j]:  # 是不是UP武器
                    return 1
                return 0
        return 0

    # 判断是否位于某武器UP池
    start_time = get_time(start_times[pool_number - 1])
    end_time = get_time(end_times[pool_number - 1])
    pull_time = get_time(time)

    if (pull_time >= start_time) and (pull_time <= end_time):  # 没错是我要的池
        return 1
    return 0


base_folder = 'GI_gacha_dataset_02'
file_list = os.listdir(base_folder)  # 获取数据文件夹下的文件夹
print('分析样本数量:' + str(len(file_list)))
file_names = ['gacha100.csv', 'gacha200.csv', 'gacha301.csv', 'gacha302.csv']  # 新手池/常驻池/角色池/武器池

star_5_distribution = np.zeros([91, 4, 2], dtype=int)  # 记录五星分布情况 分别对应四个池 是否UP
star_4_distribution = np.zeros([21, 4, 3], dtype=int)  # 记录四星分布情况 分别对应四个池 [UP数量 非UP但是同类型数量 其他数量]
default_header = ['抽卡时间', '编号', '名称', '类别', '星级']
gacha_time_5 = 0
gacha_time_4 = 0
all_raw_pull = 0
max_5_star_pull = 0

least_gacha_time = 0  # 每个池至少的抽卡数量
ignore_5_star = 0  # 每个池略去前几个五星
ignore_4_star = 0  # 每个池略去前几个四星
pure_4_star_model = 0  # 设为1时用于分析四星模型，若四星中途抽到五星则跳过
pool_select = 0  # 零表示不进行指定UP池选择 有数字代表选择某一个池
pool_list = [1, ]  # 选择的UP池
temp = 0
weapon_A = 0
weapon_B = 0
weapon_else = 0
weapon_list = ['磐岩结绿', '和璞鸢']

for i in tqdm.tqdm(file_list):  # progressBar
    folder_paths = [base_folder, i]
    folder_path = osp.join(*folder_paths)
    for j in range(3, 4):  # 武器池子
        file_name = file_names[j]
        processing_file = osp.join(base_folder, str(i).rjust(4, '0'), file_name)
        if os.path.exists(processing_file):
            try:
                data = pd.read_csv(processing_file)
            except:  # 文件为空
                continue
        else:
            continue
        if max(data.index) < least_gacha_time:  # 略去量少数据
            continue
        counter_5 = 0  # 抽取计数器
        first_5 = ignore_5_star  # 取消刷初始号偏差,需要略去的前几个出五星数量
        first_4 = ignore_4_star
        counter_4 = 0
        been_5 = 0  # 四星中间是否有五星
        for index, row in data.iterrows():
            all_raw_pull += 1
            counter_4 += 1
            counter_5 += 1
            this_star = data.iloc[index].values[3]
            if this_star == 4:  # 这次是四星
                if been_5 and pure_4_star_model:  # 特殊分析时，中间有五星，就略过本次
                    counter_4 = 0
                    been_5 = 0
                    continue
                if first_4 > 0:  # 消除初始号影响
                    first_4 -= 1
                    counter_4 = 0
                    continue
                # 筛选UP池时发现不是这个池子
                if pool_select:  # 开启了UP池筛选
                    check_select_mark = 0
                    for pool_num in pool_list:
                        if weapon_filter(0, data.iloc[index].values[0], pool_num, 'NULL'):
                            check_select_mark = 1
                    if check_select_mark == 0:
                        counter_4 = 0
                        continue
                if counter_4 >= 12:  # 极低概率事件
                    print(i)
                    print('四星间隔超出12，需要检查')
                if data.iloc[index].values[2] == '武器':
                    if weapon_filter(1, data.iloc[index].values[0], 0, data.iloc[index].values[1]):
                        # 是UP武器
                        star_4_distribution[counter_4][j][0] += 1
                    else:  # 非UP四星武器
                        star_4_distribution[counter_4][j][1] += 1
                if data.iloc[index].values[2] == '角色':
                    star_4_distribution[counter_4][j][2] += 1
                gacha_time_4 += counter_4  # 记录本次所用抽数
                counter_4 = 0
                been_5 = 0
            if this_star == 5:
                max_5_star_pull = max(max_5_star_pull, counter_5)
                been_5 = 1
                if pool_select:  # 开启了UP池筛选
                    check_select_mark = 0
                    for pool_num in pool_list:
                        if weapon_filter(0, data.iloc[index].values[0], pool_num, 'NULL'):
                            check_select_mark = 1
                    if check_select_mark == 0:
                        counter_5 = 0
                        continue
                if first_5 > 0:  # 消除初始号影响
                    first_5 -= 1
                    counter_5 = 0
                    continue
                star_5_distribution[counter_5][j][1] += 1
                if weapon_filter(1, data.iloc[index].values[0], 0, data.iloc[index].values[1]):
                    # 是UP武器1
                    if data.iloc[index].values[1] == weapon_list[0]:
                        weapon_A += 1
                    # 是UP武器2
                    if data.iloc[index].values[1] == weapon_list[1]:
                        weapon_B += 1
                    # print(data.iloc[index].values[1])
                else:
                    weapon_else += 1
                gacha_time_5 += counter_5
                counter_5 = 0
# print(weapon_list[0]+':'+str(weapon_A))
# print(weapon_list[1]+':'+str(weapon_B))
# print('其他武器'+':'+str(weapon_else))


def produce_var(star, gacha_data, check_p):
    tot = 0
    for k in range(1, len(gacha_data)):
        tot += k * gacha_data[k]
    data_mean = tot / sum(gacha_data)
    s_2 = 0
    for k in range(1, len(gacha_data)):
        s_2 += gacha_data[k] * (k - data_mean) ** 2
    s_2 = s_2 / (sum(gacha_data) - 1)
    stander_check = (data_mean - 1 / check_p) / math.sqrt(s_2 / sum(gacha_data))
    print('===' + str(star) + '星分析===')
    print('样本量' + str(sum(gacha_data)))
    print('样本均值' + str(data_mean))
    print('样本平均概率' + str(1 / data_mean))
    print('样本方差' + str(s_2))
    print('转为01正态的参考值' + str(stander_check))  # 假设检验量，此方法数学上不严格，仅供参考


print('原始数据统计总抽数：' + str(all_raw_pull))
need_4 = np.sum(np.sum(star_4_distribution[0:12, 3:4, :], axis=2), axis=1)  # 选取武器池
need_5 = np.sum(np.sum(star_5_distribution[0:91, 3:4, :], axis=2), axis=1)  # 选取武器池
print(*(need_5[1:81]), sep='\t')

# 统计量分析
# produce_var(4, need_4, 0.145)

# 这部分是我分析四星时随意写的，之后会改这些乱七八糟的玩意
# print('四星数量: ' + str(need_4.sum()))
# print(*(need_4[1:12]), sep='\t')
# print('UP四星武器')
# need_4 = np.sum(np.sum(star_4_distribution[0:12, 3:4, 0:1], axis=2), axis=1)
# print(*(need_4[1:12]), sep='\t')
# print('四星角色')
# need_4 = np.sum(np.sum(star_4_distribution[0:12, 3:4, 2:3], axis=2), axis=1)
# print(*(need_4[1:12]), sep='\t')
# print('其他四星武器')
# need_4 = np.sum(np.sum(star_4_distribution[0:12, 3:4, 1:2], axis=2), axis=1)
# print(*(need_4[1:12]), sep='\t')


def plot_5_star_compare_graph(x, weapon_pool):
    P_5 = np.zeros(91, dtype=float)
    Expect_distribution_5 = np.zeros(91, dtype=float)
    state_P = 1
    expect_pull_time = 0  # 期望抽卡数
    guarantee_pull = 90  # 一定能抽到
    max_pull = 0
    change_point = 72
    file_text = 'weapon'
    for i in range(1, 81):  # 专栏模型
        P_5[i] = 0.007  # 前73发概率
        if i >= 63:  # 概率增长段
            P_5[i] = 0.007 + 0.07 * (i - 62)
        if i >= change_point:  # 概率增长段
            P_5[i] = P_5[change_point - 1] + 0.035 * (i - change_point + 1)
        if i == 80:  # 80发保底
            P_5[i] = 1
        Expect_distribution_5[i] = state_P * P_5[i]
        state_P = state_P * (1 - P_5[i])  # 下个状态的概率
        expect_pull_time += Expect_distribution_5[i] * i
    print(*(P_5[60:81]), sep='\t')
    tot = 0  # 此处用于计算样本概率的无偏估计量
    for k in range(1, len(x)):
        tot += k * x[k]
        if x[k]:
            max_pull = k
    data_mean = tot / sum(x)

    plt.plot(range(1, guarantee_pull+1), Expect_distribution_5[1:guarantee_pull+1], label='theory')
    plt.plot(range(1, guarantee_pull+1), x[1:guarantee_pull+1] / sum(x[1:guarantee_pull+1]),
             label='actual situation in dataset_02')
    plt.title(file_text+' 5 star distribution')
    plt.legend(loc="upper left")
    plt.text(15, 0.06, '5star sample number:' + str(sum(x[1:guarantee_pull+1])) + '\n' +
             'theory probability:'+str(round(100/expect_pull_time, 4))+'%' + '\n' +
             'sample probability:'+str(round(100/data_mean, 4))+'%' + '\n' +
             'max pull:' + str(max_pull),
             verticalalignment="top", horizontalalignment="left")  #
    plt.savefig('plot_graph\\temp_theory_' + file_text + '.png', figsize=(15, 8), dpi=200)
    plt.show()


plot_5_star_compare_graph(need_5, 1)  # 武器池