import pandas as pd

# センターの休止日
HOLIDAY = pd.DatetimeIndex(['2020-01-01', '2020-01-02', '2020-01-03'])
# 計算期間の開始日
START_DATE = '2019-4-1'
# 計算期間の終了日
END_DATE = '2020-4-30'
# 休止期間なら週をずらすときは、true。金沢の仕様は、true。
WEEKSHIFT = True
# 出力先
OUTPUT = 'out'

