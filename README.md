# Django stripe payment


## Тестовый проект интеграции django с платежным сервисом stripe

В проекте продемонстрированы возможности интеграции django с платежным сервисом stripe.
Реализованы модели:
- Item (товар)
- Order (заказ, объединяющий несколько товаров)
- Discount (скидка)
- Tax (налог)
- Shipping (доставка)

Дополнительные возможности:
- указание типа валюты для товара и стоимости доставки
- возможность формирования заказов как при помощи сессий, так и при помощи PaymentIntent
- выбор типа налога: включен в стоимость (inclusive) или дополнительно включается в заказ (exclusive)
- админ-панель для заполнения базы данных тестовыми данными

Текущие ограничения:
- к заказу могут прикрепляться только товары одинаковой валюты
- валюта стоимости доставки (если имеется) должна соответствовать валюте товаров
- налог и стоимость доставки может прикрепляться ко всему заказу, но не к отдельным товарам
- к заказу можно прикрепить максимуму один налог и/или один вид доставки
- величина скидки и налога задается в %, величина доставки задается в абсолютной величиной

Технологии: Python, Django, stripe, PostgreSQL, Docker, Docker Compose

Ознакомиться с проектом можно по адресу: [astimch.pythonanywhere.com](http://astimch.pythonanywhere.com/)

### Как запустить проект:

Клонировать репозиторий и перейти в папку проекта в командной строке:

```
git clone git@github.com:ASTimch/stripe-payment.git
```

Подготовить в папке проекта infra/ файл .env с переменными окружения по примеру .env.example

```
SECRET_KEY=django-insecure-key
STRIPE_PUBLIC_KEY=pk_test_1234 <публичный ключ, сгенерированный stripe>
STRIPE_SECRET_KEY=sk_test_1234 <приватный ключ, сгенерированный stripe>
DEBUG=false
DOMAIN_URL=http://127.0.0.1:8000
ALLOWED_HOSTS=localhost [::1] 127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_HOST=DB
DB_PORT=5432
POSTGRES_USER=<Имя_пользователя_базы_данных>
POSTGRES_PASSWORD=<Пароль_пользователя_базы_данных>
POSTGRES_DB=<Наименование_базы_данных>

```

Перейти в папку проекта infra/ и выполнить запуск проекта на базе Docker-контейнеров 
(предварительно убедитесь, что запущен Docker daemon):
```
cd infra
sudo docker-compose up --build
```

Создать учетную запись суперпользователя. 

```
sudo docker-compose exec backend python manage.py createsuperuser

```

Проект будет доступен по адресу

```
http://localhost/
```

Доступ к админ панели по адресу (можно заполнить базу тестовыми данными)

```
http://localhost/admin/
```

Для завершения работы оркестра контейнеров
```
sudo docker-compose down
```
