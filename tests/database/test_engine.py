import os
from unittest.mock import patch

from rates.database.engine import get_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine


class TestGetEngine:
    def test_get_engine(self):
        # given
        with patch.dict(
            os.environ,
            {
                "DB_USERNAME": "username",
                "DB_PASSWORD": "password",
                "DB_DATABASE": "database",
                "DB_HOST": "host",
                "DB_PORT": "1111",
            },
        ):
            # when
            engine = get_engine()

        # then
        expected_connection_url = URL.create(
            drivername="postgresql+asyncpg",
            username="username",
            password="password",
            host="host",
            port=1111,
            database="database",
        )

        assert (
            engine.url == expected_connection_url
        ), "engine should be created with URL that uses environment variables"
        assert isinstance(engine, AsyncEngine), "asynchronous engine should be created"
