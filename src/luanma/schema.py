"""妖谱条目的形状。

「驗」（可运行复现）是收录门槛，所以 repro 与 expect 是必填字段 ——
校验在这里拦住，比在 CI 里发现一条没有复现的妖要早得多。

字节故事（codec + hex_texture + bytes）则是**可选**的。不是每只妖都由
「字节被当成另一种编码读」造成：规范化类、排序类、断行类、编码写入
失败类的妖根本没有字节故事。逼它们填 hex_texture，它们只能填自己
expect 的编码 —— 重复一次必然通过，断言退化成同义反复，永远绿，
不再验证任何东西。那比收不进来更糟：表面上守卫覆盖六个字段，
实际有一个是空的。

但半填比不填更危险：给了 hex_texture 却不说按什么编码读，断言无从
下手；给了 codec 却没有字节，codec 也无处可用。所以两者必须同时
有或同时无。
"""

from dataclasses import dataclass, field


class SchemaError(ValueError):
    pass


REQUIRED = ("id", "name", "tag", "glyphs", "why",
            "notes", "repro", "expect")

# YAML 很容易把 glyphs: [锟, 斤, 拷] 写成 glyphs: 锟斤拷 —— 后者会被
# 解析成字符串，而字符串同样可迭代，于是一路绿到字体产物。
LIST_FIELDS = ("glyphs", "notes")

# 字节故事的两半，必须同生同灭。
BYTE_STORY_FIELDS = ("codec", "hex_texture")


@dataclass
class Yao:
    id: str
    name: str
    tag: str
    glyphs: list
    why: str
    notes: list
    repro: str
    expect: str
    bytes: list = field(default_factory=list)
    # 这只妖的字节被当成什么编码读的。空 = 它没有字节故事。
    codec: str = ""
    hex_texture: str = ""
    out: str = ""
    via: str = ""

    @classmethod
    def from_dict(cls, d):
        missing = [k for k in REQUIRED if not d.get(k)]
        if missing:
            raise SchemaError(f"条目缺少必填字段: {', '.join(missing)}")
        wrong_type = [k for k in LIST_FIELDS if not isinstance(d.get(k), list)]
        if wrong_type:
            raise SchemaError(
                f"这些字段必须是列表: {', '.join(wrong_type)}"
                f"（YAML 里别忘了方括号）"
            )
        filled = [k for k in BYTE_STORY_FIELDS if d.get(k)]
        if len(filled) == 1:
            (given,) = filled
            (absent,) = [k for k in BYTE_STORY_FIELDS if k != given]
            raise SchemaError(
                f"字节故事只填了一半：给了 {given} 却没给 {absent}。"
                f"codec 与 hex_texture 必须同时有（这只妖的字节被误读了）"
                f"或同时无（它根本不是字节类的妖）"
            )
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})
