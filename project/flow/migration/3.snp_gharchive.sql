CREATE TABLE IF NOT EXISTS snp_gharchive._events_raw ON CLUSTER sharded_cluster
(
    `json` String,
    `date_load` DateTime,
    `proccessed_dttm` DateTime DEFAULT now(),  -- tech field
    `hash_row` UInt64 DEFAULT xxHash64(  -- tech field
        concat(
            ifNull(toString(json), ' '),
            ifNull(toString(date_load), ' ')
        )
    )
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{database}/{table}/{uuid}/{shard}', '{replica}')
ORDER BY date_load
SETTINGS index_granularity = 8192
;

CREATE TABLE IF NOT EXISTS snp_gharchive.events_raw ON CLUSTER sharded_cluster
AS snp_gharchive._events_raw
ENGINE = Distributed('sharded_cluster', 'snp_gharchive', '_events_raw', xxHash64(`date_load`))  -- distributed key
;

-- extract json level 1
CREATE VIEW IF NOT EXISTS snp_gharchive._events_raw_extract_v ON CLUSTER sharded_cluster
(
    `json` String,
    `date_load` DateTime,
    `id` Tuple(Nullable(UInt64), Bool),
    `type` Tuple(Nullable(String), Bool),
    `public` Tuple(Nullable(Bool), Bool),
    `created_at` Tuple(Nullable(DateTime64(3)), Bool),
    `actor` Tuple(Nullable(String), Bool),
    `repo` Tuple(Nullable(String), Bool),
    `payload` Tuple(Nullable(String), Bool),
    `org` Tuple(Nullable(String), Bool),
    `proccessed_dttm` DateTime,  -- tech field
    `hash_row` UInt64    -- tech field
) AS
SELECT
  json,
  date_load,
  tuple(JSONExtract(json, 'id', 'Nullable(UInt64)'), JSONHas(json, 'id')) AS id,
  tuple(JSONExtract(json, 'type', 'Nullable(String)'), JSONHas(json, 'type')) AS type,
  tuple(JSONExtract(json, 'public', 'Nullable(Bool)'), JSONHas(json, 'public')) AS public,
  tuple(parseDateTime64BestEffortOrZero(JSONExtract(json, 'created_at', 'Nullable(String)')), JSONHas(json, 'created_at')) AS created_at,
  tuple(JSONExtract(json, 'actor', 'Nullable(String)'), JSONHas(json, 'actor')) AS actor,
  tuple(JSONExtract(json, 'repo', 'Nullable(String)'), JSONHas(json, 'repo')) AS repo,
  tuple(JSONExtract(json, 'payload', 'Nullable(String)'), JSONHas(json, 'payload')) AS payload,
  tuple(JSONExtract(json, 'org', 'Nullable(String)'), JSONHas(json, 'org')) AS org,
  proccessed_dttm,
  hash_row
FROM snp_gharchive._events_raw
;

CREATE TABLE IF NOT EXISTS snp_gharchive.events_raw_extract_v ON CLUSTER sharded_cluster
AS snp_gharchive._events_raw_extract_v
ENGINE = Distributed('sharded_cluster', 'snp_gharchive', '_events_raw_extract_v')
;

CREATE TABLE IF NOT EXISTS snp_gharchive._events_raw_extract ON CLUSTER sharded_cluster
(
    `date_load` DateTime,
    `id` Nullable(UInt64),
    `type` Nullable(String),
    `public` Nullable(Bool),
    `created_at` Nullable(DateTime64(3)),
    `actor` Nullable(String),
    `repo` Nullable(String),
    `payload` Nullable(String),
    `org` Nullable(String),
    `proccessed_dttm` DateTime DEFAULT now(),  -- tech field
    `hash_row` UInt64    -- tech field
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{database}/{table}/{uuid}/{shard}', '{replica}')
ORDER BY date_load
SETTINGS index_granularity = 8192
;

CREATE TABLE IF NOT EXISTS snp_gharchive.events_raw_extract ON CLUSTER sharded_cluster
AS snp_gharchive._events_raw_extract
ENGINE = Distributed('sharded_cluster', 'snp_gharchive', '_events_raw_extract', xxHash64(`date_load`))  -- distributed key
;
