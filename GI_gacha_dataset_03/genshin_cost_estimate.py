# 尽量对玩家氪金进行低估

# 资源估算模型，固定部分按照某半衰时间获得一半计算，变动部分线性计算
def mixed_source_model(play_days, fixed_source, half_life, daily_source):
    base_number = pow(1/2, 1/half_life)
    fixed_get_rate = 1 - base_number ** play_days
    return fixed_get_rate * fixed_source + daily_source * play_days

# 估计免费的相遇之缘(折原石)
def free_acquaint_fate_primo(play_days, total_pull):
    # 使用总抽数估算拥有角色数量，估算获得角色升级得到相遇之缘数量
    total_character = 53
    half_collect = total_character / 2 * 62.5 * 1.5 / 2  # 估计值
    character_acquaint_fate = mixed_source_model(total_pull, total_character * 3 * 160, half_collect, 0)
    # 按照资源估算模型进行计算
    fixed_source = (30 + 20) * 160 # 这里我手工加了二用于调低获取量
    half_life = 42
    daily_source = 160 / 2.7
    # 开服送20抽
    return  character_acquaint_fate + \
            mixed_source_model(play_days, fixed_source, half_life, daily_source) + \
            20 * 160

# 估计免费的纠缠之缘(折原石)
def free_intertwined_fate_primo(play_days):
    fixed_source = 8300
    half_life = 42
    daily_source = 288
    return mixed_source_model(play_days, fixed_source, half_life, daily_source)

# 购买体力
def purchase_resin(play_days, price=800):
    # 档位分别为每60树脂 50 100 100 150 200 200 原石
    return play_days * price

# 以最省钱的方式估计氪金选项
def get_pay_choice(play_days):
    # 可供使用的氪金选项
    pay_choice = []
    # 格式 可购买的原石数量 单价
    # 小月卡
    pay_choice.append([play_days*100, 0.01])
    # 首充
    pay_choice.append([min(int((play_days+10)/365), 1) * 26160, 0.05])
    # 大月卡
    pay_choice.append([min(int((play_days+10)/42), 1) * 1480, 68/1480])
    # 后续都按照648档位计算
    return pay_choice

# 星辉兑换折扣表
def get_discount(total_pull):
    if total_pull <= 6000:
        return 0.865 * total_pull / 6000 + 1 * (6000 - total_pull) / 6000
    if total_pull < 12000:
        return 0.848 * (total_pull - 6000) / 6000 + 0.865 * (12000 - total_pull) / 6000
    return 0.848

# 计算消费
def calc_cost(  play_days,              # 游玩时间
                newbee_pull,            # 新手池抽数
                stander_pull,           # 常驻池抽数
                character_pull,         # 角色池抽数
                weapon_pull,            # 武器池抽数
                resin_price=0,          # 不购买体力，则0为价格，否则填每天的原石数量
            ):
    total_pull = 8 * newbee_pull / 10 + stander_pull + character_pull + weapon_pull
    # 纠缠之缘数量
    intertwined_pull = character_pull + weapon_pull
    # 相遇之缘数量
    acquaint_pull = 8 * newbee_pull / 10 + stander_pull  
    
    # 需要购买的原石数量
    purchase_primogem = get_discount(total_pull) * max( \
                        max(0, acquaint_pull * 160 - free_acquaint_fate_primo(play_days, total_pull)) + \
                        intertwined_pull * 160 - free_intertwined_fate_primo(play_days) \
                        , 0) + purchase_resin(play_days, resin_price)
                        
    pay_choice = get_pay_choice(play_days)

    # 计算总开销
    total_cost = 0
    for amount, price in pay_choice:
        if purchase_primogem > amount:
            purchase_primogem -= amount
            total_cost += amount * price
        else:
            total_cost += purchase_primogem * price
            purchase_primogem = 0
    if purchase_primogem > 0:
        total_cost += purchase_primogem / 8080 * 648
        purchase_primogem = 0
    
    return total_cost

if __name__ == '__main__':
    print(calc_cost(365*2-40, 20, 408, 1526+200, 68))
