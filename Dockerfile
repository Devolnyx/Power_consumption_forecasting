FROM apache/airflow:2.2.4-python3.8
USER root

COPY . .

ENV TZ=Europe/Moscow

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential libopenmpi-dev \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get install -yy tzdata

RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

USER airflow

RUN pip install --no-cache-dir -r requirements.txt


