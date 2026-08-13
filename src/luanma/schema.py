"""妖谱条目的形状。

「驗」（可运行复现）是收录门槛，所以 repro 与 expect 是必填字段 ——
校验在这里拦住，比在 CI 里发现一条没有复现的妖要早得多。
"""

from dataclasses import dataclass, field


class SchemaError(ValueError):
    pass


REQUIRED = ("id", "name", "tag", "glyphs", "hex_texture", "why",
            "notes", "repro", "expect")

# YAML 很容易把 glyphs: [锟, 斤, 拷] 写成 glyphs: 锟斤拷 —— 后者会被
# 解析成字符串，而字符串同样可迭代，于是一路绿到字体产物。
LIST_FIELDS = ("glyphs", "notes")


@dataclass
class Yao:
    id: str
    name: str
    tag: str
    glyphs: list
    hex_texture: str
    why: str
    notes: list
    repro: str
    expect: str
    bytes: list = field(default_factory=list)
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
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})
