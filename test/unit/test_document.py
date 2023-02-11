from yamlang.yamltools import Document
from yamlang.yamltools import FoldMap
from yamlang.yamltools import Map
from yamlang.yamltools import load


def test_load_yaml() -> None:
    document = load(r"{foo: {bar: baz, qux: [12, 34]}}")
    assert document == {"foo": {"bar": "baz", "qux": [12, 34]}}

    document = load(r"{foo: null, bar: yes, baz: off, on: true}")
    assert document == {"foo": None, "bar": "yes", "baz": "off", "on": True}

    document = load(r"{foo: &A {bar: 2.0, baz: 3.0}, qux: *A}")
    assert document == {"foo": {"bar": 2.0, "baz": 3.0}, "qux": {"bar": 2.0, "baz": 3.0}}


def test_map_yaml() -> None:
    def value_to_upper(x: dict[str, Document]) -> dict[str, Document]:
        return {k: v.upper() for k, v in x.items() if isinstance(v, str)}

    map = Map[Document](on_object=value_to_upper)

    document = {"foo": "bar", "baz": 1}
    assert map(document) == {"foo": "BAR"}

    document = {"foo": ["bar", "baz"], "ham": "egg"}
    assert map(document) == {"ham": "EGG"}


def test_fold_map_yaml() -> None:
    def increment(x: int) -> Document:
        return x + 1

    fold_map = FoldMap[Document](on_integer=increment)

    document: Document = [1, 2, 3]
    assert fold_map(document) == [2, 3, 4]

    document = {"foo": 1, "bar": 2}
    assert fold_map(document) == {"foo": 2, "bar": 3}

    document = {"foo": [1, 2], "bar": 3}
    assert fold_map(document) == {"foo": [2, 3], "bar": 4}

    document = {"foo": {"bar": 4, "baz": 5}, "ham": 6}
    assert fold_map(document) == {"foo": {"bar": 5, "baz": 6}, "ham": 7}
