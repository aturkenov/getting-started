from typing import (
    Dict, Callable, Union, Optional, Mapping, Iterable, Any, Type, Tuple, List, Sequence
)
import orjson as json
from aioredis import Redis
from sqlalchemy import (
    Table, Column, and_, select, insert, update, delete, func, nullslast
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, Insert, Update, Delete
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.sql.selectable import Alias
from sqlalchemy_utils.functions import get_primary_keys
from wampify.story import *
from shared.base_async import BaseAsync
import domain
from exceptions import (
    ObjectDoesNotExist,
    FiltersMustBePassedException,
    AttributeMustBeSetException,
    ColumnDoesNotExistException,
    LookupOperatorNotFoundException,
    ColumnIsUniqueException,
    IncorrectReferenceNameException
)
from .shared.clear_from_ellipsis import clear_from_ellipsis
from . import models as orm_models


class BaseProvider(BaseAsync):
    """
    """

    ORM_MODEL: orm_models.ORMBaseModel

    async def __ainit__(
        self
    ):
        self._story = get_current_story()


class BaseAlchemyProvider(BaseProvider):
    """
    """

    session: AsyncSession

    async def __ainit__(
        self
    ):
        await super().__ainit__()
        self.session = self._story.postgres


class AlchemyFilters:
    """
    """

    LOOKUP_STRING = '__'
    EQUAL_OPERATOR = 'e'
    NOT_EQUAL_OPERATOR = 'ne'
    LESS_THAN_OPERATOR = 'l'
    LESS_THAN_OR_EQUAL_TO_OPERATOR = 'le'
    GREATER_THAN_OPERATOR = 'g'
    GREATER_THAN_OR_EQUAL_TO_OPERATOR = 'ge'
    LIKE_OPERATOR = 'like'
    ILIKE_OPERATOR = 'ilike'
    IN_OPERATOR = 'in'
    NOT_IN_OPERATOR = 'not_in'
    ALL_OBJECTS_FILTER = domain.ALL

    LOOKUP_OPERATORS = {
        EQUAL_OPERATOR: lambda c, v: c == v,
        NOT_EQUAL_OPERATOR: lambda c, v: c != v,
        LESS_THAN_OPERATOR: lambda c, v: c < v,
        LESS_THAN_OR_EQUAL_TO_OPERATOR: lambda c, v: c <= v,
        GREATER_THAN_OPERATOR: lambda c, v: c > v,
        GREATER_THAN_OR_EQUAL_TO_OPERATOR: lambda c, v: c >= v,
        LIKE_OPERATOR: lambda c, v: c.like(v),
        ILIKE_OPERATOR: lambda c, v: c.ilike(v),
        IN_OPERATOR: lambda c, v: c.in_(v),
        NOT_IN_OPERATOR: lambda c, v: c.not_in(v),
    }

    _mapper: Type[orm_models.ORMBaseModel]
    _table: Table
    _joined_aliases: Tuple[Alias] = tuple()

    @property
    def _get_joined_aliases(self) -> Tuple[Optional[Alias]]:
        try:
            return self._joined_aliases
        except AttributeError:
            return tuple()

    @property
    def _get_mapper(self) -> Type[orm_models.ORMBaseModel]:
        try:
            return self._mapper
        except AttributeError:
            raise AttributeMustBeSetException

    def _get_table(
        self,
        reference_name: Optional[str] = None
    ) -> Union[Table, Alias]:
        """
        If reference_name passed as str tries to find reference in self._get_joined_aliases.
        If reference was found returns it else tries to find reference in attributes
        of self._get_mapper if reference not found so raises exception
        """
        if type(reference_name) is str:
            aliases: Tuple[Optional[Alias]] = self._get_joined_aliases
            filtered_aliases: Tuple[Optional[Alias]] = tuple(filter(
                lambda alias: reference_name in alias.name, aliases
            ))
            if filtered_aliases:
                return filtered_aliases[0]

            try:
                reference = getattr(self._get_mapper, reference_name)
                tables: List[Table] = reference.property.mapper.tables
                return tables[0]
            except (IndexError, AttributeError):
                raise IncorrectReferenceNameException

        try:
            return self._table
        except AttributeError:
            raise AttributeMustBeSetException

    def _get_column(
        self,
        name: str,
        reference_name: Optional[str] = None,
    ) -> Column:
        table: Union[Table, Alias] = self._get_table(reference_name=reference_name)

        column = table.columns.get(name)
        if isinstance(column, Column):
            return column

        raise ColumnDoesNotExistException

    def _build_expression(
        self,
        lookup: str,
        value: Any,
        reference_name: Optional[str] = None,
    ) -> BinaryExpression:
        """
        Build sqlalchemy expression by passed lookup, value
        if value was passed as dict so this function will work recursive.
        """
        column_name, *operator_name = lookup.split(self.LOOKUP_STRING)
        operator_name = operator_name[-1] if operator_name else self.EQUAL_OPERATOR
        try:
            # self_method this is method that implemented in class Filters in Provider
            self_method: Callable = getattr(self, column_name)
            return self_method(operator_name, value)
        except AttributeError:
            pass

        column = self._get_column(name=column_name, reference_name=reference_name)

        # Handle if value passed as self.ALL_OBJECTS_FILTER
        # it forms expression like field != None
        if value == self.ALL_OBJECTS_FILTER:
            operator_name = self.NOT_EQUAL_OPERATOR
            value = None

        lookup_operator = self.LOOKUP_OPERATORS.get(operator_name)
        if not callable(lookup_operator):
            raise LookupOperatorNotFoundException
        return lookup_operator(column, value)

    def build_where_clause(
        self,
        reference_name: Optional[str] = None,
        **filters: Dict[str, Any]
    ):
        """
        """
        E = []
        for l, v in filters.items():
            try:
                if type(v) == dict:
                    self_method = getattr(self, l, None)
                    if self_method is not None:
                        e = self_method(v)
                    else:
                        e = self.build_where_clause(reference_name=l, **v)
                else:
                    e = self._build_expression(lookup=l, value=v, reference_name=reference_name)
            except Exception as e:
                raise e
            E.append(e)
        return and_(*E)


class BaseAlchemyModelProvider(BaseAlchemyProvider):
    """
    """

    _mapper: Type[orm_models.ORMBaseModel]
    _usage_mappers: Optional[Tuple[Type[orm_models.ORMBaseModel]]] = None

    _table: Optional[Table] = None
    _usage_aliases: Optional[Tuple[Alias]] = tuple()

    _select_stmt: Optional[Select] = None
    _select_count_stmt: Optional[Select] = None
    _insert_stmt: Optional[Insert] = None
    _update_stmt: Optional[Update] = None
    _delete_stmt: Optional[Delete] = None

    _first_pk_column_name: Optional[str] = None

    _sorting_columns: Tuple[str]

    _single_record_adapter: Callable
    _multiple_records_adapter: Callable

    _does_not_exist_exception: Optional[Type[ObjectDoesNotExist]] = ObjectDoesNotExist

    class Filters(AlchemyFilters):
        """
        """

    @property
    def _get_mapper(self) -> Type[orm_models.ORMBaseModel]:
        try:
            return self._mapper
        except AttributeError:
            raise AttributeMustBeSetException

    def _get_table(
        self,
        reference_name: Optional[str] = None
    ) -> Union[Table, Alias]:
        if type(reference_name) is str:
            aliases: Tuple[Optional[Alias]] = self._get_usage_aliases
            filtered_aliases: Tuple[Optional[Alias]] = tuple(
                filter(lambda alias: reference_name in alias.name, aliases))
            if filtered_aliases:
                return filtered_aliases[0]

            try:
                reference = getattr(self._get_mapper, reference_name)
                tables: List[Table] = reference.property.mapper.tables
                return tables[0]
            except (IndexError, AttributeError):
                raise IncorrectReferenceNameException

        if not self._table:
            return self._get_mapper.__table__

        return self._table

    @property
    def _get_first_pk_column_name(self) -> str:
        """
        If self._first_pk_column_name is not defined
        searches in mapper pk columns, sets to self._first_pk_column_name that column name and
        returns first of the columns name, e.g. id column name
        else returns self._first_pk_column_name
        """
        if self._first_pk_column_name is None:
            primary_key_columns = get_primary_keys(self._get_mapper)
            first_pk_column_name: str = next(iter(primary_key_columns))
            self._first_pk_column_name = first_pk_column_name

        return self._first_pk_column_name

    @property
    def _get_first_pk_column(self) -> Column:
        """
        Returns first pk column of self._mapper
        """
        first_pk_column_name = self._get_first_pk_column_name
        return getattr(self._get_mapper, first_pk_column_name)

    @property
    def _get_usage_mappers(self) -> Iterable[orm_models.ORMBaseModel]:
        if not self._usage_mappers:
            return [self._get_mapper]
        return self._usage_mappers

    @property
    def _get_usage_aliases(self) -> Tuple[Alias]:
        if not self._usage_aliases:
            return tuple()
        return self._usage_aliases

    def _get_column(
        self,
        name: str,
        reference_name: Optional[str] = None,
    ) -> Column:
        table: Union[Table, Alias] = self._get_table(reference_name=reference_name)

        column = table.columns.get(name)
        if isinstance(column, Column):
            return column

        raise ColumnDoesNotExistException

    @property
    def _get_select_stmt(self) -> Select:
        """
        Returns self._select_stmt if it's not None and defined in subclasses or
        returns select self._mapper
        """
        if self._select_stmt is not None:
            return self._select_stmt
        return select(self._get_mapper)

    @property
    def _get_single_record_adapter(self) -> Callable:
        try:
            return self._single_record_adapter
        except AttributeError:
            raise AttributeMustBeSetException

    @property
    def _get_multiple_records_adapter(self) -> Callable:
        try:
            return self._multiple_records_adapter
        except AttributeError:
            raise AttributeMustBeSetException

    @property
    def _get_sorting_columns(self) -> Tuple[str]:
        try:
            return self._sorting_columns
        except AttributeError:
            raise AttributeMustBeSetException

    async def __ainit__(
        self
    ):
        await super().__ainit__()
        self._filters = self.Filters()
        self._filters._mapper = self._get_mapper
        self._filters._table = self._get_table()
        self._filters._joined_aliases = self._get_usage_aliases

    def _bind_order_limit_offset_to_stmt(
        self,
        select_stmt: Select,
        order_by: str = ...,
        order_reversed: bool = ...,
        limit: int = ...,
        offset: int = ...,
    ) -> Select:
        """
        Binds to passed select_stmt order_by, limit and offset statements
        and returns select_stmt
        """
        if type(order_by) == str and order_by in self._get_sorting_columns:
            by_column = self._get_column(order_by)
            if type(order_reversed) == bool:
                by_column = by_column.desc() if order_reversed else by_column.asc()
            select_stmt = select_stmt.order_by(nullslast(by_column))

        if type(limit) == int:
            select_stmt = select_stmt.limit(limit)
        if type(offset) == int:
            select_stmt = select_stmt.offset(offset)

        return select_stmt

    def _make_select_stmt(
        self,
        select_stmt: Select = None,
        order_by: str = None,
        order_reversed: bool = None,
        limit: int = None,
        offset: int = None,
        **filters
    ) -> Select:
        """
        Builds select statement by passed filters and return instance of Select class
        """
        filters = clear_from_ellipsis(**filters)

        stmt = select_stmt
        if stmt is None:
            stmt = self._select_stmt
        if stmt is None:
            stmt = select(self._get_mapper)

        stmt = self._bind_order_limit_offset_to_stmt(
            select_stmt=stmt,
            order_by=order_by,
            order_reversed=order_reversed,
            limit=limit,
            offset=offset,
        )

        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.where(where_clause)

        return stmt

    def _form_returning_stmt(
        self,
        stmt: Union[Insert, Update]
    ) -> Union[Insert, Update]:
        """
        Adds returning statement to insert or update statement which will return mapper first pk value
        """
        first_pk_column = self._get_first_pk_column
        return stmt.returning(first_pk_column)

    def _base_update_stmt(
        self,
        filters = {},
        values = {}
    ) -> Union[Update, Select]:
        """
        Builds necessary statement for using it in update methods
        """
        update_stmt = self._update_stmt
        if not update_stmt:
            update_stmt = update(self._get_mapper)

        where_clause = self._filters.build_where_clause(**filters)
        update_stmt = update_stmt.values(**values)
        update_stmt = update_stmt.where(where_clause)

        update_stmt = self._form_returning_stmt(stmt=update_stmt)

        return update_stmt

    async def _do_select(
        self,
        order_by: str = None,
        order_reversed: bool = None,
        limit: int = None,
        offset: int = None,
        **filters
    ):
        """
        """
        stmt = self._make_select_stmt(
            order_by=order_by,
            order_reversed=order_reversed,
            limit=limit,
            offset=offset,
            **filters
        )

        return (await self.session.execute(stmt)).all()

    async def _do_select_count(
        self,
        **filters
    ) -> int:
        """
        """
        stmt = self._select_count_stmt
        if stmt is None:
            stmt = select(func.count()).select_from(self._get_mapper)

        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.where(where_clause)

        return await self.session.scalar(stmt)

    async def _do_get(
        self,
        **filters
    ):
        """
        """
        stmt = self._select_stmt
        if stmt is None:
            stmt = select(self._get_mapper)

        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.where(where_clause)

        return (await self.session.execute(stmt)).first()

    async def _do_insert(
        self,
        **values
    ) -> Union[str, int]:
        """
        Does insert and returns value of first pk column in table
        """
        insert_stmt = self._insert_stmt
        if not insert_stmt:
            insert_stmt = insert(self._get_mapper)

        insert_stmt = insert_stmt.values(**values)

        insert_stmt = self._form_returning_stmt(stmt=insert_stmt)

        return await self.session.scalar(insert_stmt)

    async def _do_bulk_insert(
        self,
        VT: Tuple[Mapping[str, Any]],
    ) -> List[Union[str, int]]:
        """
        Does bulk inserts to table and returns first pk column values of each inserted rows
        """
        insert_stmt = self._insert_stmt
        if not insert_stmt:
            insert_stmt = insert(self._get_mapper)

        insert_stmt = insert_stmt.values(VT)

        insert_stmt = self._form_returning_stmt(stmt=insert_stmt)

        return await self.session.scalars(insert_stmt)

    async def _do_update(
        self,
        filters,
        values
    ) -> Union[int, str]:
        """
        This method expects only one row to update and returns the row if this necessary
        """
        stmt = self._base_update_stmt(filters, values)

        # something went wrong, we couldn't find any solutions then `execution_options={"synchronize_session": False}`
        # see more in https://stackoverflow.com/questions/51221686/sqlalchemy-cannot-evaluate-binaryexpression-with-operator
        return await self.session.scalar(stmt, execution_options={"synchronize_session": False})

    async def _do_bulk_update(
        self,
        filters,
        values
    ) -> List[Union[int, str]]:
        """
        This method expects multiple rows to update and returns the rows if this necessary
        """
        stmt = self._base_update_stmt(filters, values)

        # something went wrong, we couldn't find any solutions then `execution_options={"synchronize_session": False}`
        # see more in https://stackoverflow.com/questions/51221686/sqlalchemy-cannot-evaluate-binaryexpression-with-operator
        return await self.session.scalars(stmt, execution_options={"synchronize_session": False})

    async def _do_delete(
        self,
        **filters
    ) -> None:
        """
        """
        stmt = self._delete_stmt
        if stmt is None:
            stmt = delete(self._get_mapper)

        where_clause = self._filters.build_where_clause(**filters)
        stmt = stmt.where(where_clause)

        await self.session.execute(stmt, execution_options={"synchronize_session": False})

    async def select(
        self,
        order_by: str = None,
        order_reversed: bool = None,
        limit: int = None,
        offset: int = None,
        **filters
    ):
        """
        """
        filters = clear_from_ellipsis(**filters)

        records = await self._do_select(
            order_by=order_by,
            order_reversed=order_reversed,
            limit=limit,
            offset=offset,
            **filters
        )

        return await self._get_multiple_records_adapter(records)

    async def select_count(
        self,
        **filters
    ) -> int:
        """
        """
        filters = clear_from_ellipsis(**filters)

        return await self._do_select_count(**filters)

    async def select_rows(
        self,
        order_by: str = ...,
        order_reversed: bool = ...,
        **filters
    ) -> List[Tuple[Any]]:
        """
        Returns list of tuple where tuple contains only rows which were included to filters
        """
        select_columns: List[Column] = []
        for lookup, value in filters.items():
            column_name, *_ = lookup.split(self._filters.LOOKUP_STRING)
            select_columns.append(self._get_column(column_name))
        where_clause = self._filters.build_where_clause(**filters)
        stmt = select(*select_columns).where(where_clause)

        if type(order_by) == str and order_by in self._get_sorting_columns:
            by_column = self._get_column(order_by)
            if type(order_reversed) == bool:
                by_column = by_column.desc() if order_reversed else by_column.asc()
            stmt = stmt.order_by(by_column)

        return (await self.session.execute(stmt)).all()

    async def get(
        self,
        **filters
    ):
        """
        """
        filters = clear_from_ellipsis(**filters)
        if not filters:
            raise FiltersMustBePassedException

        record = await self._do_get(**filters)

        if not record:
            raise self._does_not_exist_exception

        return await self._get_single_record_adapter(*record)

    async def get_row(
        self,
        **filters
    ) -> Tuple[Any]:
        """
        Returns tuple contains only rows which were included to filters
        """
        select_columns: List[Column] = []
        for lookup, value in filters.items():
            column_name, *_ = lookup.split(self._filters.LOOKUP_STRING)
            select_columns.append(self._get_column(column_name))
        where_clause = self._filters.build_where_clause(**filters)
        stmt = select(*select_columns).where(where_clause)
        return (await self.session.execute(stmt)).first()

    async def insert(
        self,
        **values
    ):
        """
        Makes insert and returns self.get
        """
        values = clear_from_ellipsis(**values)

        first_pk_column_name: str = self._get_first_pk_column_name
        record_pk_value: Union[int, str] = await self._do_insert(**values)

        return await self.get(
            **{
                first_pk_column_name: record_pk_value
            }
        )

    async def bulk_insert(
        self,
        VT: Tuple[Dict[str, Any]]
    ):
        """
        Make bulk insert and returns self.select result
        """
        first_pk_column_name: str = self._get_first_pk_column_name
        records_pk_values: List[Union[int, str]] = await self._do_bulk_insert(VT=VT)

        return await self.select(
            **{
                first_pk_column_name + AlchemyFilters.LOOKUP_STRING + AlchemyFilters.IN_OPERATOR: records_pk_values
            }
        )

    async def get_or_insert(
        self,
        **values
    ):
        """
        Can accept only values with column which are not unique or pk,
        Tries to find row table with passed values params if such row does not exist
        then insert new row with passed values params
        """
        values = clear_from_ellipsis(**values)
        for column_name, value in values.items():
            column: Column = self._get_column(column_name)
            if column.unique:
                raise ColumnIsUniqueException

        try:
            return await self.get(**values)
        except self._does_not_exist_exception:
            return await self.insert(**values)

    async def update(
        self,
        **kwargs
    ):
        """
        """
        kwargs = clear_from_ellipsis(**kwargs)
        # Separate filters and values from kwargs,
        # so filters is string that contains LOOKUP_STRING
        # and values is regular string
        # that does not contain LOOKUP_STRING
        filters: Dict[str, Any] = dict()
        values: Dict[str, Any] = dict()
        for key, value in kwargs.items():
            if self._filters.LOOKUP_STRING in key:
                filters[key] = value
            else:
                values[key] = value

        if not filters:
            raise FiltersMustBePassedException

        if not values:
            return await self.get(**filters)

        first_pk_column_name: str = self._get_first_pk_column_name
        record_pk_value: Union[int, str] = await self._do_update(filters, values)

        return await self.get(
            **{
                first_pk_column_name: record_pk_value
            }
        )

    async def bulk_update(
        self,
        **kwargs
    ):
        """
        """
        kwargs = clear_from_ellipsis(**kwargs)

        # Separate filters and values from kwargs,
        # so filters is string that contains LOOKUP_STRING
        # and values is regular string
        # that does not contain LOOKUP_STRING
        filters: Dict[str, Any] = dict()
        values: Dict[str, Any] = dict()
        for key, value in kwargs.items():
            if self._filters.LOOKUP_STRING in key:
                filters[key] = value
            else:
                values[key] = value

        if not filters:
            raise FiltersMustBePassedException

        first_pk_column_name: str = self._get_first_pk_column_name
        records_pk_values: List[Union[int, str]] = await self._do_bulk_update(filters, values)

        return await self.select(
            **{
                first_pk_column_name + AlchemyFilters.LOOKUP_STRING + AlchemyFilters.IN_OPERATOR: records_pk_values
            }
        )

    async def update_or_insert(
        self,
        **kwargs
    ):
        """
        Keys with LOOKUP FILTER perceived as filter params to find rows that satisfied passed filters
        and tries to update them columns that was passed in kwargs without LOOKUP FILTER
        """
        # Separate filters and values from kwargs,
        # so filters is string that contains LOOKUP_STRING
        # and values is regular string
        # that does not contain LOOKUP_STRING
        kwargs = clear_from_ellipsis(**kwargs)

        filters: Dict[str, Any] = dict()
        values: Dict[str, Any] = dict()
        for key, value in kwargs.items():
            if self._filters.LOOKUP_STRING in key:
                filters[key] = value
            else:
                values[key] = value
                column: Column = self._get_column(key)
                if column.unique:
                    raise ColumnIsUniqueException

        if not filters:
            raise FiltersMustBePassedException

        try:
            return await self.update(**kwargs)
        except:
            return await self.insert(**values)

    async def delete(
        self,
        **filters
    ) -> None:
        """
        Delete all rows from table that satisfies to filters
        """
        filters = clear_from_ellipsis(**filters)
        # If not filters raise exception
        if not filters:
            raise FiltersMustBePassedException

        await self._do_delete(**filters)

    async def bulk_delete(
        self,
        **filters
    ) -> None:
        """
        Delete all rows from table that satisfies to filters
        """
        return await self.delete(**filters)


class RedisProvider(BaseProvider):

    redis: Redis

    async def __ainit__(
        self
    ):
        await super().__ainit__()
        self.redis = self._story.redis


class BaseRedisModelProvider(RedisProvider):

    async def set(
        self,
        key: Any,
        value: Any,
    ):
        key = json.dumps(key)
        value = json.dumps(value)

        await self.redis.set(name=key, value=value)

    async def get(
        self,
        key: Any
    ) -> Any:
        key = json.dumps(key)
        value = await self.redis.get(name=key)
        if value:
            return json.loads(value)

    async def hset(
        self,
        hash_name: Any,
        key: Any,
        value: Any,
    ):
        hash_name = json.dumps(hash_name)
        key = json.dumps(key)
        value = json.dumps(value)

        await self.redis.hset(name=hash_name, key=key, value=value)

    async def hget(
        self,
        hash_name: str,
        key: Any,
    ) -> Any:
        hash_name = json.dumps(hash_name)
        key = json.dumps(key)
        value = await self.redis.hget(name=hash_name, key=key)
        if value:
            return json.loads(value)

    async def hmget(
        self,
        hash_name: str,
        keys: Sequence[Any]
    ) -> Iterable[Optional[Any]]:
        hash_name = json.dumps(hash_name)
        values = await self.redis.hmget(
            name=hash_name,
            keys=keys
        )
        return json.loads(values)

    async def hdelete(
        self,
        hash_name: Any,
        key: Optional[Any] = None
    ):
        hash_name = json.dumps(hash_name)
        if key:
            key = json.dumps(key)
            return await self.redis.hdel(name=hash_name, key=key)

        await self.redis.hdel(name=hash_name)

    async def keys(
        self,
        key_sub: str
    ) -> Optional[Union[str, bytes]]:
        return await self.redis.keys(f'*{key_sub}*')

    async def delete(
        self,
        key: Any
    ):
        key = json.dumps(key)
        await self.redis.delete(key)
