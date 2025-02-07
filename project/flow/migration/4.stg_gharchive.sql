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


CREATE TABLE IF NOT EXISTS stg_gharchive._actor_and_org ON CLUSTER sharded_cluster
(
    `date_load` DateTime,
    `type` Nullable(String),
    `event_id` Nullable(UInt64),
    `id` Nullable(UInt64),
    `login` Nullable(String),
    `display_login` Nullable(String),
    `gravatar_id` Nullable(String),
    `url` Nullable(String),
    `avatar_url` Nullable(String),
    `proccessed_dttm` DateTime DEFAULT now()  -- tech field
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{database}/{table}/{uuid}/{shard}', '{replica}')
ORDER BY date_load
SETTINGS index_granularity = 8192
;

CREATE TABLE IF NOT EXISTS stg_gharchive.actor_and_org ON CLUSTER sharded_cluster
AS stg_gharchive._actor_and_org
ENGINE = Distributed('sharded_cluster', 'stg_gharchive', '_actor_and_org', xxHash64(`date_load`))  -- distributed key
;
