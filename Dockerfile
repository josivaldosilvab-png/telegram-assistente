# Dockerfile funcional usando Python 3.10 (compatível com python-telegram-bot 13)
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar dependências primeiro
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . /app

EXPOSE 8000

CMD ["python", "bot.py"]
