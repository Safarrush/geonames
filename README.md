## GeoNames API
Это мини-приложение предоставляет простой API для получения информации о городах на основе данных из файла RU.txt.

## Установка

### 1) Склонировать репозиторий:
Клонировать репозиторий (git clone https://github.com/Safarrush/geonames.git) и перейти в него в командной строке (cd)

### 2) Создать и активировать виртуальное окружение для проекта
```
python3 -m venv venv
source venv/scripts/activate
```
### 3) Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
python3 pip install -r requirements.txt
```
### 5) Загрузите данные из файла RU.txt и создайте базу данных SQLite:
```
python3 script.py
```
## Примеры запросов

Получение информации о городе по идентификатору geonameid:
Откройте ваш любимый инструмент для работы с API (например, Postman) и отправьте GET-запрос на:

```
[python3 -m pip install --upgrade pip
python3 pip install -r requirements.txt](http://127.0.0.1:8000/get_city_by_geonameid/12345
Где 12345 - это идентификатор geonameid города.)
```

Получение списка городов:
```
[[python3 -m pip install --upgrade pip
python3 pip install -r requirements.txt](http://127.0.0.1:8000/get_city_by_geonameid/12345
Где 12345 - это идентификатор geonameid города.)](http://127.0.0.1:8000/get_cities_list/1/10
Этот запрос вернет первые 10 городов из списка.)
```

Получение информации о двух городах:
```
[[[python3 -m pip install --upgrade pip
python3 pip install -r requirements.txt](http://127.0.0.1:8000/get_city_by_geonameid/12345
Где 12345 - это идентификатор geonameid города.)](http://127.0.0.1:8000/get_cities_list/1/10
Этот запрос вернет первые 10 городов из списка.)](http://127.0.0.1:8000/get_city_info_by_names/?city_name1=Москва&city_name2=Санкт-Петербург
Этот запрос вернет информацию о городах Москва и Санкт-Петербург, включая данные о населении, временной зоне и др.)http://127.0.0.1:8000/get_city_info_by_names/?city_name1=Москва&city_name2=Санкт-Петербург
Этот запрос вернет информацию о городах Москва и Санкт-Петербург, включая данные о населении, временной зоне и др.
```
Автор:
----------
Рушан - tg @safa_ru

[Safarrush](https://github.com/Safarrush)
Дата: 08.08.2023
