# Stufe 1: Build-Phase
FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED 1

WORKDIR /backend

COPY . .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stufe 2: Ausführungs-Phase
FROM python:3.11

WORKDIR /backend

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /backend /backend

EXPOSE 7999

RUN python manage.py makemigrations

CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:7999"]
# CMD ["tail", "-f", "/dev/null"]