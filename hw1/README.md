# Homework 1

## Task

Create a data pipeline that will scrape the data from [OpenWeather](https://openweathermap.org/)

- API version 3.0
- Scrape the city's temperature, humidity, cloudiness, and wind speed.
- Scrape previous dates.
- Cities: Lviv, Kyiv, Kharkiv, Odesa, and Zhmerynka.

I am using Ubuntu 24.10, Python 3.12.3, and SQLite 3.45.1



## Preparation

Before starting, you must get your personal API key from OpenWeather https://home.openweathermap.org/api_keys and set the variable WEATHER_API_KEY.

```bash
export AIRFLOW_VAR_WEATHER_API_KEY="<your WEATHER_API_KEY>"
```



## Two launch options



### Option #1

- Start by one command

```bash
bash start_airflow.sh
```



### Option #2 (step by step)

- Install environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- Create the database for weather
```bash
sqlite3 weather.db ".databases"
```
- Set connections
```bash
export AIRFLOW_CONN_WEATHER_HTTP_CONN='{"conn_type": "http", "host": "https://api.openweathermap.org"}'

export AIRFLOW_CONN_WEATHER_SQLITE_CONN='{"conn_type": "sqlite", "host": "'$PWD'/weather.db"}'
```

- Start Airflow
```bash
export AIRFLOW_HOME=$PWD/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$PWD/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__DEFAULT_TIMEZONE="Europe/Kyiv"

airflow standalone
```

