# Практика 1: Ленивые вычисления в DuckDB
import duckdb
import os
import sys

csv_path = "large_research_logs.csv"
# Число строк можно передать аргументом: 18000000 строк дают CSV около 0.5 ГБ
rows = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
if not os.path.exists(csv_path) or len(sys.argv) > 1:
    print(f"Генерация исходного файла для практики: {rows} строк...")
    # COPY из подзапроса пишет строки в файл потоком, без промежуточной таблицы в RAM
    duckdb.sql(f"""
        COPY (
            SELECT
                (random() * 10000)::INT as device_id,
                CASE WHEN random() > 0.5 THEN 'SUCCESS' ELSE 'ERROR' END as status,
                random() * 100 as metric_value
            FROM range({rows})
        ) TO '{csv_path}' (HEADER, DELIMITER ',');
    """)
print(f"Размер CSV: {os.path.getsize(csv_path) / 1024**2:.1f} МБ")

con = duckdb.connect(database=':memory:')
con.execute("SET memory_limit = '512MB'")

# --- СТУДЕНТ ДОЛЖЕН НАПИСАТЬ КОД НИЖЕ ---
# Напишите аналитический запрос в переменную query к 'large_research_logs.csv'
# Фильтрация по status = 'ERROR', группировка по device_id, агрегаты: count(*) и avg(metric_value)
# Добавьте HAVING по количеству ошибок > 5, сортировку по убыванию и LIMIT 10.

query = f"""
SELECT
    device_id,
    count(*) AS error_count,
    avg(metric_value) AS avg_error_value
FROM read_csv_auto('{csv_path}')
WHERE status = 'ERROR'
GROUP BY device_id
HAVING count(*) > 5
ORDER BY error_count DESC
LIMIT 10
"""

print("=== ФИЗИЧЕСКИЙ ПЛАН ВЫПОЛНЕНИЯ ===")
print(con.sql(f"EXPLAIN {query}").fetchall()[0][1])
print("\n=== EXPLAIN ANALYZE ===")
print(con.sql(f"EXPLAIN ANALYZE {query}").fetchall()[0][1])
print("\n=== ВЫЧИСЛЕНИЕ РЕЗУЛЬТАТА ===")
print(con.sql(query).pl())
