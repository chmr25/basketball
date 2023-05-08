from dagster_dbt import load_assets_from_dbt_project
from dagster import load_assets_from_modules
from dagster import file_relative_path
from . import retrieve_game_pdfs, game_data

DBT_PROJECT_PATH = file_relative_path(__file__, "../../transformations")
DBT_PROFILES = file_relative_path(__file__, "../../transformations/config")

dbt_assets = load_assets_from_dbt_project(
    project_dir=DBT_PROJECT_PATH, profiles_dir=DBT_PROFILES, key_prefix=["transformations"]
)
get_game_data = game_data.get_game_data
game_pdfs = retrieve_game_pdfs.fetch_protocol
