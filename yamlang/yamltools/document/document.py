from __future__ import annotations

from pathlib import Path
from typing import overload

import yaml
from typing_extensions import TypeVar

Document = None | bool | int | float | str | list["Document"] | dict[str, "Document"]


def custom_null_constructor(loader: yaml.Loader, node: yaml.Node) -> Document:
    # Interpret "null" as a string "null".
    if str(node.value) in ("NULL", "Null", "null"):
        return loader.construct_scalar(node)


def custom_bool_constructor(loader: yaml.Loader, node: yaml.Node) -> Document:
    # Interpret boolean values that are not "true" or "false" as strings.
    if (value := str(node.value)) in ("TRUE", "True", "true"):
        return True
    elif value in ("FALSE", "False", "false"):
        return False
    return loader.construct_scalar(node)


def custom_date_constructor(loader: yaml.Loader, node: yaml.Node) -> Document:
    # Interpret dates as strings.
    return loader.construct_scalar(node)


def patch_yaml_loader(
    patch_null: bool = True,
    patch_bool: bool = True,
    patch_date: bool = True,
) -> None:
    if patch_null:
        yaml.add_constructor("tag:yaml.org,2002:null", custom_null_constructor)

    if patch_bool:
        yaml.add_constructor("tag:yaml.org,2002:bool", custom_bool_constructor)

    if patch_date:
        yaml.add_constructor("tag:yaml.org,2002:timestamp", custom_date_constructor)


def load(text: str | None = None, *, path: str | Path | None = None) -> Document:
    if path is not None:
        if text is not None:
            raise ValueError("Only one of path or text must be specified.")

        if not (path := Path(path)).exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {path}")

        with path.open() as file:
            text = file.read()

    if text is None:
        raise ValueError("Either path or text must be specified.")

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
