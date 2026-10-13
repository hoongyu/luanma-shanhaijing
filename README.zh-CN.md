[English](README.md) | **简体中文**

# 乱码山海经

中文乱码的妖怪图鉴。每一只「字妖」都有名字、形貌，以及**字节级精确、可运行复现**的成因。

## 为什么它和别的乱码大全不一样

每一条考据都绑定一段可执行的复现代码。CI 配置（`.github/workflows/ci.yml`）
会在每次 push 与每日定时运行全套断言，覆盖 Linux/Windows × Python 3.11/3.13/3.14。
**考据哪天不成立了，测试会红。**

> 注：`schedule` 触发器只在仓库默认分支上生效，所以每日验证要等本分支合入
> 默认分支并推送到远端之后才真正开始。GitHub 还会在仓库 60 天无活动后
> 自动停用定时任务。

```python
>>> ("\ufffd" * 2).encode("utf-8").hex(" ")
'ef bf bd ef bf bd'
>>> ("\ufffd" * 2).encode("utf-8").decode("gbk")
'锟斤拷'
```

两枚 U+FFFD 的 UTF-8 是 `EF BF BD EF BF BD`，按 GBK 双字节切开正是 锟(`EF BF`)·斤(`BD EF`)·拷(`BF BD`)。

### CI 验证到什么程度

| 字段 | 是否被断言 |
|---|---|
| `expect` | ✅ 复现函数的产出必须与之相等 |
| `glyphs` | ✅ 拼起来必须等于 `expect`（妖形即所证） |
| `bytes` | ✅ 每个字的真实 GBK 编码必须等于所声称的十六进制 |
| `out` | ✅ 必须与 `glyphs` 一致 |
| `hex_texture` | ✅ 重复若干次按 GBK 解码必须得到 `expect` |
| `why` / `notes` / `via` / `tag` | ❌ 自然语言，无法机械验证 |

## 目录

| 路径 | 内容 |
|---|---|
| `yao/` | 妖谱，一妖一个 YAML |
| `src/luanma/` | 加载、校验、复现 |
| `tests/test_yaopu_integrity.py` | **全谱一致性测试 —— 本项目的地基** |
| `scripts/build_fonts.py` | 字体子集化 |
| `docs/design-luanma-shanhaijing.md` | 设计规格 |

## 开发

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/ -v
```

字体原件不进仓库（体积大且可从上游重新下载），下载地址见 `scripts/build_fonts.py` 的 docstring：

```bash
python scripts/build_fonts.py
```

## 字体授权

本项目使用的字体均为 SIL OFL 1.1，原文归档在 `fonts/LICENSES/`。
子集化产物的 CSS family 名（`YaoBrush` / `YaoSeal`）刻意不同于原字体名 ——
子集化在 OFL FAQ 2.6 下算 modification。

| 用途 | 字体 | 授权 |
|---|---|---|
| 妖形与妖名（横排） | 马善政毛笔楷书 | SIL OFL 1.1 |
| 竖排版式 | 源流明體 TW-R | SIL OFL 1.1 |
| 说明正文 | 系统无衬线（仅 font-family 引用，不分发文件） | — |

**马善政没有竖排度量表**，因此严格限定于横排用途。
