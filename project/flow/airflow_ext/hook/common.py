from airflow.hooks.base import BaseHook
from airflow_ext.hook.clickhouse_hook import ClickhouseHook


def get_hook_by_conn_id(conn_id) -> BaseHook:
    if conn_id.startswith('clickhouse'):
        return ClickhouseHook(click_conn_id=conn_id)

    raise ValueError(f'Unknown hook type by id {conn_id}')
