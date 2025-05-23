import os
from typing import Any

from airflow.hooks.dbapi import DbApiHook
from airflow.models import BaseOperator
from airflow_ext.constant import HOME_DIR, LOCAL_TZ
from airflow_ext.hook.common import get_hook_by_conn_id
from airflow_ext.utils.jinja import Jinja2


class GhArchiveOperator(BaseOperator):
    """
    url example https://data.gharchive.org/2025-01-01-15.json.gz
    """
    _hook: DbApiHook
    _jinja2: Jinja2

    def __init__(self, main_config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_config = main_config
        self._conn_id = self.main_config['conn_id']
        self._api_url = self.main_config.get('api_url', 'https://data.gharchive.org')
        self._api_foramt = self.main_config.get('api_format', '%Y-%m-%d-%H')
        self._context_column = self.main_config.get('context_column', 'data_interval_end')

        self._schema = self.main_config['schema']
        self._table = self.main_config['table']

    def _load_from_clickhouse(self):
        pass

    def _load_from_pandas(self):
        pass

    def pre_execute(self, context: Any):
        self._hook = get_hook_by_conn_id(self._conn_id)
        self._jinja2 = Jinja2(os.path.join(HOME_DIR, 'flow/dags/api_gharchive/resources'))

    def execute(self, context: Any):
        date_load = context[self._context_column].in_tz(LOCAL_TZ)

        delete_sql = self._jinja2.env.get_template('ch_delete.sql.j2').render(
            cluster=self._hook.cluster,
            schema=self._schema,
            table=self._table,
            date_load=date_load.strftime('%Y-%m-%d %H:%M:%S'),
        )
        self._hook.run(delete_sql)

        date_load_url = date_load.strftime(self._api_foramt).split('-')
        date_load_url = '-'.join(date_load_url[:-1] + [str(int(date_load_url[-1]))])
        sql = self._jinja2.env.get_template('ch_insert_from_url.sql.j2').render(
            api_url=self._api_url,
            schema=self._schema,
            table=self._table,
            date_load=date_load.strftime('%Y-%m-%d %H:%M:%S'),
            date_load_url=date_load_url,
        )
        self._hook.run(sql)

    def post_execute(self, context: Any, result: Any = None):
        pass
