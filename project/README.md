
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
docker exec -it clickhouse1 clickhouse-client --user default --password ch_course_2024
```
* вход в консоль клиент ch as airflow_user
```shell
docker exec -it clickhouse1 clickhouse-client --user airflow_user --password airflow_password
```





Загрузка изменений из GitHub по всем репозиториям за последние 7 дней. 
Построение snp, stg, mart слоев с использованием Apache Airflow и Clickhouse.

drop database snp_gharchive ON CLUSTER sharded_cluster;
create database snp_gharchive ON CLUSTER sharded_cluster;

drop table snp_gharchive._events_raw  ON CLUSTER sharded_cluster;
drop table snp_gharchive.events_raw  ON CLUSTER sharded_cluster;

select *,
    hostName(),
    _shard_num from snp_gharchive.events_raw;
select * from snp_gharchive._events_raw;

insert into snp_gharchive.events_raw
(json, date_load)
select 'awd', '2021-01-01 15:00:00'

insert into snp_gharchive.events_raw
(json, date_load)
select 
    line as json,
    '2025-01-01 15:00:00' as date_load
FROM url(
    'https://data.gharchive.org/2025-01-01-15.json.gz', 
    'LineAsString'
)
where '2025-01-01 15:00:00' not in (select date_load from snp_gharchive.events_raw group by 1)
;

insert into snp_gharchive.events_raw
(json, date_load)
select 
    line as json,
    '2025-01-01 14:00:00' as date_load
FROM url(
    'https://data.gharchive.org/2025-01-01-14.json.gz', 
    'LineAsString'
)
;


SELECT
    getMacro('replica'),
    getMacro('shard'),
    database,
    name,
    engine,
    total_rows,
    round((total_bytes / 1024) / 1024, 3) AS total_Mbytes
from clusterAllReplicas('sharded_cluster', system.tables)
WHERE database = 'snp_gharchive'


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
