import json
import pendulum
from airflow.decorators import dag, task_group, task
from airflow.models.taskinstance import TaskInstance
from airflow.models.dagrun import DagRun
from airflow.models.variable import Variable
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


@dag(
    schedule="@daily",
    start_date=pendulum.datetime(2025, 6, 17, tz="Europe/Kyiv"),
    catchup=True,
    tags=["de-m3-pipeline"],
)
def scrape_open_weather():
    """
    ### Scrape the data from OpenWeather
    Create a data pipeline that will scrape the data from [OpenWeather](https://openweathermap.org/)

    - API version 3.0
    - Scrape the city's temperature, humidity, cloudiness, and wind speed.
    - Scrape previous dates.
    - Cities: Lviv, Kyiv, Kharkiv, Odesa, and Zhmerynka.
    - Store the data in SQLite database.
    """

    @task_group()
    def preparation():
        """
        Check if the OpenWeather API is available and create a SQLite database and table to store the data.
        """

        check_sqlite_cities_data = SQLExecuteQueryOperator(
            task_id="check_sqlite_cities_data",
            conn_id="weather_sqlite_conn",
            sql="SELECT city, longitude, latitude FROM cities;",
            do_xcom_push=True,
        )
        check_sqlite_cities_data.doc_md = """
        Check if the cities table exists in the SQLite database and read the data.
        - SQLite database: `weather.db`
        - Table: `cities`
        - Columns: `city`, `longitude`, `latitude`
        """

        create_sqlite_table = SQLExecuteQueryOperator(
            task_id="create_sqlite_table",
            conn_id="weather_sqlite_conn",
            sql="""
                CREATE TABLE IF NOT EXISTS measures
                (
                    timestamp TIMESTAMP,
                    city TEXT,
                    temperature FLOAT,
                    humidity INT,
                    cloudiness INT,
                    wind_speed FLOAT
                );
            """,
        )
        create_sqlite_table.doc_md = """
        Create a SQLite database and table to store the data.
        - SQLite database: `weather.db`
        """

        check_weather_api = HttpSensor(
            task_id="check_weather_api",
            http_conn_id="weather_http_conn",
            # endpoint="data/3.0/onecall",
            endpoint="data/2.5/weather",
            request_params={
                "lon": 24.0232,
                "lat": 49.8383,
                "appid": Variable.get("WEATHER_API_KEY"),
            },
        )
        check_weather_api.doc_md = """
        Check if the OpenWeather API is available.
        - API version 2.5
        - Endpoint: `data/2.5/weather`
        """

    # @task_group()
    # def extract(ti: TaskInstance, **kwargs):
    #     """
    #     Extract the data from OpenWeather API for each city.
    #     """
    #     rows = ti.xcom_pull(task_ids="check_sqlite_cities_data")
    #     for row in rows:
    #         city, (lon, lat) = row
    #         extract = HttpOperator(
    #             task_id=f"{city}",
    #             http_conn_id="weather_http_conn",
    #             endpoint="data/3.0/onecall/day_summary",
    #             data={
    #                 "lon": lon,
    #                 "lat": lat,
    #                 "date": "{{ ds }}",
    #                 "units": "metric",
    #                 "appid": Variable.get("WEATHER_API_KEY"),
    #             },
    #             method="GET",
    #             response_filter=lambda x: json.loads(x.text),
    #             log_response=True,
    #         )
    #         extract.doc_md = f"""
    #         Extract the data from OpenWeather API for {city}.
    #         - API version 3.0
    #         - Endpoint: `data/3.0/onecall/day_summary`
    #         - City: {city}
    #         """

    # @task
    # def process(ti: TaskInstance):
    #     """
    #     Process the data from OpenWeather API for each city.
    #     """
    #     output = []
    #     rows = ti.xcom_pull(task_ids="check_sqlite_cities_data")
    #     for row in rows:
    #         city, _ = row

    #         # for city in cities.keys():
    #         data = ti.xcom_pull(task_ids=f"extract.{city}")
    #         output.append(
    #             ", ".join(
    #                 [
    #                     f'"{str(pendulum.from_format(data["date"], "YYYY-MM-DD", tz="Europe/Kyiv"))}"',
    #                     f'"{city}"',
    #                     str(data["temperature"]["afternoon"]),
    #                     str(data["humidity"]["afternoon"]),
    #                     str(data["cloud_cover"]["afternoon"]),
    #                     str(data["wind"]["max"]["speed"]),
    #                 ]
    #             )
    #         )
    #     return f"({') , ('.join(output)})"

    # inject_data = SQLExecuteQueryOperator(
    #     task_id="inject_data",
    #     conn_id="weather_sqlite_conn",
    #     params={"task_ids": "process"},
    #     sql="""
    #     INSERT INTO measures
    #     (timestamp, city, temperature, humidity, cloudiness, wind_speed)
    #     VALUES
    #     {{ti.xcom_pull(task_ids=params.task_ids)}};
    #     """,
    # )
    # inject_data.doc_md = """
    # Insert the data into SQLite database.
    # - SQLite database: `weather.db`
    # - Table: `measures`
    # """

    # # cities = {
    # #     "Lviv": ("49.8383", "24.0232"),
    # #     "Kyiv": ("50.4333", "30.5167"),
    # #     "Kharkiv": ("50", "36.25"),
    # #     "Odesa": ("46.4775", "30.7326"),
    # #     "Zhmerynka": ("49.037", "28.112"),
    # # }

    # preparation() >> extract() >> process() >> inject_data  # type: ignore
    preparation()
    # >> extract() >> process() >> inject_data  # type: ignore


scrape_open_weather()
