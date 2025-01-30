/* roles */
CREATE ROLE IF NOT EXISTS airflow_group ON CLUSTER sharded_cluster;
GRANT SELECT ON *.* TO airflow_group ON CLUSTER sharded_cluster;
-- нужны для работы on cluster конструкции и distributed таблиц
GRANT CLUSTER, CREATE TEMPORARY TABLE, REMOTE, URL ON *.* TO airflow_group ON CLUSTER sharded_cluster;

/* databases access */
GRANT ALL ON snp_gharchive.* TO airflow_group ON CLUSTER sharded_cluster;

/* users */
CREATE USER IF NOT EXISTS airflow_user IDENTIFIED WITH plaintext_password BY 'airflow_password' ON CLUSTER sharded_cluster;
GRANT airflow_group TO airflow_user ON CLUSTER sharded_cluster;
