from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import product
from typing import Generic, Self, cast, overload

from typing_extensions import TypeVar

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import NeverPattern, Pattern

_T1 = TypeVar("_T1", bound=Pattern, default=Pattern, infer_variance=True)


class ListPattern(Pattern, Generic[_T1]):
    def __init__(self, pattern: _T1) -> None:
        self.__pattern = pattern

    def apply(self, document: Document) -> Iterable[list[Document]]:
        if isinstance(document, list):
            for items in product(*(self.__pattern.apply(item) for item in document)):
                yield list(items)

    @overload
    def __getitem__(self, __key: int) -> _T1:
        ...

    @overload
    def __getitem__(self, __key: str) -> NeverPattern:
        ...

    def __getitem__(self, __key: int | str) -> _T1 | NeverPattern:
        return cast(_T1, GetPattern[_T1](self, __key))


class DictPattern(Pattern, Generic[_T1]):
    def __init__(self, patterns: Mapping[str, _T1]) -> None:
        self.__patterns = dict(patterns)

    def apply(self, document: Document) -> Iterable[dict[str, Document]]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, dict):
            return

        if not all(key in document for key in self.__patterns):
            return

        for values in product(
            *(
                pattern.apply(value)
                for key, value in document.items()
                if (pattern := self.__patterns.get(key))
            )
        ):
            yield dict(zip(self.__patterns.keys(), values))

    @overload
    def __getitem__(self, __key: str) -> _T1:
        ...

    @overload
    def __getitem__(self, __key: int) -> NeverPattern:
        ...

    def __getitem__(self, __key: int | str) -> _T1 | NeverPattern:
        return cast(_T1, GetPattern[_T1](self, __key))


class GetPattern(Pattern, Generic[_T1]):
    def __init__(
        self,
        pattern: ListPattern[_T1] | DictPattern[_T1],
        *key: int | str,
    ) -> None:
        self.__pattern = pattern
        self.__keys = key

    def apply(self, document: Document) -> Iterable[Document]:
        for result in self.__pattern.apply(document):
            for key in self.__keys:
                if isinstance(key, int):
                    if isinstance(result, list) and (-len(result) <= key < len(result)):
                        result = result[key]
                    else:
                        break
                elif isinstance(key, str):
                    if isinstance(result, dict) and key in result:
                        result = result[key]
                    else:
                        break
                else:
                    return
            else:
                yield result

    def __getitem__(self, __key: int | str) -> Self:
        return GetPattern(self.__pattern, *self.__keys, __key)
