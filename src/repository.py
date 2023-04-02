from dagster import Definitions, load_assets_from_modules, define_asset_job, ScheduleDefinition
from src.io_manager.postgres_io_manager import postgres_io_manager
from src.resources.file_finder import store_to_folder
from src.assets import retrieve_game_pdfs, game_data
import os

user = os.environ.get("DB_USER")
passw = os.environ.get("DB_PASS")

conn_str = f"postgresql://{user}:{passw}@christos-N501VW:5432/postgres"

fetch_protocol_job = define_asset_job(
    name="fetch_protocols_process",
    selection=[retrieve_game_pdfs.fetch_protocol, game_data.get_game_data],
)

weekly_schedule = ScheduleDefinition(job=fetch_protocol_job, cron_schedule="0 9 * * 1")

path_to_local_folder  = store_to_folder.configured(
    {
        "target_path": "/Users/christosmarinos/protocols"
    }
)
postgres_io_manager_conf = postgres_io_manager.configured(
    {
        "conn_str": conn_str
    }
)

defs = Definitions(
    assets=load_assets_from_modules([retrieve_game_pdfs]) + load_assets_from_modules([game_data]),
    jobs=[fetch_protocol_job],
    schedules=[weekly_schedule],
    resources={
        "local_folder": path_to_local_folder,
        "postgres_io_manager": postgres_io_manager_conf,
        },
)
