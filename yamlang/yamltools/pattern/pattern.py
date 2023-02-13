from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Generic, Self, TypeVar, cast, final, overload

from yamlang.yamltools import Document

_T = TypeVar("_T", bound="Pattern")


class Pattern(ABC):
    @abstractmethod
    def apply(self, document: Document) -> Iterable[Document]:
        raise NotImplementedError

    def __getitem__(self, __key: int | str | slice) -> FailPattern[Self]:
        raise TypeError(self)

    @overload
    def __or__(self, __pattern: None) -> Self:
        ...

    @overload
    def __or__(self, __pattern: _T) -> Self | _T:
        ...

    @final
    def __or__(self, __pattern: _T | None) -> Self | _T:
        if __pattern is None:
            return NullPattern(self)

        return OrPattern([self, __pattern])

    @final
    def __rrshift__(self, __pattern: Pattern) -> Self:
        return ThenPattern(__pattern, self)


class FailPattern(Pattern, Generic[_T]):
    def __new__(cls) -> _T:
        return cast(_T, super().__new__(cls))

    def apply(self, document: Document) -> Iterable[Document]:
        return iter(())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class NullPattern(Pattern):
    def __init__(self, pattern: Pattern) -> None:
        self.__pattern = pattern

    def apply(self, document: Document) -> Iterable[Document]:
        result = iter(self.__pattern.apply(document))

        try:
            yield next(result)
        except StopIteration:
            yield None

        yield from result

    def __getitem__(self, __key: int | str | slice) -> Self:
        return NullPattern(self.__pattern[__key])

    def __repr__(self) -> str:
        return f"({self.__pattern})?"


class OrPattern(Pattern):
    def __init__(self, patterns: Iterable[Pattern]) -> None:
        self.__patterns = tuple(p for p in patterns if not isinstance(p, FailPattern))

    def apply(self, document: Document) -> Iterable[Document]:
        for pattern in self.__patterns:
            yield from pattern.apply(document)

    def __getitem__(self, __key: int | str | slice) -> Self:
        return OrPattern(pattern[__key] for pattern in self.__patterns)

    def __repr__(self) -> str:
        return f"({' | '.join(map(str, self.__patterns))})"


class ThenPattern(Pattern):
    def __init__(self, frontend_pattern: Pattern, backend_pattern: Pattern) -> None:
        self.__frontend_pattern = frontend_pattern
        self.__backend_pattern = backend_pattern

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__frontend_pattern.apply(document):
            yield from self.__backend_pattern.apply(result)

    def __getitem__(self, __key: int | str | slice) -> Self:
        return ThenPattern(self.__frontend_pattern, self.__backend_pattern[__key])

    def __repr__(self) -> str:
        return f"({self.__frontend_pattern} -> {self.__backend_pattern})"
