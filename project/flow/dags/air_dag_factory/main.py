import os
from airflow_ext.constant import HOME_DIR
from airflow_ext.utils.dag_factory import DagFactory

config = [
    # api
    'ch-migration-manual',
]

dg = DagFactory()
dg.config_path = os.path.join(HOME_DIR, 'dags/air_dag_factory/configs')

for c in config:
    dg.register_dag(c, globals())
