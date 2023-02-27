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


def test_scalar_access_pattern() -> None:
    assert match_failure(Bool()[0], True)  # type: ignore
    assert match_failure(Int()[0], 1)  # type: ignore
    assert match_failure(Float()[0], 1.0)  # type: ignore
    assert match_failure(Str()[0], "A")  # type: ignore

    assert match_failure(Bool()[0][0], True)  # type: ignore
    assert match_failure(Int()[0][0], 1)  # type: ignore
    assert match_failure(Float()[0][0], 1.0)  # type: ignore
    assert match_failure(Str()[0][0], "A")  # type: ignore

    assert match_failure(Bool()["a"], True)  # type: ignore
    assert match_failure(Int()["a"], 1)  # type: ignore
    assert match_failure(Float()["a"], 1.0)  # type: ignore
    assert match_failure(Str()["a"], "A")  # type: ignore

    assert match_failure(Bool()["a"]["b"], True)  # type: ignore
    assert match_failure(Int()["a"]["b"], 1)  # type: ignore
    assert match_failure(Float()["a"]["b"], 1.0)  # type: ignore
    assert match_failure(Str()["a"]["b"], "A")  # type: ignore

    assert match_failure(Bool()[0]["a"], True)  # type: ignore
    assert match_failure(Int()[0]["a"], 1)  # type: ignore
    assert match_failure(Float()[0]["a"], 1.0)  # type: ignore
    assert match_failure(Str()[0]["a"], "A")  # type: ignore

    assert match_failure(Bool()["a"][0], True)  # type: ignore
    assert match_failure(Int()["a"][0], 1)  # type: ignore
    assert match_failure(Float()["a"][0], 1.0)  # type: ignore
    assert match_failure(Str()["a"][0], "A")  # type: ignore


def test_list_access_pattern() -> None:
    assert match_success(List(Int())[0], [1, 2, 3, 4], 1)
    assert match_success(List(Int())[2], [1, 2, 3, 4], 3)
    assert match_success(List(Int())[-1], [1, 2, 3, 4], 4)
    assert match_success(List(Int())[-4], [1, 2, 3, 4], 1)
    assert match_failure(List(Int())[0], [])
    assert match_failure(List(Int())[-1], [])
    assert match_failure(List(Int())[4], [1, 2, 3, 4])
    assert match_failure(List(Int())[-5], [1, 2, 3, 4])

    assert match_success(List(Int() | Str())[0], [1, "A"], 1)
    assert match_success(List(Int() | Str())[1], [1, "A"], "A")
    assert match_failure(List(Int() | Str())[0], [])
    assert match_failure(List(Int() | Str())[-1], [])

    assert match_success((List(Int()) | List(Str()))[0], [1, 2, 3, 4], 1)
    assert match_success((List(Int()) | List(Str()))[3], [1, 2, 3, 4], 4)
    assert match_success((List(Int()) | List(Str()))[-1], [1, 2, 3, 4], 4)
    assert match_success((List(Int()) | List(Str()))[0], ["A", "B"], "A")
    assert match_success((List(Int()) | List(Str()))[1], ["A", "B"], "B")
    assert match_success((List(Int()) | List(Str()))[-2], ["A", "B"], "A")
    assert match_failure((List(Int()) | List(Str()))[4], [1, 2, 3, 4])
    assert match_failure((List(Int()) | List(Str()))[5], [1, 2, 3, 4])
    assert match_failure((List(Int()) | List(Str()))[-5], [1, 2, 3, 4])
    assert match_failure((List(Int()) | List(Str()))[3], ["A", "B"])
    assert match_failure((List(Int()) | List(Str()))[-3], ["A", "B"])
    assert match_failure((List(Int()) | List(Str()))[-4], ["A", "B"])
    assert match_failure((List(Int()) | List(Str()))[0], [1, "A", "B"])
    assert match_failure((List(Int()) | List(Str()))[1], [1, "A", "B"])
    assert match_failure((List(Int()) | List(Str()))[2], [1, "A", "B"])
    assert match_failure((List(Int()) | List(Str()))[-1], [1, "A", "B"])


def test_dict_access_pattern() -> None:
    assert match_success(Dict(a=Int())["a"], {"a": 1}, 1)
    assert match_failure(Dict(a=Int())["a"], {})

    assert match_success(Dict(a=Int() | None)["a"], {"a": 1}, 1)
    assert match_success(Dict(a=Int() | None)["a"], {"a": "A"}, None)

    assert match_success(Dict(a=Int(), b=Str())["b"], {"a": 1, "b": "A"}, "A")
    assert match_failure(Dict(a=Int(), b=Str())["b"], {"a": 1})
    assert match_failure(Dict(a=Int(), b=Str())["b"], {"b": "A"})
    assert match_failure(Dict(a=Int(), b=Str())["b"], {"a": "A", "b": "B"})

    assert match_success(Dict(a=Int() | Str())["a"], {"a": 1}, 1)
    assert match_success(Dict(a=Int() | Str())["a"], {"a": "A"}, "A")
    assert match_success(Dict(a=Int() | Str())["a"], {"a": [1, 2]}, (1, 2))
    assert match_success(Dict(a=Int() | Str())["a"], {"a": ["A", 2]}, (2, "A"))
    assert match_failure(Dict(a=Int() | Str())["a"], {"a": False})
    assert match_failure(Dict(a=Int() | Str())["b"], {"a": [1, "A"]})


def test_nested_list_access_pattern() -> None:
    assert match_success(List(List(Int()))[0][0], [[1, 2, 3], [4, 5, 6]], 1)
    assert match_success(List(List(Int()))[1][1], [[1, 2, 3], [4, 5, 6]], 5)
    assert match_success(List(List(Int()))[-1][-1], [[1, 2, 3], [4, 5, 6]], 6)
    assert match_failure(List(List(Int()))[2][2], [[1, 2, 3], [4, 5, 6]])
    assert match_failure(List(List(Int()))[1][3], [[1, 2, 3], [4, 5, 6]])
    assert match_failure(List(List(Int()))[0][0], [[], [4, 5, 6]])
    assert match_failure(List(List(Int()))[1][0], [[1, 2, 3], []])

    assert match_success(List(List(Int() | Str()))[0][1], [[1, 2, 3], [4, 5, 6]], 2)
    assert match_success(List(List(Int() | Str()))[1][0], [["A", 2], ["B", 5]], "B")
    assert match_success(List(List(Int() | Str()))[1][0], [[], ["B", 5]], "B")
    assert match_success(
        List(List(Int() | Str()))[1][0],
        [[], [["B", "C"], 5]],
        ("B", "C"),
    )
    assert match_failure(List(List(Int() | Str()))[0][0], [["A", 2], [None]])
    assert match_failure(List(List(Int() | Str()))[0][1], [[[], 2], [1]])

    assert match_success(
        List(List(Int()) | List(Str()))[1][0],
        [[1, 2, 3], [4, 5, 6], ["A", "B", "C"]],
        4,
    )
    assert match_success(
        List(List(Int()) | List(Str()))[0][2],
        [["A", "B", "C"], [4, 5, 6], [7, 8, 9]],
        "C",
    )
    assert match_success(
        List(List(Int()) | List(Str()))[1][1],
        [[1, 2, 3], [["A", "B", "C"], ["D", "E"]]],
        ("D", "E", "D", "E", "D", "E"),
    )
    assert match_success(
        List(List(Int()) | List(Str()))[1][1],
        [[], [["A", "B", "C"], ["D", "E"]]],
        ("D", "E", "D", "E", "D", "E", "D", "E", "D", "E", "D", "E"),
    )
    assert match_failure(
        List(List(Int()) | List(Str()))[1][2],
        [[1, 2, 3], [["A", "B", "C"], ["D", "E"]]],
    )
    assert match_failure(
        List(List(Int()) | List(Str()))[1][0],
        [[1, "A"], [2, 3, 4], ["B", "C"]],
    )
    assert match_failure(
        List(List(Int()) | List(Str()))[1][0],
        [[1, 2, 3], ["A", "B", "C"], 4, 5, 6],
    )
    assert match_failure(
        List(List(Int()) | List(Str()))[1][0],
        [[1, 2, 3], ["A", "B", "C"], "D", "E", "F"],
    )


def test_nested_dict_access_pattern() -> None:
    assert match_success(
        Dict(a=Dict(b=Int()))["a"]["b"],
        {"a": {"b": 1}},
        1,
    )
    assert match_success(
        Dict(a=Dict(b=Int()))["a"]["b"],
        {"a": {"b": 1, "c": 2}, "d": 3},
        1,
    )
    assert match_success(
        Dict(a=Dict(b=Int()))["a"]["b"],
        {"a": {"b": [1, 2]}},
        (1, 2),
    )
    assert match_success(
        Dict(a=Dict(b=Int()))["a"]["b"],
        {"a": {"b": [1, 2], "c": [3, 4]}, "d": [5, 6]},
        (1, 2),
    )
    assert match_failure(Dict(a=Dict(b=Int()))["a"]["b"], {"a": {"b": None}})
    assert match_failure(Dict(a=Dict(b=Int()))["a"]["b"], {"a": {"b": False}})
    assert match_failure(
        Dict(a=Dict(b=Int()))["a"]["b"],
        {"a": {"c": 1}, "b": 2},
    )
    assert match_failure(Dict(a=Dict(b=Int()))["a"]["b"], {"a": {}})

    assert match_success(
        Dict(a=Dict(b=Int() | Str()))["a"]["b"],
        {"a": {"b": 1}},
        1,
    )
    assert match_success(
        Dict(a=Dict(b=Int() | Str()))["a"]["b"],
        {"a": {"b": "A"}},
        "A",
    )
    assert match_success(
        Dict(a=Dict(b=Int() | Str()))["a"]["b"],
        {"a": {"b": [1, 2]}},
        (1, 2),
    )
    assert match_success(
        Dict(a=Dict(b=Int() | Str()))["a"]["b"],
        {"a": {"b": [1, "A"]}},
        (1, "A"),
    )
    assert match_success(
        Dict(a=Dict(b=Int() | Str()))["a"]["b"],
        {"a": {"b": ["A", 2, "B"]}},
        (2, "A", "B"),
    )
    assert match_success(
        Dict(a=Dict(b=Int() | Str()), c=Bool())["a"]["b"],
        {"a": {"b": ["A", 2, "B"]}, "c": True},
        (2, "A", "B"),
    )
    assert match_success(
        Dict(a=Dict(b=Int() | Str()), c=Bool())["a"]["b"],
        {"a": {"b": ["A", 2, "B"]}, "c": [True, False]},
        (2, 2, "A", "A", "B", "B"),
    )
    assert match_failure(
        Dict(a=Dict(b=Int() | Str()), c=Bool())["a"]["b"],
        {"a": {"b": 1}, "c": []},
    )
    assert match_failure(
        Dict(a=Dict(b=Int() | Str()), c=Bool())["a"]["b"],
        {"a": {"b": []}, "c": True},
    )

    assert match_success(
        Dict(a=Dict(b=Int()), c=Dict(d=Str()))["a"]["b"],
        {"a": {"b": 1}, "c": {"d": "A"}},
        1,
    )
    assert match_success(
        Dict(a=Dict(b=Int()), c=Dict(d=Str()))["c"]["d"],
        {"a": {"b": 1}, "c": {"d": "A"}},
        "A",
    )
    assert match_failure(
        Dict(a=Dict(b=Int()), c=Dict(d=Str()))["a"]["d"],
        {"a": {"b": 1}, "c": {"d": "A"}},
    )
    assert match_failure(
        Dict(a=Dict(b=Int()), c=Dict(d=Str()))["c"]["b"],
        {"a": {"b": 1}, "c": {"d": "A"}},
    )


def test_nested_dict_and_list_access_pattern() -> None:
    assert match_success(
        Dict(a=List(Dict(b=Int())))["a"][0]["b"],
        {"a": [{"b": 1}]},
        1,
    )
    assert match_success(
        Dict(a=List(Dict(b=Int())))["a"][0]["b"],
        {"a": [{"b": 1}, {"b": 2}]},
        1,
    )
    assert match_success(
        Dict(a=List(Dict(b=Int())))["a"][1]["b"],
        {"a": [{"b": 1}, {"b": 2}]},
        2,
    )
    assert match_success(
        Dict(a=List(Dict(b=Int())))["a"][0]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
        1,
    )
    assert match_success(
        Dict(a=List(Dict(b=Int())))["a"][1]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
        2,
    )
    assert match_success(
        Dict(a=List(Dict(b=Int())))["a"][2]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
        3,
    )
    assert match_success(
        Dict(a=List(Dict(b=Int())))["a"][2]["b"],
        {"a": [{"b": 1, "c": True}, {"b": 2, "c": False}, {"b": 3, "c": True}]},
        3,
    )
    assert match_failure(
        Dict(a=List(Dict(b=Int())))["a"][3]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict(a=List(Dict(b=Int())))["a"][0]["b"],
        {"a": [{}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict(a=List(Dict(b=Int())))["a"][0]["b"],
        {"a": [{}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict(a=List(Dict(b=Int())))["b"][0]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict(a=List(Dict(b=Int())))["a"]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict(a=List(Dict(b=Int())))["a"]["b"][0],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict(a=List(Dict(b=Int())))["a"][0]["b"][0],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )

    assert match_success(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[0]["a"][0],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
        1,
    )
    assert match_success(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[1]["a"][0],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
        2,
    )
    assert match_success(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[0]["b"]["c"],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
        "A",
    )
    assert match_success(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[1]["b"]["c"],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
        "B",
    )
    assert match_failure(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[0]["a"][1],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[0]["b"]["a"],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[0]["b"][0],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[1]["a"][-2],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[1]["b"]["a"],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict(a=List(Int()), b=Dict(c=Str())))[1]["b"][0],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
