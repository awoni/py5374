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


main.my_calendar = cal
"""
ゴミのカテゴリの書式について

曜日は「日」・「月」・「火」・「水」・「木」・「金」・「土」という各曜日の一文字を記述します。

    毎週の場合は、一文字だけ記述する。
    複数ある場合は、半角スペースで区切り記述する。つまり、毎週月曜・木曜の場合は 月 木と記述する。
    毎月第1週月曜の場合は、月1と記述する。
"""

cd = main.CollectionDate('月 木')
print(cd.error_message)
print(cd.dayLabel)
dl = pd.concat(cd.dayList).sort_values().astype(str)
dl1 = dl.values.tolist()
print(dl1[:10])

cd = main.CollectionDate('月1')
print(cd.error_message)
print(cd.dayLabel)
print(cd.dayList)

"""
毎月収集が無いゴミ

毎月収集が無いゴミは対象月をコロン(:)の後に指定できます。 例えば、4、6、8、10、12、2月の偶数月の第2火曜、第4金曜の場合には、 火2 金4:4 6 8 10 12 2 のように記述します。(茨城町版仕様より追加)
"""

cd = main.CollectionDate('金4:4 6 8 10 12 2')
print(cd.error_message)
print(cd.dayLabel)
print(cd.dayList)
