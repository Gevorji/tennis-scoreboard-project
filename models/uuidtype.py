from operator import attrgetter
from sqlalchemy.types import TypeDecorator, BINARY
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UUIDBin(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type or MSSQL's UNIQUEIDENTIFIER,
    otherwise uses LargeBinary, storing UUID as raw bytes.

    """

    impl = BINARY(16)
    cache_ok = True

    _default_type = BINARY(16)
    _uuid_as_bytes = attrgetter("bytes")

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        elif dialect.name == "mssql":
            return dialect.type_descriptor(UNIQUEIDENTIFIER())
        else:
            return dialect.type_descriptor(self._default_type)

    def process_bind_param(self, value: uuid.UUID, dialect):
        if value is None or dialect.name in ("postgresql", "mssql"):
            return value
        else:
            return self._uuid_as_bytes(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(bytes=value)
            return value


