from datetime import timedelta
from airflow.models import DAG


default_args = {}


def reg_dag(dag_id: str, schedule_interval: str = None):
    debug = __name__ == "__main__" and __debug__
    dag = DAG(
        dag_id=dag_id,
        schedule=schedule_interval,
        catchup=False,
        dagrun_timeout=timedelta(minutes=5),
        tags=['test'],
        default_args=default_args,
    )

    if debug:
        dag.test()

    globals()[dag_id] = dag


reg_dag('api-gh-archive')
