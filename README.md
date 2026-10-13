**English** | [简体中文](README.zh-CN.md)

# Luanma Shanhaijing: a bestiary of Chinese mojibake

A field guide to the monsters of Chinese mojibake. Every "glyph monster" (字妖) has a name, an appearance, and a cause that can be **reproduced byte for byte by running code**. The bestiary entries themselves are written in Chinese.

The title borrows from the *Shanhaijing* (山海经, Classic of Mountains and Seas), the ancient Chinese catalogue of strange creatures; *luanma* (乱码) is Chinese for mojibake.

## Why it is different from other mojibake collections

Every explanation is tied to a piece of executable reproduction code. The CI configuration (`.github/workflows/ci.yml`) runs the full set of assertions on every push and once a day, across Linux and Windows × Python 3.11, 3.13 and 3.14. **If an explanation ever stops being true, the tests turn red.**

> Note: the `schedule` trigger only runs on the repository's default branch, so the daily check starts once this
> branch is merged into the default branch and pushed. GitHub also disables scheduled workflows after 60 days
> without activity in the repository.

```python
>>> ("�" * 2).encode("utf-8").hex(" ")
'ef bf bd ef bf bd'
>>> ("�" * 2).encode("utf-8").decode("gbk")
'锟斤拷'
```

Two U+FFFD replacement characters are `EF BF BD EF BF BD` in UTF-8. Split into GBK double-byte pairs, they read exactly 锟 (`EF BF`) · 斤 (`BD EF`) · 拷 (`BF BD`).

### How much CI actually verifies

| Field | Asserted? |
|---|---|
| `expect` | ✅ the output of the reproduction function must equal it |
| `glyphs` | ✅ joined together they must equal `expect` (the monster's shape is the proof) |
| `bytes` | ✅ the real GBK encoding of each character must equal the claimed hex |
| `out` | ✅ must match `glyphs` |
| `hex_texture` | ✅ repeated several times and decoded as GBK, it must give `expect` |
| `why` / `notes` / `via` / `tag` | ❌ natural language, cannot be checked mechanically |

## Layout

| Path | Contents |
|---|---|
| `yao/` | the bestiary, one YAML file per monster |
| `src/luanma/` | loading, validation, reproduction |
| `tests/test_yaopu_integrity.py` | **consistency test over the whole bestiary: the foundation of this project** |
| `scripts/build_fonts.py` | font subsetting |
| `docs/design-luanma-shanhaijing.md` | design specification (Chinese) |

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/ -v
```

The original font files are not in the repository (they are large and can be downloaded again from upstream); the download locations are in the docstring of `scripts/build_fonts.py`:

```bash
python scripts/build_fonts.py
```

## Font licences

All fonts used here are licensed under SIL OFL 1.1; the licence texts are archived in `fonts/LICENSES/`. The CSS family names of the subset fonts (`YaoBrush` / `YaoSeal`) deliberately differ from the original font names, because subsetting counts as a modification under OFL FAQ 2.6.

| Use | Font | Licence |
|---|---|---|
| Monster glyphs and names (horizontal) | Ma Shan Zheng brush regular script | SIL OFL 1.1 |
| Vertical layout | GenRyuMin TW-R | SIL OFL 1.1 |
| Body text | system sans-serif (referenced by font-family only, no files distributed) | — |

**Ma Shan Zheng has no vertical metrics table**, so it is used strictly for horizontal text.

## License

The code is licensed under the [Apache License 2.0](LICENSE). The fonts keep their own licence, SIL OFL 1.1 (see "Font licences" above and `fonts/LICENSES/`).
