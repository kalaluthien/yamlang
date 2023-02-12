from abc import abstractmethod
from collections.abc import Iterable
from itertools import product
from typing import Generic, Self, TypeVar, final

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import Pattern

_T = TypeVar("_T", bound=Pattern)


class SequencePattern(Pattern, Generic[_T]):
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
        self.__pattern = pattern

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for items in product(*(self.__pattern.apply(item) for item in document)):
                yield list(items)

    def __getitem__(self, index: int) -> _T:
        return ListPattern.__GetItemPattern(self, index) >> self.__pattern

    class __GetItemPattern(Pattern):
        def __init__(self, pattern: SequencePattern[_T], index: int) -> None:
            self.pattern = pattern
            self.index = index

        def apply(self, document: Document) -> Iterable[Document]:
            for result in self.pattern.apply(document):
                if isinstance(result, list) and -len(result) <= self.index < len(
                    result
                ):
                    yield result[self.index]


class TakeSequencePattern(SequencePattern[_T]):
    def __init__(self, pattern: SequencePattern[_T], count: int) -> None:
        self.__pattern = pattern
        self.__count = count

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__pattern.apply(document):
            if isinstance(result, list):
                yield result[: self.__count]

    def __getitem__(self, index: int) -> _T:
        return self.__pattern[index]


class DropSequencePattern(SequencePattern[_T]):
    def __init__(self, pattern: SequencePattern[_T], count: int) -> None:
        self.__pattern = pattern
        self.__count = count

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__pattern.apply(document):
            if isinstance(result, list):
                yield result[self.__count :]

    def __getitem__(self, index: int) -> _T:
        return self.__pattern[index]
