
# Установка сервисов

### Airflow install
* перед запуском команд, необходимо создать venv!
```shell
cd project

cd services/air
./update_requirements.sh

export BUILDKIT_PROGRESS=plain
docker-compose build

docker-compose down
docker-compose up -d
```

### ClickHouse install
* Разворачивание ch
```shell
cd project

cd services/ch
docker-compose down
docker-compose up -d
```
* вход в консоль клиент ch as default
```shell
docker exec -it ch-clickhouse1-1 clickhouse-client --user default --password ch_course_2024
```
* вход в консоль клиент ch as airflow_user
```shell
docker exec -it ch-clickhouse1-1 clickhouse-client --user airflow_user --password airflow_password
```





Загрузка изменений из GitHub по всем репозиториям за последние 7 дней. 
Построение snp, stg, mart слоев с использованием Apache Airflow и Clickhouse.





select 
    -- xxHash64(json) as hash_row,
    -- json
    *
FROM url(
    'https://data.gharchive.org/2025-01-01-15.json.gz', 
    'JSONEachRow',
    'id String, type String, actor String, repo String, payload String, public String, created_at String'
)
-- WHERE isValidJSON(json)
LIMIT 100
;



select *
from format(
    JSONEachRow,
    'id String, type String, actor String, repo String, payload String, public String, created_at String',
    (
    select line
    from url('https://data.gharchive.org/2025-01-01-15.json.gz', 'LineAsString')
    WHERE isValidJSON(line)
    limit 10
    )
)
;

from format(
    JSONEachRow,
    '{{ ','.join(columns_with_types) }}',
    (
        select JSON_QUERY(json, '$.value[*]') as json
        from url(
            '{{ url }}',
            'JSONAsString',
            headers(
                {{ ',\n\t\t\t\t'.join(headers) }}
            )
        )
    )
)



    ┌─json───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ {"id":"45193146633",
"type":"WatchEvent",
"actor":{"id":20070526,"login":"weltenwandler","display_login":"weltenwandler","gravatar_id":"","url":"https://api.github.com/users/weltenwandler","avatar_url":"https://avatars.githubusercontent.com/u/20070526?"},
"repo":{"id":311594993,"name":"slashback100/presence_simulation","url":"https://api.github.com/repos/slashback100/presence_simulation"},
"payload":{"action":"started"},
"public":true,
"created_at":"2025-01-01T15:00:00Z"} │
