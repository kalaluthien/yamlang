import datetime

from yamlang.yamltools import Document, FoldMap, load


def test_load_yaml() -> None:
    document = load(r"{foo: {bar: baz, qux: [12, 34]}}")
    assert document == {"foo": {"bar": "baz", "qux": [12, 34]}}

    document = load(r"{foo: null, bar: yes, baz: off, on: true, no: FALSE, ? else}")
    assert document == {
        "foo": "null",
        "bar": "yes",
        "baz": "off",
        "on": True,
        "no": False,
        "else": "",
    }

    document = load(r"{foo: &A {bar: 2.0, baz: 3.0}, qux: *A}")
    assert document == {
        "foo": {"bar": 2.0, "baz": 3.0},
        "qux": {"bar": 2.0, "baz": 3.0},
    }

    document = load(r"{foo: [2023-01-01], bar: [2023-01-01 12:34:56]}")
    assert document == {
        "foo": [datetime.date(2023, 1, 1)],
        "bar": [datetime.datetime(2023, 1, 1, 12, 34, 56)],
    }


def test_fold_map_increment() -> None:
    def increment(x: int) -> int:
        return x + 1

    fold_map = FoldMap[Document](on_int=increment)

    document: Document = [1, 2, 3]
    assert fold_map(document) == [2, 3, 4]

    document = {"foo": 1, "bar": 2}
    assert fold_map(document) == {"foo": 2, "bar": 3}

    document = {"foo": [1, 2], "bar": 3}
    assert fold_map(document) == {"foo": [2, 3], "bar": 4}

    document = {"foo": {"bar": 4, "baz": 5}, "ham": 6}
    assert fold_map(document) == {"foo": {"bar": 5, "baz": 6}, "ham": 7}


def test_fold_map_skip_null() -> None:
    def skip_null_list(xs: list[Document]) -> list[Document]:
        return [x for x in xs if x is not None]

    def skip_null_dict(xs: dict[str, Document]) -> dict[str, Document]:
        return {k: v for k, v in xs.items() if v is not None}

    fold_map = FoldMap[Document](
        on_list=skip_null_list,
        on_dict=skip_null_dict,
    )

    document: Document = None
    assert fold_map(document) == None

    document = [1, None, 2, None, 3]
    assert fold_map(document) == [1, 2, 3]

    document = {"foo": 1, "bar": None, "baz": 2, "qux": None, "ham": 3}
    assert fold_map(document) == {"foo": 1, "baz": 2, "ham": 3}

    document = {"foo": [1, None, 2, None, 3], "bar": None, "baz": 4}
    assert fold_map(document) == {"foo": [1, 2, 3], "baz": 4}


def test_fold_map_format() -> None:
    def format_none(x: None) -> str:
        return "None"

    def format_bool(x: bool) -> str:
        return f"Bool({str(x).lower()})"

    def format_int(x: int) -> str:
        return f"Int({x})"

    def format_float(x: float) -> str:
        return f"Float({x})"

    def format_str(x: str) -> str:
        return f"Str({x})"

    def format_date(x: datetime.date) -> str:
        return f"Date({x.year}-{x.month}-{x.day})"

    def format_datetime(x: datetime.datetime) -> str:
        return f"DateTime({x.year}-{x.month}-{x.day} {x.hour}:{x.minute}:{x.second})"

    def format_list(xs: list[str]) -> str:
        return f"List({', '.join(xs)})"

    def format_dict(xs: dict[str, str]) -> str:
        return f"Dict({', '.join(f'{k}: {v}' for k, v in xs.items())})"

    fold_map = FoldMap[str](
        on_none=format_none,
        on_bool=format_bool,
        on_int=format_int,
        on_float=format_float,
        on_str=format_str,
        on_date=format_date,
        on_datetime=format_datetime,
        on_list=format_list,
        on_dict=format_dict,
    )

    document: Document = None
    assert fold_map(document) == "None"

    document = True
    assert fold_map(document) == "Bool(true)"

    document = 1234
    assert fold_map(document) == "Int(1234)"

    document = 12.34
    assert fold_map(document) == "Float(12.34)"

    document = "foo"
    assert fold_map(document) == "Str(foo)"

    document = datetime.date(2023, 1, 1)
    assert fold_map(document) == "Date(2023-1-1)"

    document = datetime.datetime(2023, 1, 1, 12, 34, 56)
    assert fold_map(document) == "DateTime(2023-1-1 12:34:56)"

    document = [1, 2, 3]
    assert fold_map(document) == "List(Int(1), Int(2), Int(3))"

    document = {"foo": 1, "bar": 2}
    assert fold_map(document) == "Dict(foo: Int(1), bar: Int(2))"

    document = {"foo": [1, 2], "bar": 3}
    assert fold_map(document) == "Dict(foo: List(Int(1), Int(2)), bar: Int(3))"
