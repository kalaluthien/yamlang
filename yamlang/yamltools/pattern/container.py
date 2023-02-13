from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import product
from typing import Generic, Self, TypeVar, final, overload

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import Pattern

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
    def __getitem__(self, __key: int) -> GetPattern[_T1]:
        return GetPattern[_T1](self, __key)


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
        pattern_string = str(self.__pattern)
        if pattern_string.startswith("(") and pattern_string.endswith(")"):
            pattern_string = pattern_string[1:-1]
        return f"{self.__class__.__name__}({pattern_string})"


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
        pattern_strings: list[str] = []
        for key, pattern in self.__patterns.items():
            pattern_string = str(pattern)
            if pattern_string.startswith("(") and pattern_string.endswith(")"):
                pattern_string = pattern_string[1:-1]
            pattern_strings.append(f"{key}: {pattern_string}")
        pattern_string = ", ".join(pattern_strings)
        return f"{self.__class__.__name__}({{{pattern_string}}})"


class GetPattern(Pattern, Generic[_T1]):
    def __init__(self, pattern: Pattern, *key: int | str) -> None:
        self.__pattern = pattern
        self.__keys = key

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__pattern.apply(document):
            for key in self.__keys:
                if isinstance(key, int):
                    if isinstance(result, list) and (-len(result) <= key < len(result)):
                        result = result[key]
                    else:
                        break
                else:
                    if isinstance(result, dict) and key in result:
                        result = result[key]
                    else:
                        break
            else:
                yield result

    @overload
    def __getitem__(self: GetPattern[ListPattern[_T2]], __key: int) -> GetPattern[_T2]:
        ...

    @overload
    def __getitem__(self: GetPattern[DictPattern[_T2]], __key: str) -> GetPattern[_T2]:
        ...

    @overload
    def __getitem__(self, __key: int | str) -> GetPattern[_T1]:
        ...

    def __getitem__(self, __key: int | str) -> Pattern:
        return GetPattern(self.__pattern, *self.__keys, __key)

    def __repr__(self) -> str:
        return f"{self.__pattern}[{']['.join(map(str, self.__keys))}]"


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
