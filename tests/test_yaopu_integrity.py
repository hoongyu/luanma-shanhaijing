"""全谱一致性 —— 本项目的地基。

别人写图鉴靠记忆和转述；这里每一条都是活的、可执行的、被持续验证的。
考据哪天因环境变化不成立了，这个测试会红。
"""

import pytest

from luanma.loader import load_all
from luanma.repro import REGISTRY

YAOS = load_all()


def test_the_yaopu_is_not_empty():
    assert YAOS


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_every_yao_has_a_registered_repro(y):
    assert y.repro in REGISTRY, f"{y.id} 的复现函数 {y.repro!r} 未注册"


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_every_repro_actually_produces_the_mojibake_it_claims(y):
    assert REGISTRY[y.repro]() == y.expect


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_ids_match_filenames_so_the_registry_stays_navigable(y):
    from luanma.loader import YAO_DIR
    assert (YAO_DIR / f"{y.id}.yaml").exists()
