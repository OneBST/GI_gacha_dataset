import pandas as pd
import os
from os import path as osp
from tqdm import tqdm
from multiprocessing.pool import Pool
import datetime

# 读取csv文件
def get_df(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except:  # 文件为空
            return None
    else:
        return None

# 时间处理
time_format = '%Y-%m-%d %H:%M:%S'
def get_time(time_str):
    return datetime.datetime.strptime(time_str, time_format)
def str_time(date_time):
    return date_time.strftime(time_format)

# 读取玩家信息
def read_player(hashed_uid, source_path='player_data'):
    # 条目顺序为
    # hash后的uid 新手池抽数 新手池五星数 常驻池抽数 常驻池五星数 角色池抽数 角色池五星数 武器池抽数 武器池五星数 总抽数 总五星数 最早时间 最晚时间
    begin_time = get_time('2050-12-31 12:00:00')
    end_time = get_time('2000-12-31 12:00:00')
    ans = []
    ans.append(hashed_uid[:-4])
    pools = [[100], [200], [301, 400], [302]]
    total_pulls = 0
    total_5stars = 0
    
    full_data = get_df(osp.join(source_path, hashed_uid))
    for pool in pools:
        data = full_data[full_data['gacha_type'].isin(pool)]
        if len(data) == 0:
            ans.append(0)
            ans.append(0)
            continue
        t1 = get_time(data.iloc[0]['gacha_time'])
        t2 = get_time(data.iloc[-1]['gacha_time'])

        begin_time = min(begin_time, t1)
        end_time = max(end_time, t2)

        pulls = len(data)
        fives = len(data[data['rank_type']==5])
        total_pulls += pulls
        total_5stars += fives
        ans.append(pulls)
        ans.append(fives)
    # 汇总值
    ans.append(total_pulls)
    ans.append(total_5stars)
    ans.append(str_time(begin_time))
    ans.append(str_time(end_time))
    ans.append((end_time-begin_time).days)
    return ans


if __name__=='__main__':
    # 读取文件列表
    csv_folder = 'player_data'
    file_list = os.listdir(os.path.join(csv_folder))
    file_list.sort()

    with Pool(8) as p:
        ans_list = list(tqdm(p.imap(read_player, file_list), total=len(file_list)))

    # 保存索引
    data = pd.DataFrame(ans_list, columns=[
        'uid',
        'newbee_pull', 'newbee_5',
        'stander_pull', 'stander_5',
        'character_pull', 'character_5',
        'weapon_pull', 'weapon_5',
        'total_pull', 'total_5',
        'begin_time', 'end_time', 'record_days'])
    data.to_csv('player_index.csv')