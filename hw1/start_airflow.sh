# Install environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create the database for weather
sqlite3 weather.db ".databases"

### Set connections
export AIRFLOW_CONN_WEATHER_HTTP_CONN='{"conn_type": "http", "host": "https://api.openweathermap.org"}'
export AIRFLOW_CONN_WEATHER_SQLITE_CONN='{"conn_type": "sqlite", "host": "'$PWD'/weather.db"}'

### Start Airflow
export AIRFLOW_HOME=$PWD/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$PWD/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__DEFAULT_TIMEZONE="Europe/Kyiv"

airflow standalone
