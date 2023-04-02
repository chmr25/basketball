from upath import UPath
from dagster import (
    Field,
    InitResourceContext,
    InputContext,
    OutputContext,
    UPathIOManager,
    io_manager,
    get_dagster_logger,
)
import pandas as pd
import fitz

logger = get_dagster_logger()


class FileIOManager(UPathIOManager):
    extension: str = ".pdf"

    def dump_to_path(self, context: OutputContext, obj, path: UPath):
        logger.info(path)
        with open(path, "wb") as f:
            f.write(obj)

    def load_from_path(self, context: InputContext, path: UPath) -> pd.DataFrame:
        with path.open("rb") as file:
            return fitz.open(file)


@io_manager(config_schema={"base_path": Field(str, is_required=False)})
def pdf_io_manager(
    init_context: InitResourceContext,
) -> FileIOManager:
    assert init_context.instance is not None  # to please mypy
    base_path = UPath("adrian_basket/protocols")
    logger.info(base_path)
    return FileIOManager(base_path=base_path)
