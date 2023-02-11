from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar
from typing import cast

import yaml
from yaml.constructor import ConstructorError


_DocumentT = TypeVar("_DocumentT", bound="Document")
_DocumentF = None | bool | int | float | str | list[_DocumentT] | dict[str, _DocumentT]
Document = _DocumentF["Document"]

_T1 = TypeVar("_T1", bound=Document)
_T2 = TypeVar("_T2", bound=Document)


def load(source: str | Path) -> Document:
    # Add custom constructors for YamLang.
    def constructor_bool(loader: yaml.Loader, node: yaml.Node) -> Document:
        if (value := str(node.value).lower()) == "true":
            return True
        elif value == "false":
            return False
        else:
            return loader.construct_scalar(node)

    # Fix default constructors for boolean.
    yaml.add_constructor("tag:yaml.org,2002:bool", constructor_bool)
    yaml.add_constructor("tag:yaml.org,2002:python/bool", constructor_bool)

    # Load the text from the source.
    if isinstance(source, Path):
        with source.open() as file:
            text = file.read()
    else:
        text = source

    # Load the document from the text.
    document = cast(Document, yaml.load(text, Loader=yaml.FullLoader))

    return document


@dataclass
class Combinator(ABC, Generic[_T1, _T2]):
    on_null: Callable[[None], _T2] | None = None
    on_boolean: Callable[[bool], _T2] | None = None
    on_integer: Callable[[int], _T2] | None = None
    on_float: Callable[[float], _T2] | None = None
    on_string: Callable[[str], _T2] | None = None
    on_array: Callable[[list[_T1]], _T2] | None = None
    on_object: Callable[[dict[str, _T1]], _T2] | None = None
    default: Callable[[_DocumentF[_T1]], _T2] = lambda document: cast(_T2, document)

    @abstractmethod
    def __call__(self, document: Document) -> _T2:
        raise NotImplementedError


@dataclass
class Map(Combinator[Document, _T1]):
    if TYPE_CHECKING:
        on_null: Callable[[None], _T1]
        on_boolean: Callable[[bool], _T1]
        on_integer: Callable[[int], _T1]
        on_float: Callable[[float], _T1]
        on_string: Callable[[str], _T1]
        on_array: Callable[[list[Document]], _T1]
        on_object: Callable[[dict[str, Document]], _T1]
        default: Callable[[Document], _T1]

    def __call__(self, document: Document) -> _T1:
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

        if isinstance(document, list) and self.on_array:
            return self.on_array(document)

        if isinstance(document, dict) and self.on_object:
            return self.on_object(document)

        return self.default(document)


@dataclass
class FoldMap(Combinator[_T1, _T1]):
    if TYPE_CHECKING:
        on_null: Callable[[None], _T1]
        on_boolean: Callable[[bool], _T1]
        on_integer: Callable[[int], _T1]
        on_float: Callable[[float], _T1]
        on_string: Callable[[str], _T1]
        on_array: Callable[[list[_T1]], _T1]
        on_object: Callable[[dict[str, _T1]], _T1]
        default: Callable[[_DocumentF[_T1]], _T1]

    def __call__(self, document: Document) -> _T1:
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
