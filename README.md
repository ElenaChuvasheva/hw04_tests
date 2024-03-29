# Тесты для социальной сети Yatube

## Описание
Тесты для приложения posts.

Проверяется доступность страниц, правильность использования шаблонов, соответствие словаря контекста ожидаемому, работа форм.

## Технологии
Python 3, Django, pytest

## Запуск
Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone <адрес репозитория>
```
```
cd hw04_tests/
```
Cоздайте и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/bin/activate
```
Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Перейдите в папку yatube с файлом manage.py:
```
cd .\yatube\
```
Зайдите в shell:
```
python manage.py shell
```
и выполните там команду для получения SECRET_KEY:
```
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```
Запишите SECRET_KEY в соответствующее место в файле settings.py.
Выполните миграции:
```
python manage.py migrate
```
Запуск тестов:
```
python manage.py test
```
Тесты находятся в папке hw04_tests\yatube\posts\tests.
