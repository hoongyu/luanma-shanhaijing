"""Build a self-contained font comparison page.

Subsetted woff2 files are base64-inlined so the page travels as one file.
Total inline weight is ~25KB -- the whole point of the subsetting step.
"""
import base64
import json
import pathlib

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"

CANDIDATES = [
    ("mashan", "sub-MaShanZheng-Regular.woff2", "马善政毛笔楷书", "SIL OFL 1.1",
     "毛笔行楷 · 提按飞白 · 唯一零风险强毛笔感"),
    ("genryuH", "sub-GenRyuMin2TW-H.woff2", "源流明體 H", "SIL OFL 1.1",
     "刻本明朝 · 最重字重 · 雕版压印厚度"),
    ("genryuB", "sub-GenRyuMin2TW-B.woff2", "源流明體 B", "SIL OFL 1.1",
     "刻本明朝 · 次重 · 可与 H 做层次"),
    ("genryuR", "sub-GenRyuMin2TW-R.woff2", "源流明體 R", "SIL OFL 1.1",
     "刻本明朝 · 常规 · 细笔层"),
    ("wenkai", "sub-LXGWWenKai-Regular.woff2", "霞鹜文楷", "SIL OFL 1.1",
     "钢笔楷 · 笔画克制 · 调研判定为正文而非妖形"),
]

faces, cards = [], []
for key, fn, name, lic, note in CANDIDATES:
    p = FONTS / fn
    if not p.exists():
        continue
    b64 = base64.b64encode(p.read_bytes()).decode()
    faces.append(
        f"@font-face{{font-family:'{key}';"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');font-display:block}}"
    )
    cards.append({"key": key, "name": name, "lic": lic,
                  "note": note, "kb": round(p.stat().st_size / 1024, 1)})

# 隶书 baseline uses the local system font -- included precisely to show
# that it is NOT a deployable option (absent on macOS/Linux/mobile).
cards.append({"key": "lisu", "name": "隶书 LiSu（现状）", "lic": "系统字体 · 不可部署",
              "note": "只有 Windows 有。别的平台看到的是回退字体", "kb": 0})
faces.append("@font-face{font-family:'lisu';src:local('LiSu'),local('隶书')}")

html = f"""<meta charset="utf-8">
<title>妖形字体对比</title>
<style>
{"".join(faces)}
:root{{--paper:#EAE3D5;--ink:#171410;--ink-55:rgba(23,20,16,.55);
--ink-12:rgba(23,20,16,.12);--zhu:#A32D22;
--hei:"PingFang SC","Microsoft YaHei","Noto Sans SC",sans-serif}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--paper);color:var(--ink);font-family:var(--hei);padding:38px 44px 64px;
 background-image:radial-gradient(circle at 18% 22%,rgba(0,0,0,.022) 0 1px,transparent 1px);
 background-size:6px 6px}}
h1{{font-size:17px;font-weight:600;letter-spacing:.24em;margin-bottom:6px}}
.sub{{font-size:12px;color:var(--ink-55);margin-bottom:32px;line-height:1.9}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:26px}}
.card{{border:1px solid var(--ink-12);padding:22px 20px 18px;background:rgba(255,252,244,.42)}}
.hd{{display:flex;align-items:baseline;gap:9px;margin-bottom:3px}}
.nm{{font-size:13.5px;font-weight:600}}
.kb{{font-size:10.5px;color:var(--zhu);font-variant-numeric:tabular-nums}}
.lic{{font-size:10px;color:var(--ink-55);letter-spacing:.1em;margin-bottom:2px}}
.note{{font-size:11px;color:var(--ink-55);line-height:1.8;margin-bottom:16px;min-height:36px}}
.raw{{font-size:62px;line-height:1.25;letter-spacing:.06em;margin-bottom:6px}}
.raw2{{font-size:34px;color:rgba(23,20,16,.62);margin-bottom:14px}}
svg{{display:block;overflow:visible;margin:0 auto}}
.cap{{font-size:10px;color:var(--ink-55);text-align:center;margin-top:8px;letter-spacing:.16em}}
</style>
<h1>妖形字体对比 · 锟斤拷</h1>
<div class="sub">
同一套构成规则（身／肢／尾／冠 + 十六进制底纹），只换字体。<br>
每款均为子集化后的 woff2，已 base64 内联 —— 整页字体总量约 {sum(c['kb'] for c in cards):.0f} KB。
</div>
<div class="grid" id="g"></div>
<script>
const CARDS = {json.dumps(cards, ensure_ascii=False)};
const NS='http://www.w3.org/2000/svg';
const G=['锟','斤','拷'];

function beast(key,i){{
  const W=250,H=262;
  const s=document.createElementNS(NS,'svg');
  s.setAttribute('width',W);s.setAttribute('height',H);
  s.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`);
  s.innerHTML=`<defs><pattern id="p${{i}}" width="118" height="24"
      patternUnits="userSpaceOnUse" patternTransform="rotate(-13)">
      <text x="0" y="14" font-family="ui-monospace,Consolas,monospace" font-size="10"
       fill="rgba(23,20,16,.16)" letter-spacing="2">EF BF BD</text></pattern></defs>`;
  const T=(ch,x,y,sz,op,rot,flip,fill)=>{{
    const t=document.createElementNS(NS,'text');
    t.setAttribute('font-family',key);t.setAttribute('font-size',sz);
    t.setAttribute('text-anchor','middle');t.setAttribute('dominant-baseline','central');
    t.setAttribute('opacity',op);if(fill)t.setAttribute('fill',fill);
    t.setAttribute('transform',
      `translate(${{x}} ${{y}}) rotate(${{rot||0}}) scale(${{flip?-1:1}} 1)`);
    t.textContent=ch;return t;
  }};
  const [a,b,c]=G;
  s.appendChild(T(a,W/2,H*.40,110,.93));
  s.appendChild(T(b,W/2-70,H*.62,55,.60,-17,false));
  s.appendChild(T(b,W/2+70,H*.62,55,.60,17,true));
  s.appendChild(T(c,W/2,H*.79,70,.74));
  s.appendChild(T(a,W/2-38,H*.14,29,.28,-24,false));
  s.appendChild(T(a,W/2+38,H*.14,29,.28,24,true));
  s.appendChild(T(a,W/2,H*.40,110,1,0,false,`url(#p${{i}})`));
  s.appendChild(T(c,W/2,H*.79,70,1,0,false,`url(#p${{i}})`));
  return s;
}}

const g=document.getElementById('g');
CARDS.forEach((c,i)=>{{
  const d=document.createElement('div');d.className='card';
  d.innerHTML=`<div class="hd"><span class="nm">${{c.name}}</span>
    <span class="kb">${{c.kb?c.kb+' KB':''}}</span></div>
    <div class="lic">${{c.lic}}</div><div class="note">${{c.note}}</div>
    <div class="raw" style="font-family:${{c.key}}">锟斤拷</div>
    <div class="raw2" style="font-family:${{c.key}}">烫烫烫 屯屯屯 锘</div>`;
  d.appendChild(beast(c.key,i));
  const cap=document.createElement('div');cap.className='cap';cap.textContent='同一构成规则';
  d.appendChild(cap);
  g.appendChild(d);
}});
</script>
"""

out = HERE / "compare.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out.name}  {out.stat().st_size/1024:.1f} KB")
for c in cards:
    print(f"  {c['name']:<22} {c['kb']:>6} KB")
