﻿#  Описание проекта: "Yatube".

Данный сервис является социальной сетью для публикации личных дневников.

- Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи.
- Автор может выбрать имя и уникальный адрес для своей страницы.
- Администратор будет иметь возможность модерировать записи.
- Пользователи могут создавать новые посты, а также редактировать уже созданные.
- Пользователю могут оставлять лайки постам.
- Реализована аутентификация, авторизация и регистрация пользователей.


# Технологии
- Python 3.9 
- Django 3.2.16
- SQLite 3

## Запуск проекта


Клонировать репозиторий:

```
git@github.com:arvindj8/yatube_project.git

```

Перейти в корень проекта:
```
cd yatube_project

```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env

```

```
source env/bin/activate

```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip

```

```
pip install -r requirements.txt

```

Выполнить миграции:

```
python3 manage.py migrate

```

Запустить проект:

```
python3 manage.py runserver
```
