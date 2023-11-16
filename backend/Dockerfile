FROM python:3.9.10

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ../data /app/data

COPY . .

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]