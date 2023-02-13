from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import product
from typing import Generic, Self, TypeVar, final, overload

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import FailPattern, Pattern

_T1 = TypeVar("_T1", bound=Pattern)
_T2 = TypeVar("_T2", bound=Pattern)


class SequencePattern(Pattern, Generic[_T1]):
    @final
    def take(self, count: int) -> Self:
        return TakeSequencePattern(self, count)

    @final
    def drop(self, count: int) -> Self:
        return DropSequencePattern(self, count)

    @final
    def __getitem__(self, __key: int) -> AtPattern[_T1]:
        return AtPattern[_T1](self, __key)


class MappingPattern(Pattern, Generic[_T1]):
    @final
    def __getitem__(self, __key: str) -> GetPattern[_T1]:
        return GetPattern[_T1](self, __key)


class ListPattern(SequencePattern[_T1]):
    def __init__(self, pattern: _T1) -> None:
        self.__pattern = pattern

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for items in product(*(self.__pattern.apply(item) for item in document)):
                yield list(items)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__pattern})"


class AtPattern(Pattern, Generic[_T1]):
    def __init__(self, pattern: Pattern, *index: int) -> None:
        self.__pattern = pattern
        self.__indexes = index

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__pattern.apply(document):
            for index in self.__indexes:
                if not isinstance(result, list):
                    return
                if index >= len(result) or index < -len(result):
                    return
                result = result[index]
            yield result

    @overload
    def __getitem__(self: AtPattern[ListPattern[_T2]], __key: int) -> AtPattern[_T2]:
        ...

    @overload
    def __getitem__(self: AtPattern[DictPattern[_T2]], __key: str) -> GetPattern[_T2]:
        ...

    @overload
    def __getitem__(self, __key: int | str) -> FailPattern[_T1]:
        ...

    def __getitem__(self, __key: int | str) -> Pattern:
        if isinstance(__key, str):
            return GetPattern(self, __key)
        return AtPattern(self.__pattern, *self.__indexes, __key)

    def __repr__(self) -> str:
        return f"{self.__pattern}[{']['.join(map(str, self.__indexes))}]"


class DictPattern(MappingPattern[_T1]):
    def __init__(self, patterns: Mapping[str, _T1]) -> None:
        self.__patterns = dict(patterns)

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, dict):
            return

        if not all(key in document for key in self.__patterns):
            return

        for values in product(
            *(
                pattern.apply(value)
                for key, value in document.items()
                if (pattern := self.__patterns.get(key))
            )
        ):
            yield dict(zip(self.__patterns.keys(), values))

    def __repr__(self) -> str:
        patterns = ", ".join(
            f"{key}: {value}" for key, value in self.__patterns.items()
        )
        return f"{self.__class__.__name__}({{{patterns}}})"


class GetPattern(Pattern, Generic[_T1]):
    def __init__(self, pattern: Pattern, *key: str) -> None:
        self.__pattern = pattern
        self.__keys = key

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__pattern.apply(document):
            for key in self.__keys:
                if not isinstance(result, dict):
                    return
                if key not in result:
                    return
                result = result[key]
            yield result

    @overload
    def __getitem__(self: GetPattern[DictPattern[_T2]], __key: str) -> GetPattern[_T2]:
        ...

    @overload
    def __getitem__(self: GetPattern[ListPattern[_T2]], __key: int) -> AtPattern[_T2]:
        ...

    @overload
    def __getitem__(self, __key: str | int) -> FailPattern[_T1]:
        ...

    def __getitem__(self, __key: str | int) -> Pattern:
        if isinstance(__key, int):
            return AtPattern(self, __key)
        return GetPattern(self.__pattern, *self.__keys, __key)

    def __repr__(self) -> str:
        return f"{self.__pattern}[{']['.join(self.__keys)}]"


class TakeSequencePattern(SequencePattern[_T1]):
    def __init__(self, pattern: SequencePattern[_T1], count: int) -> None:
        self.__pattern = pattern
        self.__count = count

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__pattern.apply(document):
            if isinstance(result, list):
                yield result[: self.__count]

    def __repr__(self) -> str:
        return f"{self.__pattern}[:{self.__count}]"


class DropSequencePattern(SequencePattern[_T1]):
    def __init__(self, pattern: SequencePattern[_T1], count: int) -> None:
        self.__pattern = pattern
        self.__count = count

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__pattern.apply(document):
            if isinstance(result, list):
                yield result[self.__count :]

    def __repr__(self) -> str:
        return f"{self.__pattern}[{self.__count}:]"
