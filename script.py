import http.server
import json
import sqlite3
from datetime import datetime
from urllib.parse import parse_qs, unquote, urlparse

import pymorphy2
import pytz


# Загрузка данных из файла RU.txt и создание словаря с информацией
def load_geonames_data():
    geoname_dict = {}
    alternatenames_dict = {}

    # Заполняем словари данными из файла
    with open("RU.txt", "r", encoding="utf-8") as file:
        for line in file:
            fields = line.strip().split("\t")
            geonameid = int(fields[0])
            name = fields[1]
            latitude = float(fields[4])
            longitude = float(fields[5])
            population = int(fields[16])
            timezone = fields[17]
            alternatenames = fields[3].split(",")

            geoname_dict[geonameid] = {
                "geonameid": geonameid,
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "population": population,
                "timezone": timezone,
                "alternatenames": alternatenames
            }

            alternatenames_dict[geonameid] = alternatenames
    return geoname_dict


# Создание и заполнение базы данных SQLite
def create_database(geoname_dict):
    conn = sqlite3.connect("geonames.db")
    cursor = conn.cursor()

    # Создаем таблицу для хранения данных, если ее нет
    cursor.execute('''CREATE TABLE IF NOT EXISTS geonames (
                      geonameid INTEGER PRIMARY KEY,
                      name TEXT,
                      latitude REAL,
                      longitude REAL,
                      population INTEGER,
                      timezone TEXT
                  )''')

    # Заполняем таблицу данными
    for geonameid, data in geoname_dict.items():
        # Проверяем, существует ли уже запись с таким geonameid
        cursor.execute(
            "SELECT geonameid FROM geonames WHERE geonameid=?",
            (geonameid,)
        )
        existing_data = cursor.fetchone()
        if not existing_data:
            cursor.execute('''INSERT INTO geonames (
                           geonameid, name, latitude, longitude,
                           population, timezone)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                           (geonameid, data["name"], data["latitude"],
                            data["longitude"], data["population"],
                            data["timezone"]))
    conn.commit()
    conn.close()


# Поиск города по идентификатору geonameid
def get_city_by_geonameid(geonameid, geoname_dict):
    return geoname_dict.get(geonameid, {})


# Поиск списка городов по странице и количеству на странице
def get_cities_list(page, items_per_page, geoname_dict):
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    cities = list(geoname_dict.values())[start_index:end_index]
    return cities


# Поиск информации о двух городах и определение севернее ли один из них
def get_city_info_by_names(city_name1, city_name2, geoname_dict):
    city1 = None
    city2 = None

    for city_data in geoname_dict.values():
        if (city_name1.lower() in city_data['name'].lower() or
                city_name1 in city_data['alternatenames']):
            if city1 is None or city1['population'] < city_data['population']:
                city1 = city_data
        if (city_name2.lower() in city_data['name'].lower() or
                city_name2 in city_data['alternatenames']):
            if city2 is None or city2['population'] < city_data['population']:
                city2 = city_data

    if city1 is None or city2 is None:
        return {"error": "City not found"}

    # Определение города, расположенного севернее
    northern_city = city1 if city1["latitude"] > city2["latitude"] else city2

    # Проверка, имеют ли города одинаковую временную зону
    same_timezone = city1["timezone"] == city2["timezone"]

    if not same_timezone:
        timezone1 = pytz.timezone(city1["timezone"])
        timezone2 = pytz.timezone(city2["timezone"])
        current_time = datetime.now()

        time_difference = timezone2.utcoffset(
            current_time
        ) - timezone1.utcoffset(current_time)
        hours_difference = time_difference.total_seconds() / 3600
    else:
        hours_difference = 0

    result = {
        "city1": city1,
        "city2": city2,
        "northern_city": northern_city["name"],
        "same_timezone": same_timezone,
        "hours_difference": hours_difference
    }

    return result


# Обработчик HTTP-запросов
class GeoNamesRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Получаем путь запроса без первого слеша
        path = self.path[1:]

        # Устанавливаем заголовок ответа для возврата JSON
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        # Обрабатываем запросы
        if path.startswith("get_city_by_geonameid/"):
            # Обрабатываем запрос на получение информации о городе по geonameid
            geonameid = path.split("/")[-1]
            try:
                geonameid = int(geonameid)
                city_info = get_city_by_geonameid(geonameid, geoname_dict)
                self.wfile.write(json.dumps(city_info).encode())
            except ValueError:
                self.wfile.write(b"Invalid geonameid in the request.")
        elif path.startswith("get_cities_list/"):
            # Обрабатываем запрос на получение списка городов
            _, page_str, items_per_page_str = path.split("/")
            page = int(page_str)
            items_per_page = int(items_per_page_str)
            cities_list = get_cities_list(page, items_per_page, geoname_dict)
            self.wfile.write(json.dumps(cities_list).encode())
        elif path.startswith("get_city_info_by_names/"):
            # Разбиваем путь запроса на части
            # и получаем параметры city_name1 и city_name2
            parsed_params = parse_qs(urlparse(self.path).query)
            city_name1 = parsed_params.get("city_name1", [""])[0]
            city_name2 = parsed_params.get("city_name2", [""])[0]
            city_name1 = unquote(city_name1)
            city_name2 = unquote(city_name2)

            city_info = get_city_info_by_names(
                city_name1, city_name2, geoname_dict
            )
            self.wfile.write(
                json.dumps(city_info,
                           ensure_ascii=False).encode('utf-8')
            )
        else:
            # Возвращаем ошибку, если запрос не распознан
            self.send_response(404)
            self.wfile.write(b"Not found")


# Загружаем данные из файла RU.txt и сохраняем их в базу данных SQLite
geoname_dict = load_geonames_data()
create_database(geoname_dict)

# Запускаем HTTP-сервер на localhost и порту 8000
if __name__ == "__main__":
    geoname_dict = load_geonames_data()
    create_database(geoname_dict)
    server_address = ("127.0.0.1", 8000)
    httpd = http.server.HTTPServer(server_address, GeoNamesRequestHandler)
    print("Сервер запущен на http://{}:{}".format(*server_address))
    httpd.serve_forever()
