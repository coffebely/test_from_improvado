import csv
import json
import xml.etree.cElementTree as ET
from copy import deepcopy

with open('advanced_results.tsv', 'w', newline='') as result:
    tree = ET.parse('xml_data.xml')
    root = tree.getroot()

    column = []

    incorrect = False

    for objects in root:
        for object in objects:
            if object.attrib['name'][0] not in ['D', 'M'] or not object.attrib['name'][1:].isnumeric():
                print(f'Column {object.attrib["name"]} has an incorrect name')
                incorrect = True
            else:
                column.append(object.attrib['name'])

    xml_list = []
    # проверка колонок на валидность, заполнение списка словарей
    for objects in root:
        dictionary = {}
        counter = 0
        for object in objects:
            if object.attrib['name'][0] in ['D', 'M']:
                for value in object:
                    try:
                        dictionary[column[counter]] = value.text
                        counter += 1
                    except IndexError:
                        incorrect = True
            else:
                print('Invalid input found in xml file')
                print(f'object named {object.attrib["name"]} is invalid')
        xml_list.append(dictionary)
    # проверка, нет ли пропущенных колонок
    sum_d = 0
    sum_m = 0
    for key in xml_list[0].keys():
        if key[0] == 'D':
            sum_d += int(key[1:])
            range_max_d = int(key[1:])
        else:
            sum_m += int(key[1:])
            range_max_m = int(key[1:])
    if sum_d != sum(range(range_max_d + 1)):
        print(f'Column D{sum(range(range_max_d + 1)) - sum_d} is missing in xml file')
    if sum_m != sum(range(range_max_m + 1)):
        print(f'Column M{sum(range(range_max_m + 1)) - sum_m} is missing in xml file')

    column.sort()

    writer = csv.DictWriter(result, delimiter='\t', fieldnames=column, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(xml_list)

    with open('csv_data_1.csv', 'r') as f1:
        reader = csv.DictReader(f1, delimiter=',')
        writer.writerows(reader)

    with open('csv_data_2.csv', 'r') as f2:
        reader = csv.DictReader(f2, delimiter=',')
        writer.writerows(reader)

    with open('json_data.json', 'r') as f3:
        templates = json.load(f3)
        writer.writerows(templates['fields'])

with open('advanced_results.tsv', 'r') as result:
    reader = csv.DictReader(result, delimiter='\t')
    reader = list(reader)

    # сортировка по колонкам D
    col_D = []


    def for_sort(columns, list_key):
        res = []
        for key_dict in list_key:
            res.append(columns[key_dict])
        return tuple(res)


    for D in reader[0].keys():
        if D[0] == 'D':
            col_D.append(D)
    try:
        reader.sort(key=lambda columns: for_sort(columns, col_D))
    except KeyError:
        incorrect = True
    # проверка строк на одинаковые комбинации по D
    same_element1 = []
    same_element2 = []
    to_del = []

    for count, dictionary in enumerate(reader):
        for item in dictionary.items():
            if item[0][0] == 'D':
                same_element2.append(item[1])
            else:
                break
        if same_element2 == same_element1:
            to_del.append(count)
        same_element1 = same_element2[::]
        same_element2 = []
    # группировка по уникальным комбинациям
    for number in to_del[::-1]:
        for item in reader[number].keys():
            if item[0] == 'M':
                try:
                    reader[number - 1][item] = str(int(reader[number - 1][item]) + int(reader[number][item]))
                except ValueError:
                    reader[number - 1][item] = 'None'

    new_reader = []
    copy_reader = deepcopy(reader)
    # переименование колонок M1..Mn в MS1...MSn
    for key in range(len(reader)):
        if key not in to_del:
            for item in copy_reader[key].keys():
                if item[0] == 'M':
                    reader[key][item[0] + 'S' + item[1]] = reader[key].pop(item)
            new_reader.append(reader[key])
    # проверка значений на валидность
    for key in enumerate(new_reader):
        for j in key[1].items():
            if j[0][0] == 'D' and not j[1].isalpha():
                new_reader[key[0]][j[0]] = 'None'
                incorrect = True
            elif j[0][0] == 'M' and not j[1].isnumeric():
                new_reader[key[0]][j[0]] = 'None'
                incorrect = True

with open('advanced_results.tsv', 'w', newline='') as advanced_results:
    columns_finally = []
    for col in column:
        if col[0] == 'M':
            columns_finally.append(col[0] + 'S' + col[1])
        else:
            columns_finally.append(col)

    writer = csv.DictWriter(advanced_results, delimiter='\t', fieldnames=columns_finally, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(new_reader)

    if incorrect:
        print('Incorrect input detected')
