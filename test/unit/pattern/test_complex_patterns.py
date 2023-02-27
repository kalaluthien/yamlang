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


def test_nested_list_pattern() -> None:
    assert match_success(List(List(Bool())), [])
    assert match_success(List(List(Bool())), [[]])
    assert match_success(List(List(Bool())), [[True]])
    assert match_success(List(List(Bool())), [[False]])
    assert match_success(List(List(Bool())), [[True, False]])
    assert match_success(List(List(Bool())), [[True], [False]])
    assert match_success(List(List(Bool())), [[], [True, False]])
    assert match_success(List(List(Bool())), [[True, True], [False], [True, False]])
    assert match_failure(List(List(Bool())), None)
    assert match_failure(List(List(Bool())), {})
    assert match_failure(List(List(Bool())), True)
    assert match_failure(List(List(Bool())), False)
    assert match_failure(List(List(Bool())), [[True, False, None]])
    assert match_failure(List(List(Bool())), [[None], [True, False]])

    assert match_success(
        List(List(Bool())),
        [[[True]], [False], [True, False]],
        [[True], [False], [True, False]],
    )
    assert match_success(
        List(List(Bool())),
        [[[True]], [[False, True]], [True, False]],
        (
            [[True], [False], [True, False]],
            [[True], [True], [True, False]],
        ),
    )
    assert match_success(
        List(List(Bool())),
        [[[True, False], [False, [True]]], [[False, True]], [[True], False]],
        (
            [[True, False], [False], [True, False]],
            [[True, False], [True], [True, False]],
            [[True, True], [False], [True, False]],
            [[True, True], [True], [True, False]],
            [[False, False], [False], [True, False]],
            [[False, False], [True], [True, False]],
            [[False, True], [False], [True, False]],
            [[False, True], [True], [True, False]],
        ),
    )


def test_nested_dict_pattern() -> None:
    assert match_success(Dict({"a": Dict({"b": Int()})}), {"a": {"b": 1}})
    assert match_success(
        Dict({"a": Dict({"b": Int()}), "b": Bool()}),
        {"a": {"b": 1}, "b": True},
    )
    assert match_success(
        Dict({"a": Dict({"b": Int()}), "c": Str()}),
        {"a": {"b": 1, "c": "C"}, "c": "D"},
        {"a": {"b": 1}, "c": "D"},
    )
    assert match_success(
        Dict({"a": Dict({"b": Int(1)}), "c": Str("C")}),
        {"a": {"b": 1}, "c": "C", "d": None},
        {"a": {"b": 1}, "c": "C"},
    )
    assert match_failure(Dict({"a": Dict({"b": Int()})}), {"a": {"b": None}})
    assert match_failure(
        Dict({"a": Dict({"b": Int()}), "b": Bool()}),
        {"a": {"b": False}, "b": True},
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int(1)}), "c": Str("C")}),
        {"a": {"b": 2}, "c": "C"},
    )

    assert match_success(
        Dict({"a": Dict({"b": Int()}), "b": Dict({"a": Str()})}),
        ({"a": {"b": 1}, "b": {"a": "A"}}, {"a": {"b": 1}, "b": {"a": "B"}}),
    )
    assert match_success(
        Dict({"a": Dict({"b": Int()}), "b": Dict({"a": Str()})}),
        {"a": {"a": "A", "b": 1}, "b": {"a": "A", "b": 1}},
        {"a": {"b": 1}, "b": {"a": "A"}},
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int()}), "b": Dict({"a": Str()})}),
        ({"a": {"b": 1}, "b": {"a": 1}}, {"a": {"b": 1}, "b": {"a": None}}),
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int(1)}), "b": Dict({"a": Str()})}),
        ({"a": {"b": 0}, "b": {"a": "A", "b": 1}}, {"a": {"b": 1}, "b": {"a": 1}}),
    )

    assert match_success(
        Dict({"a": Dict({"b": Int(), "c": Str()}), "d": Bool()}),
        {"a": {"b": [1, 2], "c": ["A", "B"]}, "d": [True, False]},
        (
            {"a": {"b": 1, "c": "A"}, "d": True},
            {"a": {"b": 1, "c": "A"}, "d": False},
            {"a": {"b": 1, "c": "B"}, "d": True},
            {"a": {"b": 1, "c": "B"}, "d": False},
            {"a": {"b": 2, "c": "A"}, "d": True},
            {"a": {"b": 2, "c": "A"}, "d": False},
            {"a": {"b": 2, "c": "B"}, "d": True},
            {"a": {"b": 2, "c": "B"}, "d": False},
        ),
    )
    assert match_success(
        Dict({"a": Dict({"b": Int(), "c": Str()}), "d": Bool()}),
        {"a": {"b": [1, None], "c": ["A", "B", None]}, "d": [False]},
        (
            {"a": {"b": 1, "c": "A"}, "d": False},
            {"a": {"b": 1, "c": "B"}, "d": False},
        ),
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int(), "c": Str()}), "d": Bool()}),
        {"a": {"b": [], "c": ["A", "B"]}, "d": [True, False]},
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int(), "c": Str()}), "d": Bool()}),
        {"a": {"b": [None], "c": ["A", "B"]}, "d": [True, False]},
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int(), "c": Str()}), "d": Bool()}),
        {"a": {"b": None, "c": ["A", "B"]}, "d": [True, False]},
    )

    assert match_success(
        Dict({"a": Dict({"b": Int(), "c": Str()}), "d": Bool()}),
        {"a": [{"b": 1, "c": "A"}, {"b": 2, "c": "B"}], "d": [True, None]},
        (
            {"a": {"b": 1, "c": "A"}, "d": True},
            {"a": {"b": 2, "c": "B"}, "d": True},
        ),
    )
    assert match_success(
        Dict({"a": Dict({"b": Int()}), "b": Dict({"a": Str()})}),
        {
            "a": [{"b": [1, 2]}, {"b": 3, "c": 4}],
            "b": [{"a": ["A", "B"]}, {"a": "C", "b": 5}],
        },
        (
            {"a": {"b": 1}, "b": {"a": "A"}},
            {"a": {"b": 1}, "b": {"a": "B"}},
            {"a": {"b": 1}, "b": {"a": "C"}},
            {"a": {"b": 2}, "b": {"a": "A"}},
            {"a": {"b": 2}, "b": {"a": "B"}},
            {"a": {"b": 2}, "b": {"a": "C"}},
            {"a": {"b": 3}, "b": {"a": "A"}},
            {"a": {"b": 3}, "b": {"a": "B"}},
            {"a": {"b": 3}, "b": {"a": "C"}},
        ),
    )


def test_list_of_dict_pattern() -> None:
    assert match_success(
        List(Dict({"a": Int(), "b": Str()})),
        [{"a": 1, "b": "A"}, {"a": 2, "b": "B"}],
        [{"a": 1, "b": "A"}, {"a": 2, "b": "B"}],
    )
    assert match_success(
        List(Dict({"a": Int(), "b": Str()})),
        [{"a": 1, "b": "A"}, {"a": 2, "b": ["B", None]}],
        [{"a": 1, "b": "A"}, {"a": 2, "b": "B"}],
    )
    assert match_success(
        List(Dict({"a": Int(), "b": Str()})),
        [{"a": [1, 2], "b": ["A", "B"]}, {"a": 3, "b": "C"}],
        (
            [{"a": 1, "b": "A"}, {"a": 3, "b": "C"}],
            [{"a": 1, "b": "B"}, {"a": 3, "b": "C"}],
            [{"a": 2, "b": "A"}, {"a": 3, "b": "C"}],
            [{"a": 2, "b": "B"}, {"a": 3, "b": "C"}],
        ),
    )
    assert match_success(
        List(Dict({"a": Int(), "b": Str()})),
        [
            [{"a": 1, "b": "A"}, {"a": [2, 4], "b": "B"}],
            {"a": 3, "b": "C"},
        ],
        (
            [{"a": 1, "b": "A"}, {"a": 3, "b": "C"}],
            [{"a": 2, "b": "B"}, {"a": 3, "b": "C"}],
            [{"a": 4, "b": "B"}, {"a": 3, "b": "C"}],
        ),
    )
    assert match_success(
        List(Dict({"a": Int(1), "b": Str("B")})),
        [
            [{"a": [1, 2], "b": ["B", "C", "B"]}],
            [{"a": [1, 2], "b": "B"}],
        ],
        (
            [{"a": 1, "b": "B"}, {"a": 1, "b": "B"}],
            [{"a": 1, "b": "B"}, {"a": 1, "b": "B"}],
        ),
    )
    assert match_failure(
        List(Dict({"a": Int(), "b": Str()})),
        [{"a": 1, "b": "A"}, None],
    )
    assert match_failure(
        List(Dict({"a": Int(), "b": Str()})),
        [{"a": 1, "b": "A"}, {"a": 2, "b": None}],
    )
    assert match_failure(
        List(Dict({"a": Int(), "b": Str()})),
        [{"a": 1, "b": []}, {"a": 2, "b": "B"}],
    )
    assert match_failure(
        List(Dict({"a": Int(1), "b": Str("B")})),
        [{"a": 1, "b": "A"}, {"a": 2, "b": "B"}],
    )
    assert match_failure(
        List(Dict({"a": Int(1), "b": Str("B")})),
        [[{"a": 1, "b": "A"}, {"a": 2, "b": "B"}]],
    )


def test_dict_of_list_pattern() -> None:
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [1, 2], "b": ["A", "B"]},
    )
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [1, 2], "b": [["A", "B"], "C"]},
        (
            {"a": [1, 2], "b": ["A", "C"]},
            {"a": [1, 2], "b": ["B", "C"]},
        ),
    )
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [1, [2, 3]], "b": [["A", "B", None], "C"]},
        (
            {"a": [1, 2], "b": ["A", "C"]},
            {"a": [1, 2], "b": ["B", "C"]},
            {"a": [1, 3], "b": ["A", "C"]},
            {"a": [1, 3], "b": ["B", "C"]},
        ),
    )
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [], "b": [], "c": []},
        {"a": [], "b": []},
    )
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str()), "c": List(Bool())}),
        {"a": [1], "b": [], "c": [], "d": None},
        {"a": [1], "b": [], "c": []},
    )
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str()), "c": List(Bool())}),
        {"a": [], "b": ["B"], "c": [], "d": None},
        {"a": [], "b": ["B"], "c": []},
    )
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [[1, 2, 3], [4, None, 5]], "b": ["A", ["B", "C"], ["D", None]]},
        (
            {"a": [1, 4], "b": ["A", "B", "D"]},
            {"a": [1, 4], "b": ["A", "C", "D"]},
            {"a": [1, 5], "b": ["A", "B", "D"]},
            {"a": [1, 5], "b": ["A", "C", "D"]},
            {"a": [2, 4], "b": ["A", "B", "D"]},
            {"a": [2, 4], "b": ["A", "C", "D"]},
            {"a": [2, 5], "b": ["A", "B", "D"]},
            {"a": [2, 5], "b": ["A", "C", "D"]},
            {"a": [3, 4], "b": ["A", "B", "D"]},
            {"a": [3, 4], "b": ["A", "C", "D"]},
            {"a": [3, 5], "b": ["A", "B", "D"]},
            {"a": [3, 5], "b": ["A", "C", "D"]},
        ),
    )
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str())}),
        ({"a": [1, 2], "b": ["A", "B"]}, {"a": [3, 4], "b": ["C", "D"]}),
    )
    assert match_success(
        Dict({"a": List(Int()), "b": List(Str())}),
        [
            {"a": [[1, 2], [3, 4]], "b": ["A", ["B", "C"]], "c": [True, False]},
            {"a": [1, [2, 3, 4]], "b": [["A", "B"], "C"]},
        ],
        (
            {"a": [1, 3], "b": ["A", "B"]},
            {"a": [1, 3], "b": ["A", "C"]},
            {"a": [1, 4], "b": ["A", "B"]},
            {"a": [1, 4], "b": ["A", "C"]},
            {"a": [2, 3], "b": ["A", "B"]},
            {"a": [2, 3], "b": ["A", "C"]},
            {"a": [2, 4], "b": ["A", "B"]},
            {"a": [2, 4], "b": ["A", "C"]},
            {"a": [1, 2], "b": ["A", "C"]},
            {"a": [1, 2], "b": ["B", "C"]},
            {"a": [1, 3], "b": ["A", "C"]},
            {"a": [1, 3], "b": ["B", "C"]},
            {"a": [1, 4], "b": ["A", "C"]},
            {"a": [1, 4], "b": ["B", "C"]},
        ),
    )
    assert match_failure(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": ["A", "B"], "b": [1, 2]},
    )
    assert match_failure(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [1, 2, 3.0], "b": ["A", "B"]},
    )
    assert match_failure(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [1, 2], "b": ["A", "B", None]},
    )
    assert match_failure(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [[], [1, 2]], "b": ["A", ["B", "C"]]},
    )
    assert match_failure(
        Dict({"a": List(Int()), "b": List(Str())}),
        {"a": [1, 2], "b": [[], ["B", "C"]]},
    )
    assert match_failure(
        Dict({"a": List(Int()), "b": List(Str())}),
        ({"a": 1, "b": ["A", "B"]}, {"a": [1, 2], "b": "A"}),
    )


def test_list_or_pattern() -> None:
    assert match_success(List(Int() | Str()), [])
    assert match_success(List(Int() | Str()), [1, 2])
    assert match_success(List(Int() | Str()), ["A", "B"])
    assert match_success(List(Int() | Str()), [1, "B"])
    assert match_success(List(Int() | Str()), ["A", 2])
    assert match_success(List(Int() | Str()), [1, "A", 2, "B", "C", 3])
    assert match_failure(List(Int() | Str()), 1)
    assert match_failure(List(Int() | Str()), "A")
    assert match_failure(List(Int() | Str()), None)
    assert match_failure(List(Int() | Str()), False)
    assert match_failure(List(Int() | Str()), {})
    assert match_failure(List(Int() | Str()), [None])
    assert match_failure(List(Int() | Str()), [None, 1])
    assert match_failure(List(Int() | Str()), [None, "A"])
    assert match_failure(List(Int() | Str()), [None, 1, "A"])
    assert match_failure(List(Int() | Str()), [True, False])
    assert match_failure(List(Int() | Str()), [[]])
    assert match_failure(List(Int() | Str()), [{}])

    assert match_success(List(Int()) | List(Str()), [], ([], []))
    assert match_success(List(Int()) | List(Str()), [1, 2])
    assert match_success(List(Int()) | List(Str()), ["A", "B", "C"])
    assert match_success(
        List(Int()) | List(Str()), [[1, "A"], [2, "B"]], ([1, 2], ["A", "B"])
    )
    assert match_failure(List(Int()) | List(Str()), [1, 2, "A", "B"])
    assert match_failure(List(Int()) | List(Str()), [[1, 2], ["A", "B"]])

    assert match_success(Int() | List(Int()), 1)
    assert match_success(Int() | List(Int()), [])
    assert match_success(
        Int() | List(Int()),
        [1, 2, 3, 4, 5],
        (1, 2, 3, 4, 5, [1, 2, 3, 4, 5]),
    )
    assert match_success(
        Int() | List(Int()),
        [1, 2, None, 3, 4, None, 5, 6.0],
        (1, 2, 3, 4, 5),
    )
    assert match_success(
        Int() | List(Int()),
        [[1, 2], [3, 4], [5, 6]],
        (
            1,
            2,
            3,
            4,
            5,
            6,
            [1, 3, 5],
            [1, 3, 6],
            [1, 4, 5],
            [1, 4, 6],
            [2, 3, 5],
            [2, 3, 6],
            [2, 4, 5],
            [2, 4, 6],
        ),
    )
    assert match_failure(Int() | List(Int()), "A")
    assert match_failure(Int() | List(Int()), None)
    assert match_failure(Int() | List(Int()), {})

    assert match_success(List(Int() | List(Int())), [1, 2, 3, 4])
    assert match_success(List(Int() | List(Int())), [[], 1, 2, 3, 4])
    assert match_success(List(Int() | List(Int())), [1, 2, 3, 4, []])
    assert match_success(
        List(Int() | List(Int())),
        [[1, 2, 3, 4]],
        ([1], [2], [3], [4], [[1, 2, 3, 4]]),
    )
    assert match_success(
        List(Int() | List(Int())),
        [[1, 2], [3, 4]],
        (
            [1, 3],
            [1, 4],
            [1, [3, 4]],
            [2, 3],
            [2, 4],
            [2, [3, 4]],
            [[1, 2], 3],
            [[1, 2], 4],
            [[1, 2], [3, 4]],
        ),
    )
    assert match_failure(List(Int() | List(Int())), [None, 1, 2, 3, 4])
    assert match_failure(List(Int() | List(Int())), [[1, 2], [3, 4], None])


def test_dict_or_pattern() -> None:
    assert match_success(Dict({"a": Int() | Str()}), {"a": 1})
    assert match_success(Dict({"a": Int() | Str()}), {"a": "A"})
    assert match_success(
        Dict({"a": Int() | Str()}),
        {"a": [1, None, "A", 2]},
        ({"a": 1}, {"a": 2}, {"a": "A"}),
    )
    assert match_success(
        Dict({"a": Int() | Str()}),
        (
            {"a": 1},
            {"a": [2, "A"]},
            {"a": ["B", 3, 4]},
        ),
        (
            {"a": 1},
            {"a": 2},
            {"a": "A"},
            {"a": 3},
            {"a": 4},
            {"a": "B"},
        ),
    )
    assert match_failure(Dict({"a": Int() | Str()}), {"a": None})
    assert match_failure(Dict({"a": Int() | Str()}), {"a": False})
    assert match_failure(Dict({"a": Int() | Str()}), {"a": []})
    assert match_failure(Dict({"a": Int() | Str()}), {"a": {}})
    assert match_failure(Dict({"a": Int() | Str()}), {"b": 1})
    assert match_failure(Dict({"a": Int() | Str()}), {"b": "A"})

    assert match_success(
        Dict({"a": Int() | Str(), "b": Int()}) | Dict({"a": Int(), "b": Str()}),
        ({"a": 1, "b": 2}, {"a": "A", "b": 2}, {"a": 1, "b": "B"}),
    )
    assert match_success(
        Dict({"a": Int() | Str(), "b": Int()}) | Dict({"a": Int(), "b": Str()}),
        {"a": [1, 2, "A", "B", None], "b": [None, "C", "D", 3, 4]},
        (
            {"a": 1, "b": 3},
            {"a": 1, "b": 4},
            {"a": 2, "b": 3},
            {"a": 2, "b": 4},
            {"a": "A", "b": 3},
            {"a": "A", "b": 4},
            {"a": "B", "b": 3},
            {"a": "B", "b": 4},
            {"a": 1, "b": "C"},
            {"a": 1, "b": "D"},
            {"a": 2, "b": "C"},
            {"a": 2, "b": "D"},
        ),
    )
    assert match_failure(
        Dict({"a": Int() | Str(), "b": Int()}) | Dict({"a": Int(), "b": Str()}),
        {"a": ["A", "B", "C"], "b": "D", "c": "E"},
    )
    assert match_failure(
        Dict({"a": Int() | Str(), "b": Int()}) | Dict({"a": Int(), "b": Str()}),
        {"a": [1, 2, 3, 4, "A"], "b": [], "c": "E"},
    )
    assert match_failure(
        Dict({"a": Int() | Str(), "b": Int()}) | Dict({"a": Int(), "b": Str()}),
        {"a": False, "b": [1, 2, 3, "A", "B", "C"], "c": "E"},
    )
    assert match_failure(
        Dict({"a": Int() | Str(), "b": Int()}) | Dict({"a": Int(), "b": Str()}),
        (
            {"a": [1, 2, 3]},
            {"a": ["A", "B", "C"]},
            {"b": [1, 2, 3]},
            {"b": ["A", "B", "C"]},
        ),
    )
