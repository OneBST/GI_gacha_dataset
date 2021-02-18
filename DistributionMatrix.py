import numpy as np
from numpy import linalg as LA
M = np.zeros((990, 990), dtype=float)
# 状态定义state[i * 90 + j] (i, j>0时)i表示抽了i抽没有五星，j表示抽了j抽没有四星
# 当i == 0时，表示刚好抽到五星 j == 0时，表示刚好抽到四星
# 使用概率转移矩阵计算 M[m, n]中m表示转移到的状态，n表示转移前的状态
# state_1 = M * state_0 通过M将概率向量进行递推


# 设定抽卡概率
P_5 = np.zeros(91, dtype=float)
for i in range(1, 91):  # 专栏模型
    P_5[i] = 0.006  # 前73发概率
    if i > 73:  # 概率增长段
        P_5[i] = 0.006 + 0.053 * (i-73)
    if i == 90:  # 90发保底
        P_5[i] = 1
P_4 = np.zeros(21, dtype=float)
for i in range(1, 12):  # 专栏模型
    P_4[i] = 0.051  # 前8发概率
    if i == 9:  # 概率增长
        P_4[i] = 0.5575  # 0.575 0.5111
    if i == 10:  # 10发保底
        P_4[i] = 1
    if i == 11:  # 11发必出
        P_4[i] = 1


# 生成概率转移矩阵
for i in range(1, 90):  # 生成没抽到五星时候的矩阵
    # 抽到四星状态
    now_state = i * 11
    for j in range(11):  # 枚举上一种状态
        pre_state = (i - 1) * 11 + j
        # M[now_state, pre_state] = (1 - P_5[i]) * P_4[j+1]
        M[now_state, pre_state] = min((1 - P_5[i]), P_4[j + 1])
    # 没抽到四星状态 即抽到三星
    for j in range(11):  # 枚举上一种状态
        now_state = i * 11 + min(j+1, 10)
        pre_state = (i - 1) * 11 + j
        # M[now_state, pre_state] = (1 - P_5[i]) * (1 - P_4[j+1])
        M[now_state, pre_state] = max(1 - P_5[i] - P_4[j + 1], 0)
# 生成抽到五星时候的矩阵
for j in range(1, 11):
    now_state = j  # i一定是0 i j 不可能同时为0
    for m in range(90):
        pre_state = 11 * m + j - 1  # 前一抽四星计数小于10
        M[now_state, pre_state] = P_5[m+1]
now_state = 10  # 对于四星保底时一直出五星的情况
pre_state = 10
M[now_state, pre_state] = P_5[1]
# print(M)
# np.savetxt("P_transfer_matrix.csv", M, delimiter=',')
w, v = LA.eig(M)
for i in range(990):
    if abs(w[i] - 1) < 0.001:
        pos = i
        print(w[i])
distribution_vector = v[:, pos]
distribution_vector = distribution_vector/sum(distribution_vector)
print(sum(distribution_vector[1:11]).real)  # 取出五星的概率
P_4_tot = 0
for i in range(1, 90):
    P_4_tot += distribution_vector[i*11]
print(P_4_tot.real)  # 四星的概率
distribution_4 = np.zeros(21, dtype=float)
for i in range(90):
    for j in range(11):
        distribution_4[j+1] += (min((1 - P_5[i + 1]), P_4[j + 1]) * distribution_vector[i * 11 + j]).real
distribution_4 = distribution_4/sum(distribution_4)
print(*(distribution_4[1:12]), sep='\t')
temp = 0
for j in range(1, 12):
    temp += j * distribution_4[j]
print(1/temp)