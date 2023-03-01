from yamlang.pattern import BoolPattern as Bool
from yamlang.pattern import DictPattern as Dict
from yamlang.pattern import FloatPattern as Float
from yamlang.pattern import IntPattern as Int
from yamlang.pattern import ListPattern as List
from yamlang.pattern import ParsePattern as Parse
from yamlang.pattern import Pattern
from yamlang.pattern import StrPattern as Str
from yamlang.yamltools import Document

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


def test_parse_simple_pattern() -> None:
    assert match_success(
        Parse.from_text(Dict(a=Int(), b=Str(), c=Bool(), d=Float())),
        r"{'a': 1, 'b': '2', 'c': True, 'd': 3.0}",
        {"a": 1, "b": "2", "c": True, "d": 3.0},
    )
    assert match_success(
        Parse.from_text(Dict(a=Int() | Str(), b=Bool() | Float() | None)),
        (
            r"{'a': 1, 'b': True}",
            r"{'a': '2', 'b': 3.0, 'c': 5}",
            r"{'a': '2', 'b': None}",
        ),
        (
            {"a": 1, "b": True},
            {"a": "2", "b": 3.0},
            {"a": "2", "b": None},
        ),
    )

    assert match_failure(Parse.from_text(Dict(a=Int(), b=Str())), r"{'a': 1}")
    assert match_failure(Parse.from_text(Dict(a=Int(), b=Str())), r"{'a': 1, 'b': 2}")
    assert match_failure(Parse.from_text(Dict(a=Int(), b=Str())), r"{'a': '1', 'b': 2}")


def test_parse_complex_pattern() -> None:
    assert match_success(
        Parse.from_text(List(Dict(a=Int(), b=Str())) | Dict(c=List(Bool() | Float()))),
        r"[{'a': 1, 'b': '2'}, {'a': 3, 'b': '4'}]",
        [{"a": 1, "b": "2"}, {"a": 3, "b": "4"}],
    )
    assert match_success(
        Parse.from_text(List(Dict(a=Int(), b=Str())) | Dict(c=List(Bool() | Float()))),
        r"{'c': [[True, 3.0], [False, 5.0]]}",
        (
            {"c": [True, False]},
            {"c": [True, 5.0]},
            {"c": [3.0, False]},
            {"c": [3.0, 5.0]},
        ),
    )


def test_parse_access_pattern() -> None:
    assert match_success(
        Parse.from_text(Dict(a=Int(), b=Str(), c=Bool(), d=Float()))["a"],
        r"{'a': 1, 'b': '2', 'c': True, 'd': 3.0}",
        1,
    )
    assert match_success(
        Parse.from_text(List(Int() | Str()))[1],
        r"[1, '2', 3, '4']",
        "2",
    )

    assert match_failure(
        Parse.from_text(Dict(a=Int(), b=Str()))["c"],
        r"{'a': 1, 'b': 2}",
    )
    assert match_failure(
        Parse.from_text(List(Int() | Str()))[4],
        r"[1, '2', 3, '4']",
    )

    assert match_success(
        Parse.from_text(Dict(a=List(Int() | Str())))["a"][1],
        r"{'a': [1, '2', 3, '4'], 'b': [5, '6', 7, '8']}",
        "2",
    )
    assert match_success(
        Parse.from_text(
            (List(Dict(a=Int(), b=Str())) | Dict(c=List(Bool() | Float())))["c"][1],
        ),
        r"{c: [1.1, 2.2, 3.3]}",
        2.2,
    )

    assert match_failure(
        Parse.from_text(Dict(a=List(Int() | Str())))["b"][1],
        r"{'a': [1, '2', 3, '4'], 'b': [5, '6', 7, '8']}",
    )
    assert match_failure(
        Parse.from_text(Dict(a=List(Int() | Str())))["a"][4],
        r"{'a': [1, '2', 3, '4'], 'b': [5, '6', 7, '8']}",
    )
