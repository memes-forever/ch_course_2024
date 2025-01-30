# Базовый образ, for logs: export BUILDKIT_PROGRESS=plain
ARG AIRFLOW_IMAGE_NAME
FROM ${AIRFLOW_IMAGE_NAME}

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      ca-certificates \
      libssl-dev \
      wget \
      default-libmysqlclient-dev \
      build-essential \
      libldap2-dev \
      libsasl2-dev \
      libicu-dev \
      libffi-dev \
      openssl \
      git \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

COPY ./requirements.txt ./constraints.txt /

RUN pip3 install --no-deps --no-cache-dir -r /requirements.txt --constraint /constraints.txt
