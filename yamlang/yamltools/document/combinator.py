from __future__ import annotations

import datetime
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, overload

from typing_extensions import TypeVar

from yamlang.yamltools.document.document import Document

_T = TypeVar("_T", bound=Document, default=Document, infer_variance=True)
_T2 = TypeVar("_T2", bound=Document, default=Document, infer_variance=True)
_F = (
    None
    | bool
    | int
    | float
    | str
    | datetime.date
    | datetime.datetime
    | list[_T]
    | dict[str, _T]
)


_IDENTITY_FUNCTION: Any = lambda x: x


@dataclass
class _Map:
    on_none: Callable[[None], None] | None = None
    on_bool: Callable[[bool], bool] | None = None
    on_int: Callable[[int], int] | None = None
    on_float: Callable[[float], float] | None = None
    on_str: Callable[[str], str] | None = None
    on_date: Callable[[datetime.date], datetime.date] | None = None
    on_datetime: Callable[[datetime.datetime], datetime.datetime] | None = None
    default: Callable[[Document], Document] = _IDENTITY_FUNCTION


@dataclass
class Map(_Map):
    if TYPE_CHECKING:
        on_none: Callable[[None], None]
        on_bool: Callable[[bool], bool]
        on_int: Callable[[int], int]
        on_float: Callable[[float], float]
        on_str: Callable[[str], str]
        on_date: Callable[[datetime.date], datetime.date]
        on_datetime: Callable[[datetime.datetime], datetime.datetime]
        default: Callable[[Document], Document]

    @overload
    def __call__(self, document: None) -> None:
        ...

    @overload
    def __call__(self, document: bool) -> bool:
        ...

    @overload
    def __call__(self, document: int) -> int:
        ...

    @overload
    def __call__(self, document: float) -> float:
        ...

    @overload
    def __call__(self, document: str) -> str:
        ...

    @overload
    def __call__(self, document: datetime.datetime) -> datetime.datetime:
        ...

    @overload
    def __call__(self, document: datetime.date) -> datetime.date:
        ...

    @overload
    def __call__(self, document: list[_T]) -> list[_T]:
        ...

    @overload
    def __call__(self, document: dict[str, _T]) -> dict[str, _T]:
        ...

    def __call__(self, document: Any) -> Any:
        return self.apply(document)

    def apply(self, document: Document) -> Document:
        if document is None and self.on_none:
            return self.on_none(document)

        if isinstance(document, bool) and self.on_bool:
            return self.on_bool(document)

        if isinstance(document, int) and self.on_int:
            return self.on_int(document)

        if isinstance(document, float) and self.on_float:
            return self.on_float(document)

        if isinstance(document, str) and self.on_str:
            return self.on_str(document)

        if isinstance(document, datetime.datetime) and self.on_datetime:
            return self.on_datetime(document)

        if isinstance(document, datetime.date) and self.on_date:
            return self.on_date(document)

        if isinstance(document, list):
            return [self.apply(x) for x in document]

        if isinstance(document, dict):
            return {k: self.apply(v) for k, v in document.items()}

        return self.default(document)


@dataclass
class _FoldMap(Generic[_T]):
    on_none: Callable[[None], _T] | None = None
    on_bool: Callable[[bool], _T] | None = None
    on_int: Callable[[int], _T] | None = None
    on_float: Callable[[float], _T] | None = None
    on_str: Callable[[str], _T] | None = None
    on_date: Callable[[datetime.date], _T] | None = None
    on_datetime: Callable[[datetime.datetime], _T] | None = None
    on_list: Callable[[list[_T]], _T] | None = None
    on_dict: Callable[[dict[str, _T]], _T] | None = None
    default: Callable[[_F[_T]], _T] = _IDENTITY_FUNCTION


@dataclass
class FoldMap(_FoldMap[_T]):
    if TYPE_CHECKING:
        on_none: Callable[[None], _T]
        on_bool: Callable[[bool], _T]
        on_int: Callable[[int], _T]
        on_float: Callable[[float], _T]
        on_str: Callable[[str], _T]
        on_date: Callable[[datetime.date], _T]
        on_datetime: Callable[[datetime.datetime], _T]
        on_list: Callable[[list[_T]], _T]
        on_dict: Callable[[dict[str, _T]], _T]
        default: Callable[[_F[_T]], _T]

    @overload
    def __call__(self, document: None) -> _T:
        ...

    @overload
    def __call__(self, document: bool) -> _T:
        ...

    @overload
    def __call__(self, document: int) -> _T:
        ...

    @overload
    def __call__(self, document: float) -> _T:
        ...

    @overload
    def __call__(self, document: str) -> _T:
        ...

    @overload
    def __call__(self, document: datetime.datetime) -> _T:
        ...

    @overload
    def __call__(self, document: datetime.date) -> _T:
        ...

    @overload
    def __call__(self, document: list[_T2]) -> _T:
        ...

    @overload
    def __call__(self, document: dict[str, _T2]) -> _T:
        ...

    def __call__(self, document: Document) -> _T:
        return self.apply(document)

    def apply(self, document: Document) -> _T:
        if document is None and self.on_none:
            return self.on_none(document)

        if isinstance(document, bool) and self.on_bool:
            return self.on_bool(document)

        if isinstance(document, int) and self.on_int:
            return self.on_int(document)

        if isinstance(document, float) and self.on_float:
            return self.on_float(document)

        if isinstance(document, str) and self.on_str:
            return self.on_str(document)

        if isinstance(document, datetime.datetime) and self.on_datetime:
            return self.on_datetime(document)

        if isinstance(document, datetime.date) and self.on_date:
            return self.on_date(document)

        if isinstance(document, list):
            if self.on_list:
                return self.on_list([self.apply(x) for x in document])
            else:
                return self.default([self.apply(x) for x in document])

        if isinstance(document, dict):
            if self.on_dict:
                return self.on_dict({k: self.apply(v) for k, v in document.items()})
            else:
                return self.default({k: self.apply(v) for k, v in document.items()})

        return self.default(document)
