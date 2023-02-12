from __future__ import annotations

from pathlib import Path

import yaml


Document = None | bool | int | float | str | list["Document"] | dict[str, "Document"]


def load(source: str | Path) -> Document:
    # Interpret null as a string "null".
    def constructor_null(loader: yaml.Loader, node: yaml.Node) -> Document:
        return loader.construct_scalar(node)

    yaml.add_constructor("tag:yaml.org,2002:null", constructor_null)
    yaml.add_constructor("tag:yaml.org,2002:python/none", constructor_null)

    # Reject boolean values that are not "true" or "false".
    def constructor_bool(loader: yaml.Loader, node: yaml.Node) -> Document:
        if (value := str(node.value)) == "true":
            return True
        elif value == "false":
            return False

        return loader.construct_scalar(node)

    yaml.add_constructor("tag:yaml.org,2002:bool", constructor_bool)
    yaml.add_constructor("tag:yaml.org,2002:python/bool", constructor_bool)

    # Load the text from the source if it is a Path.
    if isinstance(source, Path):
        if not source.is_file():
            raise FileNotFoundError(f"File not found: {source}")

        with source.open() as file:
            text = file.read()
    else:
        text = source

    # Load the document from the text.
    document: Document = yaml.load(text, Loader=yaml.FullLoader)

    return document
