from typing import Any

from airflow.hooks.base import BaseHook
from airflow.models import BaseOperator
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

        with open(self.main_config['template'], 'r', encoding='utf-8') as f:
            self.sql_text = f.read()

    def execute(self, context: Any):
        self.log.warning(self._hook.execute('select 1'))

    def post_execute(self, context: Any, result: Any = None):
        pass
