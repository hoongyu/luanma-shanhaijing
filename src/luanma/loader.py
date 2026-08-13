"""从磁盘读妖谱。

妖谱目录定位靠包的位置往上找，而不是当前工作目录 ——
测试、构建脚本、CI 的 cwd 各不相同。
"""

import pathlib

import yaml

from .schema import Yao

YAO_DIR = pathlib.Path(__file__).resolve().parents[2] / "yao"


def load_all(directory=None):
    d = pathlib.Path(directory) if directory else YAO_DIR
    out = []
    for p in sorted(d.glob("*.yaml")):
        with open(p, "r", encoding="utf-8") as f:
            out.append(Yao.from_dict(yaml.safe_load(f)))
    return out
