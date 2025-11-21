from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from pipeline import fetch_posts, export_long_posts


"""
Task 3: Create dag "v1_posts_pipeline". Set start date to yesterday.

The dag should run every monday at 8PM (use cron expression in schedule).

HINT: https://crontab.guru/
"""
with DAG(
) as dag:
    # define both tasks using PythonOperator

    # Dependency: first fetch, then export
