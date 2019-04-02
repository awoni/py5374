import os
import json
import pandas as pd
import re
import csv
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


def get_month_list(ss0):
    monthlist = []
    ss = []
    for i in range(len(ss0)):
        if re.fullmatch(r'([1-9]|1[0-2])', ss0[i]):
            monthlist.append(int(ss0[i]))
        else:
            ss = ss0[i:]
            break
    return monthlist, ss


class CollectionDate:
    def __init__(self, trash_str, week_shift=config.WEEKSHIFT, remarks={}):
        self.dayLabel = []
        self.dayList = []
        self.remark = None
        self.error_message = ''
        self.week_shift = week_shift

        str_list = trash_str.split(':')
        trashs = str_list[0].split()
        list_of_monthlist = []
        for i, s in enumerate(str_list[1:]):
            monthlist, ss = get_month_list(s.split())
            trashs[-1] = trashs[-1] + f'%{i}'
            list_of_monthlist.append(monthlist)
            trashs.extend(ss)

        irregular = []
        for trash in trashs:
            if trash[0] in weekday_dic:
                self.set_week(trash, list_of_monthlist)
            elif trash[0] == 'e':
                self.each_week(trash)
            elif re.fullmatch(r'\d{8}', trash):
                irregular.append(trash)
            elif trash[0] == '*':
                self.remark = remarks[trash[1:]]
            else:
                self.error_message = '正しい形式ではない'

            if self.error_message != '':
                return

        if any(irregular):
            try:
                self.dayList.append(pd.DatetimeIndex(irregular).to_series())
                self.dayLabel.append('不定期')
            except:
                self.error_message = f'{irregular} は正しい日付でない'

    def set_week(self, trash, list_of_monthlist):
        if len(trash) == 1:
            return self.every_week(trash)
        elif trash[1] == '%':
            return self.every_week(trash[0], list_of_monthlist[int(trash[2:])])
        elif trash[1] in ("1", "2", "3", "4", "5"):
            if len(trash) == 2:
                return self.nth_week(trash)
            elif trash[2] == '%':
                return self.nth_week(trash[:2], list_of_monthlist[int(trash[3:])])
        self.error_message = '正しい形式ではない'

    def every_week(self, trash, monthlist=None):
        """
        毎週の処理
        trash_str: ゴミのカテゴリの記述
        """
        self.dayLabel.append(f'毎週{trash}曜日' + ('' if monthlist is None else '(' + ','.join(map(str, monthlist)) + '月)'))
        self.dayList.append(my_calendar.get_every_week(weekday_dic[trash], monthlist))

    def nth_week(self, trash, monthlist=None):
        """
        第n曜日の処理
        trash_str: ゴミのカテゴリの記述
        """
        self.dayLabel.append(f'第{trash[1]}{trash[0]}曜日' + ('' if monthlist is None else '(' + ','.join(map(str, monthlist)) + '月)'))
        if self.week_shift:
            self.dayList.append(my_calendar.get_nth_week(weekday_dic[trash[0]], int(trash[1]) - 1, monthlist))
        else:
            self.dayList.append(my_calendar.get_nth_week(weekday_dic[trash[0]], int(trash[1]) - 1, monthlist))

    def each_week(self, trash):
        """
        隔週、4週毎の処理
        trash_str: ゴミのカテゴリの記述
        """
        match = re.search(r'^e(\d+)w(\d*)$', trash)
        if match:
            interval = int(match[1])
            try:
                if interval == 2:
                    s = '隔週'
                elif interval > 2:
                    s = str(interval) + '週毎'
                else:
                    self.error_message = 'n週毎のnは2以上の整数'
                    return
                w, nth = my_calendar.get_loc_year(match[2], interval)
                self.dayLabel.append(s + weekday_list[w] + '曜日')
                self.dayList.append(my_calendar.get_each_week(w, interval, nth))
            except:
                self.error_message = 'n週毎の開始日に誤り'
        else:
            self.error_message = 'n週毎の記述に誤り'


def csv2json():
    description = pd.read_csv('data/description.csv')
    description.to_json('data/description.json', orient='records', force_ascii=False)
    target = pd.read_csv('data/target.csv')
    target.to_json(os.path.join(config.OUTPUT, 'target.json'), orient='records', force_ascii=False)


def xlsx2json():
    areas = pd.read_excel('data/area.xlsx')
    areas.to_json('data/area.json', orient='records', force_ascii=False)


def get_remarks():
    remarks = {}
    with open('data/remarks.csv', newline='') as f:
        rd = csv.reader(f, delimiter=',')
        for row in rd:
            remarks[row[0]] = row[1]
    return remarks


def get_area_days():
    remarks = get_remarks()
    area_days = pd.read_csv('data/area_days.csv')
    for i, area_day in area_days.iterrows():
        area_label = area_day['収集地区']
        trash = []
        for item in area_day.index[1:]:
            cd = CollectionDate(area_day[item], remarks=remarks)
            if cd.error_message != "":
                print(f'地区「{area_label}」の収集日の書式にエラー、ゴミの種類: {item } 、エラーメッセージ: {cd.error_message}')
                cd.dayLabel = 'エラー'

            dl = pd.concat(cd.dayList).sort_values().astype(str)
            trash.append(
                {
                    'label': item,
                    'dayLabel': ' '.join(cd.dayLabel),
                    'dayList': dl.values.tolist(),
                    'remark': cd.remark
                })
        with open(os.path.join(config.OUTPUT, f'{area_label}.json'), 'w') as f:
            json.dump(trash, f, indent=2, ensure_ascii=False)


def main():
    #csv2json()
    xlsx2json()
    get_area_days()


if __name__ == '__main__':
    my_calendar = MyCalendar(config.START_DATE, config.END_DATE, config.HOLIDAY)
    main()
