from abc import abstractmethod
from collections.abc import Iterable
from collections.abc import Mapping
from itertools import product
from typing import Generic
from typing import TypeVar

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import Pattern

_T = TypeVar("_T", bound=Pattern)


class MappingPattern(Pattern, Generic[_T]):
    @abstractmethod
    def __getitem__(self, key: str) -> _T:
        raise NotImplementedError


class DictPattern(MappingPattern[_T]):
    def __init__(self, patterns: Mapping[str, _T]) -> None:
        self.patterns = dict(patterns)

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, dict):
            return

        if not all(key in document for key in self.patterns):
            return

        for values in product(
            *(
                pattern.apply(value)
                for key, value in document.items()
                if (pattern := self.patterns.get(key))
            )
        ):
            yield dict(zip(self.patterns.keys(), values))

    def __getitem__(self, key: str) -> _T:
        return DictPattern.GetItemPattern(self, key) >> self.patterns[key]

    class GetItemPattern(Pattern):
        def __init__(self, pattern: MappingPattern[_T], key: str) -> None:
            self.pattern = pattern
            self.key = key

        def apply(self, document: Document) -> Iterable[Document]:
            for result in self.pattern.apply(document):
                if isinstance(result, dict) and self.key in result:
                    yield result[self.key]
