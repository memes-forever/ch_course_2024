import os
from airflow_ext.constant import HOME_DIR
from airflow_ext.utils.dag_factory import DagFactory

config = [
    # api
    'migration-manual',
    'api-gharchive-60',
]

dg = DagFactory()
dg.config_path = os.path.join(HOME_DIR, 'flow/dags/air_dag_factory/configs')

for c in config:
    dag = dg.register_dag(c, globals())


if __name__ == '__main__':
    dag.test()
