import re, time
from typing import Dict, Any, Iterable, Union

from airflow.exceptions import AirflowException
from airflow.hooks.dbapi import DbApiHook
from airflow.models.connection import Connection
from clickhouse_driver import Client


class ClickhouseHook(DbApiHook):
    """
    ClickhouseHook
    """

    def bulk_dump(self, table, tmp_file):
        pass

    def bulk_load(self, table, tmp_file):
        pass

    conn_name_attr = 'click_conn_id'
    default_conn_name = 'click_default'
    conn_type = 'clickhouse'
    hook_name = 'ClickHouse'
    database = ''
    cluster = 'sharded_cluster'

    @staticmethod
    def get_ui_field_behaviour() -> Dict:
        """Returns custom field behaviour"""
        return {
            "hidden_fields": ['port'],
            "relabeling":    {'schema': 'Database',
                              'login': 'Username',
                              'extra': 'Advanced Connection Properties'},
            "placeholders": {
                'host' : 'The host name of Clickhouse DB',
                'schema' : 'The DB to connect to',
                'login' : 'The email address',
                'password' : 'password'
            }
        }

    def get_conn(self, conn_name_attr: str = None) -> Client:

        if conn_name_attr:
            self.conn_name_attr = conn_name_attr
        conn: Connection = self.get_connection(getattr(self, self.conn_name_attr))
        host: str = conn.host
        port: int = int(conn.port) if conn.port else 9000
        user: str = conn.login
        password: str = conn.password
        database: str = conn.schema
        click_kwargs = conn.extra_dejson.copy()
        if password is None:
            password = ''
        click_kwargs.update(port=port)
        click_kwargs.update(user=user)
        click_kwargs.update(password=password)
        if database:
            click_kwargs.update(database=database)

        result = Client(host or 'localhost', **click_kwargs)
        result.connection.connect()
        return result

    def run(self, sql: Union[str, Iterable[str]], parameters: dict = None,
            with_column_types: bool = True, **kwargs) -> Any:

        if isinstance(sql, str):
            queries = (sql,)
        client = self.get_conn()
        result = None
        index = 0
        for query in queries:
            index += 1
            self.log.info("Query_%s to database : %s", index, query)
            result = client.execute(
                query=query,
                #  params=parameters,
                with_column_types=with_column_types,
            )
            self.log.info("Query_%s completed", index)

            if result:
                self.log.warning(f'Result from sql: {str(result)[:100]} ...')

            self._check_query_replication_mutation(query)

        return result

    def _check_query_replication_mutation(self, query):
        match_delete_insert = re.search(r'(?:INSERT\s+INTO|DELETE\s+FROM)\s+([^\s\(]+)', query, re.IGNORECASE)
        if match_delete_insert:
            table_name = match_delete_insert.group(1)
            self._wait_replication(table_name)
        match_alter = re.search(
            '(?:ALTER\s+TABLE|ALTER\s+COLUMN|ALTER\s+SCHEMA|RENAME\s+TABLE|MODIFY\s+COLUMN)\s+([^\s\(]+)',
            query,
            re.IGNORECASE,
        )
        if match_alter:
            table_name = match_alter.group(1)
            self._wait_mutations(table_name)

    def get_first_value(self, *args, **kwargs) -> Any:
        result = self.get_first(*args, **kwargs)
        if result[0]:
            return result[0][0][0]
        return None

    def _wait_replication(self, table: str, wait_interval: int = 10, wait_timeout: int = 1800) -> None:
        """
        A function to wait for replications between related replicas to complete.
        Replication ends if rows in dependent replicas are equal, there are no queues for replication,
        and there are no queues in distribution_queue rows to MT table
        Args:
            table: table destination, in format "schema.table"
            wait_interval: sec waiting interval
            wait_timeout: sec waiting timeout
        """
        self.log.warning('Wait replication ...')
        database, table_name = table.split('.')

        if not table_name.startswith('_'):
            table_name = '_' + table_name

        # проверяем, что кол-во строк между репликами в одном шарде совпадают
        check_rows_query = f"""
        SELECT
            shard,
            groupArray(total_rows) as total_rows
        FROM (
            SELECT
                getMacro('shard') as shard,
                getMacro('replica') as replica,
                sum(rows) as total_rows
            FROM clusterAllReplicas('{self.cluster}', 'system', 'parts')
            WHERE (database, table) = ('{database}', '{table_name}')
                AND active
            GROUP BY shard, replica
            ORDER BY shard, replica
        ) AS parts
        GROUP BY parts.shard
        """

        # Проверяем очередь на репликацию
        check_replication_query = f"""
        SELECT count(*) = 0
        FROM clusterAllReplicas('{self.cluster}', 'system', 'replication_queue')
        WHERE (database, table) = ('{database}', '{table_name}')
        """

        # Проверяем очередь на шардирование
        check_distribution_query = f"""
        SELECT ifnull(count(data_files), 0) = 0
        FROM clusterAllReplicas('{self.cluster}', 'system', 'distribution_queue')
        WHERE (database, table) = ('{database}', '{table_name}')
        """

        t_start = time.time()
        while True:
            time.sleep(wait_interval)

            shards = self.get_records(check_rows_query)[0]
            if (
                self.get_first_value(check_replication_query)
                and self.get_first_value(check_distribution_query)
                and all(all(val == rows[0] for val in rows) for shard, rows in shards)
            ):
                break

            if time.time() - t_start > wait_timeout:
                raise AirflowException('wait replication is working too long (see timeout)')

        self.log.warning('Wait replication ... Done.')

    def _wait_mutations(self, table: str, wait_interval: int = 10, wait_timeout: int = 1800) -> None:
        """
        Wait for mutation
        Args:
            table: table destination, in format "schema.table"
            wait_interval: sec waiting interval
            wait_timeout: sec waiting timeout
        """
        self.log.warning('Wait mutation ...')
        database, table_name = table.split('.')

        # ищем активные мутации
        is_active_mutations = f"""
        SELECT 1
        FROM clusterAllReplicas('{self.cluster}', 'system', 'mutations')
        ARRAY JOIN parts_to_do_names -- массив с именами кусков данных, которые должны быть изменены для завершения мутации.
        WHERE NOT is_done
            AND (database, table) = ('{database}', '{table_name}')
            AND (hostname(), parts_to_do_names) IN (
                SELECT (hostname(), name)
                FROM clusterAllReplicas('{self.cluster}', 'system', 'parts') p
                WHERE active
                    AND (database, table) = ('{database}', '{table_name}')
            )
        LIMIT 1
        """

        # Находим застрявшие мутации
        # stuck_mutations = f"""
        # SELECT hostname(), mutation_id
        # FROM clusterAllReplicas('{self.cluster}', 'system', 'mutations')
        # ARRAY JOIN parts_to_do_names
        # WHERE NOT is_done
        #     AND (database, table) = ('{database}', '{table_name}')
        #     AND (hostname(), parts_to_do_names) NOT IN (
        #         SELECT (hostname(), name)
        #         FROM clusterAllReplicas('{self.cluster}', 'system', 'parts') p
        #         WHERE active
        #             AND (database, table) = ('{database}', '{table_name}')
        #     )
        # """

        latest_mutation_fail_reason = f"""
        SELECT latest_fail_reason
        FROM system_dist.mutations
        WHERE (database, table) = ('{database}', '{table_name}')
            AND NOT is_done
        """

        t_start = time.time()
        while True:
            time.sleep(wait_interval)

            if not bool(self.get_first_value(is_active_mutations)):
                break

            latest_fail_reason = self.get_first_value(latest_mutation_fail_reason)
            if latest_fail_reason:
                raise AirflowException(f"wait mutations is error: {latest_fail_reason[0]}")

            if time.time() - t_start > wait_timeout:
                raise AirflowException('wait mutations is working too long (see timeout)')

        self.log.warning('Wait mutation ... Done.')
