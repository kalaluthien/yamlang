from __future__ import annotations

from collections.abc import Iterable
from itertools import product
from typing import Generic, Self, cast, final, overload

from typing_extensions import TypeVar

from yamlang.pattern.pattern import NeverPattern, Pattern
from yamlang.yamltools import Document

_T = TypeVar("_T", bound=Pattern, default=Pattern, infer_variance=True)


@final
class ListPattern(Pattern, Generic[_T]):
    def __init__(self, pattern: _T) -> None:
        self.__pattern = pattern

    def apply(self, document: Document) -> Iterable[list[Document]]:
        if isinstance(document, list):
            for items in product(*(self.__pattern.apply(item) for item in document)):
                yield list(items)

    @overload
    def __getitem__(self, __key: int) -> _T:
        ...

    @overload
    def __getitem__(self, __key: str) -> NeverPattern:
        ...

    def __getitem__(self, __key: int | str) -> _T | NeverPattern:
        return cast(_T, AtPattern[_T](self, __key))

    def __copy__(self) -> Self:
        return ListPattern(self.__pattern)

    def __repr__(self) -> str:
        subrepr = repr(self.__pattern).split("\n")
        subrepr = "\n".join("    " + line for line in subrepr)
        return f"{type(self).__name__}:\n{subrepr}"


class DictPattern(Pattern, Generic[_T]):
    __patterns: dict[str, Pattern] = {}

    @final
    def __init__(self, **patterns: _T) -> None:
        if default_pattern := type(self).__patterns:
            self.__patterns = dict(default_pattern)
            for key, pattern in patterns.items():
                if key in self.__patterns:
                    self.__patterns[key] = pattern
        else:
            self.__patterns = dict(patterns)

    def __init_subclass__(cls) -> None:
        cls.__patterns = {
            key: p for key, p in vars(cls).items() if isinstance(p, Pattern)
        }

    @final
    @Pattern.lift
    def apply(self, document: Document) -> Iterable[dict[str, Document]]:
        if not isinstance(document, dict):
            return

        for values in product(
            *(p.apply(document.get(key)) for key, p in self.__patterns.items())
        ):
            yield dict(zip(self.__patterns.keys(), values))

    @overload
    def __getitem__(self, __key: str) -> _T:
        ...

    @overload
    def __getitem__(self, __key: int) -> NeverPattern:
        ...

    @final
    def __getitem__(self, __key: int | str) -> _T | NeverPattern:
        return cast(_T, AtPattern[_T](self, __key))

    @final
    def __copy__(self) -> Self:
        return type(self)(**self.__patterns)

    @final
    def __repr__(self) -> str:
        subreprs: list[str] = []
        for key, pattern in self.__patterns.items():
            subrepr = repr(pattern).split("\n")
            subrepr = "\n".join("    " + line for line in subrepr)
            subreprs.append(f"[{key}]:\n{subrepr}")
        return f"{type(self).__name__}:\n" + "\n".join("  " + line for line in subreprs)


@final
class AtPattern(Pattern, Generic[_T]):
    def __init__(
        self,
        pattern: ListPattern[_T] | DictPattern[_T],
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
        return AtPattern(self.__pattern, *self.__keys, __key)

    def __copy__(self) -> Self:
        return AtPattern(self.__pattern, *self.__keys)

    def __repr__(self) -> str:
        subrepr = repr(self.__pattern).split("\n")
        subrepr = "\n".join("    " + line for line in subrepr)
        keyrepr = "][".join(str(key) for key in self.__keys)
        return f"{type(self).__name__}[{keyrepr}]:\n{subrepr}"
