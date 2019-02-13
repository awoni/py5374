import json
from dateutil.parser import parse


CHANGE_DATA = parse('2019-2-4')
INPUT_OLD = 'out'
INPUT_NEW = 'out'
OUTPUT = 'out'
CHANGE_REMARK = '２月4日からごみの収集日が変わりました'


def main():

    list_ = [{'old': 'B', 'new': 'A', 'out': 'A-B'},
             {'old': 'A', 'new': 'B', 'out': 'B-A'},
             {'old': 'C', 'new': 'B', 'out': 'B-C'},
             {'old': 'D', 'new': 'B', 'out': 'B-D'},
             {'old': 'B', 'new': 'C', 'out': 'C-B'},
             {'old': 'D', 'new': 'C', 'out': 'C-D'},
             {'old': 'C', 'new': 'D', 'out': 'D-C'}]

    for change in list_:
        with open(f"{INPUT_OLD}/{change['old']}.json") as f:
            old_list = json.load(f)
        with open(f"{INPUT_NEW}/{change['new']}.json") as f:
            new_list = json.load(f)
        trash = []
        for old, new in zip(old_list, new_list):
            if old['label'] != new['label']:
                print('ゴミの種類が一致していません')
                return
            label = new['label']
            is_change = 0
            if '隔週' in new["dayLabel"] or '週毎' in new["dayLabel"]:
                day_list = []
                for old_day_str in old["dayList"]:
                    old_date = parse(old_day_str)
                    if old_date < CHANGE_DATA:
                        day_list.append(old_day_str)
                    else:
                        flag = True
                        for new_day_str in new["dayList"]:
                            new_date = parse(new_day_str)
                            if new_date < CHANGE_DATA:
                                continue
                            else:
                                if flag:
                                    if old_date != new_date:
                                        is_change = (new_date - old_date).days // 7
                                    flag = False
                                day_list.append(new_day_str)
                        break
                if new['dayLabel'] != old['dayLabel']:
                    # day_label = f"{old['dayLabel']}→{new['dayLabel']}"
                    day_label = f"{new['dayLabel']}"
                    remark = CHANGE_REMARK
                elif is_change:
                    # day_label = f"{new['dayLabel']}（{str(is_change)+'週遅く' if is_change > 0 else str(-is_change)+'週早く'}なります）"
                    day_label = f"{new['dayLabel']}"
                    remark = CHANGE_REMARK
                else:
                    day_label = f"{new['dayLabel']}"
                    remark = None

            elif new['dayLabel'] == old['dayLabel']:
                day_label = new['dayLabel']
                day_list = new['dayList']
                remark = None
            else:
                # day_label = f"{old['dayLabel']}→{new['dayLabel']}"
                day_label = f"{new['dayLabel']}"
                remark = CHANGE_REMARK
                day_list = []
                for old_day_str in old["dayList"]:
                    old_date = parse(old_day_str)
                    if old_date < CHANGE_DATA:
                        day_list.append(old_day_str)
                    else:
                        for new_day_str in new["dayList"]:
                            new_date = parse(new_day_str)
                            if new_date < CHANGE_DATA:
                                continue
                            else:
                                day_list.append(new_day_str)
                        break

            trash.append(
                    {
                        'label': label,
                        'dayLabel': day_label,
                        'dayList': day_list,
                        'remark': remark
                    })
            with open(f"{OUTPUT}/{change['out']}.json", 'w') as f:
                json.dump(trash, f, indent=2, ensure_ascii=False)


main()
