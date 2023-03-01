from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Generic, Self, final

from typing_extensions import TypeVar

from yamlang.pattern.pattern import NeverPattern, Pattern, lift
from yamlang.yamltools import Document

_T = TypeVar("_T", None, bool, int, float, str, default=None, infer_variance=True)


class ScalarPattern(Pattern, Generic[_T]):
    @final
    def __init__(self, value: _T | None = None) -> None:
        self._value = value

    @abstractmethod
    def apply(self, document: Document) -> Iterable[_T]:
        raise NotImplementedError

    @final
    def __getitem__(self, __key: int | str) -> NeverPattern:
        return NeverPattern()

    @final
    def __copy__(self) -> Self:
        return type(self)(self._value)

    @final
    def __repr__(self) -> str:
        return f"{type(self).__name__}: {self._value!r}"


@final
class BoolPattern(ScalarPattern[bool]):
    @lift
    def apply(self, document: Document) -> Iterable[bool]:
        if not isinstance(document, bool):
            return

        if self._value is None or document == self._value:
            yield document


@final
class IntPattern(ScalarPattern[int]):
    @lift
    def apply(self, document: Document) -> Iterable[int]:
        if not isinstance(document, int):
            return

        if isinstance(document, bool):
            return

        if self._value is None or document == self._value:
            yield document


@final
class FloatPattern(ScalarPattern[float]):
    @lift
    def apply(self, document: Document) -> Iterable[float]:
        if not isinstance(document, float):
            return

        if self._value is None or document == self._value:
            yield document


@final
class StrPattern(ScalarPattern[str]):
    @lift
    def apply(self, document: Document) -> Iterable[str]:
        if not isinstance(document, str):
            return

        if self._value is None or document == self._value:
            yield document
