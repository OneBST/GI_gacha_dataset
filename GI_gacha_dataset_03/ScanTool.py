from cmath import polar
from time import time
import pandas as pd
import os
from os import path as osp
from tqdm import tqdm
from multiprocessing.pool import Pool
import datetime
import numpy as np
from matplotlib import pyplot as plt
import json
import copy

class Counter():
    def __init__(self, name, uid, warn_pos, reject_pos, max_pull=300, ignore_pulls=0, ignore_items=1) -> None:
        self.name = name
        self.uid = uid
        self.begin_pos = 0
        self.warn_pos = warn_pos
        self.reject_pos = reject_pos
        self.max_pull = max_pull            # 记录的最高值

        # 计数器
        self.total_pull = 0
        self.counter = 0
        self.ignore_pulls = ignore_pulls    # 初始忽略抽数
        self.ignore_items = ignore_items    # 初始忽略道具数
        
        # 保存初始值
        self.original_ignore_pulls = ignore_pulls
        self.original_ignore_items = ignore_items

        # 结果数组
        self.dist = np.zeros(max_pull+1, dtype=int)

    # 记录新的一抽
    def record_pull(self):
        self.total_pull += 1
        self.counter += 1  

    # 记录获得道具
    def get_item(self, end_pos):
        used_pulls = self.counter
        self.counter = 0
        # 超过警戒值报警
        if used_pulls >= self.warn_pos:
            print(self.uid, self.name, "in most case pull is less than "+str(self.warn_pos)+" but it's "+str(used_pulls))

        # 排除过滤情况
        # 排除有偏情况
        if end_pos-self.begin_pos+1 < self.reject_pos:
            return
        # 排除开头抽数情况
        if self.ignore_pulls >= self.total_pull:
            return
        # 排除前几个道具情况
        if self.ignore_items > 0:
            self.ignore_items -= 1
            return

        # 记录道具
        self.dist[min(used_pulls, self.max_pull)] += 1
        self.begin_pos = self.total_pull

    def __add__(self, other):
        temp = Counter(self.name, self.uid, self.warn_pos, self.reject_pos, self.max_pull, self.original_ignore_pulls, self.original_ignore_items)
        temp.dist = self.dist + other.dist
        return temp
        

# 扫描基类
class Common_Scan():
    def __init__(self, name='CommonScan_', data=None, uid=None) -> None:
        self.name = name
        self.data = data
        self.uid = uid
        # 统计项目，此部分需要手工设置
        self.check_list = {}
        self.check_list['5star'] = Counter(name=self.name+'5star', uid=self.uid, warn_pos=89, reject_pos=90)
        self.check_list['4star'] = Counter(name=self.name+'4star', uid=self.uid, warn_pos=13, reject_pos=90)
    
    # 需要手工设置的部分，继承后重写本函数
    def check(self, row, cut_point):
        star = row['rank_type']
        # 记录情况
        if star == 5:
            self.check_list['5star'].get_item(cut_point)
        if star == 4:
            self.check_list['4star'].get_item(cut_point)

    # 以下部分不需要重写
    # 扫描csv文件
    def scan_csv(self):
        # 数据为空则返回
        if self.data is None or len(self.data) == 0:
            return

        # 数据重设编号
        self.data.reset_index(inplace=True)
        # 开始记录
        for index, row in self.data.iterrows():
            # 计数器+1
            for key in self.check_list.keys():
                self.check_list[key].record_pull()
            # 进行分项计数
            self.check(row, len(self.data)-1)

    # 合并两条记录
    def __add__(self, other):
        temp = Common_Scan(name=self.name)
        intersection_element = []
        for key in self.check_list.keys():
            if key in other.check_list.keys():
                intersection_element.append(key)
        # 两者不相交的元素扩充
        for key in self.check_list.keys():
            if key not in intersection_element:
                temp.check_list[key] = self.check_list[key]
        for key in other.check_list.keys():
            if key not in intersection_element:
                temp.check_list[key] = other.check_list[key]
        # 两者相交的元素累加
        for key in intersection_element:
            temp.check_list[key] = self.check_list[key] + other.check_list[key]
        return temp

    # 将记录保存到json文件
    def save_to_json(self, file_path):
        temp = {}
        for key in self.check_list.keys():
            temp[key] = self.check_list[key].dist.tolist()
        # 保存json
        with open(file_path,'w') as file_obj:
            json.dump(temp, file_obj)

    # 从json文件中读取数据
    def load_from_json(self, file_path):
        with open(file_path,'r',encoding='utf8') as fp:
            temp = json.load(fp)
        for key in self.check_list.keys():
            self.check_list[key].dist = np.array(temp[key])
        # 保存json
        with open(file_path,'w') as file_obj:
            json.dump(temp, file_obj)

class GI_newbee_Scan(Common_Scan):
    def __init__(self, name='GI_newbee_', data=None, uid=None) -> None:
        super().__init__(name, data, uid)

    def check(self, row, cut_point):
        super().check(row, cut_point)

class GI_stander_Scan(Common_Scan):
    def __init__(self, name='GI_stander_', data=None, uid=None) -> None:
        super().__init__(name, data, uid)
        self.check_list['5star_character'] = Counter(name=self.name+'5star_character', uid=self.uid, warn_pos=240, reject_pos=270)
        self.check_list['5star_weapon'] = Counter(name=self.name+'5star_weapon', uid=self.uid, warn_pos=240, reject_pos=270)
        self.check_list['4star_character'] = Counter(name=self.name+'4star_character', uid=self.uid, warn_pos=31, reject_pos=60)
        self.check_list['4star_weapon'] = Counter(name=self.name+'4star_weapon', uid=self.uid, warn_pos=31, reject_pos=60)

    def check(self, row, cut_point):
        super().check(row, cut_point)
        star = row['rank_type']
        type = row['item_type']
        # 五星武器
        if star == 5 and type == 1:
            self.check_list['5star_weapon'].get_item(cut_point)
        # 五星角色
        if star == 5 and type == 0:
            self.check_list['5star_character'].get_item(cut_point)
        # 四星武器
        if star == 4 and type == 1:
            self.check_list['4star_weapon'].get_item(cut_point)
        # 四星角色
        if star == 4 and type == 0:
            self.check_list['4star_character'].get_item(cut_point)

class GI_character_Scan(Common_Scan):
    def __init__(self, name='GI_character_', data=None, uid=None) -> None:
        super().__init__(name, data, uid)

    def check(self, row, cut_point):
        super().check(row, cut_point)
        

class GI_weapon_Scan(Common_Scan):
    def __init__(self, name='GI_weapon_', data=None, uid=None) -> None:
        super().__init__(name, data, uid)
        self.check_list['4star'] = Counter(name=self.name+'4star', uid=self.uid, warn_pos=12, reject_pos=90)

    def check(self, row, cut_point):
        super().check(row, cut_point)


# 初始化记录，需要添加类型至此
pool_index = {
    'newbee': GI_newbee_Scan,
    'stander': GI_stander_Scan,
    'character': GI_character_Scan,
    'weapon': GI_weapon_Scan,
}

def get_time(time_str, time_format='%Y-%m-%d %H:%M:%S'):
        return datetime.datetime.strptime(time_str, time_format)

def load_csv(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except:  # 文件为空
            return None
    else:
        return None

def Scan_players(input_param):
    # 解开输入
    csv_folder, file_name, time_gap, pools, end_drop = input_param
    uid = file_name[:-4]
    file_path = osp.join(csv_folder, file_name)
    full_data = load_csv(file_path)
    filter = {'newbee':[100], 'stander':[200], 'character':[301, 400], 'weapon':[302]}

    # 寻找时间断点
    cut_point = [0]
    last_time = get_time(full_data.iloc[0]['gacha_time'])
    for index, row in full_data.iterrows():
        time = get_time(row['gacha_time'])
        if (time-last_time).days >= time_gap:
            cut_point.append(index)
    cut_point.append(len(full_data))

    # 初始化记录字典
    ans = {}
    for pool in pools:
        ans[pool] = pool_index[pool]()

    # 切割表格，按每份独立进行分割
    for begin, end in zip(cut_point[:-1], cut_point[1:]):
        # 是否舍去末尾
        if end_drop != 0:
            end = end - end_drop
            if end < begin:
                continue
        data = full_data[begin:end]
        # 分卡池进行记录
        for pool in pools:
            # 过滤出对应卡池记录
            pool_data = copy.copy(data)
            pool_data.reset_index(inplace=True)
            pool_data = pool_data[pool_data['gacha_type'].isin(filter[pool])]
            # 对卡池信息进行扫描
            temp = pool_index[pool](data=pool_data, uid=uid)
            temp.scan_csv()
            # 累加结果
            ans[pool] = ans[pool] + temp
    return ans


if __name__=='__main__':
    csv_folder = 'player_data'
    player_index = pd.read_csv('player_index.csv')

    # 设定纳入统计至少应有的总抽数
    # player_index = player_index[player_index['total_pull'] >= 3000]
    uids = player_index['uid'].values.tolist()
    file_list = []
    for uid in uids:
        file_list.append(uid+'.csv')
    # 去除记录错误部分
    ban_list = [
        'bbad7b6e5fec6409.csv', # 重复gacha id
        '1bdc29ec142c3678.csv', # 英文部分类型标记错误
        '32099ca27c249257.csv', # 英文部分类型标记错误
        '6dd4248eb4118257.csv', # 2022/01/06 武器池不明原因四星多次超出9抽 推测数据出错
        '8cdf812aa8316564.csv', # 英文部分类型标记错误
        '991e17f2c70b7131.csv', # 2022/03/08 角色池不明原因四星多次超出10抽 推测数据出错
        'a93ad7c441961778.csv', # 2022/01/25 角色池不明原因四星多次超出10抽 推测数据出错
        'b1d4fba3bb661132.csv', # 2022/03/08 角色池不明原因四星多次超出10抽 推测数据出错
        'c8877e8891231637.csv', # 2022/03/08 角色池不明原因四星多次超出10抽 推测数据出错
        'ccb1d8a0d6055879.csv', # 2022/04/03 角色池不明原因四星多次超出10抽 推测数据出错
        'e8a2630413862369.csv', # 2022/03/08 角色池和武器池都超出10抽 推测数据出错
    ]
    temp = []
    for file in file_list:
        if file in ban_list:
            continue
        temp.append(file)
    file_list = temp
    file_list.sort()

    # 设置文件数量限制
    file_numer_limit = None
    if file_numer_limit is not None:
        file_list = file_list[:file_numer_limit]
    # file_list 存储了合法的玩家抽数文件
    print("Begin Scaning Data")

    
    # 设置需要扫描哪些卡池
    gacha_pools = ['character', 'weapon', 'stander', 'newbee']
    # 设置抽卡间隔超过多少天即不可信
    gacha_max_gap = 180


    # 根据自己cpu的核心数量修改Pool里的线程数量
    from itertools import repeat
    with Pool(16) as p:
        ans_list = list(tqdm(p.imap(Scan_players, zip(repeat(csv_folder), file_list, repeat(gacha_max_gap), repeat(gacha_pools), repeat(100))), total=len(file_list)))

    # 初始化记录字典
    sum_ans = {}
    for pool in gacha_pools:
        sum_ans[pool] = pool_index[pool]()

    # 汇集数据
    for ans in ans_list:
        for pool in gacha_pools:
            sum_ans[pool] = sum_ans[pool] + ans[pool]

    # 保存数据
    for pool in gacha_pools:
        # print(sum_ans[pool].name[:-1])
        if file_numer_limit is not None:
            save_name = sum_ans[pool].name[:-1]+'_'+str(file_numer_limit)+'.json'
        else:
            save_name = sum_ans[pool].name[:-1]+'_full.json'
        sum_ans[pool].save_to_json(save_name)