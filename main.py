import os
import json
import pandas as pd
import re
import dateutil
import config

weekday_dic = {'月': 0, '火': 1, '水': 2, '木': 3, '金': 4, '土': 5, '日': 6}
weekday_list = ['月', '火', '水', '木', '金', '土', '日']


class MyCalendar:
    def __init__(self):
        ti_all = pd.date_range(config.START_DATE, config.END_DATE, freq='D')
        self.month = []
        for i in range(7):
            ts = ti_all[ti_all.weekday == i].to_series()
            self.month.append(ts.groupby(pd.Grouper(freq='M')))
        ti_shift = ti_all.difference(config.HOLIDAY)
        self.shift = []
        for i in range(7):
            ts = ti_shift[ti_shift.weekday == i].to_series()
            self.shift.append(ts.groupby(pd.Grouper(freq='M')))
        self.year = [ti_shift[ti_shift.weekday == i].to_series() for i in range(7)]


def csv2json():
    areas = pd.read_csv('data/area.csv')
    areas.to_json('data/area.json', orient='records', force_ascii=False)
    description = pd.read_csv('data/description.csv')
    description.to_json('data/description.json', orient='records', force_ascii=False)
    target = pd.read_csv('data/target.csv')
    target.to_json(os.path.join(config.OUTPUT, 'target.json'), orient='records', force_ascii=False)


def every_week(trash_str):
    """
    毎週の処理
    trash_str: ゴミのカテゴリの記述
    """
    label = f'毎週{trash_str}曜日'
    l = my_calendar.year[weekday_dic[trash_str]]
    return label, l, ''


def each_week(trash_str):
    """
    隔週、4週毎の処理
    trash_str: ゴミのカテゴリの記述
    """
    match = re.search(r'^e(\d+)w(\d*)$', trash_str)
    if match:
        interval = int(match[1])
        try:
            start_date = dateutil.parser.parse(match[2])
            if interval == 2:
                label = '隔週'
            elif interval > 2:
                label = str(interval) + '週毎'
            else:
                return 'エラー', pd.Series(), 'n週毎のnは2以上の整数'
            w = start_date.weekday()
            label += weekday_list[w] + '曜日'
            p = my_calendar.year[w].index.get_loc(start_date)
            p = p % interval
            l = my_calendar.year[w][p::interval]
            return label, l, ''
        except:
            return 'エラー', pd.Series(), 'n週毎の開始日に誤り'
    else:
        return 'エラー', pd.Series(), 'n週毎の記述に誤り'


def get_trash(trash_str):
    if trash_str in weekday_dic:
        return every_week(trash_str)
    elif trash_str[0] == 'e':
        return each_week(trash_str)
    return 'エラー', pd.Series(), '対応する処理がありません'


def get_trash_model(trash_str):
    trashs = trash_str.split()
    s = trashs[-1]
    if s.startswith('*'):
        remark = int(s[1:])
        trashs.pop(-1)
    else:
        remark = None

    dayLabel = []
    dayList = []
    for trash in trashs:
        label, l, error_message = get_trash(trash)
        dayLabel.append(label)
        dayList.append(l)
    dl = pd.concat(dayList).sort_values().astype(str)
    return ' '.join(dayLabel), dl, remark


def get_area_days():
    area_days = pd.read_csv('data/area_days.csv')

    for i, area in area_days.iterrows():
        trash = []
        for item in area.index:
            if item == '収集地区':
                ca = area['収集地区']
            else:
                dayLabel, dayList, remark = get_trash_model(area[item])
                trash.append(
                    {
                        'label': item,
                        'dayLabel': dayLabel,
                        'dayList': dayList.values.tolist(),
                        'remark': remark
                    })
        with open(os.path.join(config.OUTPUT,f'{ca}.json'), 'w') as f:
            json.dump(trash, f, indent=2, ensure_ascii=False)


def main():
    csv2json()
    get_area_days()


if __name__ == '__main__':
    my_calendar = MyCalendar()
    main()
