import os
from datetime import datetime
from importlib import import_module
from logging import getLogger
from time import time

from airflow.models import DAG
from airflow.utils.task_group import TaskGroup
from airflow_ext.utils.yml import Yaml


class DagFactory:
    config_path = ''

    @staticmethod
    def import_module_from_string(module_path):
        module_name, class_name = module_path.rsplit(".", 1)
        module = import_module(module_name)
        return getattr(module, class_name)

    def create_task(self, helper: Yaml, task_config: dict, dag: DAG, task_groups: dict = None):
        operator_class = self.import_module_from_string(task_config['operator'])
        operator_params = task_config['operator_params'].copy()
        upstream_tasks = task_config.get('upstream', [])
        downstream_tasks = task_config.get('downstream', [])

        if 'python_callable' in operator_params:
            operator_params['python_callable'] = self.import_module_from_string(operator_params['python_callable'])

        if task_groups is None:
            task_groups = {}

        if 'task_group' in operator_params:
            if operator_params['task_group']['group_id'] not in task_groups:
                task_groups[operator_params['task_group']['group_id']] = TaskGroup(
                    dag=dag,
                    **operator_params['task_group'],
                )
            operator_params['task_group'] = task_groups[operator_params['task_group']['group_id']]

        task = operator_class(
            dag=dag,
            doc_yaml=helper.dump_yaml(task_config),
            **operator_params,
        )

        for stream_type, tasks in {'upstream': upstream_tasks, 'downstream': downstream_tasks}.items():
            for t in tasks:
                if isinstance(t, dict):
                    connected_task = self.create_task(helper, t, dag, task_groups)
                elif isinstance(t, str):
                    connected_task = dag.task_dict.get(t)
                else:
                    raise Exception('upstream or downstream must be list with str or dict')

                if connected_task:
                    if stream_type == 'upstream':
                        task.set_upstream(connected_task)
                    elif stream_type == 'downstream':
                        connected_task.set_upstream(task)
                else:
                    raise Exception(f'upstream or downstream task not found {str(t)}')

        return task


    def register_dag(self, dag_id: str, local_globals=None) -> DAG:
        start_time_dag = time()
        log = getLogger('airflow.task')
        log.info(f'start reg {dag_id} ...')

        if not local_globals:
            local_globals = globals()

        helper = Yaml()
        dag_config = helper.read_yaml(os.path.join(self.config_path, f'{dag_id}.yaml'))

        dag = DAG(
            **{
                'dag_id': dag_id,
                **dag_config['dag'],
            },
        )

        task_groups = {}
        for t in dag_config['tasks']:
            self.create_task(helper, t, dag, task_groups)

        now = datetime.now().strftime("%H:%M:%S")
        t_str = f'Reg end: {now}, Reg time: {str(round(time()-start_time_dag, 1))} sec'
        if dag._description:
            dag._description += f" ({t_str})"
        else:
            dag._description = f"({t_str})"
        local_globals[dag.dag_id] = dag
        log.info(dag._description)

        return dag
