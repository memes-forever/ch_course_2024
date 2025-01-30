from typing import Any

from airflow.hooks.base import BaseHook
from airflow.models import BaseOperator
from airflow_ext.constant import LOCAL_TZ
from airflow_ext.hook.common import get_hook_by_conn_id


class GhArchiveOperator(BaseOperator):
    """
    url example https://data.gharchive.org/2025-01-01-15.json.gz
    """
    _hook: BaseHook

    def __init__(self, main_config: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_config = main_config
        self._conn_id = self.main_config['conn_id']
        self._api_url = self.main_config.get('api_url', 'https://data.gharchive.org')
        self._api_foramt = self.main_config.get('api_format', '%Y-%m-%d-%H')
        self._context_column = self.main_config.get('context_column', 'data_interval_end')

        # .strftime('%Y-%m-%d %H:%M:%S')

    def _load_from_clickhouse(self):
        pass

    def _load_from_pandas(self):
        pass

    def pre_execute(self, context: Any):
        self._hook = get_hook_by_conn_id(self._conn_id)

    def execute(self, context: Any):
        self.log.warning(context[self._context_column].in_tz(LOCAL_TZ))

    def post_execute(self, context: Any, result: Any = None):
        pass
