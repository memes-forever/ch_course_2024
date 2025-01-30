from airflow.hooks.base import BaseHook
from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook


def get_hook_by_conn_id(conn_id) -> BaseHook:
    if conn_id.startswith('clickhouse'):
        return ClickHouseHook(clickhouse_conn_id=conn_id)

    raise ValueError(f'Unknown hook type by id {conn_id}')
