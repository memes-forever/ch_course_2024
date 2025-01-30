import os
from typing import Any

from airflow.hooks.base import BaseHook
from airflow.models import BaseOperator
from airflow_ext.constant import HOME_DIR
from airflow_ext.hook.common import get_hook_by_conn_id


class SqlExecutorOperator(BaseOperator):
    _hook: BaseHook
    sql_text: str

    def __init__(self, main_config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_config = main_config
        self._conn_id = self.main_config['conn_id']
        self._template = self.main_config['template']

    def pre_execute(self, context: Any):
        self._hook = get_hook_by_conn_id(self._conn_id)

        with open(os.path.join(HOME_DIR, self.main_config['template']), 'r', encoding='utf-8') as f:
            self.sql_text = f.read()

    def execute(self, context: Any):
        # delete comments from sql
        self.sql_text = '\n'.join(
            r
            for r in self.sql_text.split('\n')
            if not r.strip().startswith('--')
                and not r.strip().startswith('/*')
        )

        # run sql
        for sql in self.sql_text.split(';'):
            sql = sql.strip()
            if not sql:
                continue

            last_result = self._hook.execute(sql)
            if last_result:
                self.log.warning(f'Last result from sql: {last_result}')

    def post_execute(self, context: Any, result: Any = None):
        pass
