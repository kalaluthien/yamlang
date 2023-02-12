from yamlang.yamltools import Document
from yamlang.yamltools import Pattern
from yamlang.yamltools import BoolPattern as Bool
from yamlang.yamltools import IntPattern as Int
from yamlang.yamltools import FloatPattern as Float
from yamlang.yamltools import StrPattern as Str
from yamlang.yamltools import ListPattern as List
from yamlang.yamltools import DictPattern as Dict


def match_success(
    p: Pattern,
    d: Document | tuple[Document, ...],
    r: Document | tuple[Document, ...] = None,
) -> bool:
    result = tuple(p.apply(list(d) if isinstance(d, tuple) else d))
    answer = (
        r
        if isinstance(r, tuple)
        else (r,)
        if r is not None
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
        [[[True, False], [False, True]], [[False, True]], [True, False]],
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
