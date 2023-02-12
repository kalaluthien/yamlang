from abc import abstractmethod
from collections.abc import Iterable
from typing import Generic
from typing import TypeGuard
from typing import TypeVar

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import Pattern


_T = TypeVar("_T", bool, int, float, str)


class ScalarPattern(Pattern, Generic[_T]):
    def __init__(self, scalar: _T | None = None) -> None:
        self.scalar = scalar

    def apply(self, document: Document) -> Iterable[_T]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if isinstance(document, dict):
            for value in document.values():
                yield from self.apply(value)
            return

        if self.match(document):
            yield document

    @abstractmethod
    def match(self, document: Document) -> TypeGuard[_T]:
        raise NotImplementedError


class BoolPattern(ScalarPattern[bool]):
    def match(self, document: Document) -> TypeGuard[bool]:
        if not isinstance(document, bool):
            return False

        if self.scalar is None:
            return True

        return document == self.scalar


class IntPattern(ScalarPattern[int]):
    def match(self, document: Document) -> TypeGuard[int]:
        if not isinstance(document, int):
            return False

        if isinstance(document, bool):
            return False

        if self.scalar is None:
            return True

        return document == self.scalar


class FloatPattern(ScalarPattern[float]):
    def match(self, document: Document) -> TypeGuard[float]:
        if not isinstance(document, float):
            return False

        if self.scalar is None:
            return True

        return document == self.scalar


class StrPattern(ScalarPattern[str]):
    def match(self, document: Document) -> TypeGuard[str]:
        if not isinstance(document, str):
            return False

        if self.scalar is None:
            return True

        return document == self.scalar
