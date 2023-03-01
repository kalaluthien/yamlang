from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from copy import copy
from functools import wraps
from types import MethodType
from typing import Any, Generic, Self, final, overload

from typing_extensions import TypeVar

from yamlang.yamltools import Document

_T1 = TypeVar("_T1", bound="Pattern", default="Pattern", infer_variance=True)
_T2 = TypeVar("_T2", bound="Pattern", default="Pattern", infer_variance=True)
_T3 = TypeVar("_T3", bound=Document, default=Document, infer_variance=True)


class Pattern(ABC):
    @abstractmethod
    def apply(self, document: Document) -> Iterable[Document]:
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, __key: int | str) -> Self:
        raise NotImplementedError

    @abstractmethod
    def __copy__(self) -> Self:
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
            old_apply = self.apply

            def new_apply(self: Pattern, document: Document) -> Iterable[Document]:
                results = iter(old_apply(document))

                try:
                    yield next(results)
                except StopIteration:
                    yield None
                    return

                yield from results

            return self.updated(new_apply)

        return OrPattern(self, __pattern)

    @final
    def __get__(self, __instance: Pattern, __owner: type[Pattern]) -> Self:
        return ThenPattern(__instance[self.name], self)

    @final
    def __set_name__(self, __owner: type[Pattern], __name: str) -> None:
        self.name = __name

    @final
    def __lshift__(self, __function: Callable[[Document], Document]) -> Self:
        old_apply = self.apply

        def new_apply(self: Pattern, document: Document) -> Iterable[Document]:
            yield from old_apply(__function(document))

        return self.updated(new_apply)

    @final
    def __rshift__(self, __function: Callable[[Document], Document]) -> Self:
        old_apply = self.apply

        def new_apply(self: Pattern, document: Document) -> Iterable[Document]:
            for result in old_apply(document):
                yield __function(result)

        return self.updated(new_apply)

    @final
    def updated(
        self,
        new_apply: Callable[[Self, Document], Iterable[Document]],
    ) -> Self:
        new = copy(self)
        if hasattr(self, "name"):
            setattr(new, "name", getattr(self, "name"))
        new.apply = MethodType(new_apply, new)
        return new

    @final
    @staticmethod
    def lift(
        old_apply: Callable[[_T1, Document], Iterable[_T3]],
    ) -> Callable[[_T1, Document], Iterable[_T3]]:
        @wraps(old_apply)
        def new_apply(self: _T1, document: Document) -> Iterable[_T3]:
            if isinstance(document, list):
                for item in document:
                    yield from old_apply(self, item)
                return

            yield from old_apply(self, document)

        return new_apply


@final
class NeverPattern(Pattern):
    def apply(self, document: Document) -> Iterable[None]:
        return iter(())

    def __getitem__(self, __key: int | str) -> Self:
        return self

    def __copy__(self) -> Self:
        return NeverPattern()

    def __repr__(self) -> str:
        return type(self).__name__


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

    def __copy__(self) -> Self:
        return OrPattern(self.__left_pattern, self.__right_pattern)

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

    def __copy__(self) -> Self:
        return ThenPattern(self.__left_pattern, self.__right_pattern)

    def __repr__(self) -> str:
        left_repr = repr(self.__left_pattern).split("\n")
        right_repr = repr(self.__right_pattern).split("\n")

        left_repr = "\n".join("    " + line for line in left_repr)
        right_repr = "\n".join("    " + line for line in right_repr)

        return f"{type(self).__name__}:\n{left_repr}\n{right_repr}"
