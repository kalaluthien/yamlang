from typing import TypeVar


_YamlLikeT = TypeVar("_YamlLikeT", bound="YamlLike")
_YamlLikeF = None | bool | int | float | str | list[_YamlLikeT] | dict[str, _YamlLikeT]
YamlLike = _YamlLikeF["YamlLike"]
