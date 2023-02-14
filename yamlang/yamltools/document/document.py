from __future__ import annotations

import datetime
from pathlib import Path

import yaml

Document = (
    None
    | bool
    | int
    | float
    | str
    | datetime.date
    | datetime.datetime
    | list["Document"]
    | dict[str, "Document"]
)


def load(source: str | Path) -> Document:
    # Interpret "null" as a string "null".
    def constructor_null(loader: yaml.Loader, node: yaml.Node) -> Document:
        if (value := loader.construct_scalar(node)) == "null":
            return value

    yaml.add_constructor("tag:yaml.org,2002:null", constructor_null)

    # Reject boolean values that are not "true" or "false".
    def constructor_bool(loader: yaml.Loader, node: yaml.Node) -> Document:
        if (value := str(node.value)) == "true":
            return True
        elif value == "false":
            return False

        return loader.construct_scalar(node)

    yaml.add_constructor("tag:yaml.org,2002:bool", constructor_bool)

    # Get rid of some keyword tags. For now, we don't need them.
    def constructor_keyword(loader: yaml.Loader, node: yaml.Node) -> Document:
        node.value = f"{node.tag} {node.value}".lstrip("!")
        return loader.construct_scalar(node)

    for keyword in ["def"]:
        yaml.add_constructor(f"!{keyword}", constructor_keyword)

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


def dump(document: Document) -> str:
    maybe_text = yaml.dump(document, sort_keys=False, default_flow_style=False)
    text = str(maybe_text) if maybe_text else ""

    return text
