# Практика 4: Работа с S3 и DuckDB
import boto3
import duckdb

BUCKET = "research-data"

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

# DuckDB умеет писать файлы в S3, но не создаёт бакеты, поэтому бакет создаём через boto3
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="SuperSecretPassword123",
)
if BUCKET not in [b["Name"] for b in s3.list_buckets()["Buckets"]]:
    s3.create_bucket(Bucket=BUCKET)

# Тестовые логи, разбитые по дням: s3://research-data/logs/event_date=.../*.parquet
con.execute(f"""
    COPY (
        SELECT
            (random() * 1000)::INT AS device_id,
            CASE WHEN random() > 0.8 THEN 'ERROR' ELSE 'SUCCESS' END AS status,
            random() * 100 AS metric_value,
            '2026-10-0' || (i % 3 + 1) AS event_date
        FROM range(300000) t(i)
    ) TO 's3://{BUCKET}/logs' (FORMAT PARQUET, PARTITION_BY (event_date), OVERWRITE_OR_IGNORE true)
""")

query = f"""
SELECT
    event_date,
    count(*) AS error_count,
    avg(metric_value) AS avg_error_value
FROM read_parquet('s3://{BUCKET}/logs/*/*.parquet', hive_partitioning = true)
WHERE status = 'ERROR' AND event_date >= '2026-10-02'
GROUP BY event_date
ORDER BY event_date
"""

print("=== ФИЗИЧЕСКИЙ ПЛАН ВЫПОЛНЕНИЯ ===")
print(con.sql(f"EXPLAIN {query}").fetchall()[0][1])
print("\n=== РЕЗУЛЬТАТ ===")
print(con.sql(query).pl())
