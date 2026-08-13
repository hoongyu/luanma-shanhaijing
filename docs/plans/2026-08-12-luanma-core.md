# 乱码山海经 · 可信内核实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立一个 CI 每日验证的妖谱——每一条乱码考据都有可运行的复现代码，考据失效时测试会红——外加一条 Windows 可跑的字体子集化流水线。

**Architecture:** 妖谱是 YAML 数据；每只妖在 `repro.py` 里有一个注册的复现函数；一个全谱一致性测试遍历妖谱、调用每只妖的复现函数、断言它确实产出该妖的乱码。字体流水线从妖谱抽取用字，用 `pyftsubset` 子集化，并断言竖排 feature 未被剥掉。

**Tech Stack:** Python 3.14 · pytest · PyYAML · fontTools + Brotli · GitHub Actions

**Scope:** 本计划只做**可信内核与字体流水线**。Astro 站点与妖形渲染是第二份计划（`docs/plans/` 下另立），因为站点依赖内容先存在。本计划完成后交付物是：一个被 CI 守护的妖谱库 + 可复现的字体产物。

**依据规格：** [`docs/design-luanma-shanhaijing.md`](../design-luanma-shanhaijing.md)

---

## File Structure

| 文件 | 职责 |
|---|---|
| `pyproject.toml` | 改名 sessionprint → luanma；依赖加 PyYAML |
| `yao/kunjinkao.yaml` | 妖谱条目：锟斤拷 |
| `yao/tangtangtang.yaml` | 妖谱条目：烫烫烫 |
| `yao/tuntuntun.yaml` | 妖谱条目：屯屯屯 |
| `src/luanma/schema.py` | 妖谱条目的数据类与字段校验（只管「一条长得对不对」） |
| `src/luanma/loader.py` | 读取 `yao/*.yaml` 并构造条目（只管「从磁盘到对象」） |
| `src/luanma/repro.py` | 复现函数注册表与全部复现实现（只管「产出乱码」） |
| `src/luanma/charset.py` | 从妖谱抽取分角色字符集（只管「哪些字要进字体」） |
| `scripts/build_fonts.py` | 调 pyftsubset 出 woff2，并校验竖排 feature |
| `tests/test_schema.py` · `test_loader.py` · `test_repro.py` · `test_charset.py` | 对应单元测试 |
| `tests/test_yaopu_integrity.py` | **全谱一致性测试——本项目的地基** |
| `.github/workflows/ci.yml` | 每日 + 每次 push 跑全部测试 |

删除：`src/sessionprint/`、`tests/test_redact.py`、`tests/test_parse.py`、`gen.js`、`rm.md`、`sub.py`

---

## Task 1: 初始化仓库并清理遗留

**Files:**
- Create: `.gitignore`
- Delete: `gen.js`, `rm.md`, `sub.py`, `src/sessionprint/`, `src/sessionprint.egg-info/`, `tests/test_redact.py`, `tests/test_parse.py`

`src/sessionprint/` 是被推翻的「会话解剖图」方向的遗留，与本项目无关。`gen.js` 是 cn-font-split 的 protobuf 打包产物，调研时落下的。

- [ ] **Step 1: 建 .gitignore**

写入 `.gitignore`：

```gitignore
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
build/
dist/
node_modules/
.env

# 字体原件不进仓库：体积大且可从上游重新下载。
# 子集化产物由构建脚本生成，也不进仓库。
prototype/fonts/*.ttf
prototype/fonts/*.otf
prototype/fonts/*.zip
prototype/fonts/sub-*.woff2
prototype/fonts/ui-*.woff2
fonts/source/
public/fonts/

# 授权原文必须进仓库 —— OFL 要求随分发附带
!fonts/LICENSES/
```

- [ ] **Step 2: 删除遗留文件**

```bash
cd /c/Claude_code/App
rm -rf src/sessionprint src/sessionprint.egg-info tests/test_redact.py tests/test_parse.py
rm -f gen.js rm.md sub.py
```

- [ ] **Step 3: 确认删干净**

```bash
ls src/ tests/ 2>&1; ls gen.js rm.md sub.py 2>&1
```

期望：`src/` 为空或不存在；`tests/` 只剩 `__pycache__`；三个散落文件报 "No such file"。

- [ ] **Step 4: git init 并首次提交**

```bash
cd /c/Claude_code/App
git init
git add -A
git commit -m "chore: 初始化仓库，清理被推翻方向的遗留代码

sessionprint 是「会话解剖图」方向的产物，该方向已在设计阶段被推翻
（详见 docs/design-luanma-shanhaijing.md）。"
```

---

## Task 2: 项目更名与依赖

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: 重写 pyproject.toml**

```toml
[project]
name = "luanma"
version = "0.1.0"
description = "乱码山海经 —— 中文乱码的妖怪图鉴，每一条考据都可运行复现"
requires-python = ">=3.11"
dependencies = ["PyYAML>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "fonttools[woff]>=4.60", "brotli>=1.1"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 2: 重装并确认包名生效**

```bash
cd /c/Claude_code/App
python -m pip uninstall -y sessionprint 2>&1 | tail -1
python -m pip install -e ".[dev]" -q 2>&1 | grep -v notice | tail -3
python -c "import yaml, fontTools, brotli; print('deps ready')"
```

期望输出：`deps ready`

- [ ] **Step 3: 提交**

```bash
git add pyproject.toml
git commit -m "chore: 更名为 luanma，依赖加 PyYAML 与 fontTools"
```

---

## Task 3: 妖谱条目的数据结构与校验

规格要求七个字段，其中 `驗`（可运行复现）是收录门槛。校验必须拦住缺字段的条目——否则一条没有复现的妖会悄悄混进来。

**Files:**
- Create: `src/luanma/__init__.py`, `src/luanma/schema.py`
- Test: `tests/test_schema.py`

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_schema.py`：

```python
import pytest

from luanma.schema import Yao, SchemaError

MINIMAL = {
    "id": "kunjinkao",
    "name": "錕斤拷",
    "tag": "编码误读",
    "glyphs": ["锟", "斤", "拷"],
    "hex_texture": "EF BF BD",
    "why": "它是伤上加伤。",
    "notes": [["現", "UTF-8 被当作 GBK 解读"]],
    "repro": "kunjinkao",
    "expect": "锟斤拷",
}


def test_builds_a_yao_from_a_complete_entry():
    y = Yao.from_dict(MINIMAL)

    assert y.id == "kunjinkao"
    assert y.glyphs == ["锟", "斤", "拷"]
    assert y.expect == "锟斤拷"


def test_rejects_an_entry_with_no_repro_because_that_is_the_admission_bar():
    broken = {k: v for k, v in MINIMAL.items() if k != "repro"}

    with pytest.raises(SchemaError, match="repro"):
        Yao.from_dict(broken)
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_schema.py -v 2>&1 | tail -8
```

期望：`ModuleNotFoundError: No module named 'luanma.schema'`

- [ ] **Step 3: 写最小实现**

创建 `src/luanma/__init__.py`（空文件）与 `src/luanma/schema.py`：

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_schema.py -v 2>&1 | tail -6
```

期望：2 passed

- [ ] **Step 5: 提交**

```bash
git add src/luanma/ tests/test_schema.py
git commit -m "feat: 妖谱条目数据结构，校验拦住无复现的条目"
```

---

## Task 4: 复现函数注册表

**Files:**
- Create: `src/luanma/repro.py`
- Test: `tests/test_repro.py`

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_repro.py`：

```python
from luanma.repro import REGISTRY, repro


def test_decorator_puts_the_function_in_the_registry_under_its_name():
    @repro("_probe")
    def _probe():
        return "x"

    assert REGISTRY["_probe"]() == "x"
    del REGISTRY["_probe"]
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_repro.py -v 2>&1 | tail -6
```

期望：`ModuleNotFoundError: No module named 'luanma.repro'`

- [ ] **Step 3: 写最小实现**

创建 `src/luanma/repro.py`：

```python
"""每只妖的复现代码。

这些不是示例，是断言。全谱一致性测试会调用每一个，
并要求它确实产出该妖的乱码 —— 考据哪天不成立了，CI 会红。
"""

REGISTRY = {}


def repro(name):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_repro.py -v 2>&1 | tail -5
```

期望：1 passed

- [ ] **Step 5: 提交**

```bash
git add src/luanma/repro.py tests/test_repro.py
git commit -m "feat: 复现函数注册表"
```

---

## Task 5: 复现锟斤拷

字节级事实（已在设计阶段核实）：`锟=EF BF`、`斤=BD EF`、`拷=BF BD`。两枚 U+FFFD 的 UTF-8 是 `EF BF BD EF BF BD`，按 GBK 双字节切开正是这三个字。

**Files:**
- Modify: `src/luanma/repro.py`
- Modify: `tests/test_repro.py`

- [ ] **Step 1: 写失败的测试**

在 `tests/test_repro.py` 末尾追加：

```python
def test_two_replacement_chars_read_as_gbk_become_kunjinkao():
    assert REGISTRY["kunjinkao"]() == "锟斤拷"


def test_an_odd_number_of_replacement_chars_cannot_form_it():
    """锟斤拷必成双 —— 第三枚只剩一个字节，GBK 解码直接失败。"""
    import pytest
    with pytest.raises(UnicodeDecodeError):
        ("\ufffd" * 3).encode("utf-8").decode("gbk")
```

> 用 `"\ufffd"` 转义而不是直接写字面的替换字符：这个文件本身要经历编辑器、git、CI 三道搬运，
> 而它讲的正是「字符在搬运中损坏」——用转义写才不会自己变成一只妖。

- [ ] **Step 2: 跑测试确认失败**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_repro.py -v 2>&1 | tail -8
```

期望：`KeyError: 'kunjinkao'`（第二个测试会通过——它测的是 Python 内建行为）

- [ ] **Step 3: 写最小实现**

在 `src/luanma/repro.py` 末尾追加：

```python
@repro("kunjinkao")
def kunjinkao():
    """U+FFFD 的 UTF-8 是 EF BF BD；两枚相连按 GBK 双字节切开 = 锟斤拷。"""
    return ("\ufffd" * 2).encode("utf-8").decode("gbk")
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_repro.py -v 2>&1 | tail -6
```

期望：3 passed

- [ ] **Step 5: 提交**

```bash
git add src/luanma/repro.py tests/test_repro.py
git commit -m "feat: 复现锟斤拷，并锁定「必成双」这条性质"
```

---

## Task 6: 复现烫烫烫与屯屯屯

MSVC 调试版把未初始化的**栈**内存填成 `0xCC`（int3 断点指令），`CC CC` 在 GBK 中是「烫」；**堆**填 `0xCD`，`CD CD` 是「屯」。

**Files:**
- Modify: `src/luanma/repro.py`
- Modify: `tests/test_repro.py`

- [ ] **Step 1: 写失败的测试**

在 `tests/test_repro.py` 末尾追加：

```python
def test_stack_fill_0xcc_reads_as_tang():
    assert REGISTRY["tangtangtang"]() == "烫烫烫"


def test_heap_fill_0xcd_reads_as_tun():
    assert REGISTRY["tuntuntun"]() == "屯屯屯"
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_repro.py -v 2>&1 | tail -8
```

期望：`KeyError: 'tangtangtang'`

- [ ] **Step 3: 写最小实现**

在 `src/luanma/repro.py` 末尾追加：

```python
@repro("tangtangtang")
def tangtangtang():
    """MSVC 调试版把未初始化的栈内存填成 0xCC；CC CC 在 GBK 中是「烫」。"""
    return (b"\xcc" * 6).decode("gbk")


@repro("tuntuntun")
def tuntuntun():
    """同上，堆内存填 0xCD；CD CD 是「屯」。见烫知栈，见屯知堆。"""
    return (b"\xcd" * 6).decode("gbk")
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_repro.py -v 2>&1 | tail -6
```

期望：5 passed

- [ ] **Step 5: 提交**

```bash
git add src/luanma/repro.py tests/test_repro.py
git commit -m "feat: 复现烫烫烫与屯屯屯"
```

---

## Task 7: 妖谱加载器

**Files:**
- Create: `src/luanma/loader.py`
- Create: `yao/kunjinkao.yaml`
- Test: `tests/test_loader.py`

- [ ] **Step 1: 写第一条妖谱**

创建 `yao/kunjinkao.yaml`：

```yaml
id: kunjinkao
name: 錕斤拷
tag: 编码误读
glyphs: [锟, 斤, 拷]
hex_texture: EF BF BD
bytes: [EF BF, BD EF, BF BD]
out: 锟 斤 拷
via: 按 GBK 双字节切开
why: >-
  它是伤上加伤。文本先错过一次，坏字被换成 U+FFFD；这个替换字符的 UTF-8 是
  EF BF BD。两枚相连共六字节，再被当成 GBK 读，就切出了这三个字。
notes:
  - [現, UTF-8 文本被当作 GBK 解读]
  - [異, 必成双——单数枚只剩一个字节，GBK 解码直接失败]
  - [驅, 全链路统一 UTF-8。已成形则不可逆，原字早已丢失]
repro: kunjinkao
expect: 锟斤拷
```

- [ ] **Step 2: 写失败的测试**

创建 `tests/test_loader.py`：

```python
from luanma.loader import load_all


def test_loads_every_yaml_in_the_yao_directory():
    yaos = load_all()

    ids = {y.id for y in yaos}
    assert "kunjinkao" in ids


def test_entries_come_back_as_validated_objects():
    (kjk,) = [y for y in load_all() if y.id == "kunjinkao"]

    assert kjk.name == "錕斤拷"
    assert kjk.expect == "锟斤拷"
```

- [ ] **Step 3: 跑测试确认失败**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_loader.py -v 2>&1 | tail -6
```

期望：`ModuleNotFoundError: No module named 'luanma.loader'`

- [ ] **Step 4: 写最小实现**

创建 `src/luanma/loader.py`：

```python
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
```

- [ ] **Step 5: 跑测试确认通过**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_loader.py -v 2>&1 | tail -6
```

期望：2 passed

- [ ] **Step 6: 提交**

```bash
git add src/luanma/loader.py yao/kunjinkao.yaml tests/test_loader.py
git commit -m "feat: 妖谱加载器与第一条妖谱"
```

---

## Task 8: 全谱一致性测试 —— 本项目的地基

这是整个项目和「网上乱码大全」的分界线。它遍历妖谱、调用每只妖的复现函数、断言产出与 `expect` 一致。**任何一条考据失效，CI 就红。**

**Files:**
- Create: `yao/tangtangtang.yaml`, `yao/tuntuntun.yaml`
- Test: `tests/test_yaopu_integrity.py`

- [ ] **Step 1: 补齐另外两条妖谱**

创建 `yao/tangtangtang.yaml`：

```yaml
id: tangtangtang
name: 燙燙燙
tag: 内存填充
glyphs: [烫, 烫, 烫]
hex_texture: CC CC
bytes: [CC CC, CC CC, CC CC]
out: 烫 烫 烫
via: 按 GBK 双字节切开
why: >-
  这不是编码错，是你看见了内存本身的颜色。MSVC 调试版把未初始化的栈内存
  全填成 0xCC（int3 断点指令），而 CC CC 在 GBK 里恰好是「烫」。
notes:
  - [現, MSVC 调试模式读到未初始化的栈]
  - [異, 孪生兄弟叫「屯屯屯」——堆填 0xCD，CD CD 即「屯」]
  - [驅, 初始化你的变量。修内存，不是修编码]
repro: tangtangtang
expect: 烫烫烫
```

创建 `yao/tuntuntun.yaml`：

```yaml
id: tuntuntun
name: 屯屯屯
tag: 内存填充
glyphs: [屯, 屯, 屯]
hex_texture: CD CD
bytes: [CD CD, CD CD, CD CD]
out: 屯 屯 屯
via: 按 GBK 双字节切开
why: >-
  烫烫烫的孪生兄弟。MSVC 调试版把未初始化的堆内存填成 0xCD，
  CD CD 在 GBK 里是「屯」。见烫知栈，见屯知堆。
notes:
  - [現, MSVC 调试模式读到未初始化的堆]
  - [異, 栈那一只叫「烫烫烫」，填的是 0xCC]
  - [驅, 初始化你的变量。修内存，不是修编码]
repro: tuntuntun
expect: 屯屯屯
```

- [ ] **Step 2: 写失败的测试**

创建 `tests/test_yaopu_integrity.py`：

```python
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
```

- [ ] **Step 3: 跑测试确认通过**

这一步与常规 TDD 顺序不同：三条复现已在 Task 5–6 实现，此测试是把它们**绑定到数据**上。若此刻不是全绿，说明妖谱与复现对不上，那正是这个测试存在的意义。

```bash
cd /c/Claude_code/App && python -m pytest tests/test_yaopu_integrity.py -v 2>&1 | tail -14
```

期望：10 passed（1 + 3×3）

- [ ] **Step 4: 主动验证它真的会红**

临时把 `yao/tangtangtang.yaml` 的 `expect` 改成 `烫烫烫烫`，重跑：

```bash
cd /c/Claude_code/App
sed -i 's/^expect: 烫烫烫$/expect: 烫烫烫烫/' yao/tangtangtang.yaml
python -m pytest tests/test_yaopu_integrity.py -v 2>&1 | tail -8
```

期望：1 failed，指向 `tangtangtang`。**没看到这个失败就不算验证过。**

- [ ] **Step 5: 改回来并确认恢复全绿**

```bash
cd /c/Claude_code/App
sed -i 's/^expect: 烫烫烫烫$/expect: 烫烫烫/' yao/tangtangtang.yaml
python -m pytest tests/ -q 2>&1 | tail -4
python -c "
import yaml, glob
for f in sorted(glob.glob('yao/*.yaml')):
    d = yaml.safe_load(open(f, encoding='utf-8'))
    print(d['id'], ' '.join(f'U+{ord(c):04X}' for c in d['expect']))
"
```

期望：全部通过，且三条 expect 的码位分别是
`U+951F U+65A4 U+62F7` / `U+70EB U+70EB U+70EB` / `U+5C6F U+5C6F U+5C6F`

> ⚠️ **不要用 `git diff --stat` 来证明「改回来了」。** 这些 YAML 此刻还未被 `git add`
> （步骤 6 才提交），未跟踪文件根本不会出现在 `git diff` 里——**改坏了没改回来，
> 它一样是空输出**。必须用码位复验。这个假证据是实施中被实现代理当场抓出来的。

- [ ] **Step 6: 提交**

```bash
git add yao/ tests/test_yaopu_integrity.py
git commit -m "feat: 全谱一致性测试 —— 考据失效时 CI 会红

这是本项目与「网上乱码大全」的分界线：每一条考据都绑定一段
可运行的复现代码，并被测试持续验证。"
```

---

## Task 9: 从妖谱抽取分角色字符集

规格定的字体分工：妖形与妖名走马善政（横排），竖排版式走源流明體。两者用字不同，必须分开抽。

**Files:**
- Create: `src/luanma/charset.py`
- Test: `tests/test_charset.py`

- [ ] **Step 1: 写失败的测试**

创建 `tests/test_charset.py`：

```python
from luanma.charset import beast_charset, ui_charset


def test_beast_charset_covers_every_glyph_and_name_in_the_yaopu():
    cs = beast_charset()

    for ch in "锟斤拷烫屯":      # 妖形用的简体字
        assert ch in cs
    for ch in "錕燙":            # 妖名用的繁体字
        assert ch in cs


def test_beast_charset_is_deduplicated():
    cs = beast_charset()

    assert len(cs) == len(set(cs))


def test_ui_charset_carries_the_field_names_and_punctuation():
    cs = ui_charset()

    for ch in "形現因驗異驅":
        assert ch in cs
    for ch in "「」。，":
        assert ch in cs
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_charset.py -v 2>&1 | tail -6
```

期望：`ModuleNotFoundError: No module named 'luanma.charset'`

- [ ] **Step 3: 写最小实现**

创建 `src/luanma/charset.py`：

```python
"""按字体角色抽取用字。

分开抽是硬要求：马善政没有竖排度量表，只能承担横排的妖形与妖名；
竖排版式必须走源流明體。两者的字符集因此不同。
"""

from .loader import load_all

# 版式固定用字：书名、卷次、字段名、导航、以及竖排会用到的标点。
UI_FIXED = (
    "亂碼山海經"
    "卷一二三四五六七八九十"
    "形現因驗異驅"
    "闔點其以觀詳已覆核"
    "「」『』。，、（）：；？！—…"
)


def beast_charset(yaos=None):
    """妖形与妖名用字。横排，走马善政。"""
    seen = []
    for y in yaos if yaos is not None else load_all():
        for ch in "".join(y.glyphs) + y.name:
            if ch not in seen:
                seen.append(ch)
    return "".join(seen)


def ui_charset():
    """版式用字。含竖排，走源流明體。"""
    seen = []
    for ch in UI_FIXED:
        if ch not in seen:
            seen.append(ch)
    return "".join(seen)
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd /c/Claude_code/App && python -m pytest tests/test_charset.py -v 2>&1 | tail -6
```

期望：3 passed

- [ ] **Step 5: 提交**

```bash
git add src/luanma/charset.py tests/test_charset.py
git commit -m "feat: 按字体角色抽取用字（妖形横排 / 版式竖排分开）"
```

---

## Task 10: 字体子集化脚本与竖排断言

规格里的硬规则：`pyftsubset` 必须带 `--layout-features="*"`。网上教程常写 `--layout-features=""`，会**静默毁掉竖排标点**。脚本必须自己断言这一点，不能靠人记得。

**Files:**
- Create: `scripts/build_fonts.py`
- Create: `fonts/source/.gitkeep`

前置：把两个字体原件放到 `fonts/source/`。它们不进仓库（见 .gitignore），下载命令写在脚本的 docstring 里。

- [ ] **Step 1: 准备字体原件目录并下载**

```bash
cd /c/Claude_code/App
mkdir -p fonts/source fonts/LICENSES
touch fonts/source/.gitkeep
curl -sL -o fonts/source/MaShanZheng-Regular.ttf \
  "https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf"
curl -sL -o fonts/LICENSES/MaShanZheng-OFL.txt \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/mashanzheng/OFL.txt"
curl -sL -o /tmp/genryu.zip \
  "https://github.com/ButTaiwan/genryu-font/releases/download/v2.100/GenRyuMin2TW-otf.zip"
python -c "
import zipfile
z = zipfile.ZipFile('/tmp/genryu.zip')
open('fonts/source/GenRyuMin2TW-R.otf','wb').write(z.read('GenRyuMin2TW-R.otf'))
open('fonts/LICENSES/GenRyuMin-OFL.txt','wb').write(z.read('SIL_Open_Font_License_1.1.txt'))
"
ls -la fonts/source/ fonts/LICENSES/
```

期望：`MaShanZheng-Regular.ttf` 约 5.6 MB，`GenRyuMin2TW-R.otf` 约 15.7 MB，两份 OFL 各约 4.4 KB

- [ ] **Step 2: 写构建脚本**

创建 `scripts/build_fonts.py`：

```python
"""从妖谱生成子集化字体。

上游原件下载（不进仓库，见 .gitignore）：
  马善政毛笔楷书  https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf
  源流明體 TW-R   https://github.com/ButTaiwan/genryu-font/releases  (GenRyuMin2TW-otf.zip)

两条不能违反的规则：
  1. --layout-features="*"  —— 写成 "" 会静默毁掉竖排标点
  2. CSS family 必须改名 —— 子集化在 OFL FAQ 2.6 下算 modification
"""

import pathlib
import subprocess
import sys

from fontTools.ttLib import TTFont

from luanma.charset import beast_charset, ui_charset

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "fonts" / "source"
OUT = ROOT / "public" / "fonts"

# family 名刻意不是原名：子集化算 modification，OFL 要求改名。
JOBS = [
    ("YaoBrush", "MaShanZheng-Regular.ttf", beast_charset, False),
    ("YaoSeal", "GenRyuMin2TW-R.otf", ui_charset, True),
]

VERT_FEATURES = {"vert", "vrt2", "valt", "vpal", "vhal", "halt", "palt"}


def features_of(path):
    ft = TTFont(path)
    found = set()
    for tag in ("GSUB", "GPOS"):
        if tag in ft and ft[tag].table.FeatureList:
            found |= {r.FeatureTag for r in ft[tag].table.FeatureList.FeatureRecord}
    return found


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    failures = []
    for family, src, chars_fn, needs_vertical in JOBS:
        srcp = SRC / src
        if not srcp.exists():
            sys.exit(f"缺少字体原件: {srcp}\n见本文件 docstring 里的下载地址")
        text = chars_fn()
        outp = OUT / f"{family}.woff2"
        subprocess.run(
            ["pyftsubset", str(srcp), f"--text={text}", "--flavor=woff2",
             f"--output-file={outp}", "--layout-features=*", "--no-hinting"],
            check=True,
        )
        size = outp.stat().st_size
        feats = features_of(outp)
        print(f"  {family:<10} {len(text):>3} 字  {size:>6} B  -> {outp.name}")

        if needs_vertical:
            got = feats & VERT_FEATURES
            if not got:
                failures.append(
                    f"{family} 丢失了全部竖排 feature —— "
                    f"检查 --layout-features 是否被写成了空字符串"
                )
            else:
                print(f"             竖排 feature: {','.join(sorted(got))}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    print("\n字体产物就绪。")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 跑脚本**

```bash
cd /c/Claude_code/App && python scripts/build_fonts.py
```

期望输出形如：

```
  YaoBrush     7 字    ~2.8 KB  -> YaoBrush.woff2
  YaoSeal     46 字    ~10 KB   -> YaoSeal.woff2
             竖排 feature: halt,palt,vert,vhal,vpal
字体产物就绪。
```

字数是确定的（妖形 7 字 = 锟斤拷錕烫燙屯；版式 46 字 = `UI_FIXED` 去重后），
体积随字体版本浮动，**关键是那行「竖排 feature」必须打印出来**。

- [ ] **Step 4: 验证竖排断言真的会拦住错误**

临时把脚本里的 `--layout-features=*` 改成 `--layout-features=`，重跑：

```bash
cd /c/Claude_code/App
sed -i 's/"--layout-features=\*"/"--layout-features="/' scripts/build_fonts.py
python scripts/build_fonts.py; echo "退出码: $?"
```

期望：打印 `FAIL: YaoSeal 丢失了全部竖排 feature`，退出码 1。**没看到这个失败就不算验证过。**

- [ ] **Step 5: 改回来并确认恢复**

```bash
cd /c/Claude_code/App
sed -i 's/"--layout-features="/"--layout-features=*"/' scripts/build_fonts.py
python scripts/build_fonts.py; echo "退出码: $?"
```

期望：正常输出，退出码 0

- [ ] **Step 6: 提交**

```bash
git add scripts/build_fonts.py fonts/source/.gitkeep fonts/LICENSES/
git commit -m "feat: 字体子集化脚本，自带竖排 feature 断言

--layout-features=\"\" 会静默毁掉竖排标点，所以脚本自己检查，
不靠人记得。OFL 原文随仓库归档。"
```

---

## Task 11: CI

规格要求「CI 每天跑」——考据可能因 Python 版本、编解码器行为变化而失效，需要主动发现而不是等读者报错。

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: 写 workflow**

创建 `.github/workflows/ci.yml`：

```yaml
name: 妖谱一致性

on:
  push:
  pull_request:
  schedule:
    # 每天 UTC 22:17 —— 避开整点，GitHub Actions 在 xx:00 会 drop scheduled event
    - cron: "17 22 * * *"

jobs:
  verify:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.11", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - name: 安装
        run: python -m pip install -e ".[dev]"
      - name: 跑全谱一致性
        run: python -m pytest tests/ -v
```

跨 OS 与跨 Python 版本是有意为之：编解码器行为在不同平台上可能有差异，而本项目的全部结论都建立在编解码器行为上。

- [ ] **Step 2: 本地模拟 CI 会跑的命令**

```bash
cd /c/Claude_code/App && python -m pytest tests/ -v 2>&1 | tail -8
```

期望：全部通过

- [ ] **Step 3: 提交**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: 每次 push 与每日跑全谱一致性，覆盖 Linux/Windows × Py3.11/3.13"
```

---

## Task 12: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: 写 README**

创建 `README.md`：

````markdown
# 乱码山海经

中文乱码的妖怪图鉴。每一只「字妖」都有名字、形貌，以及**字节级精确、可运行复现**的成因。

## 为什么它和别的乱码大全不一样

每一条考据都绑定一段可执行的复现代码，并由 CI 每日验证。考据哪天不成立了，测试会红。

```python
>>> ("\ufffd" * 2).encode("utf-8").hex(" ")
'ef bf bd ef bf bd'
>>> ("\ufffd" * 2).encode("utf-8").decode("gbk")
'锟斤拷'
```

## 目录

- `yao/` —— 妖谱，一妖一个 YAML
- `src/luanma/` —— 加载、校验、复现
- `tests/test_yaopu_integrity.py` —— 全谱一致性测试，本项目的地基
- `scripts/build_fonts.py` —— 字体子集化

## 开发

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/ -v
```

字体原件不进仓库，下载地址见 `scripts/build_fonts.py` 的 docstring：

```bash
python scripts/build_fonts.py
```

## 字体授权

本项目使用的字体均为 SIL OFL 1.1，原文归档在 `fonts/LICENSES/`。
子集化产物的 CSS family 名（`YaoBrush` / `YaoSeal`）刻意不同于原字体名 ——
子集化在 OFL FAQ 2.6 下算 modification，须改名。

| 用途 | 字体 | 授权 |
|---|---|---|
| 妖形与妖名 | 马善政毛笔楷书 | SIL OFL 1.1 |
| 竖排版式 | 源流明體 TW-R | SIL OFL 1.1 |
| 说明正文 | 系统无衬线（仅 font-family 引用，不分发文件） | — |

## 设计文档

- [设计规格](docs/design-luanma-shanhaijing.md)
- [实施计划](docs/plans/)
````

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: README"
```

---

## 完成判据

全部任务做完后，以下每一条都要能亲眼看到：

- [ ] `python -m pytest tests/ -v` 全绿，且包含 3 只妖 × 3 条一致性断言
- [ ] 改坏任意一条 `expect`，测试变红（Task 8 Step 4 已演练）
- [ ] `python scripts/build_fonts.py` 产出两个 woff2，且打印出竖排 feature
- [ ] 把 `--layout-features` 改空，脚本报错退出（Task 10 Step 4 已演练）
- [ ] `git log --oneline` 有 11 次以上提交，每次一件事

## 下一份计划（不在本计划范围）

Astro 站点、妖形 SVG 渲染组件、条目页、Cloudflare Pages 部署。
依赖本计划产出的妖谱与字体产物。
