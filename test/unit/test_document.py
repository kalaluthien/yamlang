from yamlang.yamltools import Document
from yamlang.yamltools import FoldMap
from yamlang.yamltools import Map
from yamlang.yamltools import load


def test_load_yaml() -> None:
    document = load(r"{foo: {bar: baz, qux: [12, 34]}, ham: null}")

    assert document == {"foo": {"bar": "baz", "qux": [12, 34]}, "ham": None}


def test_map_yaml() -> None:
    document: Document = {"foo": "bar", "baz": 1}

    def value_to_upper(x: dict[str, Document]) -> dict[str, Document]:
        return {k: v.upper() for k, v in x.items() if isinstance(v, str)}

    result = Map(on_object=value_to_upper)(document)

    assert result == {"foo": "BAR"}


def test_fold_map_yaml() -> None:
    document: Document = {
        "foo": {"bar": 1, "qux": 2, "ham": [3, 4], "egg": {"foo": 5, "bar": 6}}
    }

    def increment(x: int) -> Document:
        return x + 1

    result = FoldMap(on_integer=increment)(document)

    assert result == {
        "foo": {"bar": 2, "qux": 3, "ham": [4, 5], "egg": {"foo": 6, "bar": 7}}
    }
