# from upath import UPath
from dagster import (
    Field,
    InitResourceContext,
    InputContext,
    OutputContext,
    # UPathIOManager,
    # io_manager,
)
import pandas as pd
import fitz


# class FileIOManager(UPathIOManager):
#     extension: str = ".pdf"
# 
#     def dump_to_path(self, context: OutputContext, file, path: UPath):
#         with open(path, "wb") as f:
#             f.write(file)
# 
#     def load_from_path(self, context: InputContext, path: UPath) -> pd.DataFrame:
#         with path.open("rb") as file:
#             return fitz.open(file)
# 
# 
# @io_manager(config_schema={"base_path": Field(str, is_required=False)})
# def pdf_io_manager(
#     init_context: InitResourceContext,
# ) -> FileIOManager:
#     assert init_context.instance is not None  # to please mypy
#     base_path = UPath(
#         init_context.resource_config.get(
#             "base_path", init_context.instance.storage_directory()
#         )
#     )
#     return FileIOManager(base_path=base_path)

