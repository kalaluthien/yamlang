from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Generic, Self, final, overload

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
    def __or__(self, __pattern: NeverPattern) -> Self:
        ...

    @overload
    def __or__(self, __pattern: _T1) -> Self | _T1:
        ...

    @final
    def __or__(self, __pattern: _T1 | None) -> Self | _T1:
        if __pattern is None:
            return MaybePattern(self)

        if isinstance(__pattern, NeverPattern):
            return self

        return OrPattern(self, __pattern)

    @final
    def __get__(self, __instance: Pattern, __owner: type[Pattern]) -> Self:
        return ThenPattern(__instance[self.name], self)

    @final
    def __set_name__(self, __owner: type[Pattern], __name: str) -> None:
        self.name = __name


@final
class NeverPattern(Pattern):
    def apply(self, document: Document) -> Iterable[None]:
        return iter(())

    def __getitem__(self, __key: int | str) -> Self:
        return self

    def __repr__(self) -> str:
        return type(self).__name__


@final
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

    def __getattr__(self, __name: str) -> Any:
        attr = getattr(self.__pattern, __name)

        if isinstance(attr, Pattern):
            return MaybePattern(attr)

        return attr

    def __repr__(self) -> str:
        subrepr = repr(self.__pattern).split("\n")
        subrepr = "\n".join("    " + line for line in subrepr)
        return f"{type(self).__name__}:\n{subrepr}"


@final
class OrPattern(Pattern, Generic[_T1, _T2]):
    def __init__(self, left_pattern: _T1, right_pattern: _T2) -> None:
        self.__left_pattern = left_pattern
        self.__right_pattern = right_pattern

    def apply(self, document: Document) -> Iterable[Document]:
        yield from self.__left_pattern.apply(document)
        yield from self.__right_pattern.apply(document)

    def __getitem__(self, __key: int | str) -> Self:
        return OrPattern(self.__left_pattern[__key], self.__right_pattern[__key])

    def __getattr__(self, __name: str) -> Any:
        left_attr = getattr(self.__left_pattern, __name, None)
        right_attr = getattr(self.__right_pattern, __name, None)

        if isinstance(left_attr, Pattern) and isinstance(right_attr, Pattern):
            return OrPattern(left_attr, right_attr)

        if left_attr is not None:
            return left_attr

        if right_attr is not None:
            return right_attr

        raise AttributeError(__name)

    def __repr__(self) -> str:
        left_repr = repr(self.__left_pattern).split("\n")
        right_repr = repr(self.__right_pattern).split("\n")

        left_repr = "\n".join("    " + line for line in left_repr)
        right_repr = "\n".join("    " + line for line in right_repr)

        return f"{type(self).__name__}:\n{left_repr}\n{right_repr}"


@final
class ThenPattern(Pattern, Generic[_T1, _T2]):
    def __init__(self, left_pattern: _T1, right_pattern: _T2) -> None:
        self.__left_pattern = left_pattern
        self.__right_pattern = right_pattern

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__left_pattern.apply(document):
            yield from self.__right_pattern.apply(result)

    def __getitem__(self, __key: int | str) -> Self:
        return ThenPattern(self.__left_pattern, self.__right_pattern[__key])

    def __getattr__(self, __name: str) -> Any:
        attr = getattr(self.__right_pattern, __name)

        if isinstance(attr, Pattern):
            return ThenPattern(self.__left_pattern, attr)

        return attr

    def __repr__(self) -> str:
        left_repr = repr(self.__left_pattern).split("\n")
        right_repr = repr(self.__right_pattern).split("\n")

        left_repr = "\n".join("    " + line for line in left_repr)
        right_repr = "\n".join("    " + line for line in right_repr)

        return f"{type(self).__name__}:\n{left_repr}\n{right_repr}"
