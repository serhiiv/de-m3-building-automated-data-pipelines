import pendulum
import json

from airflow import DAG
from airflow.decorators import task_group
from airflow.models.variable import Variable
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator


cities = {
    "Lviv": {"49.8383", "24.0232"},
    "Kyiv": ("50.4333", "30.5167"),
    "Kharkiv": ("50", "36.25"),
    "Odesa": ("46.4775", "30.7326"),
    "Zhmerynka": ("49.037", "28.112"),
}


def _process_weather(ti, city):
    data = ti.xcom_pull("by_city_" + city + ".extract_data")
    timestamp = pendulum.from_format(data["date"], "YYYY-MM-DD", tz="Europe/Kyiv")
    temperature = data["temperature"]["afternoon"]
    humidity = data["humidity"]["afternoon"]
    cloudiness = data["cloud_cover"]["afternoon"]
    wind_speed = data["wind"]["max"]["speed"]
    return timestamp, city, temperature, humidity, cloudiness, wind_speed


with DAG(
    dag_id="weather-3.0",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2025, 4, 1, 12, tz="Europe/Kyiv"),
    tags=["de-m3-pipeline"],
    catchup=True,
) as dag:

    logical_date = "{{ ds }}"

    base_create = SQLExecuteQueryOperator(
        task_id="create_sqlite_table",
        conn_id="weather_sqlite",
        sql="""
            CREATE TABLE IF NOT EXISTS measures
            (
                timestamp TIMESTAMP,
                city TEXT,
                temperature FLOAT,
                humidity FLOAT,
                cloudiness FLOAT,
                wind_speed FLOAT
            );
        """,
    )

    check_api = HttpSensor(
        task_id="check_api",
        http_conn_id="weather_http_connection",
        endpoint="data/3.0/onecall",
        request_params={
            "lon": 24.0232,
            "lat": 49.8383,
            "appid": Variable.get("WEATHER_API_KEY"),
        },
    )

    @task_group()
    def etl():
        for city, (lat, lon) in cities.items():

            @task_group(group_id=city)
            def by_city():
                extract_data = HttpOperator(
                    task_id="extract_data",
                    http_conn_id="weather_http_connection",
                    endpoint="data/3.0/onecall/day_summary",
                    data={
                        "lon": lon,
                        "lat": lat,
                        "date": logical_date,
                        "units": "metric",
                        "appid": Variable.get("WEATHER_API_KEY"),
                    },
                    method="GET",
                    response_filter=lambda x: json.loads(x.text),
                    log_response=True,
                )

                process_data = PythonOperator(
                    task_id="process_data",
                    python_callable=_process_weather,
                    op_kwargs={"city": city},
                )

                inject_data = SQLExecuteQueryOperator(
                    task_id="inject_data",
                    conn_id="weather_sqlite",
                    params={"task_ids": "by_city_" + city + ".process_data"},
                    sql="""
                    INSERT INTO measures (timestamp, city, temperature, humidity, cloudiness, wind_speed) VALUES (
                        "{{ ti.xcom_pull(task_ids=params.task_ids)[0] }}",
                        "{{ ti.xcom_pull(task_ids=params.task_ids)[1] }}",
                        {{ ti.xcom_pull(task_ids=params.task_ids)[2] }},
                        {{ ti.xcom_pull(task_ids=params.task_ids)[3] }},
                        {{ ti.xcom_pull(task_ids=params.task_ids)[4] }},
                        {{ ti.xcom_pull(task_ids=params.task_ids)[5] }}
                        );
                    """,
                )

                extract_data >> process_data >> inject_data
                
            by_city()

    base_create >> check_api >> etl()


if __name__ == "__main__":
    dag.test()
