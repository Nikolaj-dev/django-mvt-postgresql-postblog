# django-mvt-postgresql-postblog
 Django-mvt postblog app with authentication system(registration, login, password reset),
 profile/followers/like/comments/feedback functionality.
 Bootstrap + custom css.
 Django-MVT(Model-view-template) project.
 Name: PostBlog(NixBlog).
 Database: PostgreSQL.
 - Authentication system(registration, login, password reset)
 - profile/followers/like/comments functionality
 - caching to a file or redis database
 - json-logging system to the .log file
 - pagination
 - feedback
 - django-messages
 - tests provided
 - templatetags
 - bootstrap css/js
 - admin interface with grappelli
 - the variables are in the environment
![Alt Text](https://github.com/Nikolaj-dev/django-mvt-sqlite-postblog/blob/main/bandicam%202023-08-16%2017-35-39-689.gif)

## Запуск проекта

1. Убедитесь, что у вас установлен Docker и Docker Compose.

2. Склонируйте репозиторий:

- git clone https://github.com/Nikolaj-dev/django-mvt-postgresql-postblog.git

3. Перейдите в каталог проекта:

- cd django-mvt-postgresql-postblog

4. Запустите контейнеры Docker с помощью команды:

- docker-compose up --build

5. После запуска контейнеров откройте браузер и перейдите по адресу [http://localhost:8000/](http://localhost:8000/) для доступа к приложению.

## Использование

- Приложение будет доступно по адресу [http://localhost:8000/](http://localhost:8000/).
- Административная панель Django будет доступна по адресу [http://localhost:8000/admin/](http://localhost:8000/admin/). Вы можете войти, используя созданный суперпользовательский аккаунт(логин admin, пароль admin).

## Остановка проекта

Чтобы остановить проект, выполните команду:

- docker-compose down

Это остановит и удалит контейнеры, связанные с проектом.

## Автор

[Ваше имя](https://github.com/Nikolaj-dev)

