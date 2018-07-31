""" OpenWeatherMap (экспорт)

Сделать скрипт, экспортирующий данные из базы данных погоды,
созданной скриптом openweather.py. Экспорт происходит в формате CSV или JSON.

Скрипт запускается из командной строки и получает на входе:
    export_openweather.py --csv filename [<город>]
    export_openweather.py --json filename [<город>]
    export_openweather.py --html filename [<город>]

При выгрузке в html можно по коду погоды (weather.id) подтянуть
соответствующие картинки отсюда:  http://openweathermap.org/weather-conditions

Экспорт происходит в файл filename.

Опционально можно задать в командной строке город. В этом случае
экспортируются только данные по указанному городу. Если города нет в базе -
выводится соответствующее сообщение.

"""


import sys
import sqlite3
import os
import csv
import json
import copy
def export():
    # Если при запуске указан город, то в SQL-запрос добавляется условие "WHERE"

    # Проверка на корректность параметра формата экспорта
    try:
        exp_format = sys.argv[1]
    except IndexError:
        print('Вы не указали формат экспорта! (--csv/--xml/--html)')
        exit()
    exp_formats_lst = ['--csv', '--xml', '--html']
    if exp_format not in exp_formats_lst:
        print('Вы указали неверный формат экспорта! (--csv/--xml/--html)')
        exit()

    if len(sys.argv) > 2:
        city_name = sys.argv[2]
        file_name = '{}.txt'.format(city_name)
        sql_condition = 'WHERE city = "{}"'.format(city_name)
    else:
        file_name = 'weather.txt'
        sql_condition = ''
    db_name = 'weather.db'  # задаем имя файла с базой данных
    if os.path.exists(db_name):
        weather_db = sqlite3.connect(db_name)
        cursor = weather_db.cursor()
        cursor.executescript('.headers on')
        cursor.execute(
            '''
            SELECT *
            FROM weather
            {}
            '''.format(sql_condition)
        )
        weather_data = cursor.fetchmany(10)
        print(weather_data)
        with open(file_name, 'w', encoding='UTF-8') as file:
            file.write(str(weather_data))
    else:
        print('Файл с базой данных не найден! Он должен называться "weather.db" и лежать в одной папке со скриптом!')
        exit()


if __name__ == '__main__':
    export()

