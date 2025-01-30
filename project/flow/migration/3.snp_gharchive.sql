CREATE TABLE IF NOT EXISTS snp_gharchive._events_raw ON CLUSTER sharded_cluster
(
    `json` String,
    `date_load` DateTime,
    `proccessed_dttm` DEFAULT now(),  -- tech field
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
