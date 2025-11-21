# Dockerfile mínimo e confiável para rodar o bot com Python 3.10
FROM python:3.10-slim

# Prevent Python from writing pyc files to disc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia apenas requirements primeiro (cache de dependências)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia todo o código
COPY . /app

# Expor porta (não obrigatória para polling; só para compatibilidade)
EXPOSE 8000

# Comando de inicialização
CMD ["python", "bot.py"]
