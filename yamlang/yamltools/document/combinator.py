from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic
from typing import TypeVar
from typing import cast

from yamlang.yamltools.document.document import Document

_T = TypeVar("_T", bound=Document)


@dataclass
class FoldMap(Generic[_T]):
    on_none: Callable[[None], _T] | None = None
    on_bool: Callable[[bool], _T] | None = None
    on_int: Callable[[int], _T] | None = None
    on_float: Callable[[float], _T] | None = None
    on_str: Callable[[str], _T] | None = None
    on_list: Callable[[list[_T]], _T] | None = None
    on_dict: Callable[[dict[str, _T]], _T] | None = None
    default: Callable[[Document], _T] = lambda document: cast(_T, document)

    def __call__(self, document: Document) -> _T:
        if document is None and self.on_none:
            return self.on_none(document)

        if isinstance(document, bool) and self.on_bool:
            return self.on_bool(document)

        if isinstance(document, int) and self.on_int:
            return self.on_int(document)

        if isinstance(document, float) and self.on_float:
            return self.on_float(document)

        if isinstance(document, str) and self.on_str:
            return self.on_str(document)

        if isinstance(document, list):
            if self.on_list:
                return self.on_list([self(x) for x in document])
            else:
                return self.default([self(x) for x in document])

        if isinstance(document, dict):
            if self.on_dict:
                return self.on_dict({k: self(v) for k, v in document.items()})
            else:
                return self.default({k: self(v) for k, v in document.items()})

        return self.default(document)
