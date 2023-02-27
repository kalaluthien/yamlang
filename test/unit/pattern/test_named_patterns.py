from yamlang.yamltools import BoolPattern as Bool
from yamlang.yamltools import DictPattern as Dict
from yamlang.yamltools import Document
from yamlang.yamltools import FloatPattern as Float
from yamlang.yamltools import IntPattern as Int
from yamlang.yamltools import ListPattern as List
from yamlang.yamltools import Pattern
from yamlang.yamltools import StrPattern as Str

SENTINEL_LITERAL_STR = "__SENTINEL_LITERAL_STR__"


def match_success(
    p: Pattern,
    d: Document | tuple[Document, ...],
    r: Document | tuple[Document, ...] = SENTINEL_LITERAL_STR,
) -> bool:
    result = tuple(p.apply(list(d) if isinstance(d, tuple) else d))
    answer = (
        r
        if isinstance(r, tuple)
        else (r,)
        if r != SENTINEL_LITERAL_STR
        else d
        if isinstance(d, tuple)
        else (d,)
    )
    if result != answer:
        print("actual:", result)
        print("expected:", answer)
    return result == answer


def match_failure(p: Pattern, d: Document | tuple[Document, ...]) -> bool:
    return match_success(p, d, ())


def test_custom_dict_pattern() -> None:
    class My(Dict):
        a = Int()
        b = Str()

    assert match_success(My(), {"a": 1, "b": "2"})
    assert match_success(My(), {"a": 1, "b": "2", "c": 3}, {"a": 1, "b": "2"})

    assert match_failure(My(), {"a": 1, "b": 2})
    assert match_failure(My(), {"a": "1", "b": "2"})

    assert match_failure(My(), {"a": 1, "c": 3})
    assert match_failure(My(), {"b": "2", "c": 3})


def test_custom_dict_maybe_pattern() -> None:
    class My(Dict):
        a = Int() | None
        b = Str() | None

    assert match_success(My(), {"a": 1, "b": "2"})
    assert match_success(My(), {"a": 1, "b": "2", "c": 3}, {"a": 1, "b": "2"})

    assert match_success(My(), {"a": 1}, {"a": 1, "b": None})
    assert match_success(My(), {"a": 1, "c": 3}, {"a": 1, "b": None})
    assert match_success(My(), {"b": "2"}, {"a": None, "b": "2"})
    assert match_success(My(), {"b": "2", "c": 3}, {"a": None, "b": "2"})
    assert match_success(My(), {}, {"a": None, "b": None})

    assert match_success(My(), {"a": 1, "b": 2}, {"a": 1, "b": None})
    assert match_success(My(), {"a": "1", "b": "2"}, {"a": None, "b": "2"})
    assert match_success(My(), {"a": "1", "b": 2}, {"a": None, "b": None})


def test_custom_dict_access_pattern() -> None:
    class My(Dict):
        a = Int()
        b = Str() | None

    assert match_success(My()["a"], {"a": 1, "b": "2"}, 1)
    assert match_success(My()["b"], {"a": 1, "b": "2"}, "2")
    assert match_success(My()["b"], {"a": 1}, None)
    assert match_success(My()["b"], {"a": 1, "b": 2}, None)

    assert match_failure(My()["a"], {"a": "1", "b": "2"})
    assert match_failure(My()["a"], {"b": "2"})


def test_custom_dict_attribute_pattern() -> None:
    class My(Dict):
        a = Int()
        b = Str() | None

    assert match_success(My().a, {"a": 1, "b": "2"}, 1)
    assert match_success(My().b, {"a": 1, "b": "2"}, "2")
    assert match_success(My().b, {"a": 1}, None)
    assert match_success(My().b, {"a": 1, "b": 2}, None)

    assert match_failure(My().a, {"a": "1", "b": "2"})
    assert match_failure(My().a, {"b": "2"})


def test_custom_nested_dict_pattern() -> None:
    class Parent(Dict):
        class Child(Dict):
            a = Int()

        child = List(Child())

    assert match_success(Parent(), {"child": [{"a": 1}]})
    assert match_success(Parent(), {"child": [{"a": 1}, {"a": 2}]})
    assert match_success(
        Parent(),
        {"child": [{"a": 1}, {"a": 2}], "c": 3},
        {"child": [{"a": 1}, {"a": 2}]},
    )

    assert match_failure(Parent(), {"child": [{"a": 1}, {"a": "2"}]})
    assert match_failure(Parent(), {"child": [{"a": 1}, {"b": 2}]})


def test_custom_nested_dict_access_pattern() -> None:
    class Parent(Dict[List[Dict[Int]]]):
        class Child(Dict[Int]):
            a = Int()

        child = List(Child())

    assert match_success(Parent()["child"][0]["a"], {"child": [{"a": 1}]}, 1)
    assert match_success(Parent()["child"][1]["a"], {"child": [{"a": 1}, {"a": 2}]}, 2)
    assert match_success(
        Parent()["child"][1]["a"],
        {"child": [{"a": 1}, {"a": 2}], "c": 3},
        2,
    )

    assert match_failure(Parent()["child"][0]["a"], {"child": [{"a": 1}, {"a": "2"}]})
    assert match_failure(Parent()["child"][0]["a"], {"child": [{"a": 1}, {"b": 2}]})


def test_custom_nested_dict_attribute_pattern() -> None:
    class Parent(Dict):
        class ChildA(Dict):
            name = Str("A")
            a = Int()

        class ChildB(Dict):
            name = Str("B")
            a = Int()
            b = Bool()

        child = ChildA() | ChildB()

    assert match_success(Parent().child.a, {"child": {"name": "A", "a": 1}}, 1)
    assert match_success(
        Parent().child.a,
        {"child": {"name": "B", "a": 1, "b": True}},
        1,
    )
    assert match_success(
        Parent().child.a,
        {"child": {"name": "B", "a": 1, "b": True}, "c": 3},
        1,
    )

    assert match_failure(Parent().child.a, {"child": {"name": "A", "a": "1"}})
    assert match_failure(
        Parent().child.a,
        {"child": {"name": "B", "a": "1", "b": True}},
    )

    assert match_success(
        Parent().child["b"],
        {"child": {"name": "B", "a": 1, "b": True}},
        True,
    )
    assert match_success(
        Parent().child["b"],
        {"child": {"name": "B", "a": 1, "b": True}, "c": 3},
        True,
    )

    assert match_failure(Parent().child["b"], {"child": {"name": "A", "a": 1}})
    assert match_failure(Parent().child["b"], {"child": {"name": "B", "a": 1}})
