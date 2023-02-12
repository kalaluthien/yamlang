from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any
from typing import Self
from typing import TypeVar
from typing import final
from typing import overload

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

        is_nullable: bool = False
        patterns: list[Pattern] = []

        if isinstance(self, NullPattern):
            is_nullable = True
            patterns.append(self.pattern)

        if isinstance(__pattern, NullPattern):
            is_nullable = True
            patterns.append(__pattern.pattern)

        if isinstance(self, OrPattern):
            patterns.extend(self.patterns)

        if isinstance(__pattern, OrPattern):
            patterns.extend(__pattern.patterns)

        if not patterns:
            return OrPattern([self, __pattern])

        if is_nullable:
            return NullPattern(OrPattern(patterns))

        return OrPattern(patterns)

    @final
    def __ror__(self, __pattern: None) -> Self:
        return NullPattern(self)

    @final
    def __rrshift__(self, __pattern: Pattern) -> Self:
        return ThenPattern(__pattern, self)


class NullPattern(Pattern):
    def __init__(self, pattern: Pattern) -> None:
        self.pattern = pattern

    def apply(self, document: Document) -> Iterable[Document]:
        result = iter(self.pattern.apply(document))

        try:
            yield next(result)
        except StopIteration:
            yield None

        yield from result

    def __getattr__(self, name: str) -> Any:
        return getattr(self.pattern, name)


class OrPattern(Pattern):
    def __init__(self, patterns: Iterable[Pattern]) -> None:
        self.patterns = tuple(patterns)

    def apply(self, document: Document) -> Iterable[Document]:
        for pattern in self.patterns:
            yield from pattern.apply(document)

    def __getattr__(self, name: str) -> Any:
        for pattern in self.patterns:
            if (attr := getattr(pattern, name, None)) is not None:
                return attr
        raise AttributeError(*self.patterns, name=name)


class ThenPattern(Pattern):
    def __init__(self, frontend_pattern: Pattern, backend_pattern: Pattern) -> None:
        self.frontend_pattern = frontend_pattern
        self.backend_result = backend_pattern

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.frontend_pattern.apply(document):
            yield from self.backend_result.apply(result)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.backend_result, name)
