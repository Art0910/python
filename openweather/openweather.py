"""
== OpenWeatherMap ==

OpenWeatherMap — онлайн-сервис, который предоставляет бесплатный API
 для доступа к данным о текущей погоде, прогнозам, для web-сервисов
 и мобильных приложений. Архивные данные доступны только на коммерческой основе.
 В качестве источника данных используются официальные метеорологические службы
 данные из метеостанций аэропортов, и данные с частных метеостанций.

Необходимо решить следующие задачи:

== Получение APPID ==
    Чтобы получать данные о погоде необходимо получить бесплатный APPID.

    Предлагается 2 варианта (по желанию):
    - получить APPID вручную
    - автоматизировать процесс получения APPID,
    используя дополнительную библиотеку GRAB (pip install grab)

        Необходимо зарегистрироваться на сайте openweathermap.org:
        https://home.openweathermap.org/users/sign_up

        Войти на сайт по ссылке:
        https://home.openweathermap.org/users/sign_in

        Свой ключ "вытащить" со страницы отсюда:
        https://home.openweathermap.org/api_keys

        Ключ имеет смысл сохранить в локальный файл, например, "app.json"


== Получение списка городов ==
    Список городов может быть получен по ссылке:
    http://bulk.openweathermap.org/sample/city.list.json.gz

    Далее снова есть несколько вариантов (по желанию):
    - скачать и распаковать список вручную
    - автоматизировать скачивание (ulrlib) и распаковку списка
     (воспользоваться модулем gzip
      или распаковать внешним архиватором, воспользовавшись модулем subprocess)

    Список достаточно большой. Представляет собой JSON-строки:
{"_id":707860,"name":"Hurzuf","country":"UA","coord":{"lon":34.283333,"lat":44.549999}}
{"_id":519188,"name":"Novinki","country":"RU","coord":{"lon":37.666668,"lat":55.683334}}


== Получение погоды ==
    На основе списка городов можно делать запрос к сервису по id города. И тут как раз понадобится APPID.
        By city ID
        Examples of API calls:
        http://api.openweathermap.org/data/2.5/weather?id=2172797&appid=b1b15e88fa797225412429c1c50c122a

    Для получения температуры по Цельсию:
    http://api.openweathermap.org/data/2.5/weather?id=520068&units=metric&appid=b1b15e88fa797225412429c1c50c122a

    Для запроса по нескольким городам сразу:
    http://api.openweathermap.org/data/2.5/group?id=524901,703448,2643743&units=metric&appid=b1b15e88fa797225412429c1c50c122a


    Данные о погоде выдаются в JSON-формате
    {"coord":{"lon":38.44,"lat":55.87},
    "weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],
    "base":"cmc stations","main":{"temp":280.03,"pressure":1006,"humidity":83,
    "temp_min":273.15,"temp_max":284.55},"wind":{"speed":3.08,"deg":265,"gust":7.2},
    "rain":{"3h":0.015},"clouds":{"all":76},"dt":1465156452,
    "sys":{"type":3,"id":57233,"message":0.0024,"country":"RU","sunrise":1465087473,
    "sunset":1465149961},"id":520068,"name":"Noginsk","cod":200}


== Сохранение данных в локальную БД ==
Программа должна позволять:
1. Создавать файл базы данных SQLite со следующей структурой данных
   (если файла базы данных не существует):

    Погода
        id_города           INTEGER PRIMARY KEY
        Город               VARCHAR(255)
        Дата                DATE
        Температура         INTEGER
        id_погоды           INTEGER                 # weather.id из JSON-данных

2. Выводить список стран из файла и предлагать пользователю выбрать страну
(ввиду того, что список городов и стран весьма велик
 имеет смысл запрашивать у пользователя имя города или страны
 и искать данные в списке доступных городов/стран (регуляркой))

3. Скачивать JSON (XML) файлы погоды в городах выбранной страны
4. Парсить последовательно каждый из файлов и добавлять данные о погоде в базу
   данных. Если данные для данного города и данного дня есть в базе - обновить
   температуру в существующей записи.


При повторном запуске скрипта:
- используется уже скачанный файл с городами;
- используется созданная база данных, новые данные добавляются и обновляются.


При работе с XML-файлами:

Доступ к данным в XML-файлах происходит через пространство имен:
<forecast ... xmlns="http://weather.yandex.ru/forecast ...>

Чтобы работать с пространствами имен удобно пользоваться такими функциями:

    # Получим пространство имен из первого тега:
    def gen_ns(tag):
        if tag.startswith('{'):
            ns, tag = tag.split('}')
            return ns[1:]
        else:
            return ''

    tree = ET.parse(f)
    root = tree.getroot()

    # Определим словарь с namespace
    namespaces = {'ns': gen_ns(root.tag)}

    # Ищем по дереву тегов
    for day in root.iterfind('ns:day', namespaces=namespaces):
        ...

"""

import urllib.request
import gzip
import os
import json
import sqlite3
from datetime import date


def main():
    """
    Выводит доступные команды на экран и обрабатывает пользователький выбор.
    Также проверяет наличие необходимой инфраструктуры (архив городов и база данных)
    """
    check_cities()
    check_database()
    while True:
        print('''Добро пожаловать в сервисы погоды!
Доступные команды:
1. Узнать погоду в городе
2. Узнать погоду во всех городах выбранной страны
3. Посмотреть список стран
4. Посмотреть список городов в выбранной стране'''
        )
        action = input('Введите номер действия ("q" для выхода): ')
        if action == '1':
            get_weather('city')
            if cont():
                continue
            else:
                break
        elif action == '2':
            get_weather('country')
            if cont():
                continue
            else:
                break
        if action == '3':
            countries_list()
            if cont():
                continue
            else:
                break
        elif action == '4':
            county_cities()
            if cont():
                continue
            else:
                break
        elif action == 'q':
            break
        else:
            action = input('Неизвестный выбор! Попробуйте еще раз: ')
    print('До свидания!')


def cont():
    print('_ '*29)
    cont = input('Для выхода введите "q", Для продолжения - нажмите "enter": ')
    if cont == 'q':
        return False
    else:
        print()
        return True


def check_cities():
    """
    Проверяет наличие архива городов и скачаивает его при необходимости
    и распаковывает  в .json
    """
    if not os.path.exists('./cities.json'):
        city_url = 'http://bulk.openweathermap.org/sample/city.list.json.gz'
        city_file_compressed = urllib.request.urlretrieve(city_url, './cities.gz')[0]
        city_file = './cities.json'

        with gzip.open(city_file_compressed, 'rt', encoding='UTF-8') as comp, \
                open(city_file, 'wt', encoding='UTF-8') as decomp:
            decomp.write(comp.read())


def check_database():
    db_name = 'weather.db'
    weather_db = sqlite3.connect(db_name)
    cursor = weather_db.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS weather (
        city_id INT,
        city VARCHAR(255),
        date TEXT,
        temperature INT,
        weather_id INT
        )
        '''
    )
    weather_db.commit()
    weather_db.close()


def countries_list():
    """
    Выводит доступный список стран
    """
    with open('./cities.json', 'rt', encoding='UTF-8') as f:
        cities_data = tuple(json.load(f))
    countries_list = sorted(set(city["country"] for city in cities_data))
    print(countries_list)
    return countries_list

def county_cities():
    """
    Выводит список городов в желаемой стране
    """
    with open('./cities.json', 'rt', encoding='UTF-8') as f:
        cities_data = tuple(json.load(f))
    country_name_user = input('\nВведите название страны (2 английских символа): ').upper()
    while True:
        if country_name_user in countries_list():
            city_name = sorted(city['name'] for city in cities_data if city['country'] == country_name_user)
            for i in city_name:
                print(i)
            break
        elif country_name_user == 'exit':
            break
        else:
            country_name_user = input('\nТакой страны нет в списке. Попробуйте еще раз '
                                      'или "exit" для выхода: ').upper()


def get_weather(mode):
    """
    В зависимости от переданного параметра выводит на экран погоду в выбранном городе
    либо во всех городах выбранной страны
    :param mode: принимает 'city' или 'country'
    """
    with open('./cities.json', 'rt', encoding='UTF-8') as f:
        cities_data = tuple(json.load(f))
    if mode == 'city':
        city_name_user = input('\nВведите название города на английском (можно неполностью): ').lower()
        cities_tech = []
        for city in cities_data:
            if city_name_user in city['name'].lower():
                cities_tech.append(city)
        if len(cities_tech) > 1:
            for i in cities_tech:
                print(i)
            city_id_user = input("Надено {} совпадений! Уточните id города: ".format(len(cities_tech)))
            for i in cities_tech:
                if str(i['id']) == city_id_user:
                    city_id = (i['id'], )
                    break
        else:
            city_id = (cities_tech[0]['id'], )
    if mode == 'country':
        country_name_user = input('\nВведите название страны (2 английских символа): ').upper()
        country_list = frozenset(city["country"] for city in cities_data)
        while True:
            if country_name_user in country_list:
                city_id = (city['id'] for city in cities_data if city['country'] == country_name_user)
                break
            elif country_name_user == 'exit':
                break
            else:
                country_name_user = input('\nТакой страны нет в списке. Попробуйте еще раз '
                                          'или "exit" для выхода: ').upper()
    get_weather_city(city_id)


def get_weather_city(cities_id):
    """
    По коду/названию города идет на сайт и запрашивает информацию о погоде с использованием api_key из файла app.json
    :return: объект (либо словарь) город (или погода)
    :param cities_id: массив id городов
    """

    # берем api_key из файла
    api_key_file = './app.json'
    with open(api_key_file, 'rt', encoding='UTF-8') as f:
        api_key = json.load(f)[0]['api_key']

    # формируем URL и скачиваем данные
    root_url = 'http://api.openweathermap.org/data/2.5/weather?id='
    cities_id = map(str, cities_id)

    for city_id in cities_id:
        full_url = '{root}{id}&units=metric&appid={api_key}'.format(root=root_url,
                                                                    id=city_id, api_key=api_key)
        with urllib.request.urlopen(full_url) as url:
            weather_data_full = json.loads(url.read())

        weather_data = {
            'city_id': weather_data_full['id'],
            'city': weather_data_full['name'],
            'date': str(date.fromtimestamp(weather_data_full['dt']).strftime('%Y.%m.%d')),
            'temp': weather_data_full['main']['temp'],
            'weather_id': weather_data_full['weather'][0]['id']
        }
        print(weather_data)
        update_weather(weather_data)


def update_weather(weather_data):
    """
    Обновление базы данных после обращения к сайту
    :param weather_data: Словарь с данными о погоде для записи в базу данных
    """
    db_name = 'weather.db'
    weather_db = sqlite3.connect(db_name)
    cursor = weather_db.cursor()
    cursor.execute(
        '''
        SELECT COUNT(*)
        FROM weather
        WHERE city_id = {city_id}
        AND date = '{date}'
        '''.format(city_id=weather_data['city_id'], date=weather_data['date'])
    )
    check = cursor.fetchone()

    # Если в базе не найдена запись с выбранным городом и сегодняшним днем, то создается новая запись
    # Если найдена - то запись обновляется
    if not check[0]:
        cursor.execute(
            '''
            INSERT INTO weather VALUES
            ({city_id}, '{city}', '{date}', {temp},{weather_id})
            '''.format(city_id=weather_data['city_id'], city=weather_data['city'],
                       date=weather_data['date'], temp=weather_data['temp'], weather_id=weather_data['weather_id'])
        )
    else:
        cursor.execute(
            '''
            UPDATE weather  
            SET temperature = {temp},
                weather_id = {weather_id}
            WHERE city_id = {city_id}
            AND date = '{date}'
            '''.format(city_id=weather_data['city_id'], date=weather_data['date'],
                       temp=weather_data['temp'], weather_id=weather_data['weather_id'])
        )
    weather_db.commit()
    weather_db.close()


if __name__ == '__main__':
    main()

