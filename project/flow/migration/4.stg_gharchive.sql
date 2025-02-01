CREATE TABLE IF NOT EXISTS stg_gharchive._events ON CLUSTER sharded_cluster
(
    `date_load` DateTime,
    `id` Nullable(UInt64),
    `type` Nullable(String),
    `public` Nullable(Bool),
    `created_at` Nullable(DateTime64(3)),
    `proccessed_dttm` DateTime DEFAULT now()  -- tech field
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{database}/{table}/{uuid}/{shard}', '{replica}')
ORDER BY date_load
SETTINGS index_granularity = 8192
;

CREATE TABLE IF NOT EXISTS stg_gharchive.events ON CLUSTER sharded_cluster
AS stg_gharchive._events
ENGINE = Distributed('sharded_cluster', 'stg_gharchive', '_events', xxHash64(`date_load`))  -- distributed key
;
