from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any, Generic, Self, cast, final

from typing_extensions import TypeVar

from yamlang.pattern.pattern import Pattern
from yamlang.yamltools import Document, load

_T1 = TypeVar("_T1", bound=Pattern, default=Pattern, infer_variance=True)


@final
class ParsePattern(Pattern, Generic[_T1]):
    def __init__(self, pattern: _T1, from_file: bool) -> None:
        self.__pattern = pattern
        self.__from_file = from_file

    @classmethod
    def from_file(cls, pattern: _T1) -> _T1:
        return cast(_T1, cls(pattern, from_file=True))

    @classmethod
    def from_text(cls, pattern: _T1) -> _T1:
        return cast(_T1, cls(pattern, from_file=False))

    def apply(self, document: Document) -> Iterable[Document]:
        if isinstance(document, list):
            for item in document:
                yield from self.apply(item)
            return

        if not isinstance(document, str):
            return

        if self.__from_file:
            if Path(document).exists():
                yield from self.__pattern.apply(load(path=document))
            return

        yield from self.__pattern.apply(load(text=document))

    def __getitem__(self, __key: int | str) -> Self:
        return ParsePattern(self.__pattern[__key], self.__from_file)

    def __getattr__(self, __name: str) -> Any:
        attr = getattr(self.__pattern, __name)

        if isinstance(attr, Pattern):
            return ParsePattern(attr, self.__from_file)

        return attr

    def __copy__(self) -> Self:
        return ParsePattern(self.__pattern, self.__from_file)

    def __repr__(self) -> str:
        subrepr = repr(self.__pattern).split("\n")
        subrepr = "\n".join("    " + line for line in subrepr)
        return f"{type(self).__name__}:\n{subrepr}"
