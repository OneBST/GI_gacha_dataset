from ScanTool import *
from matplotlib import pyplot as plt

gacha_pool = 'character'
temp1 = pool_index[gacha_pool]()
temp1.load_from_json('GI_' + gacha_pool + '_full.json')

gacha_pool = 'stander'
temp2 = pool_index[gacha_pool]()
temp2.load_from_json('GI_' + gacha_pool + '_full.json')

temp = temp1 + temp2
print('五星数量', sum(temp.check_list['5star'].dist))
print('估计概率', sum(temp.check_list['5star'].dist)/sum(temp.check_list['5star'].dist[:91] * np.array(range(91))))
