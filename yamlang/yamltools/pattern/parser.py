from collections.abc import Iterable

from yamlang.yamltools import Document, load
from yamlang.yamltools.pattern.pattern import Pattern


class Parser:
    def __init__(self, pattern: Pattern) -> None:
        self.__pattern = pattern

    def parse(self, path: str) -> Iterable[Document]:
        yield from self.__pattern.apply(load(path))
