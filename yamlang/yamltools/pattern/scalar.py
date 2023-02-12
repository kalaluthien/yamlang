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

        if isinstance(document, dict):
            for value in document.values():
                yield from self.apply(value)
            return

        if not isinstance(document, bool):
            return

        if self.value is None or document == self.value:
            yield document


class IntPattern(Pattern):
    def __init__(self, value: int | None = None) -> None:
        self.value = value

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if isinstance(document, dict):
            for value in document.values():
                yield from self.apply(value)
            return

        if not isinstance(document, int):
            return

        if isinstance(document, bool):
            return

        if self.value is None or document == self.value:
            yield document


class FloatPattern(Pattern):
    def __init__(self, value: float | None = None) -> None:
        self.value = value

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if isinstance(document, dict):
            for value in document.values():
                yield from self.apply(value)
            return

        if not isinstance(document, float):
            return

        if self.value is None or document == self.value:
            yield document


class StrPattern(Pattern):
    def __init__(self, value: str | None = None) -> None:
        self.value = value

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if isinstance(document, dict):
            for value in document.values():
                yield from self.apply(value)
            return

        if not isinstance(document, str):
            return

        if self.value is None or document == self.value:
            yield document
