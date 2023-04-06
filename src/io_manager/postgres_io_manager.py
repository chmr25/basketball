from sqlalchemy import create_engine, Column, JSON, String, Date, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from dagster import (
    Field as d_Field,
    InitResourceContext,
    InputContext,
    OutputContext,
    IOManager,
    io_manager,
    get_dagster_logger,
)
import os

logger = get_dagster_logger()
Base=declarative_base()

class RawBasketInput(Base):
    __tablename__ = "raw_basket_input"
    id = Column(String, primary_key=True)
    ingested_date= Column(Date)
    home_team = Column(String)
    away_team = Column(String)
    game_timestamp = Column(DateTime)
    game_data = Column(JSON)

class PostgresIOManager(IOManager):
    def __init__(self, conn_str):
        self.engine = create_engine(conn_str, echo=True)
        Base.metadata.create_all(self.engine)

    def handle_output(self, context: OutputContext, elements):
        ids = [i.id for i in elements]
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as s:
            already_there = s.query(RawBasketInput.id)
            ids_existing = [aa.id for aa in already_there]
            to_be_added = [i for i in elements if i.id not in ids_existing]
            logger.info(f"{len(to_be_added)} new elements will be added")
            s.add_all([i for i in elements if i.id not in ids_existing])
            s.commit()


    def load_input(self, context: InputContext):
        pass

@io_manager(config_schema={"conn_str": d_Field(str, is_required=True)})
def postgres_io_manager(init_context: InitResourceContext):
    assert init_context.instance is not None
    conn_str = init_context.resource_config["conn_str"]
    return PostgresIOManager(conn_str=conn_str)


