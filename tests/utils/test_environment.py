import os
from unittest.mock import patch

from rates.utils.environment import Environment


class TestEnvironment:
    def test_environment_init_with_env_variables(self):
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
            environment = Environment()

        # then
        expected_environment = Environment(
            db_username="username",
            db_password="password",
            db_database="database",
            db_host="host",
            db_port=1111,
        )

        assert (
            expected_environment == environment
        ), "Environment should use set environment variables"
