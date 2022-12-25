from rates.utils.environment import Environment
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine


def get_engine() -> Engine:
    environment = Environment()
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=environment.db_username,
        password=environment.db_password,
        host=environment.db_host,
        port=environment.db_port,
        database=environment.db_database,
    )

    return create_engine(database_url, future=True)
