import os
from typing import Any

from airflow.hooks.dbapi import DbApiHook
from airflow.models import BaseOperator
from airflow_ext.constant import HOME_DIR, LOCAL_TZ
from airflow_ext.hook.common import get_hook_by_conn_id
from airflow_ext.utils.jinja import Jinja2


class SqlExecutorOperator(BaseOperator):
    _hook: DbApiHook
    _jinja2: Jinja2
    sql_text: str

    def __init__(self, main_config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_config = main_config
        self._conn_id = self.main_config['conn_id']
        self._template = self.main_config['template']

    def pre_execute(self, context: Any):
        self._hook = get_hook_by_conn_id(self._conn_id)

        if self.main_config['template'].endswith('.j2'):
            self._jinja2 = Jinja2(HOME_DIR)
            self.sql_text = self._jinja2.env.get_template(self.main_config['template']).render(
                data_interval_start=context['data_interval_start'].in_tz(LOCAL_TZ).strftime('%Y-%m-%d %H:%M:%S'),
                data_interval_end=context['data_interval_end'].in_tz(LOCAL_TZ).strftime('%Y-%m-%d %H:%M:%S'),
            )
        else:
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

            self._hook.run(sql)

    def post_execute(self, context: Any, result: Any = None):
        pass
