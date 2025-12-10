# Multi-stage build для C++ backend з SQLite

# Stage 1: Build
FROM gcc:11 as builder

# Встановлюємо необхідні інструменти
RUN apt-get update && apt-get install -y \
    cmake \
    make \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо вихідний код
COPY . .

# Створюємо директорію для збірки
RUN mkdir -p build && cd build && \
    cmake .. && \
    cmake --build . --config Release

# Stage 2: Runtime
FROM ubuntu:22.04

# Встановлюємо тільки необхідні runtime залежності
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

# Створюємо робочу директорію
WORKDIR /app

# Копіюємо всю build директорію і знаходимо виконуваний файл
COPY --from=builder /app/build /tmp/build

# Знаходимо і копіюємо виконуваний файл
RUN find /tmp/build -name "voting_server" -type f -executable -exec cp {} /app/voting_server \; && \
    chmod +x /app/voting_server && \
    rm -rf /tmp/build

# Створюємо директорію для бази даних
RUN mkdir -p /app/data

# Копіюємо базу даних якщо вона є
COPY --from=builder /app/data /app/data

# Встановлюємо змінну оточення для шляху до даних
ENV DATA_DIR=/app/data

# Відкриваємо порт
EXPOSE 8080

# Запускаємо сервер
CMD ["./voting_server"]
