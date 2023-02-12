from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from itertools import product
from typing import Generic
from typing import TypeVar
from typing import Self
from typing import final

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import Pattern

_T = TypeVar("_T", bound=Pattern)


class SequencePattern(Pattern, Generic[_T]):
    @abstractmethod
    def apply(self, document: Document) -> Iterable[list[Document]]:
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, index: int) -> _T:
        raise NotImplementedError

    @final
    def take(self, count: int) -> Self:
        return TakeSequencePattern(self, count)

    @final
    def drop(self, count: int) -> Self:
        return DropSequencePattern(self, count)


class ListPattern(SequencePattern[_T]):
    def __init__(self, pattern: _T) -> None:
        self.pattern = pattern

    def apply(self, document: Document) -> Iterable[list[Document]]:
        if not isinstance(document, list):
            return

        for items in product(*(self.pattern.apply(item) for item in document)):
            yield list(items)

    def __getitem__(self, index: int) -> _T:
        return ListPattern.GetItemPattern(self, index) >> self.pattern

    class GetItemPattern(Pattern):
        def __init__(self, pattern: SequencePattern[_T], index: int) -> None:
            self.pattern = pattern
            self.index = index

        def apply(self, document: Document) -> Iterable[Document]:
            for result in self.pattern.apply(document):
                yield result[self.index]


class TakeSequencePattern(SequencePattern[_T]):
    def __init__(self, pattern: SequencePattern[_T], count: int) -> None:
        self.pattern = pattern
        self.count = count

    def apply(self, document: Document) -> Iterable[list[Document]]:
        for result in self.pattern.apply(document):
            yield result[: self.count]

    def __getitem__(self, index: int) -> _T:
        return self.pattern[index]


class DropSequencePattern(SequencePattern[_T]):
    def __init__(self, pattern: SequencePattern[_T], count: int) -> None:
        self.pattern = pattern
        self.count = count

    def apply(self, document: Document) -> Iterable[list[Document]]:
        for result in self.pattern.apply(document):
            yield result[self.count :]

    def __getitem__(self, index: int) -> _T:
        return self.pattern[index]
