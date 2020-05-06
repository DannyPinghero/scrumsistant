from dataclasses import asdict as dataclass_serialize
from dataclasses import dataclass
from dataclasses import replace as dataclass_replace
from enum import Enum
from typing import Any, Callable, Dict, Literal, Mapping, Optional, Union

from flask_login import AnonymousUserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .exceptions import UserNameTakenError
from .redis_schema import CurrentPKTable, PKByEmail, Users
from .scrum_types import RedisClient
from .utils import transform_to_redis_safe_dict


class AnonymousUserWrapper(AnonymousUserMixin):
    # current user will either be this or a UserInfo
    # the flask builtin has is_authenticated as a property
    # but UserInfo needs it to be a method.
    # To maintain ducktyping, we need this shell of a class
    # to expose a method for is_authenticated
    # it always returns False by definition (because this is a representation of a user prior to logging in)
    def is_authenticated(self, _) -> Literal[False]:  # pylint: disable=arguments-differ,invalid-overridden-method
        return False


@dataclass
class UserInfo:
    pk: int
    display_name: str = ''
    email: str = ''
    password: Optional[str] = None

    def serialize(
        self, skip_list=None, serialize_method=transform_to_redis_safe_dict,
    ):
        # typed in stub file!
        if skip_list is None:
            skip_list = []
        serialized_form = dataclass_serialize(self)
        reduced_serialized_form = {k: v for k, v in serialized_form.items() if not k in skip_list}
        return serialize_method(reduced_serialized_form)

    @staticmethod
    def redis_transformers(field_name: str) -> Callable[[bytes], Union[str, int, Union[None, str]]]:
        def _string_transformer(byte_string: bytes) -> str:
            return byte_string.decode("utf8")

        def _int_transformer(num_as_byte_string: bytes) -> int:
            return int(num_as_byte_string)

        def _pk_transformer(pk_byte_string: bytes) -> int:
            return _int_transformer(pk_byte_string)

        def _email_transformer(name_byte_string: bytes) -> str:
            return _string_transformer(name_byte_string)

        def _display_name_transformer(display_name_byte_string: bytes) -> str:
            return _string_transformer(display_name_byte_string)

        def _password_transformer(password_byte_string: bytes) -> Union[None, str]:
            password_or_null = _string_transformer(password_byte_string)
            if password_or_null == "null":
                return None
            return password_or_null

        return locals()[f"_{field_name}_transformer"]

    @staticmethod
    def deserialize(serialized_obj: Mapping[bytes, bytes], from_redis: bool = True) -> 'UserInfo':
        new_obj = UserInfo(pk=-1,)

        if from_redis:
            ser = {}
            for k, v in serialized_obj.items():
                key_str = k.decode("utf8")
                ser[key_str] = UserInfo.redis_transformers(key_str)(v)

        return dataclass_replace(new_obj, **ser)

    # methods required by flask-login
    def is_authenticated(self, session: Mapping[str, Dict[str, Any]]) -> bool:
        return session.get("_user_id") == Users(self.pk)

    def is_active(self,) -> Literal[True]:  # pylint: disable=no-self-use
        # This method is required by the flask-login library, but we don't really have this concept
        return True

    def is_anonymous(self) -> bool:
        return self.email == ''

    def get_id(self) -> str:
        return Users(self.pk)

    # end login required methods

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password:
            return False
        return check_password_hash(self.password, password)

    def save_new_user(self, redis_client: RedisClient) -> None:
        self._check_not_overwriting(redis_client)
        redis_client.set(PKByEmail(self.email), self.pk)
        redis_client.hmset(Users(self.pk), self.serialize())

    def update_user(self, redis_client: RedisClient) -> 'UserInfo':
        self._check_not_overwriting(redis_client)
        redis_client.hmset(Users(self.pk), self.serialize())
        updated_model_dict = redis_client.hgetall(Users(self.pk))
        updated_model = UserInfo.deserialize(updated_model_dict)
        return updated_model

    def _check_not_overwriting(self, redis_client: RedisClient) -> None:
        pk_associated_with_my_username_dirty = redis_client.get(PKByEmail(self.email))  # by dirty I mean, its bytes atm
        if not pk_associated_with_my_username_dirty:
            return
        pk = int(pk_associated_with_my_username_dirty)
        if self.pk != pk:
            raise UserNameTakenError

    @staticmethod
    def get_new_pk(redis_client: RedisClient) -> int:
        return int(redis_client.incr(CurrentPKTable()))


class MessageType(Enum):
    USER_JOINED = "userJoined"


class HTTP_STATUS_CODE(Enum):
    HTTP_200_OK = 200
    HTTP_401_UNAUTHORIZED = 401
    HTTP_404_NOT_FOUND = 404
