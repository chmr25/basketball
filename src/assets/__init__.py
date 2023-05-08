from dagster_dbt import load_assets_from_dbt_project
from . import retrieve_game_pdfs, game_data

DBT_PROJECT_PATH = "/opt/dagster/app/transformations"
DBT_PROFILES = f"/opt/dagster/app/transformations/config"

dbt_assets = load_assets_from_dbt_project(
    project_dir=DBT_PROJECT_PATH,
    profiles_dir=DBT_PROFILES,
    key_prefix=["transformations"],
)
get_game_data = game_data.get_game_data
game_pdfs = retrieve_game_pdfs.fetch_protocol
