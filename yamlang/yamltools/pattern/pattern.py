from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, Self, TypeVar, cast, final, overload

from yamlang.yamltools import Document

_T = TypeVar("_T", bound="Pattern")


class Pattern(ABC):
    @abstractmethod
    def apply(self, document: Document) -> Iterable[Document]:
        raise NotImplementedError

    def __getitem__(self, __key: int | str | slice) -> NeverPattern[Self]:
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


class NeverPattern(Pattern, Generic[_T]):
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
        pattern_string = str(self.__pattern)
        if pattern_string.startswith("(") and pattern_string.endswith(")"):
            pattern_string = pattern_string[1:-1]
        return f"({pattern_string})?"


class OrPattern(Pattern):
    def __init__(self, patterns: Iterable[Pattern]) -> None:
        self.__patterns = tuple(p for p in patterns if not isinstance(p, NeverPattern))

    def apply(self, document: Document) -> Iterable[Document]:
        for pattern in self.__patterns:
            yield from pattern.apply(document)

    def __getitem__(self, __key: int | str | slice) -> Self:
        return OrPattern(pattern[__key] for pattern in self.__patterns)

    def __repr__(self) -> str:
        pattern_strings: list[str] = []
        for pattern in self.__patterns:
            pattern_string = str(pattern)
            if pattern_string.startswith("(") and pattern_string.endswith(")"):
                pattern_string = pattern_string[1:-1]
            pattern_strings.append(pattern_string)
        return " | ".join(pattern_strings)


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
        frontend_string = str(self.__frontend_pattern)
        if frontend_string.startswith("(") and frontend_string.endswith(")"):
            frontend_string = frontend_string[1:-1]
        backend_string = str(self.__backend_pattern)
        if backend_string.startswith("(") and backend_string.endswith(")"):
            backend_string = backend_string[1:-1]
        return f"(({frontend_string}) >> ({backend_string}))"
