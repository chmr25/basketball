from dagster import (
    load_assets_from_modules,
    define_asset_job,
    ScheduleDefinition,
    Definitions,
)

from dagster import with_resources
from src.io_manager.postgres_io_manager import postgres_io_manager
from src.resources.file_finder import store_to_folder
from src.assets import retrieve_game_pdfs, game_data, dbt_assets
from src import assets
import os


USER = os.getenv("DB_USER")
PASSW = os.getenv("DB_PASS")

conn_str = f"postgresql://{USER}:{PASSW}@christos-un45h.local:5432/postgres"

fetch_protocol_job = define_asset_job(
    name="collect_profixio_data",
    selection=[retrieve_game_pdfs.fetch_protocol, game_data.get_game_data],
)

weekly_schedule = ScheduleDefinition(job=fetch_protocol_job, cron_schedule="0 9 * * 1")


path_to_local_folder = store_to_folder.configured({"target_path": "/opt/dagster/app/protocols"})
postgres_io_manager_conf = postgres_io_manager.configured({"conn_str": conn_str})


dbt_job = define_asset_job(name="transform_profixio_data", selection=dbt_assets)
weekly_schedule_dbt = ScheduleDefinition(job=dbt_job, cron_schedule="15 9 * * 1")

basketball = Definitions(
    assets=load_assets_from_modules([assets]),
    jobs=[fetch_protocol_job, dbt_job],
    schedules=[weekly_schedule, weekly_schedule_dbt],
    resources={
        "local_folder": path_to_local_folder,
        "postgres_io_manager": postgres_io_manager_conf,
    },
)
