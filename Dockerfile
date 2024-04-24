# Установка базового образа
FROM python:3.11-slim

# Устанавливаем переменную окружения PYTHONUNBUFFERED на значение 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию /app
WORKDIR /app

# Копируем файл requirements.txt в рабочую директорию
COPY ./requirements.txt /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы из подкаталога в текущую директорию внутри контейнера
COPY ./PostBlog /app/PostBlog

# Создаем переменные окружения
ENV SECRET_KEY=i5mlr*4n-s)$ezpz&nv&9re+f-984zrt*+7m5yf%fgxsz)o+ka
ENV DEBUG=True
ENV DB_HOST=db
ENV DB_NAME=postblog_db
ENV DB_USER=nick
ENV DB_PASSWORD=nick
ENV ALLOWED_HOSTS=*
ENV DB_PORT=5432
ENV STATIC_URL=/static/
ENV STATIC_ROOT=static
ENV MEDIA_URL=media/
ENV MEDIA_ROOT=media
ENV EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
ENV EMAIL_USE_TLS=True
ENV EMAIL_HOST=smtp.list.ru
ENV EMAIL_HOST_USER=dzhango93@list.ru
ENV EMAIL_HOST_PASSWORD=PZPsdEbi4G2tK3SKVZFW
ENV EMAIL_PORT=587
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0
ENV DB_ENGINE=django.db.backends.postgresql
ENV LANGUAGE_CODE=en
ENV TIME_ZONE=Asia/Almaty
ENV STATICFILES_DIRS=staticfiles/
ENV DEFAULT_AUTO_FIELD=django.db.models.BigAutoField
ENV CSRF_COOKIE_SECURE=True
ENV FEEDBACK_EMAIL=dzhango93@list.ru
ENV REDIS_LOCATION=redis://redis:6379/0
ENV FILE_CACHE=blog_cache

# Команда для запуска сервера Django
CMD ["python", "PostBlog/manage.py", "runserver", "0.0.0.0:8000"]

