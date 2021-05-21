import numpy as np
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties  # 字体管理器

begin_pull = 0  # 距离上一次出五星已经垫了0抽
up_pity = 0  # 是否有大保底 1表示有 0表示没有

# DP数组 每个状态表示本抽刚好抽到五星时的概率 三个维度分别表示抽卡次数 抽到UP五星数 本次是否抽到UP五星
M = np.zeros((3001, 10, 2), dtype=float)
# 五星条件概率数组
P_5 = np.zeros(91, dtype=float)
# 在第i发抽到的转移概率
P_trans = np.zeros(91, dtype=float)
pity_pull = 90  # 九十保底
base_P = 0.006  # 基础概率
change_pull = 73  # 概率转折点
state_P = 1
for i in range(1, pity_pull+1):
    P_5[i] = base_P
    if i > change_pull:
        P_5[i] = base_P + base_P*10*(i-change_pull)
    P_5[pity_pull] = 1
    P_trans[i] = state_P * P_5[i]
    state_P = state_P * (1-P_5[i])
# print(P_trans.sum())


# 保底及垫抽数预处理
if up_pity:
    M[0][0][0] = 1
else:
    M[0][0][1] = 1
fix_const = 1-sum(P_trans[1:begin_pull+1])  # 垫抽修正常数


# DP部分
for i in range(1, 1+pity_pull*2*7):  # 抽到满命时需要的理论最大抽数
    for j in range(0, 7+1):  # 最高抽7个UP角色
        for pull in range(1, 1 + pity_pull):  # 本抽五星可能用了i抽抽出
            last_5_star = i - pull
            if last_5_star < 0:  # 从0开始
                continue
            P_trans_now = P_trans[pull]
            if last_5_star == 0:  # 垫抽修正
                if pull <= begin_pull:
                    continue
                else:
                    P_trans_now = P_trans[pull] / fix_const
            # 这次没抽到UP
            M[i][j][0] += 0.5 * M[last_5_star][j][1] * P_trans_now
            # 这次抽到了UP
            if j != 0:
                M[i][j][1] += M[last_5_star][j - 1][0] * P_trans_now + 0.5 * M[last_5_star][j - 1][1] * P_trans_now


# 设置汉字格式
font = FontProperties(fname=r"fonts\SourceHanSansSC-Bold.otf", size=10)
font_title = FontProperties(fname=r"fonts\SourceHanSansSC-Bold.otf", size=15)
# 进行绘图
plt.figure(dpi=150, figsize=(6, 5))
plt.title("原神UP角色获取概率", fontproperties=font_title)
for i in range(0, 1301, 100):  # 抽数线
    plt.axhline(y=i, ls=":", c="lightgray")
# plt.axvline(x=644-290, ls="--", c="lightgray")
# plt.axvline(x=644+290, ls="--", c="lightgray")
# plt.axvline(x=644-190, ls="--", c="lightgray")
# plt.axvline(x=644+190, ls="--", c="lightgray")
# plt.axvline(x=644, ls="-", c="gray")
max_pos = np.zeros(10, dtype=int)
attention_pos = [0.5, 0.9, 0.99]
for each_pos in attention_pos:
    plt.axvline(x=each_pos, ls="--", c="lightgray")
    plt.text(each_pos-0.08, 1225, str(int(each_pos*100))+"%", fontproperties=font, c='lightgray')
for j in range(1, 8):
    P_full_constellation = M[:, j, 1]  # 取出j-1命时的概率分布
    max_p = 0
    P_sum = np.zeros(1500, dtype=float)
    Expectation = 0
    for i in range(1, 1+pity_pull*2*7):
        if P_full_constellation[i] > max_p:
            max_p = P_full_constellation[i]
            max_pos[j] = i
        Expectation += i * P_full_constellation[i]
        P_sum[i] = P_sum[i-1] + P_full_constellation[i]  # 累加
        for each_pos in attention_pos:
            if P_sum[i] >= each_pos >= P_sum[i - 1]:
                plt.text(each_pos-0.06, i, str(i), fontproperties=font)
                if each_pos == 0.5:
                    plt.text(each_pos-0.12, i, str(j-1)+"命", fontproperties=font, c='#d96d62')
    # print(P_full_constellation.sum())
    print("Expectation of pulling "+str(j)+" UP characters is "+str(Expectation)+"  max probability at "+str(max_pos[j]))
    # print(sum(P_full_constellation[max_pos[j]-290:max_pos[j]+291]))
    # plt.plot(range(1, 1+pity_pull*2*7), P_full_constellation[1:1+pity_pull*2*7], label='theory', linewidth=1.5, c='orange')
    plt.plot(P_sum[1:1 + pity_pull * 2 * 7], range(1, 1 + pity_pull * 2 * 7), label='theory', linewidth=1.5, c='salmon')
plt.text(0.7, 30, "@一棵平衡树", fontproperties=font, c="lightgray")
plt.show()
np.save("character.npy", M)
