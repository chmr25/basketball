from dagster import (
    load_assets_from_modules,
    define_asset_job,
    ScheduleDefinition,
    Definitions,
)
from dagster_dbt import DbtCliClientResource
from src.io_manager.postgres_io_manager import postgres_io_manager
from src.resources.file_finder import store_to_folder
from src.assets import DBT_PROFILES, DBT_PROJECT_PATH, retrieve_game_pdfs, game_data
from src import assets
import os


USER = os.getenv("DB_USER")
PASSW = os.getenv("DB_PASS")

conn_str = f"postgresql://{USER}:{PASSW}@192.168.1.66:5432/postgres"

fetch_protocol_job = define_asset_job(
    name="fetch_protocols_process",
    selection=[retrieve_game_pdfs.fetch_protocol, game_data.get_game_data],
)

weekly_schedule = ScheduleDefinition(job=fetch_protocol_job, cron_schedule="0 9 * * 1")

path_to_local_folder = store_to_folder.configured({"target_path": "protocols"})
postgres_io_manager_conf = postgres_io_manager.configured({"conn_str": conn_str})
dbt_configured = DbtCliClientResource(
    project_dir=DBT_PROJECT_PATH,
    profiles_dir=DBT_PROFILES,
)

basketball = Definitions(
    assets=load_assets_from_modules([assets]),
    jobs=[],
    schedules=[],
    resources={
        "local_folder": path_to_local_folder,
        "postgres_io_manager": postgres_io_manager_conf,
        "dbt": dbt_configured,
    },
)
