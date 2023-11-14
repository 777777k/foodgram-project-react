# foodgram-project-react
## Продуктовый помощник
### Дипломный проект курса: "Python-разработчик" (Яндекс Практикум)
[IP сервера](http://158.160.77.253/)

[Домен](https://jdk-foodgram.ddns.net/)

### Описание

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок», позволяющий создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Создание и развертка контейнеров проекта:
Форкнуть репозиторий, сконировать и перейти в корневую папку `foodgram-project-react`.
Создать файл .env и заполнить его переменными:
```
SECRET_KEY=...
DEBUG=Fasle
ALLOWED_HOSTS=...

DB_ENGINE=...
POSTGRES_DB=
POSTGRES_USER=...
POSTGRES_PASSWORD=...
DB_HOST=...
DB_PORT=...
```

Убедиться, что сервис Docker активен в системе:
```
sudo systemctl status docker
```
Собрать контейнеры:
```
sudo docker compose -f docker-compose.production.yml pull
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
```
Выполнить миграции, собрать статику:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/
```
Установить nginx:
```
sudo apt install nginx -y
sudo systemctl start nginx
```
Настроить фаерволл:
```
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```
Настроить nginx:
```
sudo nano /etc/nginx/sites-enabled/default
```
Заменяем содержимое файла на:
```
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_set_header HOST $host;
        proxy_pass http://127.0.0.1:8000;

    }
}
```
Проверяем и перезагружаем nginx:
```
sudo nginx -t
sudo systemctl reload nginx
```
### Стек технологий
* #### Django REST
* #### Python 3.9.10
* #### Gunicorn
* #### Nginx
* #### JS
* #### Node.js
* #### PostgreSQL
* #### Docker

### Автор проекта
#### [Дмитрий К.](https://github.com/777777k)

# Информация для ревьюера
### Доменное имя
https://jdk-foodgram.ddns.net/

### Информация для доступа к админке:
```
login: jidiot@yandex.ru
password: lvbnhbq123
```
### После успешного прохождения ревью, этот блок будет убран