FROM python:3.13

# Установка Xvfb и других зависимостей
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Запуск через xvfb-run
CMD ["xvfb-run", "-a", "python", "main.py"]