#!/bin/bash
# You need to have installed uv (
# https://docs.astral.sh/uv/getting-started/installation/


PYTHON_VERSION=3.12


### Install python environment
uv venv --python ${PYTHON_VERSION} .venv
source .venv/bin/activate


### Create the database for weather
sqlite3 weather.db ".databases"

### Create the cities table and insert some data
sqlite3 weather.db <<SQL
DROP TABLE IF EXISTS cities;

CREATE TABLE cities (
    city TEXT,
    longitude REAL,
    latitude REAL
);

INSERT INTO cities (city, longitude, latitude) VALUES ("Lviv",49.8383,24.0232);
INSERT INTO cities (city, longitude, latitude) VALUES ("Kyiv",50.4333,30.5167);
INSERT INTO cities (city, longitude, latitude) VALUES ("Kharkiv",50,36.25);
INSERT INTO cities (city, longitude, latitude) VALUES ("Odesa",46.4775,30.7326);
INSERT INTO cities (city, longitude, latitude) VALUES ("Zhmerynka",49.037,28.112);
SQL


### Set airflow variables
read -p "Please enter api key for OpenWeatherMap: " api_key
export AIRFLOW_VAR_WEATHER_API_KEY=$api_key


### Set airflow connections
export AIRFLOW_CONN_WEATHER_HTTP_CONN='{"conn_type": "http", "host": "https://api.openweathermap.org"}'
export AIRFLOW_CONN_WEATHER_SQLITE_CONN='{"conn_type": "sqlite", "host": "'$PWD'/weather.db"}'


### Set airflow configurations
export AIRFLOW_HOME=$PWD/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$PWD/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__DEFAULT_TIMEZONE="Europe/Kyiv"


### Install Airflow
AIRFLOW_VERSION=3.0.2

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example this would install 3.0.0 with python 3.9: https://raw.githubusercontent.com/apache/airflow/constraints-3.0.2/constraints-3.9.txt

uv pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
uv pip install -r requirements.txt

### Start Airflow
airflow standalone
