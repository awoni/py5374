import os
import json
import pandas as pd
import re
import dateutil
import config

weekday_dic = {'月': 0, '火': 1, '水': 2, '木': 3, '金': 4, '土': 5, '日': 6}
weekday_list = ['月', '火', '水', '木', '金', '土', '日']


class MyCalendar:
    def __init__(self, start, end, holiday):
        """
        :param start: 計算期間の開始日
        :param end: 計算機関の終了日
        :param holiday: センターの休止日
        """
        self.holiday = holiday
        self.start = start
        ti_all = pd.date_range(start, end, freq='D')
        self.month = []
        for i in range(7):
            ts = ti_all[ti_all.weekday == i].to_series()
            self.month.append(ts.groupby(pd.Grouper(freq='M')))
        ti_shift = ti_all.difference(holiday)
        self.shift = []
        for i in range(7):
            ts = ti_shift[ti_shift.weekday == i].to_series()
            self.shift.append(ts.groupby(pd.Grouper(freq='M')))
        self.year = [ti_shift[ti_shift.weekday == i].to_series() for i in range(7)]

    def get_every_week(self, weekday, monthlist=None):
        """
        :param weekday: 曜日
        :return:
        """
        if monthlist is None:
            return self.year[weekday]
        else:
            ps = self.year[weekday]
            pt = ps.dt.month
            return ps[pt.isin(monthlist)]

    def get_each_week(self, weekday, interval, nth):
        """
        :param weekday: 曜日
        :param interval: 隔週の場合は2、4週ごとの場合は4
        :param nth: 0は計算期間の1週目、1は計算期間の2週目
        :return:
        """
        return self.year[weekday][nth::interval]

    def get_loc_year(self, date_str, interval):
        date_ = dateutil.parser.parse(date_str)
        weekday = date_.weekday()
        p = self.year[weekday].index.get_loc(date_)
        return weekday, p % interval

    def get_nth_week(self, weekday, nth, monthlist=None):
        ps = self.month[weekday].nth(nth)
        ps = pd.DatetimeIndex(ps).difference(self.holiday).to_series()
        if monthlist is None:
            return ps
        else:
            pt = ps.dt.month
            return ps[pt.isin(monthlist)]

    def get_shift_nth_week(self, weekday, nth, monthlist=None):
        ps = self.shift[weekday].nth(nth)
        if monthlist is None:
            return ps
        else:
            pt = ps.dt.month
            return ps[pt.isin(monthlist)]


def csv2json():
    areas = pd.read_csv('data/area.csv')
    areas.to_json('data/area.json', orient='records', force_ascii=False)
    description = pd.read_csv('data/description.csv')
    description.to_json('data/description.json', orient='records', force_ascii=False)
    target = pd.read_csv('data/target.csv')
    target.to_json(os.path.join(config.OUTPUT, 'target.json'), orient='records', force_ascii=False)


def xlsx2json():
    areas = pd.read_excel('data/area.xlsx')
    areas.to_json('data/area1.json', orient='records', force_ascii=False)


def every_week(trash_str, monthlist=None):
    """
    毎週の処理
    trash_str: ゴミのカテゴリの記述
    """
    label = f'毎週{trash_str}曜日'
    colle_date = my_calendar.get_every_week(weekday_dic[trash_str], monthlist)
    return label, colle_date, ''


def each_week(trash_str):
    """
    隔週、4週毎の処理
    trash_str: ゴミのカテゴリの記述
    """
    match = re.search(r'^e(\d+)w(\d*)$', trash_str)
    if match:
        interval = int(match[1])
        try:
            if interval == 2:
                label = '隔週'
            elif interval > 2:
                label = str(interval) + '週毎'
            else:
                return 'エラー', pd.Series(), 'n週毎のnは2以上の整数'
            w, nth = my_calendar.get_loc_year(match[2])
            label += weekday_list[w] + '曜日'
            colle_date = my_calendar.get_each_week(w, interval, nth)
            return label, colle_date, ''
        except:
            return 'エラー', pd.Series(), 'n週毎の開始日に誤り'
    else:
        return 'エラー', pd.Series(), 'n週毎の記述に誤り'


def nth_week(trash_str, monthlist=None):
    """
    第n曜日の処理
    trash_str: ゴミのカテゴリの記述
    """
    label = f'第{trash_str[1]}{trash_str[0]}曜日'
    if config.WEEKSHIFT:
        colle_date = my_calendar.get_nth_week(weekday_dic[trash_str[0]], int(trash_str[1]), monthlist)
    else:
        colle_date = my_calendar.get_nth_week(weekday_dic[trash_str[0]], trash_str[1], monthlist)
    return label, colle_date, ''


def get_month_list(n, trashs, a):
    monthlist = []
    if len(a) > 1:
        if re.fullmatch(r'([1-9]|1[0-2])', a[1:]):
            monthlist.append(int(a[1:]))
        else:
            return []
    while n + 1 < len(trashs) and re.fullmatch(r'([1-9]|1[0-2])', trashs[n + 1]):
        n = n + 1
        monthlist.append(int(trashs[n]))
    return n, monthlist


def get_trash_model(trash_str):
    trashs = trash_str.split()
    if trashs[-1].startswith('*'):
        remark = int(trashs[-1][1:])
        trashs.pop(-1)
    else:
        remark = None

    dayLabel = []
    dayList = []
    n = 0
    while n < len(trashs):
        error_mesage = '形式エラー'
        trash = trashs[n]
        if trashs[n][0] in weekday_dic:
            if len(trash) == 1:
                label, colle_date, error_mesage = every_week(trash)
            elif trash[1] == ':':
                n, monthlist = get_month_list(n, trashs, trash[1:])
                if len(monthlist) > 0:
                    label, colle_date, error_mesage = every_week(trash[0], monthlist)
            elif trash[1] in ("1", "2", "3", "4", "5"):
                if len(trash) == 2:
                    label, colle_date, error_mesage = nth_week(trash)
                elif trash[2] == ':':
                    n, monthlist = get_month_list(n, trashs, trash[1:])
                    if len(monthlist) > 0:
                        label, colle_date, error_mesage = nth_week(trash[:2], monthlist)
        elif trash_str[n] == 'e':
            label, colle_date, error_mesage = each_week(trash)
        elif re.fullmatch(r'\d{8}', trash):
            label = '不定期'
            list_ = [trash]
            while n + 1 < len(trashs) and re.fullmatch(r'\d{8}', trashs[n + 1]):
                n += 1
                list_.append(trashs[n])
            try:
                colle_date = pd.DatetimeIndex(list_).to_series()
            except:
                error_mesage = f'{list_} は正しい日付でない'

        if error_mesage != '':
            print(f'{error_mesage}: {trash}')
            n += 1
            continue

        dayLabel.append(label)
        dayList.append(colle_date)
        n += 1

    dl = pd.concat(dayList).sort_values().astype(str)
    return ' '.join(dayLabel), dl, remark


def get_area_days():
    area_days = pd.read_csv('data/area_days.csv')
    for i, area_day in area_days.iterrows():
        area_label = area_day['収集地区']
        trash = []
        for item in area_day.index[1:]:
            dayLabel, dayList, remark = get_trash_model(area_day[item])
            trash.append(
                {
                    'label': item,
                    'dayLabel': dayLabel,
                    'dayList': dayList.values.tolist(),
                    'trash_str': area_day[item],
                    'remark': remark
                })
        with open(os.path.join(config.OUTPUT, f'{area_label}.json'), 'w') as f:
            json.dump(trash, f, indent=2, ensure_ascii=False)


def main():
    csv2json()
    xlsx2json()
    get_area_days()


if __name__ == '__main__':
    my_calendar = MyCalendar(config.START_DATE, config.END_DATE, config.HOLIDAY)
    main()
