from yamlang.yamltools import Document
from yamlang.yamltools import FoldMap
from yamlang.yamltools import load


def test_load_yaml() -> None:
    document = load(r"{foo: {bar: baz, qux: [12, 34]}}")
    assert document == {"foo": {"bar": "baz", "qux": [12, 34]}}

    document = load(r"{foo: null, bar: yes, baz: off, on: true, no: FALSE}")
    assert document == {
        "foo": "null",
        "bar": "yes",
        "baz": "off",
        "on": True,
        "no": "FALSE",
    }

    document = load(r"{foo: &A {bar: 2.0, baz: 3.0}, qux: *A}")
    assert document == {
        "foo": {"bar": 2.0, "baz": 3.0},
        "qux": {"bar": 2.0, "baz": 3.0},
    }


def test_fold_map_increment() -> None:
    def increment(x: int) -> int:
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


def test_fold_map_skip_null() -> None:
    def skip_null_array(xs: list[Document]) -> list[Document]:
        return [x for x in xs if x is not None]

    def skip_null_object(xs: dict[str, Document]) -> dict[str, Document]:
        return {k: v for k, v in xs.items() if v is not None}

    fold_map = FoldMap[Document](
        on_array=skip_null_array,
        on_object=skip_null_object,
    )

    document: Document = None
    assert fold_map(document) == None

    document = [1, None, 2, None, 3]
    assert fold_map(document) == [1, 2, 3]

    document = {"foo": 1, "bar": None, "baz": 2, "qux": None, "ham": 3}
    assert fold_map(document) == {"foo": 1, "baz": 2, "ham": 3}

    document = {"foo": [1, None, 2, None, 3], "bar": None, "baz": 4}
    assert fold_map(document) == {"foo": [1, 2, 3], "baz": 4}
