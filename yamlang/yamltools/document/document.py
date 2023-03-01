from __future__ import annotations

from pathlib import Path
from typing import overload

import yaml
from typing_extensions import TypeVar

Document = (
    None | bool | int | float | str | list["Document"] | dict[str, "Document"]
)


def null_constructor(
    loader: yaml.Loader | yaml.FullLoader | yaml.UnsafeLoader,
    node: yaml.Node,
) -> Document:
    if not isinstance(node, yaml.ScalarNode):
        raise yaml.constructor.ConstructorError(
            None,
            None,
            f"expected a scalar node, but found {type(node)}",
            node.start_mark,
        )

    # Interpret "null" as a string "null".
    if str(node.value) in ("NULL", "Null", "null"):
        return loader.construct_scalar(node)


def bool_constructor(
    loader: yaml.Loader | yaml.FullLoader | yaml.UnsafeLoader,
    node: yaml.Node,
) -> Document:
    if not isinstance(node, yaml.ScalarNode):
        raise yaml.constructor.ConstructorError(
            None,
            None,
            f"expected a scalar node, but found {type(node)}",
            node.start_mark,
        )

    # Interpret boolean values that are not "true" or "false" as strings.
    if (value := str(node.value)) in ("TRUE", "True", "true"):
        return True
    elif value in ("FALSE", "False", "false"):
        return False

    return loader.construct_scalar(node)


def date_constructor(
    loader: yaml.Loader | yaml.FullLoader | yaml.UnsafeLoader,
    node: yaml.Node,
) -> Document:
    if not isinstance(node, yaml.ScalarNode):
        raise yaml.constructor.ConstructorError(
            None,
            None,
            f"expected a scalar node, but found {type(node)}",
            node.start_mark,
        )

    # Interpret dates as strings.
    return loader.construct_scalar(node)


def patch_yaml_loader(
    patch_null: bool = True,
    patch_bool: bool = True,
    patch_date: bool = True,
) -> None:
    if patch_null:
        yaml.add_constructor("tag:yaml.org,2002:null", null_constructor)

    if patch_bool:
        yaml.add_constructor("tag:yaml.org,2002:bool", bool_constructor)

    if patch_date:
        yaml.add_constructor("tag:yaml.org,2002:timestamp", date_constructor)


def load_from_file(document: Document) -> Document:
    if isinstance(document, list):
        return [load_from_file(item) for item in document]

    path = Path(str(document))

    if path.exists() or not path.is_file():
        return

    with path.open() as file:
        return yaml.load(file.read(), Loader=yaml.FullLoader)


def load_from_text(document: Document) -> Document:
    if isinstance(document, list):
        return [load_from_text(item) for item in document]

    text = str(document)

    return yaml.load(text, Loader=yaml.FullLoader)


_T = TypeVar("_T", infer_variance=True)


@overload
def dump(document: Document) -> str:
    ...


@overload
def dump(document: Document, *, default: _T) -> str | _T:
    ...


def dump(document: Document, *, default: _T | str = "") -> str | _T:
    maybe_text = yaml.dump(document, sort_keys=False, default_flow_style=False)

    return str(maybe_text) if maybe_text else default
