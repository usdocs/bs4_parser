# Проект парсинга pep
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=ffffff&color=5fe620)](https://www.python.org/)
[![Beautiful Soup](https://img.shields.io/badge/-BeautifulSoup-464646?style=flat&logo=BeautifulSoup&logoColor=ffffff&color=5fe620)](https://beautiful-soup-4.readthedocs.io)

## Описание
Парсер собирает данные обо всех PEP-документах

### Функции парсера:

* Сбор ссылок на статьи о нововведениях в Python;
* Сбор информации о версиях Python;
* Скачивание архива с актуальной документацией;
* Сбор статусов документов PEP и подсчёт статусов документов;
* Вывод информации в терминал (в обычном и табличном виде) и сохранение результатов работы парсинга в формате csv;
* Логирование работы парсинга;
* Обработка ошибок в работе парсинга.

## Применяемые технологии

* Python — высокоуровневый язык программирования.
* Beautiful Soup — это Python библиотека для синтаксического разбора файлов HTML/XML, которая может преобразовать даже неправильную разметку в дерево синтаксического разбора.

### Порядок действия для запуска парсера

Клонировать репозиторий и перейти в папку в проектом:

```bash
git clone git@github.com:usdocs/bs4_parser_pep.git
```

```bash
cd bs4_parser_pep
```

Создать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

```bash
source venv/scripts/activate
```

Обновить менеджер пакетов pip:

```bash
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

## Работа с парсером

### Режимы работы
Сброр ссылок на статьи о нововведениях в Python:
```bash
python main.py whats-new
```
Сброр информации о версиях Python:
```bash
python main.py latest-versions
```
Скачивание архива с актуальной документацией:
```bash
python main.py download
```
Сброр статусов документов PEP и подсчёт статусов:
```bash
python main.py pep
```

### Аргументы командной строки
Полный список аргументов:
```bash
python main.py -h
```
```bash
usage: main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```

## Директории для файлов с результатами парсинга
* _downloads_ - для архива с документацией Python;
* _results_ - для результатов парсинга;
* _logs_ - для логов.

### Разработчик проекта

Автор: Andrey Balakin  
E-mail: [usdocs@ya.ru](mailto:usdocs@ya.ru)
