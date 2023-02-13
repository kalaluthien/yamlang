from collections.abc import Iterable
from typing import Generic, TypeVar, final

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import Pattern

_T = TypeVar("_T", bool, int, float, str)


class ScalarPattern(Pattern, Generic[_T]):
    def __init__(self, value: _T | None = None) -> None:
        self._value = value

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
