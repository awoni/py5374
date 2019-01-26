import pandas as pd
import main

holiday = pd.DatetimeIndex(['2018-12-31', '2019-01-01', '2019-01-02', '2019-01-03'])
cal = main.MyCalendar('2018-04-01', '2019-04-30', holiday)

weekday, nth = cal.get_loc_year('20180402', 4)
a = cal.get_each_week(weekday, 4, nth)
print('20180402から始まる４週毎')
print(a)

a = cal.get_nth_week(1, 0)
print('第一火曜日')
print(a)

b = cal.get_nth_week(1, 0, [5, 8, 1])
print('5月8月1月の第一火曜日')
print(b)

a = cal.get_shift_nth_week(1, 0)
print('第一火曜日（休止期間はずらす）')
print(a)

b = cal.get_shift_nth_week(1, 0, [5, 8, 1])
print('5月8月1月の第一火曜日（休止期間はずらす）')
print(b)
