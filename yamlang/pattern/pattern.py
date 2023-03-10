from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Iterable
from copy import copy
from functools import wraps
from types import MethodType
from typing import Self
from typing import final
from typing import overload

from typing_extensions import TypeVar

from yamlang.yamltools import Document

_T1 = TypeVar("_T1", bound="Pattern", default="Pattern", infer_variance=True)
_T2 = TypeVar("_T2", bound=Document, default=Document, infer_variance=True)


class Pattern(ABC):
    @abstractmethod
    def apply(self, document: Document) -> Iterable[Document]:
        raise NotImplementedError

    def __getitem__(self, __key: int | str) -> Pattern:
        if isinstance(__key, int):

            def new_apply(_, document: Document) -> Iterable[Document]:
                for result in self.apply(document):
                    if isinstance(result, list):
                        if -len(result) <= __key < len(result):
                            yield result[__key]

        elif isinstance(__key, str):

            def new_apply(_, document: Document) -> Iterable[Document]:
                for result in self.apply(document):
                    if isinstance(result, dict):
                        if __key in result:
                            yield result[__key]

        else:

            def new_apply(_, document: Document) -> Iterable[Document]:
                yield from ()

        return self._updated(new_apply)

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

            def new_apply(_, document: Document) -> Iterable[Document]:
                results = iter(self.apply(document))

                try:
                    yield next(results)
                except StopIteration:
                    yield None
                    return

                yield from results

        else:

            def new_apply(_, document: Document) -> Iterable[Document]:
                yield from self.apply(document)
                yield from __pattern.apply(document)

        return self._updated(new_apply)

    @final
    def __get__(self, __instance: Pattern, __owner: type[Pattern]) -> Self:
        parent = __instance[getattr(self, "name")]

        def new_apply(_, document: Document) -> Iterable[Document]:
            for result in parent.apply(document):
                yield from self.apply(result)

        return self._updated(new_apply)

    @final
    def __set_name__(self, __owner: type, __name: str) -> None:
        if issubclass(__owner, Pattern):
            self.name = __name

    @final
    def __lshift__(self, __function: Callable[[Document], Document]) -> Self:
        def new_apply(_, document: Document) -> Iterable[Document]:
            yield from self.apply(__function(document))

        return self._updated(new_apply)

    @final
    def __rshift__(self, __function: Callable[[Document], Document]) -> Self:
        def new_apply(_, document: Document) -> Iterable[Document]:
            for result in self.apply(document):
                yield __function(result)

        return self._updated(new_apply)

    @final
    def _updated(
        self,
        apply: Callable[[Self, Document], Iterable[Document]],
    ) -> Self:
        new = copy(self)
        if "name" in self.__dict__:
            new.name = self.name
        new.apply = MethodType(apply, new)
        return new

    @final
    @staticmethod
    def lift(
        apply: Callable[[_T1, Document], Iterable[_T2]],
    ) -> Callable[[_T1, Document], Iterable[_T2]]:
        @wraps(apply)
        def new_apply(self: _T1, document: Document) -> Iterable[_T2]:
            if isinstance(document, list):
                for item in document:
                    yield from apply(self, item)
                return

            yield from apply(self, document)

        return new_apply
