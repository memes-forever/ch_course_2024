#!/bin/bash

# export env
. ./.env


#if [ ! -f constraints.txt ]; then
  CONSTAINTS_URL=https://raw.githubusercontent.com/apache/airflow/constraints-$AIRFLOW_MIN_VERSION/constraints-$AIRFLOW_MIN_PYTHON_VERSION.txt
  echo load $CONSTAINTS_URL ...
  curl -o constraints.txt $CONSTAINTS_URL || exit

#  echo donwgrade libs in constraints.txt ...
#  sed -i -e 's/spython==.*/spython==0.3.14/g' constraints.txt || exit
#fi

#if [ ! -f docker-compose-default.yaml ]; then
  COMPOSE_URL=https://airflow.apache.org/docs/apache-airflow/$AIRFLOW_MIN_VERSION/docker-compose.yaml
  echo load $COMPOSE_URL ...
  curl -o docker-compose-default.yaml $COMPOSE_URL || exit
#fi

echo test pip install ...
pip install --no-deps --no-cache-dir -r requirements.txt --constraint constraints.txt

#echo generate defaults configs ...
#AIRFLOW__LOGGING__LOGGING_LEVEL=INFO airflow config list --defaults --color off > airflow.default.cfg || exit

echo success
