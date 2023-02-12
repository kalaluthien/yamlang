from abc import abstractmethod
from collections.abc import Iterable, Mapping
from itertools import product
from typing import Generic, TypeVar, cast

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import FailPattern, Pattern

_T = TypeVar("_T", bound=Pattern)


class MappingPattern(Pattern, Generic[_T]):
    @abstractmethod
    def __getitem__(self, key: str) -> _T:
        raise NotImplementedError


class DictPattern(MappingPattern[_T]):
    def __init__(self, patterns: Mapping[str, _T]) -> None:
        self.__patterns = dict(patterns)

    def apply(self, document: Document) -> Iterable[Document]:
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

    def __getitem__(self, key: str) -> _T:
        if key not in self.__patterns:
            return FailPattern[_T]()

        return DictPattern.GetItemPattern(self, key) >> self.__patterns[key]

    class GetItemPattern(Pattern):
        def __init__(self, pattern: MappingPattern[_T], key: str) -> None:
            self.__pattern = pattern
            self.__key = key

        def apply(self, document: Document) -> Iterable[Document]:
            for result in self.__pattern.apply(document):
                if isinstance(result, dict) and self.__key in result:
                    yield result[self.__key]
