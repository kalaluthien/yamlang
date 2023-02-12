from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic
from typing import TypeVar
from typing import cast

from yamlang.yamltools.document.document import Document

_T = TypeVar("_T", bound=Document)


@dataclass
class FoldMap(Generic[_T]):
    on_null: Callable[[None], _T] | None = None
    on_boolean: Callable[[bool], _T] | None = None
    on_integer: Callable[[int], _T] | None = None
    on_float: Callable[[float], _T] | None = None
    on_string: Callable[[str], _T] | None = None
    on_array: Callable[[list[_T]], _T] | None = None
    on_object: Callable[[dict[str, _T]], _T] | None = None
    default: Callable[[Document], _T] = lambda document: cast(_T, document)

    def __call__(self, document: Document) -> _T:
        if document is None and self.on_null:
            return self.on_null(document)

        if isinstance(document, bool) and self.on_boolean:
            return self.on_boolean(document)

        if isinstance(document, int) and self.on_integer:
            return self.on_integer(document)

        if isinstance(document, float) and self.on_float:
            return self.on_float(document)

        if isinstance(document, str) and self.on_string:
            return self.on_string(document)

        if isinstance(document, list):
            if self.on_array:
                return self.on_array([self(x) for x in document])
            else:
                return self.default([self(x) for x in document])

        if isinstance(document, dict):
            if self.on_object:
                return self.on_object({k: self(v) for k, v in document.items()})
            else:
                return self.default({k: self(v) for k, v in document.items()})

        return self.default(document)
