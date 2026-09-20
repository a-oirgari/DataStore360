from __future__ import annotations

import sys
import os
from datetime import datetime

from airflow.decorators import dag, task

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

CSV_PATH = "/opt/airflow/data/raw/Sample - Superstore.csv"
PROCESSED_DIR = "/opt/airflow/data/processed"


default_args = {
    "owner": "data-engineer",
    "retries": 1,
}


@dag(
    dag_id="superstore_pipeline",
    description="Pipeline Superstore : extraction -> staging -> nettoyage RGPD -> core -> contrôle qualité",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["datastore360", "superstore", "etl"],
)
def superstore_pipeline():

    @task
    def extract_task():
        from db import get_engine
        from extract import extract_and_load

        engine = get_engine()
        df_raw = extract_and_load(CSV_PATH, engine)

        os.makedirs(PROCESSED_DIR, exist_ok=True)
        output_path = os.path.join(PROCESSED_DIR, "01_raw.csv")
        df_raw.to_csv(output_path, index=False)
        return output_path

    @task
    def clean_task(raw_path):
        import pandas as pd
        from clean import clean_pipeline

        df_raw = pd.read_csv(raw_path)
        df_clean = clean_pipeline(df_raw)

        output_path = os.path.join(PROCESSED_DIR, "02_clean.csv")
        df_clean.to_csv(output_path, index=False)
        return output_path

    @task
    def load_task(clean_path):
        import pandas as pd
        from db import get_engine
        from load import load_pipeline

        df_clean = pd.read_csv(clean_path)
        engine = get_engine()
        stats = load_pipeline(df_clean, engine)
        return stats

    @task
    def quality_check_task(load_stats):
        from db import get_engine
        from quality_check import run_quality_checks

        engine = get_engine()
        checks = run_quality_checks(engine)
        print(f"[quality_check] Stats de chargement : {load_stats}")
        print(f"[quality_check] Résultats des contrôles : {checks}")

    raw_path = extract_task()
    clean_path = clean_task(raw_path)
    stats = load_task(clean_path)
    quality_check_task(stats)

superstore_pipeline()
