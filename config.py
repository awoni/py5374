import pandas as pd

# センターの休止日
HOLIDAY = pd.DatetimeIndex(['2018-12-31', '2019-01-01', '2019-01-02', '2019-01-03'])
# 計算期間の開始日
START_DATE = '2018-4-1'
# 計算期間の終了日
END_DATE = '2019-4-30'
# 出力先
OUTPUT = 'www/data'

'''
以下は変更がある場合の処理用です
'''
CHANGE_DATA = '2018-2-4'
INPUT_OLD = 'www/data'
INPUT_NEW = 'www/data'
