from collections.abc import Iterable
from typing import Generic

from typing_extensions import TypeVar

from yamlang.yamltools import Document, load
from yamlang.yamltools.pattern.pattern import Pattern

_T = TypeVar("_T", bound=Pattern, default=Pattern, infer_variance=True)


class Parser(Generic[_T]):
    def __init__(self, pattern: _T) -> None:
        self.__pattern = pattern

    def parse(self, path: str) -> Iterable[Document]:
        yield from self.__pattern.apply(load(path))
