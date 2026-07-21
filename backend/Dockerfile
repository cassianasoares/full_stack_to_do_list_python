FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN useradd -m django

# Copia dependências e instala
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . /app/

# Cria diretório do banco e ajusta permissões
RUN mkdir -p /app/db /app/staticfiles && \
    chown -R django:django /app/db /app/staticfiles

RUN chmod -R 755 /app && chmod -R 770 /app/db /app/staticfiles

USER django

EXPOSE 8000

# Roda migrate, coleta estáticos e inicia o gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
