from __future__ import annotations

import datetime
from collections.abc import Iterable
from typing import Generic, final

from typing_extensions import TypeVar

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import NeverPattern, Pattern

_T = TypeVar("_T", None, bool, int, float, str, default=None, infer_variance=True)


class ScalarPattern(Pattern, Generic[_T]):
    def __init__(self, value: _T | None = None) -> None:
        self._value = value

    @final
    def __getitem__(self, __key: int | str) -> NeverPattern:
        return NeverPattern()

    def __repr__(self) -> str:
        return f"{type(self).__name__}: {self._value!r}"


@final
class BoolPattern(ScalarPattern[bool]):
    def apply(self, document: Document) -> Iterable[bool]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, bool):
            return

        if self._value is None or document == self._value:
            yield document


@final
class IntPattern(ScalarPattern[int]):
    def apply(self, document: Document) -> Iterable[int]:
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


@final
class FloatPattern(ScalarPattern[float]):
    def apply(self, document: Document) -> Iterable[float]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, float):
            return

        if self._value is None or document == self._value:
            yield document


@final
class StrPattern(ScalarPattern[str]):
    def apply(self, document: Document) -> Iterable[str]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, str):
            return

        if self._value is None or document == self._value:
            yield document
