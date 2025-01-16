import copy
import os
import yaml
from datetime import timedelta

from airflow.models.dag import DAG
from universal_executor.operators.universal_executor_operator import UniversalExecutorOperator


def register_dag(dag_id: str, schedule_interval):
    with open(os.path.join(os.path.dirname(__file__), 'configs', f'{dag_id}.yml'), 'r', encoding="utf-8") as yml:
        configs = yaml.load(yml, yaml.SafeLoader)

    dag = DAG(
        dag_id=dag_id,
        schedule=schedule_interval,
        catchup=False,
    )
    for config in configs['tasks']:
        assert isinstance(config['sql'], list), 'SQL block must be list type in config'
        for tab in config['sql']:
            config_new = copy.copy(config)
            config_new.pop('sql')
            config_new = {**config_new, **tab}

            """
            UniversalExecutorOperator просто мелкий оператор, который разбивает входящий шаблон через .split(';'),
            и в цикле запускает запросы
            """
            universal_query_exec = UniversalExecutorOperator(
                dag=dag,
                task_id=f'{config_new["conn_id"]}__{config_new["name"]}',
                config=config_new,
                trigger_rule=config_new.get('trigger_rule', 'none_failed'),
                execution_timeout=timedelta(minutes=60),
            )
            globals()[f'{config_new["conn_id"]}__{config_new["name"]}'] = universal_query_exec

            if config_new.get('dependent_tasks'):
                for task in config_new['dependent_tasks']:
                    ex_dag_id, ex_task_id = list(task.items())[0]
                    if ex_dag_id == dag_id:
                        universal_query_exec.set_upstream(globals()[ex_task_id])

    globals()[dag_id] = dag


register_dag('test_executor-60', '0 * * * *')
