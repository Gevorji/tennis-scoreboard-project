from collections.abc import Collection
from collections import defaultdict
from types import FunctionType

from sqlalchemy import select, and_, or_
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session

from services._storage_service_abc import StorageServiceABC


class DbMatchStorageService(StorageServiceABC):

    def __init__(self, db_connection_params: dict, procedures: Collection, orm_classes_aliases: dict):
        self._db_connection_params = db_connection_params

        self._sa_engine = create_engine(URL.create(**db_connection_params))
        self._sa_session = Session(self._sa_engine)

        self.procedures = ProceduresAccessor(procedures)

        self._orm_class_aliases = orm_classes_aliases


    def fetch(self, obj_type: str, **filters):
        orm_class = self._orm_class_aliases[obj_type]
        if filters:
            compiled_filters = self._compile_filters(orm_class, filters)
            sa_stmt = select(obj_type).where(compiled_filters)
        else:
            sa_stmt = select(obj_type)
        yield from self._sa_session.execute(sa_stmt).scalars()

    def place(self, obj):
        with self._sa_session.begin():
            self._sa_session.add(obj)
            self._sa_session.flush()

    def remove(self, obj):
        with self._sa_session.begin():
            self._sa_session.delete(obj)

    def _compile_filters(self, orm_class, filters: dict):
        filters = self._parse_filters(filters)
        by_attrs = []
        for attr_filters_k in filters:
            by_ops = []
            for op, params in filters[attr_filters_k]:
                if hasattr(params, '__iter__') and not isinstance(params, str):
                    by_val = []
                    for param in params:
                        by_val.append(self._compile_filter(orm_class, op, attr_filters_k, param))
                    by_ops.append(or_(*by_val))
                else:
                    by_ops.append(self._compile_filter(orm_class, op, attr_filters_k, params))

            by_attrs.append(and_(*by_ops))

        return and_(*by_attrs)

    def _compile_filter(self, orm_class, operation: str, attr: str, parameter):
        attr = getattr(orm_class, attr)
        operation = f'__{operation}__'
        return getattr(attr, operation)(parameter)


    def _parse_filters(self, filters: dict):
        parsed = defaultdict(list)
        for _filter, parameters in filters.items():
            attr, operation = _filter.split('_')
            parsed['attr'].append((operation, parameters))

        return parsed

class ProceduresAccessor:

    def __init__(self, procedures: Collection):
        self._procedures = {}
        for proc in procedures:
            self.add_procedure(proc)

    def __getattr__(self, item):
        if item in self._procedures:
            return self._procedures[item]
        else: raise AttributeError('No such procedure registered')

    def add_procedure(self, procedure: FunctionType):
        self._procedures[procedure.__name__] = procedure

