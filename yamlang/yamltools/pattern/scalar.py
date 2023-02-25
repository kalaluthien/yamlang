from __future__ import annotations

import datetime
from collections.abc import Iterable
from typing import Generic, final

from typing_extensions import TypeVar

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import Pattern

_T = TypeVar(
    "_T",
    None,
    bool,
    int,
    float,
    str,
    datetime.date,
    datetime.datetime,
    default=None,
    infer_variance=True,
)


class ScalarPattern(Pattern, Generic[_T]):
    def __init__(self, value: _T | None = None) -> None:
        self._value = value

    @final
    def __getitem__(self: ScalarPattern, __key: int | str) -> ScalarPattern:
        return NeverPattern()


class NeverPattern(ScalarPattern):
    def apply(self, document: Document) -> Iterable[Document]:
        return iter(())


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
