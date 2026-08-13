"""妖谱条目的形状。

「驗」（可运行复现）是收录门槛，所以 repro 与 expect 是必填字段 ——
校验在这里拦住，比在 CI 里发现一条没有复现的妖要早得多。
"""

from dataclasses import dataclass, field


class SchemaError(ValueError):
    pass


REQUIRED = ("id", "name", "tag", "glyphs", "hex_texture", "why",
            "notes", "repro", "expect")


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
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})
