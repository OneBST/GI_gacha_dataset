import os
import pandas as pd
import numpy as np
import os.path as osp
import datetime
import tqdm
import math
from matplotlib import pyplot as plt


def wish_filter(up_only, time, pool_number, name):  # 筛选角色活动祈愿
    # 单纯是否为UP监测模式 祈愿时间 祈愿池编号 物品名称
    t_formats = ['%Y-%m-%d %H:%M:%S']
    # 1     2     3    4     5      6     7   8
    # 温迪池 可莉池 公子池 钟离池 阿贝多池 甘雨池 魈池 刻晴池
    start_times = ['2020-09-28 00:00:00', '2020-10-20 18:00:00', '2020-11-09 22:00:00', '2020-12-01 18:00:00',
                   '2020-12-22 18:00:00', '2021-01-12 18:00:00', '2021-02-02 18:00:00', '2021-02-17 18:00:00']
    end_times = ['2020-10-18 17:59:59', '2020-11-09 17:59:59', '2020-12-01 15:59:59', '2020-12-22 14:59:59',
                 '2021-01-12 15:59:59', '2021-02-02 14:59:59', '2021-02-17 15:59:59', '2021-03-02 15:59:59']
    up_characters = [['芭芭拉', '菲谢尔', '香菱', '温迪'], ['行秋', '诺艾尔', '砂糖', '可莉'], ['迪奥娜', '北斗', '凝光', '达达利亚'],
                     ['辛焱', '雷泽', '重云', '钟离'], ['菲谢尔', '砂糖', '班尼特', '阿贝多'], ['香菱', '行秋', '诺艾尔', '甘雨'],
                     ['迪奥娜', '北斗', '辛焱', '魈'], ['凝光', '班尼特', '芭芭拉', '刻晴']]

    def get_time(text_time):
        w = None
        for t_format in t_formats:
            try:
                w = datetime.datetime.strptime(text_time, t_format)
            except Exception as _:
                continue
        return w

    if up_only:  # 仅判断是不是UP角色
        for j in range(len(start_times)):
            start_time = get_time(start_times[j])
            end_time = get_time(end_times[j])
            pull_time = get_time(time)
            if (pull_time >= start_time) and (pull_time <= end_time):
                if name in up_characters[j]:  # 是不是UP角色
                    return 1
                return 0
        return 0

    # 判断是否位于某一角色活动UP池
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
pool_list = [5, 6, 7, 8, ]  # 选择的UP池
temp = 0

for i in tqdm.tqdm(file_list):  # progressBar
    folder_paths = [base_folder, i]
    folder_path = osp.join(*folder_paths)
    for j in range(4):  # 四个池子
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
                        if wish_filter(0, data.iloc[index].values[0], pool_num, 'NULL'):
                            check_select_mark = 1
                    if check_select_mark == 0:
                        counter_4 = 0
                        continue
                if counter_4 >= 12:  # 极低概率事件
                    print(i)
                    print('四星间隔超出12，需要检查')
                if data.iloc[index].values[2] == '武器':
                    star_4_distribution[counter_4][j][2] += 1
                if data.iloc[index].values[2] == '角色':
                    if j == 1:  # 常驻池
                        star_4_distribution[counter_4][j][1] += 1
                    elif wish_filter(1, data.iloc[index].values[0], 0, data.iloc[index].values[1]):
                        # 是UP角色
                        star_4_distribution[counter_4][j][0] += 1
                    else:  # 非UP四星角色
                        star_4_distribution[counter_4][j][1] += 1

                gacha_time_4 += counter_4  # 记录本次所用抽数
                counter_4 = 0
                been_5 = 0
            if this_star == 5:
                # if counter_4 == 10 and (j == 1 or j == 2):
                #     temp += 1
                #     print(data.iloc[index+1].values[1])
                #     print(data.iloc[index+1].values[3])
                max_5_star_pull = max(max_5_star_pull, counter_5)
                been_5 = 1
                if first_5 > 0:  # 消除初始号影响
                    first_5 -= 1
                    counter_5 = 0
                    continue
                if data.iloc[index].values[2] == '武器':  # 试验性
                    star_5_distribution[counter_5][j][1] += 1
                elif wish_filter(1, data.iloc[index].values[0], 0, data.iloc[index].values[1]):
                    # 是UP角色
                    star_5_distribution[counter_5][j][0] += 1
                else:
                    star_5_distribution[counter_5][j][1] += 1
                gacha_time_5 += counter_5
                counter_5 = 0


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
need_4 = np.sum(np.sum(star_4_distribution[0:12, 1:3, :], axis=2), axis=1)  # 选取标准池和角色池
need_5 = np.sum(np.sum(star_5_distribution[0:91, 1:3, :], axis=2), axis=1)  # 选取标准池和角色池
# 统计量分析
produce_var(4, need_4, 0.13)
produce_var(5, need_5, 0.016)

print('四星数量: ' + str(need_4.sum()))
# print(temp)
# print(*(need_4[1:12]), sep='\t')
print('UP四星角色')
need_4 = np.sum(np.sum(star_4_distribution[0:12, 2:3, 0:1], axis=2), axis=1)  # 选取角色池
print(*(need_4[1:12]), sep='\t')
print('四星武器')
need_4 = np.sum(np.sum(star_4_distribution[0:12, 2:3, 2:3], axis=2), axis=1)  # 选取角色池
print(*(need_4[1:12]), sep='\t')
print('其他四星角色')
need_4 = np.sum(np.sum(star_4_distribution[0:12, 2:3, 1:2], axis=2), axis=1)  # 选取角色池
print(*(need_4[1:12]), sep='\t')

print('常驻四星角色')
need_4 = np.sum(np.sum(star_4_distribution[0:12, 1:2, 1:2], axis=2), axis=1)  # 选取标准池
print(*(need_4[1:12]), sep='\t')
print('常驻四星武器')
need_4 = np.sum(np.sum(star_4_distribution[0:12, 1:2, 2:3], axis=2), axis=1)  # 选取标准池
print(*(need_4[1:12]), sep='\t')

print('五星数量: ' + str(need_5.sum()))
print(*(need_5[1:91]), sep='\t')
print('抽到五星所用的最多抽数：'+str(max_5_star_pull))


def plot_5_star_compare_graph(x):
    P_5 = np.zeros(91, dtype=float)
    Expect_distribution_5 = np.zeros(91, dtype=float)
    state_P = 1
    for i in range(1, 91):  # 专栏模型
        P_5[i] = 0.006  # 前73发概率
        if i > 73:  # 概率增长段
            P_5[i] = 0.006 + 0.053 * (i - 73)
        if i == 90:  # 90发保底
            P_5[i] = 1
        Expect_distribution_5[i] = state_P * P_5[i]
        state_P = state_P * (1 - P_5[i])  # 下个状态的概率
    plt.plot(range(1, 91), Expect_distribution_5[1:91], label='my theory')
    plt.plot(range(1, 91), x[1:91] / sum(x[1:91]), label='actual situation in dataset_02')
    plt.title('5 star distribution')
    plt.legend(loc="upper left")
    plt.savefig('plot_graph\\5star_distribution.png')
    plt.show()




plot_5_star_compare_graph(need_5)
