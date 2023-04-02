import paramiko
import os
from dagster import resource, get_dagster_logger, InitResourceContext

logger = get_dagster_logger()


class FileStorage:
    def __init__(self, target_dir) -> None:
        self.target_path = target_dir

    def write_to_path(self, pdfs):
        for pdf in pdfs:
            with open(f'{self.target_path}/{pdf["file_name"]}', "wb") as f:
                f.write(pdf["bytes"][0])

    def check_if_protocol_exists(self, protocols):
        missing = [
            x
            for x in protocols
            if not os.path.exists(self.target_path + "/" + x + ".pdf")
        ]
        return missing
    
    def list_dir(self):
        pdfs = os.listdir(self.target_path)
        return [self.target_path + '/' + file for file in pdfs]

@resource(config_schema={"target_path": str})
def store_to_folder(init_context):
    target_path = init_context.resource_config["target_path"]
    file_finder = FileStorage(target_dir=target_path)
    return file_finder
