from sqlalchemy.types import TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

class StringList(TypeDecorator):
    """Platform-independent list of strings.

    Uses PostgreSQL's ARRAY(String) type for PostgreSQL, otherwise uses
    JSON to store the list.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        else:
            return dialect.type_descriptor(JSON)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return value
