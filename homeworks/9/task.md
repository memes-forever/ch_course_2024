Описание/Пошаговая инструкция выполнения домашнего задания:
1. Взять любой демонстрационный DATASET, не обязательно полный набор данных:
https://clickhouse.com/docs/en/getting-started/example-datasets
2. Конвертировать таблицу в реплицируемую, используя макрос replica
3. Добавить 2 реплики
4. отдать результаты запросов как 2 файла
```sql
SELECT
getMacro(‘replica’),
*
FROM remote(’разделенный запятыми список реплик’,system.parts)
FORMAT JSONEachRow;

SELECT * FROM system.replicas FORMAT JSONEachRow;
```
5) Добавить/выбрать колонку с типом Date в таблице, добавить TTL на таблицу «хранить последние 7 дней». Предоставить результат запроса «SHOW CREATE TABLE таблица» на проверку.
