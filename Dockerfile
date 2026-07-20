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
COPY backend/requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY backend/ /app/

# Cria diretório do banco e ajusta permissões
RUN mkdir -p /app/db && chown -R django:django /app/db

# O código pode ser lido por qualquer usuário, mas só o banco precisa de escrita
RUN chmod -R 755 /app && chmod -R 770 /app/db

USER django

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
