from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, Self, cast, final, overload

from typing_extensions import TypeVar

from yamlang.yamltools import Document

_T = TypeVar("_T", bound="Pattern", default="Pattern", infer_variance=True)


class Pattern(ABC):
    @abstractmethod
    def apply(self, document: Document) -> Iterable[Document]:
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, __key: int | str | slice) -> Self:
        raise NotImplementedError

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


class NeverPattern(Pattern, Generic[_T]):
    def __new__(cls) -> _T:
        return cast(_T, super().__new__(cls))

    def apply(self, document: Document) -> Iterable[Document]:
        return iter(())

    def __getitem__(self, __key: int | str | slice) -> Self:
        return self


class NullPattern(Pattern):
    def __init__(self, pattern: Pattern) -> None:
        self.__pattern = pattern

    def apply(self, document: Document) -> Iterable[Document]:
        results = iter(self.__pattern.apply(document))

        try:
            yield next(results)
        except StopIteration:
            yield None

        yield from results

    def __getitem__(self, __key: int | str | slice) -> Self:
        return NullPattern(self.__pattern[__key])


class OrPattern(Pattern):
    def __init__(self, patterns: Iterable[Pattern]) -> None:
        self.__patterns = tuple(patterns)

    def apply(self, document: Document) -> Iterable[Document]:
        for pattern in self.__patterns:
            yield from pattern.apply(document)

    def __getitem__(self, __key: int | str | slice) -> Self:
        return OrPattern(pattern[__key] for pattern in self.__patterns)


class ThenPattern(Pattern):
    def __init__(self, frontend_pattern: Pattern, backend_pattern: Pattern) -> None:
        self.__frontend_pattern = frontend_pattern
        self.__backend_pattern = backend_pattern

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__frontend_pattern.apply(document):
            yield from self.__backend_pattern.apply(result)

    def __getitem__(self, __key: int | str | slice) -> Self:
        return ThenPattern(self.__frontend_pattern, self.__backend_pattern[__key])
