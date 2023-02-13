from collections.abc import Iterable

from yamlang.yamltools import Document
from yamlang.yamltools.pattern.pattern import Pattern


class BoolPattern(Pattern):
    def __init__(self, value: bool | None = None) -> None:
        self.value = value

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, bool):
            return

        if self.value is None or document == self.value:
            yield document

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class IntPattern(Pattern):
    def __init__(self, value: int | None = None) -> None:
        self.value = value

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, int):
            return

        if isinstance(document, bool):
            return

        if self.value is None or document == self.value:
            yield document

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class FloatPattern(Pattern):
    def __init__(self, value: float | None = None) -> None:
        self.value = value

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, float):
            return

        if self.value is None or document == self.value:
            yield document

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class StrPattern(Pattern):
    def __init__(self, value: str | None = None) -> None:
        self.value = value

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, str):
            return

        if self.value is None or document == self.value:
            yield document

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"
