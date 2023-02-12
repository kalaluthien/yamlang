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

    def __getitem__(self, index_or_key: int | str | slice) -> Any:
        raise TypeError(self)

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(name, self)


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

    def __getitem__(self, index_or_key: int | str | slice) -> Any:
        if not hasattr(self.__pattern, "__getitem__"):
            raise TypeError(self.__pattern)

        candidate = getattr(self.__pattern, "__getitem__")(index_or_key)

        if isinstance(candidate, Pattern):
            return NullPattern(candidate)

        return candidate

    def __getattr__(self, name: str) -> Any:
        if not hasattr(self.__pattern, name):
            raise AttributeError(name, self.__pattern)

        candidate = getattr(self.__pattern, name)

        if isinstance(candidate, Pattern):
            return NullPattern(candidate)

        return candidate


class OrPattern(Pattern):
    def __init__(self, patterns: Iterable[Pattern]) -> None:
        self.__patterns = tuple(patterns)

    def apply(self, document: Document) -> Iterable[Document]:
        for pattern in self.__patterns:
            yield from pattern.apply(document)

    def __getitem__(self, index_or_key: int | str | slice) -> Any:
        candidates = [
            getattr(pattern, "__getitem__")(index_or_key)
            for pattern in self.__patterns
            if hasattr(pattern, "__getitem__")
        ]

        if not candidates:
            raise TypeError(*self.__patterns)

        if all(isinstance(c, Iterable) for c in candidates):
            return (value for candidate in candidates for value in candidate)

        if all(isinstance(c, Pattern) for c in candidates):
            return OrPattern(candidates)

        return next(iter(candidates))

    def __getattr__(self, name: str) -> Any:
        candidates = [
            getattr(pattern, name)
            for pattern in self.__patterns
            if hasattr(pattern, name)
        ]

        if not candidates:
            raise AttributeError(name, *self.__patterns)

        if all(isinstance(c, Iterable) for c in candidates):
            return (value for candidate in candidates for value in candidate)

        if all(isinstance(c, Pattern) for c in candidates):
            return OrPattern(candidates)

        return next(iter(candidates))


class ThenPattern(Pattern):
    def __init__(self, frontend_pattern: Pattern, backend_pattern: Pattern) -> None:
        self.__frontend_pattern = frontend_pattern
        self.__backend_pattern = backend_pattern

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__frontend_pattern.apply(document):
            yield from self.__backend_pattern.apply(result)

    def __getitem__(self, index_or_key: int | str | slice) -> Any:
        if not hasattr(self.__backend_pattern, "__getitem__"):
            raise TypeError(self.__backend_pattern)

        candidate = getattr(self.__backend_pattern, "__getitem__")(index_or_key)

        if isinstance(candidate, Pattern):
            return ThenPattern(self, candidate)

        return candidate

    def __getattr__(self, name: str) -> Any:
        if not hasattr(self.__backend_pattern, name):
            raise AttributeError(name, self.__backend_pattern)

        candidate = getattr(self.__backend_pattern, name)

        if isinstance(candidate, Pattern):
            return ThenPattern(self, candidate)

        return candidate
