from rates.utils.environment import Environment
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def get_engine() -> AsyncEngine:
    environment = Environment()
    database_url = URL.create(
        drivername="postgresql+asyncpg",
        username=environment.db_username,
        password=environment.db_password,
        host=environment.db_host,
        port=environment.db_port,
        database=environment.db_database,
    )

    return create_async_engine(database_url, future=True)
