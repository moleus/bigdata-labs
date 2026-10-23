# Практика 4: Работа с S3 и DuckDB
import duckdb

con = duckdb.connect(database=':memory:')

# --- СТУДЕНТ ДОЛЖЕН НАПИСАТЬ КОД НИЖЕ ---
# 1. Установите и загрузите плагин 'httpfs' в DuckDB.
# 2. Настройте конфигурационные параметры подключения к MinIO S3.
# 3. Напишите SQL-запрос, считывающий партиционированные Parquet-файлы напрямую из S3.

con.execute("INSTALL httpfs")
con.execute("LOAD httpfs")

# MinIO из infrastructure/docker-compose.yml
con.execute("SET s3_endpoint = 'localhost:9000'")
con.execute("SET s3_access_key_id = 'admin'")
con.execute("SET s3_secret_access_key = 'SuperSecretPassword123'")
con.execute("SET s3_region = 'us-east-1'")
con.execute("SET s3_url_style = 'path'")
con.execute("SET s3_use_ssl = false")

print("S3-подключение к MinIO настроено.")
