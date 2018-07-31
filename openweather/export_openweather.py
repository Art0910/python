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

    # Добавляем аргументы для теста
    sys.argv.append('--csv')
    sys.argv.append('Moscow')
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

    # Если при запуске указан город, то в SQL-запрос добавляется условие "WHERE"
    if len(sys.argv) > 2:
        city_name = sys.argv[2]
        file_name = '{}.txt'.format(city_name)
        sql_condition = 'WHERE city = "{}"'.format(city_name)
    else:
        file_name = 'weather.{}'.format(exp_format[2:])
        sql_condition = ''
    db_name = 'weather.db'  # задаем имя файла с базой данных

    # Запрос к базе
    if os.path.exists(db_name):
        weather_db = sqlite3.connect(db_name)
        cursor = weather_db.cursor()
        cursor.execute(
            '''
            SELECT *
            FROM weather
            {}
            '''.format(sql_condition)
        )
        weather_data = cursor.fetchall()

        # Проверка на наличие выбранного города в базе
        if not weather_data:
            print('Данных о городе "{}" в базе нет! Выберите другой город или загрузите данные с сервера.'
                  .format(city_name))
            exit()
        col_names = [col[0] for col in cursor.description]

        # экспорт файла в зависимости от формата
        if exp_format == '--csv':
            with open(file_name, 'w', encoding='UTF-8') as file:
                file.write(', '.join(col_names))
                file.write('\n')
                for row in weather_data:
                    file.write(str(row)[1:-1])
                    file.write('\n')
        elif exp_format == '--html':
            pass
        elif exp_format == '--json':
            pass
    else:
        print('Файл с базой данных не найден! Он должен называться "weather.db" и лежать в одной папке со скриптом!')
        exit()


if __name__ == '__main__':
    export()

