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


def test_bool_pattern() -> None:
    assert match_success(Bool(), True)
    assert match_success(Bool(), False)
    assert match_failure(Bool(), None)
    assert match_failure(Bool(), 0)
    assert match_failure(Bool(), "")

    assert match_success(Bool(), (True, False, True))
    assert match_success(Bool(), (True, False, None), (True, False))
    assert match_success(
        Bool(),
        ([True, False], [False, [False, True]], True),
        (True, False, False, False, True, True),
    )

    assert match_success(Bool(True), True)
    assert match_failure(Bool(True), None)
    assert match_failure(Bool(True), 1)
    assert match_failure(Bool(True), "True")
    assert match_failure(Bool(True), False)

    assert match_success(Bool(True), (True, True, True))
    assert match_success(Bool(True), (True, False, True), (True, True))
    assert match_failure(Bool(True), (False, None, 1))

    assert match_success(Bool(False), False)
    assert match_failure(Bool(False), None)
    assert match_failure(Bool(False), 0)
    assert match_failure(Bool(False), "False")
    assert match_failure(Bool(False), True)

    assert match_success(Bool(False), (False, False, False))
    assert match_success(Bool(False), (True, False, False), (False, False))
    assert match_failure(Bool(False), (True, None, 0))


def test_int_pattern() -> None:
    assert match_success(Int(), 0)
    assert match_success(Int(), 1)
    assert match_success(Int(), -1)
    assert match_failure(Int(), None)
    assert match_failure(Int(), False)

    assert match_success(Int(), (0, 1, -1))
    assert match_success(Int(), (0, 1, -1, None), (0, 1, -1))
    assert match_failure(Int(), (0.0, 1.0))

    assert match_success(Int(0), 0)
    assert match_failure(Int(0), None)
    assert match_failure(Int(0), "0")
    assert match_failure(Int(0), 1)
    assert match_failure(Int(0), -1)

    assert match_success(Int(0), (0, 0, 0))
    assert match_success(Int(0), (0, 1, -1, 0), (0, 0))
    assert match_failure(Int(0), (1, -1, 0.0))


def test_float_pattern() -> None:
    assert match_success(Float(), 0.0)
    assert match_success(Float(), 1.0)
    assert match_success(Float(), -1.0)
    assert match_failure(Float(), None)
    assert match_failure(Float(), True)
    assert match_failure(Float(), "1.0")

    assert match_success(Float(), (0.0, 1.0, -1.0))
    assert match_success(Float(), (0.0, 1.0, -1.0, None), (0.0, 1.0, -1.0))
    assert match_failure(Float(), (None, True, "1.0"))

    assert match_success(Float(1.0), 1.0)
    assert match_failure(Float(1.0), None)
    assert match_failure(Float(1.0), 1)
    assert match_failure(Float(1.0), "1.0")
    assert match_failure(Float(1.0), -1.0)

    assert match_success(Float(1.0), (1.0, 1.0, 1.0))
    assert match_success(Float(1.0), (0.0, 1.0, -1.0, 1.0), (1.0, 1.0))
    assert match_failure(Float(1.0), (0.0, -1.0))


def test_str_pattern() -> None:
    assert match_success(Str(), "")
    assert match_success(Str(), "a")
    assert match_failure(Str(), None)
    assert match_failure(Str(), 0)

    assert match_success(Str(), ("", "a", "b"))
    assert match_success(Str(), ("a", "b", None), ("a", "b"))
    assert match_failure(Str(), (None, 0))

    assert match_success(Str(""), "")
    assert match_failure(Str(""), None)
    assert match_failure(Str(""), 0)
    assert match_failure(Str(""), "a")

    assert match_success(Str(""), ("", "", ""))
    assert match_success(Str(""), ("", "a", "", "b", ""), ("", "", ""))
    assert match_failure(Str(""), ("a", None))

    assert match_success(Str("a"), "a")
    assert match_failure(Str("a"), None)
    assert match_failure(Str("a"), 0)
    assert match_failure(Str("a"), "")
    assert match_failure(Str("a"), "b")

    assert match_success(Str("a"), ("a", "a", "a"))
    assert match_success(Str("a"), ("", "a", "b", "a", ""), ("a", "a"))
    assert match_failure(Str("a"), ("", "b", "b"))


def test_list_pattern() -> None:
    assert match_success(List(Bool()), [])
    assert match_success(List(Bool()), [True])
    assert match_success(List(Bool()), [False])
    assert match_success(List(Bool()), [True, False])
    assert match_success(List(Bool()), [[True], [False]], [True, False])
    assert match_failure(List(Bool()), None)
    assert match_failure(List(Bool()), {})
    assert match_failure(List(Bool()), True)
    assert match_failure(List(Bool()), False)
    assert match_failure(List(Bool()), [True, False, None])

    assert match_success(
        List(Bool()),
        [[True], [False], [True, False]],
        ([True, False, True], [True, False, False]),
    )
    assert match_success(
        List(Bool()),
        [[True, True], [False, True], [True, False]],
        (
            [True, False, True],
            [True, False, False],
            [True, True, True],
            [True, True, False],
            [True, False, True],
            [True, False, False],
            [True, True, True],
            [True, True, False],
        ),
    )
    assert match_success(
        List(Bool()),
        [[True, False], [False], [True, False, None]],
        (
            [True, False, True],
            [True, False, False],
            [False, False, True],
            [False, False, False],
        ),
    )
    assert match_failure(List(Bool()), [[True], [], [True, False]])
    assert match_failure(List(Bool()), [[True], [None], [True, False]])

    assert match_success(
        List(Bool()),
        [[True], False, [True, False]],
        ([True, False, True], [True, False, False]),
    )
    assert match_success(
        List(Bool()),
        [True, False, [True, False]],
        ([True, False, True], [True, False, False]),
    )
    assert match_failure(List(Bool()), [[True], None, [True, False]])
    assert match_failure(List(Bool()), [[], False, [True, False]])
    assert match_failure(List(Bool()), [[]])

    assert match_success(
        List(Bool()),
        [
            [[True, False], True, [True, False]],
            [True, [False, True], [True], [[False]]],
            False,
        ],
        (
            [True, True, False],
            [True, False, False],
            [True, True, False],
            [True, True, False],
            [True, False, False],
            [False, True, False],
            [False, False, False],
            [False, True, False],
            [False, True, False],
            [False, False, False],
            [True, True, False],
            [True, False, False],
            [True, True, False],
            [True, True, False],
            [True, False, False],
            [True, True, False],
            [True, False, False],
            [True, True, False],
            [True, True, False],
            [True, False, False],
            [False, True, False],
            [False, False, False],
            [False, True, False],
            [False, True, False],
            [False, False, False],
        ),
    )

    assert match_success(
        List(Bool()),
        [[True, "True"], [False, "False"], [True, "TrueFalse", False]],
        ([True, False, True], [True, False, False]),
    )
    assert match_failure(List(Bool()), [["True", "False"], [True, False]])
    assert match_failure(List(Bool()), ["True", [False], [True, "False"]])


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


def test_dict_pattern() -> None:
    assert match_success(Dict({}), {})
    assert match_success(Dict({}), {"a": 1}, {})
    assert match_failure(Dict({}), None)
    assert match_failure(Dict({}), [])

    assert match_success(Dict({"a": Int()}), {"a": 1})
    assert match_success(Dict({"a": Int()}), {"a": 1, "b": "B"}, {"a": 1})
    assert match_success(Dict({"a": Int(1)}), {"a": 1})
    assert match_success(Dict({"a": Int(), "b": Str()}), {"a": 1, "b": "B"})
    assert match_success(Dict({"a": Int(1), "b": Str()}), {"a": 1, "b": "B"})
    assert match_success(Dict({"a": Int(), "b": Str("B")}), {"a": 1, "b": "B"})
    assert match_failure(Dict({"a": Int(1)}), {"a": 2})
    assert match_failure(Dict({"a": Int()}), {})
    assert match_failure(Dict({"a": Int()}), {"b": "B"})
    assert match_failure(Dict({"a": Int(), "b": Str()}), {"a": 1})
    assert match_failure(Dict({"a": Int(), "b": Str()}), {"b": "B"})
    assert match_failure(Dict({"a": Int(), "b": Str()}), {"a": None, "b": "B"})
    assert match_failure(Dict({"a": Int(), "b": Str()}), {"a": 1, "b": None})
    assert match_failure(Dict({"a": Int(1), "b": Str()}), {"a": 2, "b": "B"})
    assert match_failure(Dict({"a": Int(), "b": Str("B")}), {"a": 1, "b": "A"})

    assert match_success(
        Dict({"a": Int(), "b": Str()}),
        {"a": [1, 2], "b": ["A", "B"]},
        (
            {"a": 1, "b": "A"},
            {"a": 1, "b": "B"},
            {"a": 2, "b": "A"},
            {"a": 2, "b": "B"},
        ),
    )
    assert match_success(
        Dict({"a": Int(), "b": Str(), "c": Bool()}),
        {"a": [1], "b": ["A", "B", "C"], "c": [True, False]},
        (
            {"a": 1, "b": "A", "c": True},
            {"a": 1, "b": "A", "c": False},
            {"a": 1, "b": "B", "c": True},
            {"a": 1, "b": "B", "c": False},
            {"a": 1, "b": "C", "c": True},
            {"a": 1, "b": "C", "c": False},
        ),
    )
    assert match_success(
        Dict({"a": Int(), "b": Str(), "c": Bool()}),
        {"a": [1, None], "b": ["A", "B", None], "c": False},
        (
            {"a": 1, "b": "A", "c": False},
            {"a": 1, "b": "B", "c": False},
        ),
    )
    assert match_failure(
        Dict({"a": Int(), "b": Str(), "c": Bool()}),
        {"a": [], "b": ["A", "B", "C"], "c": [True, False]},
    )
    assert match_failure(
        Dict({"a": Int(), "b": Str(), "c": Bool()}),
        {"a": [None], "b": ["A", "B", "C"], "c": [True, False]},
    )
    assert match_failure(
        Dict({"a": Int(), "b": Str(), "c": Bool()}),
        {"a": None, "b": ["A", "B", "C"], "c": [True, False]},
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


def test_scalar_null_pattern() -> None:
    assert match_success(Bool() | None, True)
    assert match_success(Bool() | None, False)
    assert match_success(Bool() | None, None)
    assert match_success(Bool() | None, 0, None)
    assert match_success(Bool() | None, 1.0, None)
    assert match_success(Bool() | None, "", None)
    assert match_success(Bool() | None, [], None)
    assert match_success(Bool() | None, {}, None)


def test_scalar_or_pattern() -> None:
    assert match_success(Int() | Str(), 1)
    assert match_success(Int() | Str(), "A")
    assert match_success(Int() | Str(), (1, "A"))
    assert match_success(Int() | Str(), (1, 2, "A", "B"))
    assert match_success(Int() | Str(), ("A", 1), (1, "A"))
    assert match_success(Int() | Str(), (1, None, "A", False, 2), (1, 2, "A"))
    assert match_failure(Int() | Str(), None)
    assert match_failure(Int() | Str(), [])
    assert match_failure(Int() | Str(), {})
    assert match_failure(Int() | Str(), (None, False))

    assert match_success(Int(1) | Int(2) | Str(), 1)
    assert match_success(Int(1) | Int(2) | Str(), 2)
    assert match_success(Int(1) | Int(2) | Str(), "")
    assert match_success(Int(1) | Int(2) | Str(), "A")
    assert match_success(Int(1) | Int(2) | Str(), (1, 2, "A", "B"))
    assert match_success(Int(1) | Int(2) | Str(), ("A", 2, 1), (1, 2, "A"))
    assert match_failure(Int(1) | Int(2) | Str(), 3)
    assert match_failure(Int(1) | Int(2) | Str(), None)
    assert match_failure(Int(1) | Int(2) | Str(), [])
    assert match_failure(Int(1) | Int(2) | Str(), {})

    assert match_success(Int(1) | Int(2) | Str() | None, 1)
    assert match_success(Int(1) | Int(2) | Str() | None, 2)
    assert match_success(Int(1) | Int(2) | Str() | None, 3, None)
    assert match_success(Int(1) | Int(2) | Str() | None, "")
    assert match_success(Int(1) | Int(2) | Str() | None, "A")
    assert match_success(Int(1) | Int(2) | Str() | None, None)
    assert match_success(Int(1) | Int(2) | Str() | None, (None,))
    assert match_success(Int(1) | Int(2) | Str() | None, (None, 1), (1,))
    assert match_success(Int(1) | Int(2) | Str() | None, (2, "A", None, 1), (1, 2, "A"))


def test_sequence_or_pattern() -> None:
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


def test_mapping_or_pattern() -> None:
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


def test_scalar_access_pattern() -> None:
    assert match_failure(Bool()[0], True)
    assert match_failure(Int()[0], 1)
    assert match_failure(Float()[0], 1.0)
    assert match_failure(Str()[0], "A")

    assert match_failure(Bool()[0][0], True)
    assert match_failure(Int()[0][0], 1)
    assert match_failure(Float()[0][0], 1.0)
    assert match_failure(Str()[0][0], "A")

    assert match_failure(Bool()["a"], True)
    assert match_failure(Int()["a"], 1)
    assert match_failure(Float()["a"], 1.0)
    assert match_failure(Str()["a"], "A")

    assert match_failure(Bool()["a"]["b"], True)
    assert match_failure(Int()["a"]["b"], 1)
    assert match_failure(Float()["a"]["b"], 1.0)
    assert match_failure(Str()["a"]["b"], "A")

    assert match_failure(Bool()[0]["a"], True)
    assert match_failure(Int()[0]["a"], 1)
    assert match_failure(Float()[0]["a"], 1.0)
    assert match_failure(Str()[0]["a"], "A")

    assert match_failure(Bool()["a"][0], True)
    assert match_failure(Int()["a"][0], 1)
    assert match_failure(Float()["a"][0], 1.0)
    assert match_failure(Str()["a"][0], "A")


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
    assert match_success(Dict({"a": Int()})["a"], {"a": 1}, 1)
    assert match_failure(Dict({"a": Int()})["a"], {})

    assert match_success(Dict({"a": Int() | None})["a"], {"a": 1}, 1)
    assert match_success(Dict({"a": Int() | None})["a"], {"a": "A"}, None)

    assert match_success(Dict({"a": Int(), "b": Str()})["b"], {"a": 1, "b": "A"}, "A")
    assert match_failure(Dict({"a": Int(), "b": Str()})["b"], {"a": 1})
    assert match_failure(Dict({"a": Int(), "b": Str()})["b"], {"b": "A"})
    assert match_failure(Dict({"a": Int(), "b": Str()})["b"], {"a": "A", "b": "B"})

    assert match_success(Dict({"a": Int() | Str()})["a"], {"a": 1}, 1)
    assert match_success(Dict({"a": Int() | Str()})["a"], {"a": "A"}, "A")
    assert match_success(Dict({"a": Int() | Str()})["a"], {"a": [1, 2]}, (1, 2))
    assert match_success(Dict({"a": Int() | Str()})["a"], {"a": ["A", 2]}, (2, "A"))
    assert match_failure(Dict({"a": Int() | Str()})["a"], {"a": False})
    assert match_failure(Dict({"a": Int() | Str()})["b"], {"a": [1, "A"]})


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
        Dict({"a": Dict({"b": Int()})})["a"]["b"],
        {"a": {"b": 1}},
        1,
    )
    assert match_success(
        Dict({"a": Dict({"b": Int()})})["a"]["b"],
        {"a": {"b": 1, "c": 2}, "d": 3},
        1,
    )
    assert match_success(
        Dict({"a": Dict({"b": Int()})})["a"]["b"],
        {"a": {"b": [1, 2]}},
        (1, 2),
    )
    assert match_success(
        Dict({"a": Dict({"b": Int()})})["a"]["b"],
        {"a": {"b": [1, 2], "c": [3, 4]}, "d": [5, 6]},
        (1, 2),
    )
    assert match_failure(Dict({"a": Dict({"b": Int()})})["a"]["b"], {"a": {"b": None}})
    assert match_failure(Dict({"a": Dict({"b": Int()})})["a"]["b"], {"a": {"b": False}})
    assert match_failure(
        Dict({"a": Dict({"b": Int()})})["a"]["b"],
        {"a": {"c": 1}, "b": 2},
    )
    assert match_failure(Dict({"a": Dict({"b": Int()})})["a"]["b"], {"a": {}})

    assert match_success(
        Dict({"a": Dict({"b": Int() | Str()})})["a"]["b"],
        {"a": {"b": 1}},
        1,
    )
    assert match_success(
        Dict({"a": Dict({"b": Int() | Str()})})["a"]["b"],
        {"a": {"b": "A"}},
        "A",
    )
    assert match_success(
        Dict({"a": Dict({"b": Int() | Str()})})["a"]["b"],
        {"a": {"b": [1, 2]}},
        (1, 2),
    )
    assert match_success(
        Dict({"a": Dict({"b": Int() | Str()})})["a"]["b"],
        {"a": {"b": [1, "A"]}},
        (1, "A"),
    )
    assert match_success(
        Dict({"a": Dict({"b": Int() | Str()})})["a"]["b"],
        {"a": {"b": ["A", 2, "B"]}},
        (2, "A", "B"),
    )
    assert match_success(
        Dict({"a": Dict({"b": Int() | Str()}), "c": Bool()})["a"]["b"],
        {"a": {"b": ["A", 2, "B"]}, "c": True},
        (2, "A", "B"),
    )
    assert match_success(
        Dict({"a": Dict({"b": Int() | Str()}), "c": Bool()})["a"]["b"],
        {"a": {"b": ["A", 2, "B"]}, "c": [True, False]},
        (2, 2, "A", "A", "B", "B"),
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int() | Str()}), "c": Bool()})["a"]["b"],
        {"a": {"b": 1}, "c": []},
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int() | Str()}), "c": Bool()})["a"]["b"],
        {"a": {"b": []}, "c": True},
    )

    assert match_success(
        Dict({"a": Dict({"b": Int()}), "c": Dict({"d": Str()})})["a"]["b"],
        {"a": {"b": 1}, "c": {"d": "A"}},
        1,
    )
    assert match_success(
        Dict({"a": Dict({"b": Int()}), "c": Dict({"d": Str()})})["c"]["d"],
        {"a": {"b": 1}, "c": {"d": "A"}},
        "A",
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int()}), "c": Dict({"d": Str()})})["a"]["d"],
        {"a": {"b": 1}, "c": {"d": "A"}},
    )
    assert match_failure(
        Dict({"a": Dict({"b": Int()}), "c": Dict({"d": Str()})})["c"]["b"],
        {"a": {"b": 1}, "c": {"d": "A"}},
    )


def test_nested_dict_and_list_access_pattern() -> None:
    assert match_success(
        Dict({"a": List(Dict({"b": Int()}))})["a"][0]["b"],
        {"a": [{"b": 1}]},
        1,
    )
    assert match_success(
        Dict({"a": List(Dict({"b": Int()}))})["a"][0]["b"],
        {"a": [{"b": 1}, {"b": 2}]},
        1,
    )
    assert match_success(
        Dict({"a": List(Dict({"b": Int()}))})["a"][1]["b"],
        {"a": [{"b": 1}, {"b": 2}]},
        2,
    )
    assert match_success(
        Dict({"a": List(Dict({"b": Int()}))})["a"][0]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
        1,
    )
    assert match_success(
        Dict({"a": List(Dict({"b": Int()}))})["a"][1]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
        2,
    )
    assert match_success(
        Dict({"a": List(Dict({"b": Int()}))})["a"][2]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
        3,
    )
    assert match_success(
        Dict({"a": List(Dict({"b": Int()}))})["a"][2]["b"],
        {"a": [{"b": 1, "c": True}, {"b": 2, "c": False}, {"b": 3, "c": True}]},
        3,
    )
    assert match_failure(
        Dict({"a": List(Dict({"b": Int()}))})["a"][3]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict({"a": List(Dict({"b": Int()}))})["a"][0]["b"],
        {"a": [{}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict({"a": List(Dict({"b": Int()}))})["a"][0]["b"],
        {"a": [{}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict({"a": List(Dict({"b": Int()}))})["b"][0]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict({"a": List(Dict({"b": Int()}))})["a"]["b"],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict({"a": List(Dict({"b": Int()}))})["a"]["b"][0],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )
    assert match_failure(
        Dict({"a": List(Dict({"b": Int()}))})["a"][0]["b"][0],
        {"a": [{"b": 1}, {"b": 2}, {"b": 3}]},
    )

    assert match_success(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[0]["a"][0],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
        1,
    )
    assert match_success(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[1]["a"][0],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
        2,
    )
    assert match_success(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[0]["b"]["c"],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
        "A",
    )
    assert match_success(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[1]["b"]["c"],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
        "B",
    )
    assert match_failure(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[0]["a"][1],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[0]["b"]["a"],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[0]["b"][0],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[1]["a"][-2],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[1]["b"]["a"],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
    assert match_failure(
        List(Dict({"a": List(Int()), "b": Dict({"c": Str()})}))[1]["b"][0],
        [{"a": [1], "b": {"c": "A"}}, {"a": [2], "b": {"c": "B"}}],
    )
