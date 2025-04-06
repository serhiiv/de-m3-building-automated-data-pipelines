# Homework 1

### Task

Create a data pipeline that will scrape the data from [OpenWeather](https://openweathermap.org/)

- API version 3.0
- Scrape the city's temperature, humidity, cloudiness, and wind speed.
- Scrape previous dates.
- Cities: Lviv, Kyiv, Kharkiv, Odesa, and Zhmerynka.

I am using Ubuntu 24.10, Python 3.12.3, and SQLite 3.45.1

### Install environment

```ba
python3 -m venv .venv
source . venv/bin/activate
pip install -r requirements.txt
```

### Create the database for weather

```bash
sqlite3 weather.db ".databases"
```

### Start Airflow

```
# Your personal API key for OpenWeather https://home.openweathermap.org/api_keys
export AIRFLOW_VAR_WEATHER_API_KEY="3012e13068308820d24b5b2b7e535b9e...."

# connections
export AIRFLOW_CONN_weather_http_connection='{"conn_type": "HTTH","host": "https://api.openweathermap.org"}'
export AIRFLOW_CONN_weather_http_connection="{'Sqlite': 'HTTH','host': '$PWD/weather.db'}"

# config
export AIRFLOW_HOME=$PWD/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$PWD/dags

airflow standalone
```


