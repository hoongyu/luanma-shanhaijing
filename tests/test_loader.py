from luanma.loader import load_all


def test_loads_every_yaml_in_the_yao_directory():
    yaos = load_all()

    ids = {y.id for y in yaos}
    assert "kunjinkao" in ids


def test_entries_come_back_as_validated_objects():
    (kjk,) = [y for y in load_all() if y.id == "kunjinkao"]

    assert kjk.name == "錕斤拷"
    assert kjk.expect == "锟斤拷"


import pytest

from luanma.loader import YAO_DIR, load_all
from luanma.schema import SchemaError


def test_ids_are_unique_across_the_yaopu():
    yaos = load_all()

    ids = [y.id for y in yaos]
    assert len(ids) == len(set(ids)), f"妖谱里有重复 id: {ids}"


def test_a_yml_file_would_not_be_silently_ignored():
    """写成 .yml 的妖谱不能被静默吞掉。

    作者写完一条新妖、看到全绿、以为被验证了 —— 实际它根本没进妖谱。
    """
    strays = list(YAO_DIR.glob("*.yml"))

    assert not strays, f"这些文件用了 .yml 后缀，不会被加载: {strays}"
