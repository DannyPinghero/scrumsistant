import random

import pytest

from ..redis_schema import CurrentUsers
from ..structs import UserInfo
from .app_fixtures import websocket_server


@pytest.fixture
def user(websocket_server, faker):
    def _user(email=None, password=None, display_name=None, is_PM=None):
        if email is None:
            email = faker.email()
        if password is None:
            password = faker.password()
        if display_name is None:
            display_name = faker.name()
        if is_PM is None:
            is_PM = random.random() > 0.5
        new_user = UserInfo(email=email, display_name=display_name, is_PM=is_PM)
        new_user.set_password(password)
        new_user.save(websocket_server.db)
        # now we
        return new_user

    return _user


@pytest.fixture
def logged_in_user(user, flask_client, redis):
    def _logged_in_user(email=None, password=None, display_name=None, add_to_redis=False):
        if not password:
            password = 'elephants-are-always-purple!##'
        new_user = user(email=email, password=password, display_name=display_name)
        post_data = {
            'email': new_user.email,
            'password': password,
        }
        flask_client.post('login', json=post_data)
        if add_to_redis:
            redis.sadd(CurrentUsers(), new_user.id)

        return new_user

    return _logged_in_user
