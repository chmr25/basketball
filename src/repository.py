from dagster import load_assets_from_package_module, repository
from src import assets
from src.assets.fetch_protocols import return_a_list, return_a_list_job

@repository
def basketball():
    assets_all = [return_a_list]
    jobs = [return_a_list_job]
    return assets_all + jobs
