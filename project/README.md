# Проектная работа, на тему: Загрузка изменений из GitHub по всем репозиториям за последние n дней. Построение ETL с использованием Airflow и Clickhouse

## Features
### Airflow
* Используем Airflow как оркестратор
* Для Airflow собираем кастомный образ на базе официального
  * Для связи Airflow с ClickHouse используем `airflow-clickhouse-plugin`, ее в стандартном airflow нет.
    Для того, чтобы поставить ее - пишем свой [.env](services/air/.env), [docker-compose.yaml](services/air/docker-compose.yaml), [Dockerfile](services/air/Dockerfile), [constraints.txt](services/air/constraints.txt) и [requirements.txt](services/air/requirements.txt)
  * Файлы [constraints.txt](services/air/constraints.txt) и [requirements.txt](services/air/requirements.txt) помогут развернуть локальную среду для дебага дагов.
  * Файл [constraints.txt](services/air/constraints.txt) нужен для ограничения установки библиотек, которые могут поломать airflow. (такие списки готовят сами разработчики ПО)
* Локальная среда с дебагом
  * Копия среды из airflow, для удобной аннотации и подсказок из IDE
  * Дебаг, без необходимости запускать вебку airflow
* Фабрика дагов [air_dag_factory](flow/dags/air_dag_factory)
  Нужна для генерации дагов из .yaml файликов, упрощает написание дагов
* Кастомная, минибиблиотека [airflow_ext](flow/airflow_ext), написанная под проект для облегчения написания операторов
  * Включает в себя Фабрику дагов [dag_factory.py](flow/airflow_ext/utils/dag_factory.py)
  * Jinja2 хелпер, [jinja.py](flow/airflow_ext/utils/jinja.py)
  * Yaml хелпер, с поддержкой некоторых полезных тэгов (!relativedate, !timedelta)
* Использование `data_interval_start/end` из контекста airflow, для удобного отслеживания статуса загрузки за определенный час
* ...

<hr>

### Clickhouse
* Используем ClickHouse как хранилище
* Кластер в ClickHouse (2 шарда по 2 реплики), шардирование данных
* Миграции [migration](flow/migration), которые запускаются через airflow
* Ролевая модель в ClickHouse [2.roles&users.sql](flow/migration/2.roles%26users.sql)
* Загрузка данных через функцию URL в Clickhouse
* ...

<hr>

## Установка

### Установка venv и зависимостей для дебага
* перед запуском команд, необходимо создать venv! (в pycharm или `python -m venv venv & source ./venv/bin/activate`)
```shell
cd project
cd services/air
./update_requirements.sh
```

### Airflow install
* Разворачивание Airflow
```shell
cd project
cd services/air

export BUILDKIT_PROGRESS=plain
docker-compose build

docker-compose down
docker-compose up -d
```
* вход в bash клиент airflow
```shell
docker exec -it air-airflow-worker-1 bash
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

<hr>

## Полезное
* Запрос для отображения распределения данных в таблицах
```sql
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
```
