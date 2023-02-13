import datetime
from collections.abc import Iterable
from typing import Generic, Self, TypeVar, final

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import NeverPattern, Pattern

_T = TypeVar("_T", bool, int, float, str, datetime.date, datetime.datetime)


class ScalarPattern(Pattern, Generic[_T]):
    def __init__(self, value: _T | None = None) -> None:
        self._value = value

    @final
    def __getitem__(self, __key: int | str | slice) -> Self:
        return NeverPattern[Self]()

    @final
    def __repr__(self) -> str:
        if self._value is None:
            return f"{self.__class__.__name__}(*)"
        return f"{self.__class__.__name__}({self._value})"


class BoolPattern(ScalarPattern[bool]):
    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, bool):
            return

        if self._value is None or document == self._value:
            yield document


class IntPattern(ScalarPattern[int]):
    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, int):
            return

        if isinstance(document, bool):
            return

        if self._value is None or document == self._value:
            yield document


class FloatPattern(ScalarPattern[float]):
    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, float):
            return

        if self._value is None or document == self._value:
            yield document


class StrPattern(ScalarPattern[str]):
    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, str):
            return

        if self._value is None or document == self._value:
            yield document


class DatePattern(ScalarPattern[datetime.date]):
    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, datetime.date):
            return

        if isinstance(document, datetime.datetime):
            return

        if self._value is None or document == self._value:
            yield document


class DateTimePattern(ScalarPattern[datetime.datetime]):
    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, datetime.datetime):
            return

        if self._value is None or document == self._value:
            yield document
