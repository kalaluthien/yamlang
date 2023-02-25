from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, Self, final, overload

from typing_extensions import TypeVar

from yamlang.yamltools import Document

_T1 = TypeVar("_T1", bound="Pattern", default="Pattern", infer_variance=True)
_T2 = TypeVar("_T2", bound="Pattern", default="Pattern", infer_variance=True)


class Pattern(ABC):
    @abstractmethod
    def apply(self, document: Document) -> Iterable[Document]:
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, __key: int | str) -> Self:
        raise NotImplementedError

    @overload
    def __or__(self, __pattern: None) -> Self:
        ...

    @overload
    def __or__(self, __pattern: _T1) -> Self | _T1:
        ...

    @final
    def __or__(self, __pattern: _T1 | None) -> Self | _T1:
        if __pattern is None:
            return MaybePattern(self)

        return OrPattern(self, __pattern)

    @final
    def __rrshift__(self, __pattern: Pattern) -> Self:
        return ThenPattern(__pattern, self)


class MaybePattern(Pattern, Generic[_T1]):
    def __init__(self, pattern: _T1) -> None:
        self.__pattern = pattern

    def apply(self, document: Document) -> Iterable[Document]:
        results = iter(self.__pattern.apply(document))

        try:
            yield next(results)
        except StopIteration:
            yield None
            return

        yield from results

    def __getitem__(self, __key: int | str) -> Self:
        return MaybePattern(self.__pattern[__key])


class OrPattern(Pattern, Generic[_T1, _T2]):
    def __init__(self, left_pattern: _T1, right_pattern: _T2) -> None:
        self.__left_pattern = left_pattern
        self.__right_pattern = right_pattern

    def apply(self, document: Document) -> Iterable[Document]:
        yield from self.__left_pattern.apply(document)
        yield from self.__right_pattern.apply(document)

    def __getitem__(self, __key: int | str) -> Self:
        return OrPattern(self.__left_pattern[__key], self.__right_pattern[__key])


class ThenPattern(Pattern, Generic[_T1, _T2]):
    def __init__(self, left_pattern: _T1, right_pattern: _T2) -> None:
        self.__left_pattern = left_pattern
        self.__right_pattern = right_pattern

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__left_pattern.apply(document):
            yield from self.__right_pattern.apply(result)

    def __getitem__(self, __key: int | str) -> Self:
        return ThenPattern(self.__left_pattern, self.__right_pattern[__key])
