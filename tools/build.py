# -*- coding: utf-8 -*-
"""《埃及口语》静态站点生成器。

用法：python tools/build.py
输入：tools/data/unit-01.json ... unit-15.json + tools/content_extra.py
输出：books/egyptian-arabic/ 下的教材首页、15 个单元页与 5 个专题页。
总导航页 index.html 由 assets/catalog.js 数据驱动，无需本脚本重新生成。
"""
import html
import json
import re
from pathlib import Path

from content_extra import (ALPHABET, BOOK_INFO, CONSONANTS, SCRIPT_NOTES,
                           STRUCTURE, VOWELS)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data"
OUT = ROOT / "books" / "egyptian-arabic"
OUT.mkdir(parents=True, exist_ok=True)
REL = "../../"

UNITS = [json.loads((DATA / ("unit-%02d.json" % i)).read_text(encoding="utf-8")) for i in range(1, 16)]

AR_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]"
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s\u064B-\u065F\u0670\u200C\u200D"
    r"،؛؟«»\-—….,;:!?()\u00A0]*"
)


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def ar(t, cls=""):
    return '<span class="ar %s" dir="rtl" lang="ar">%s</span>' % (cls, esc(t))


def rich(t):
    """中文文本里夹杂的阿拉伯文片段自动包成 RTL，保证混排方向正确。"""
    t = str(t or "")
    out, last = [], 0
    for m in AR_RE.finditer(t):
        seg = m.group(0)
        core = seg.rstrip()
        tail = seg[len(core):]
        out.append(esc(t[last:m.start()]))
        out.append(ar(core))
        out.append(esc(tail))
        last = m.end()
    out.append(esc(t[last:]))
    return "".join(out)


def say(t):
    return '<button class="speak-btn" data-say="%s" title="朗读该句">▸ 朗读</button>' % esc(t)


def roman(t):
    if not t:
        return ""
    return '<div class="roman">原书罗马音：%s</div>' % esc(t)


def crumb(items):
    """items: [(文字, 链接或 None), ...]"""
    parts = []
    for i, (label, href) in enumerate(items):
        if i:
            parts.append('<span class="sep">›</span>')
        if href:
            parts.append('<a href="%s">%s</a>' % (href, esc(label)))
        else:
            parts.append('<span class="cur">%s</span>' % esc(label))
    return '<nav class="crumb" aria-label="面包屑">%s</nav>' % "".join(parts)


def shell(title, crumb_html, body, footer_nav, desc="", unit_id=None, tools=True):
    roman_btn = ('<button class="btn btn-sm btn-roman" data-roman-toggle onclick="toggleRoman()">原书罗马音</button>'
                 if tools else "")
    header = """<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{r}index.html"><span class="brand-mark">ع</span> 阿拉伯语口语学习站 <span class="brand-sub">《埃及口语》</span></a>
    <span class="header-spacer"></span>
    <div class="header-tools">
      <a class="header-back" href="{r}index.html"><span class="lbl-long">← 返回总导航</span><span class="lbl-short">← 总导航</span></a>
      <a class="btn btn-ghost btn-sm btn-to-book" href="index.html">教材首页</a>
      {btn}
    </div>
  </div>
  <div class="progressbar" id="scroll-progress"></div>
</header>""".format(r=REL, btn=roman_btn)
    footer = """<footer class="site-footer wrap">
  <div class="fl">
    <div>《埃及口语》· 本站第 01 册　|　本页内容依据 Routledge《Colloquial Arabic of Egypt》第三版重编，阿拉伯文已加注完整元音，讲解为中文。</div>
    <div><a href="index.html">教材首页</a>　·　<a href="{r}index.html">返回总导航 ↑</a></div>
  </div>
</footer>""".format(r=REL)
    done_attr = (' data-unit-id="%s"' % unit_id) if unit_id else ""
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 埃及口语 · 阿拉伯语口语学习站</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{r}assets/style.css">
<link rel="icon" type="image/svg+xml" href="{r}assets/favicon.svg">
</head>
<body{uid}>
{header}
<main class="wrap">
{crumb}
{body}
{footer_nav}
</main>
{footer}
<script src="{r}assets/app.js"></script>
</body>
</html>
""".format(title=esc(title), desc=esc(desc or "面向中国学习者的埃及口语阿拉伯语教材页面"),
           r=REL, uid="", header=header, crumb=crumb_html, body=body,
           footer_nav=footer_nav, footer=footer, done_attr=done_attr)


def back_strip(current):
    return """<div class="return-strip">
  <span class="rs-label">当前位置</span>
  <a class="pill" href="{r}index.html">① 总导航</a>
  <span>›</span>
  <a class="pill" href="index.html">② 教材首页</a>
  <span>›</span>
  <span class="pill gold">{cur}</span>
  <span style="margin-left:auto"><a href="{r}index.html">← 返回总导航</a>　·　<a href="index.html">↑ 返回教材首页</a></span>
</div>""".format(r=REL, cur=esc(current))


def std_footer(links):
    """links: [(label, href, primary?)]"""
    inner = "".join(
        '<a class="btn %s" href="%s">%s</a>' % ("btn-primary" if p else "", h, esc(l))
        for l, h, p in links
    )
    return '<nav class="footer-nav"><div class="group">%s</div><div class="group"><a class="btn" href="%sindex.html">↑ 返回总导航</a></div></nav>' % (inner, REL)


# ---------------------------------------------------------------- 单元页
def unit_nav_html(u, mod_list, idx):
    prev_link = ("unit-%02d.html" % (idx - 1)) if idx > 1 else "index.html"
    next_link = ("unit-%02d.html" % (idx + 1)) if idx < 15 else "grammar.html"
    links = [
        ("← 上一单元" if idx > 1 else "← 教材首页", prev_link, False),
        ("教材首页", "index.html", False),
        ("下一单元 →" if idx < 15 else "语法总表 →", next_link, True),
    ]
    return std_footer(links)


def build_unit(u, idx, page_path):
    num = u["id"]
    modules = []
    if u.get("goals"):
        modules.append(("goals", "学习目标"))
    if u.get("dialogues"):
        modules.append(("dialogues", "情景对话"))
    if u.get("vocab"):
        modules.append(("vocab", "词汇表"))
    if u.get("grammar"):
        modules.append(("grammar", "语法要点"))
    if u.get("exercises"):
        modules.append(("exercises", "练习"))
    if u.get("cultural_point"):
        modules.append(("culture", "文化点滴"))
    if u.get("letters"):
        modules.append(("letters", "本课字母"))
    if u.get("is_review"):
        modules.append(("review", "复习清单"))
    modules.append(("summary", "本单元小结"))

    hero = """<section class="unit-hero" data-num="{n:02d}">
  <div class="u-kicker">第 {n} 单元 · {level} {review}</div>
  <h1>{title}</h1>
  <div class="u-ar" dir="rtl" lang="ar">{ar}</div>
  <div class="u-sub">{sub}</div>
  <div class="u-roman">原书标题转写：{rom}</div>
  <div style="margin-top:14px;display:flex;gap:9px;flex-wrap:wrap;align-items:center">
    <button class="btn btn-sm" id="mark-done" data-unit-id="{n}" onclick="markDone('{n}',this)">标记本单元已学完</button>
    <span class="badge-done" id="done-badge" data-unit-id="{n}"></span>
  </div>
</section>""".format(n=num, level=esc(u.get("level_zh", "")), review="· 复习单元" if u.get("is_review") else "",
                     title=esc(u["title_zh"]), ar=esc(u["title_ar"]),
                     sub=esc(u.get("subtitle_zh", "")), rom=esc(u.get("title_roman", "")))

    mnav = '<nav class="module-nav">' + "".join(
        '<a href="#%s">%s</a>' % (k, esc(v)) for k, v in modules
    ) + "</nav>"

    blocks = []

    if u.get("goals"):
        blocks.append('<section class="block" id="goals"><h2><span class="zh-num">01</span> 学习目标</h2><ul class="goals">%s</ul></section>'
                      % "".join("<li>%s</li>" % rich(g) for g in u["goals"]))

    if u.get("dialogues"):
        ds = []
        for d in u["dialogues"]:
            lines = []
            for ln in d.get("lines", []):
                lines.append("""<div class="dline">
  <div class="who">%s</div>
  <div class="txt">
    <div class="ar-main" dir="rtl" lang="ar">%s</div>
    <div class="zh">%s %s</div>
    %s
  </div>
</div>""" % (esc(ln.get("speaker_zh", "")), esc(ln.get("ar", "")), rich(ln.get("zh", "")),
             say(ln.get("ar", "")), roman(ln.get("roman", ""))))
            ds.append("""<div class="dialog">
  <div class="dialog-head"><h3>%s　<span class="d-ar" dir="rtl" lang="ar">%s</span></h3><p>%s</p></div>
  %s
</div>""" % (esc(d.get("title_zh", "")), esc(d.get("title_ar", "")),
             rich(d.get("context_zh", "")), "".join(lines)))
        blocks.append('<section class="block" id="dialogues"><h2><span class="zh-num">02</span> 情景对话</h2>%s</section>' % "".join(ds))

    if u.get("vocab"):
        rows = []
        for v in u["vocab"]:
            note = v.get("note_zh", "")
            rows.append("<tr><td class='ar-cell'>%s</td><td class='zh-cell'>%s %s</td><td class='note-cell'>%s%s</td></tr>"
                        % (esc(v.get("ar", "")), rich(v.get("zh", "")), say(v.get("ar", "")),
                           rich(note), roman(v.get("roman", ""))))
        blocks.append("""<section class="block" id="vocab"><h2><span class="zh-num">03</span> 词汇表 <span class="hint" style="font-size:12px;color:var(--ink-3);font-weight:400">共 %d 条 · 可检索阿拉伯文／中文／罗马音</span></h2>
  <div class="filter-bar"><input type="search" placeholder="输入中文、阿拉伯文或原书罗马音检索本单元词汇……" oninput="filterRows(this,'vocab-table','vocab-count')"><span style="font-size:12.5px;color:var(--ink-3)">显示 <strong id="vocab-count">%d</strong> 条</span></div>
  <div class="tbl-wrap"><table id="vocab-table"><thead><tr><th>阿拉伯文（带元音）</th><th>中文</th><th>用法提示 / 原书转写</th></tr></thead><tbody>%s</tbody></table></div>
</section>""" % (len(u["vocab"]), len(u["vocab"]), "".join(rows)))

    if u.get("grammar"):
        gs = []
        for g in u["grammar"]:
            exs = []
            for e in g.get("examples", []):
                exs.append('<div class="ex-row"><div class="e-ar" dir="rtl" lang="ar">%s %s</div><div class="e-zh">%s%s</div></div>'
                           % (esc(e.get("ar", "")), say(e.get("ar", "")), rich(e.get("zh", "")), roman(e.get("roman", ""))))
            tip = ('<div class="g-tip">%s</div>' % rich(g["tip_zh"])) if g.get("tip_zh") else ""
            gs.append('<div class="gram-card"><h3>%s</h3><div class="g-body">%s</div><div class="ex-list">%s</div>%s</div>'
                      % (esc(g.get("title_zh", "")), rich(g.get("body_zh", "")), "".join(exs), tip))
        blocks.append('<section class="block" id="grammar"><h2><span class="zh-num">04</span> 语法要点</h2>%s</section>' % "".join(gs))

    if u.get("exercises"):
        ex = []
        total_items = sum(len(e.get("items", [])) for e in u["exercises"])
        for e in u["exercises"]:
            items = []
            for k, it in enumerate(e.get("items", []), 1):
                ans = '<div class="answer">%s %s<br>%s</div>' % (
                    ar(it.get("answer_ar", "")), say(it.get("answer_ar", "")), rich(it.get("answer_zh", "")))
                items.append('<div class="ex-item"><div class="n">%d</div><div><div class="q">%s</div>'
                             '<button class="ans-toggle" onclick="toggleAnswer(this)">查看参考答案</button>%s</div></div>'
                             % (k, rich(it.get("q_zh", "")), ans))
            ex.append('<div class="ex-group"><h3>%s</h3><div class="e-prompt">%s</div>%s</div>'
                      % (esc(e.get("title_zh", "")), rich(e.get("prompt_zh", "")), "".join(items)))
        blocks.append("""<section class="block" id="exercises"><h2><span class="zh-num">05</span> 练习与参考答案 <span class="hint" style="font-size:12px;color:var(--ink-3);font-weight:400">共 %d 小题</span></h2>
  <div class="filter-bar" style="margin-bottom:16px"><button class="btn btn-sm" onclick="toggleAllAnswers(true)">展开全部答案</button><button class="btn btn-sm" onclick="toggleAllAnswers(false)">收起全部答案</button><span style="font-size:12.5px;color:var(--ink-3)">答案均为带元音阿拉伯文，可点击朗读</span></div>
  %s</section>""" % (total_items, "".join(ex)))

    cp = u.get("cultural_point") or {}
    if cp:
        tip = ('<div class="tip">%s</div>' % rich(cp["tip_zh"])) if cp.get("tip_zh") else ""
        blocks.append('<section class="block" id="culture"><h2><span class="zh-num">06</span> 文化点滴</h2><div class="culture-box"><h3>%s</h3><p>%s</p>%s</div></section>'
                      % (esc(cp.get("title_zh", "")), rich(cp.get("body_zh", "")), tip))

    if u.get("letters"):
        cards = []
        for l in u["letters"]:
            cards.append('<div class="letter-card"><div class="lg" dir="rtl" lang="ar">%s</div><div class="ln">%s　<span style="font-size:12px;color:var(--ink-3)">%s</span></div><div class="ls">%s<br>%s</div></div>'
                         % (esc(l.get("ar", "")), esc(l.get("name_zh", "")), esc(l.get("name_ar", "")),
                            rich(l.get("sound_zh", "")), rich(l.get("note_zh", ""))))
        blocks.append('<section class="block" id="letters"><h2><span class="zh-num">07</span> 本单元所学字母</h2><div class="letter-grid">%s</div><p style="font-size:13px;color:var(--ink-3);margin:14px 0 0">字母按教材各单元末尾的书写部分逐个引入；<a href="alphabet.html">查看完整字母表 →</a></p></section>'
                      % "".join(cards))

    if u.get("is_review"):
        rv = u.get("review") or {}
        parts = ['<section class="block" id="review"><h2><span class="zh-num">R</span> 复习与自评</h2>']
        if rv.get("checklist"):
            parts.append('<h3 style="font-size:16px;margin:0 0 10px">学完前七单元，我能做到：</h3><ul class="review-list">%s</ul>'
                         % "".join("<li>%s</li>" % rich(x) for x in rv["checklist"]))
        if rv.get("tasks"):
            parts.append('<h3 style="font-size:16px;margin:22px 0 10px">复习活动与延展任务</h3><ul class="review-list">%s</ul>'
                         % "".join("<li>%s</li>" % rich(x) for x in rv["tasks"]))
        parts.append('</section>')
        blocks.append("".join(parts))

    blocks.append('<section class="block" id="summary"><h2><span class="zh-num">✓</span> 本单元小结</h2><div class="summary-box">%s</div><div style="margin-top:14px"><button class="btn btn-sm" id="mark-done-2" onclick="markDone(\'%s\',document.getElementById(\'mark-done\'))">标记本单元已学完</button></div></section>'
                  % (rich(u.get("summary_zh", "")), num))

    body = back_strip("第 %02d 单元 · %s" % (num, u["title_zh"])) + hero + mnav + "".join(blocks)
    cr = crumb([("总导航", REL + "index.html"), ("《埃及口语》", "index.html"),
                ("第 %02d 单元 · %s" % (num, u["title_zh"]), None)])
    page = shell("第 %02d 单元 %s" % (num, u["title_zh"]), cr, body,
                 unit_nav_html(u, modules, num),
                 desc="埃及口语第 %d 单元：%s。带完整元音标注的阿拉伯语对话、词汇、语法与练习，中文精讲。" % (num, u["title_zh"]))
    (OUT / ("unit-%02d.html" % num)).write_text(page, encoding="utf-8")


# ---------------------------------------------------------------- 教材首页
def build_book_index():
    toc = []
    for u in UNITS:
        n = u["id"]
        bits = []
        if u.get("dialogues"):
            bits.append("对话 %d 段" % len(u["dialogues"]))
        if u.get("vocab"):
            bits.append("词汇 %d 条" % len(u["vocab"]))
        if u.get("grammar"):
            bits.append("语法 %d 点" % len(u["grammar"]))
        toc.append("""<a class="toc-card %s" href="unit-%02d.html">
  <div class="toc-num">%02d</div>
  <div class="toc-body">
    <div class="toc-title">%s</div>
    <div class="toc-ar" dir="rtl" lang="ar">%s</div>
    <div class="toc-sub">%s</div>
    <div class="toc-meta">%s</div>
  </div>
  <span class="toc-check" data-unit-id="%d"></span>
</a>""" % ("is-review" if u.get("is_review") else "", n, n, esc(u["title_zh"]), esc(u["title_ar"]),
           esc(u.get("subtitle_zh", "")), "".join("<span>%s</span>" % esc(b) for b in bits), n))

    resources = [
        ("基础", "发音与转写规则", "原书 The sounds of Arabic 中文版：辅音、元音、重音、叠音，以及罗马音 → 带元音阿拉伯文的完整对照。", "sounds.html"),
        ("基础", "阿拉伯字母表", "28 个字母＋圆体 ة：字母名称、标准语与埃及口语读音对比、连写规则，按单元索引所学字母。", "alphabet.html"),
        ("总表", "语法结构总表", "原书 Structure summary 的 19 个专题中文梳理，并汇总 15 个单元的全部语法点入口。", "grammar.html"),
        ("总表", "分类词汇总表", "15 个单元全部词条汇总，可按中文、阿拉伯文或原书罗马音检索，点击即可朗读。", "glossary.html"),
        ("书写", "阿拉伯文字书写补充", "元音符号、长元音、连写、太阳字母、ق 的埃及读法、数字等书写要点。", "script.html"),
    ]
    reshtml = "".join(
        '<a class="resource-card" href="%s"><div class="rk">%s</div><h3>%s</h3><p>%s</p></a>' % (h, esc(k), esc(t), esc(d))
        for k, t, d, h in resources)

    hero = """<section class="hero">
  <p class="eyebrow">教材 01 / 已接入 · 埃及方言</p>
  <h1>《埃及口语》</h1>
  <div class="hero-ar" dir="rtl" lang="ar">{ar}</div>
  <p>{intro}</p>
  <div class="hero-meta"><span class="hero-chip">15 个单元（含 2 个复习单元）</span><span class="hero-chip">零起点 → B1</span><span class="hero-chip">带元音阿拉伯文</span><span class="hero-chip">中文精讲</span></div>
</section>""".format(ar=esc(BOOK_INFO["title_ar"]), intro=esc(BOOK_INFO["rewrite"]))

    body = back_strip("教材首页") + hero
    body += """<div class="note-band" style="margin-top:22px"><strong>本册在学习站中的位置：</strong>《埃及口语》是总导航页中的<strong>第 01 册</strong>，也是目前唯一已接入的教材；总导航页还预留了若干同层级的空白教材位。<strong>本册不等于学习站的全部内容</strong>。任何时候点击页顶「返回总导航」即可回到教材选择层。</div>"""

    body += """<section class="section"><div class="section-head"><h2>教材信息</h2><span class="hint">依据原书版权页与前言</span></div>
<div class="info-grid">
  <div class="info-card"><div class="k">原书</div><div class="v">Colloquial Arabic of Egypt</div><div class="d">The Complete Course for Beginners</div></div>
  <div class="info-card"><div class="k">作者</div><div class="v">简·怀特威克／马哈茂德·加法尔</div><div class="d">{authors}</div></div>
  <div class="info-card"><div class="k">版本</div><div class="v">Routledge 第三版（2014）</div><div class="d">Colloquial 系列</div></div>
  <div class="info-card"><div class="k">目标水平</div><div class="v">零起点 → B1</div><div class="d">{level}</div></div>
</div>
<div class="block" style="margin-top:8px"><div class="g-body" style="font-size:14px;line-height:1.9">{intro}</div></div>
</section>""".format(authors=esc(BOOK_INFO["authors"]), level=esc(BOOK_INFO["level"]), intro=esc(BOOK_INFO["intro"]))

    body += """<section class="section"><div class="section-head"><h2>学习流程</h2><span class="hint">从教材首页逐级展开，每页均可返回</span></div>
<div class="block"><div class="path-flow">
<span class="path-node"><a href="{r}index.html">① 总导航</a></span><span class="path-arrow">→</span>
<span class="path-node on">② 教材首页（本页）</span><span class="path-arrow">→</span>
<span class="path-node">③ 选择单元 / 专题</span><span class="path-arrow">→</span>
<span class="path-node">④ 单元内：对话 → 词汇 → 语法 → 练习</span><span class="path-arrow">→</span>
<span class="path-node">⑤ 返回教材首页 / 总导航</span></div>
<p style="font-size:13.5px;color:var(--ink-2);margin:14px 0 0">建议顺序：先读「发音与转写规则」与「阿拉伯字母表」，再按单元编号循序渐进；第 08、15 单元为复习。每单元页顶部有模块导航，底部有上一单元／下一单元与返回入口。</p></div></section>""".format(r=REL)

    body += """<section class="section" id="toc"><div class="section-head"><h2>单元目录</h2><span class="hint">已学 <strong id="progress-count">0</strong> / 15 单元 · 进度仅保存在本机浏览器</span></div>
<div style="height:6px;background:var(--line-2);border-radius:4px;overflow:hidden;margin-bottom:18px"><div id="progress-bar" style="height:100%;width:0;background:linear-gradient(90deg,var(--teal),var(--gold));transition:width .3s"></div></div>
<div class="toc-grid">__TOC__</div></section>""".replace("__TOC__", "".join(toc))

    body += """<section class="section"><div class="section-head"><h2>专题与工具页</h2><span class="hint">与单元同属本册，随时可返回总导航</span></div><div class="resource-grid">%s</div></section>""" % reshtml

    cr = crumb([("总导航", REL + "index.html"), ("《埃及口语》", None)])
    nav = std_footer([("← 返回总导航", REL + "index.html", False),
                      ("发音与字母", "sounds.html", False),
                      ("从第 01 单元开始 →", "unit-01.html", True)])
    (OUT / "index.html").write_text(shell("教材首页", cr, body, nav,
                                          desc="《埃及口语》教材首页：15 个单元目录、发音与字母、语法总表、词汇总表等完整学习流程入口。"),
                                    encoding="utf-8")


# ---------------------------------------------------------------- 专题页
def topic_page(title, sub, crumb_items, blocks, desc, current):
    hero = """<section class="hero" style="padding:32px 38px">
  <p class="eyebrow">教材 01 · 专题</p>
  <h1 style="font-size:28px">%s</h1>
  <p style="margin-top:10px">%s</p>
</section>""" % (esc(title), esc(sub))
    body = back_strip(current) + hero + "".join(blocks)
    cr = crumb(crumb_items)
    nav = std_footer([("← 教材首页", "index.html", False),
                      ("单元目录", "index.html#toc", False),
                      ("↑ 返回总导航", REL + "index.html", True)])
    return shell(title, cr, body, nav, desc=desc)


def build_sounds():
    rows_c = "".join("<tr><td class='ar-cell'>%s</td><td class='zh-cell'><strong>%s</strong></td><td class='note-cell'>%s</td></tr>"
                     % (ar(sym) if any("\u0600" <= ch <= "\u06ff" for ch in sym) else esc(sym),
                        esc(s), rich(d)) for s, sym, d in CONSONANTS)
    rows_v = "".join("<tr><td class='ar-cell'>%s</td><td class='zh-cell'><strong>%s</strong></td><td class='note-cell'>%s</td></tr>"
                     % (esc(sym), esc(s), rich(d)) for s, sym, d in VOWELS)
    blocks = [
        '<section class="section"><div class="section-head"><h2>原书为什么用罗马音，本站为什么改写</h2></div><div class="block"><div class="g-body" style="font-size:14px;line-height:1.9">原书正文通篇用罗马音转写阿拉伯语，因为它能同时标出元音与重音，而普通阿拉伯文不写短元音；书末另附阿拉伯文字补充与双向词汇表。本站把每个词改成<strong>带完整元音符号的阿拉伯文</strong>：读音信息一点不丢，中国学习者还能直接建立字形与读音的联系。原书罗马音在各页面默认收起，需要核对重音时可点页顶「显示原书罗马音」。</div></div></section>',
        '<section class="section"><div class="section-head"><h2>需要特别留意的辅音</h2><span class="hint">原书 The sounds of Arabic，中文改写</span></div><div class="block"><div class="tbl-wrap"><table><thead><tr><th>阿拉伯文</th><th>原书罗马音</th><th>发音要领</th></tr></thead><tbody>%s</tbody></table></div></div></section>' % rows_c,
        '<section class="section"><div class="section-head"><h2>元音与双元音</h2><span class="hint">本站按此对应关系加注元音符号</span></div><div class="block"><div class="tbl-wrap"><table><thead><tr><th>阿拉伯文写法</th><th>原书罗马音</th><th>读法说明</th></tr></thead><tbody>%s</tbody></table></div></div></section>' % rows_v,
        """<section class="section"><div class="section-head"><h2>叠音、重音与元音变体</h2></div><div class="block">
<div class="gram-card"><h3>叠辅音要读满两倍</h3><div class="g-body">原书提醒：双辅音的时长约为单辅音的两倍，可以想象中间有个连字符，如 مُدَرِّس（mudár-ris，老师）、هُوَّه（húw-wa，他）。本站用 شَدَّة（ّ）标出叠音。</div></div>
<div class="gram-card"><h3>重音会随词尾移动</h3><div class="g-body">原书罗马音用锐音符标重音，如 يِكْتِب、هُوَّه。加上接尾代词后重音常后移：مُدَرِّس → مُدَرِّسَة → مُدَرِّسِين。这是埃及口语的显著特点，教材在各单元随文说明。</div></div>
<div class="gram-card"><h3>口语元音没有唯一写法</h3><div class="g-body">同一个词，「写」这个动词在标准语读 yáktub，埃及口语读 yíktib；「我不想要」有人读 mush 9áawiz，也有人读 mish 9áayiz；「你」可以写作 énta、ínta 或 ánta。原书建议：罗马音仅供参照，最终以听音模仿为准。本站按教材选定的读法加注元音。</div></div>
</div></section>""",
        '<section class="section"><div class="section-head"><h2>继续学习</h2></div><div class="block"><div class="resource-grid"><a class="resource-card" href="alphabet.html"><div class="rk">下一步</div><h3>阿拉伯字母表</h3><p>字母名称、标准语与埃及读音对比、连写规则。</p></a><a class="resource-card" href="unit-01.html"><div class="rk">开始正课</div><h3>第 01 单元 · 你好，欢迎！</h3><p>问候、姓名、来源地，以及第一批四个字母。</p></a><a class="resource-card" href="index.html"><div class="rk">返回</div><h3>教材首页</h3><p>查看 15 个单元与全部专题入口。</p></a></div></div></section>',
    ]
    (OUT / "sounds.html").write_text(topic_page(
        "发音与转写规则", "辅音、元音、重音与叠音；罗马音 → 带元音阿拉伯文的完整对照。",
        [("总导航", REL + "index.html"), ("《埃及口语》", "index.html"), ("发音与转写规则", None)],
        blocks, "埃及阿拉伯语发音规则中文版，含罗马音转写与带元音阿拉伯文的对照表。", "专题 · 发音与转写规则"),
        encoding="utf-8")


def build_alphabet():
    rows = "".join("<tr><td class='ar-cell' style='font-size:28px'>%s</td><td class='zh-cell'>%s<br><span style='font-size:12px;color:var(--ink-3)'>%s</span></td><td class='note-cell'>%s</td><td class='note-cell'>%s</td><td class='note-cell'>%s</td></tr>"
                   % (esc(a[0]), esc(a[1]), esc(a[2]), esc(a[3]), esc(a[4]), esc(a[5])) for a in ALPHABET)
    by_unit = []
    for u in UNITS:
        if u.get("letters"):
            ls = "　".join("%s %s" % (l.get("ar", ""), l.get("name_zh", "")) for l in u["letters"])
            by_unit.append('<a class="toc-card" href="unit-%02d.html#letters"><div class="toc-num">%02d</div><div class="toc-body"><div class="toc-title">%s</div><div class="toc-sub" dir="rtl" lang="ar" style="font-family:var(--font-ar);font-size:17px;color:var(--teal)">%s</div></div></a>'
                           % (u["id"], u["id"], esc(u["title_zh"]), esc(ls)))
    blocks = [
        '<section class="section"><div class="section-head"><h2>完整字母表</h2><span class="hint">28 个字母＋阴性词尾 ة · 标准语与埃及口语读音对照</span></div><div class="block"><div class="tbl-wrap"><table><thead><tr><th>字母</th><th>名称（阿拉伯文／中文）</th><th>原书转写名</th><th>标准语读音</th><th>埃及口语读音</th></tr></thead><tbody>%s</tbody></table></div><p style="font-size:13px;color:var(--ink-3);margin:14px 0 0">字母顺序依据原书 The Arabic alphabet 一表。表中「9」是原书用来表示 ع 的数字，不是数词九；大写 H / S / D / T / Z 表示强调音或特殊辅音。</p></div></section>' % rows,
        '<section class="section"><div class="section-head"><h2>按单元逐步认识字母</h2><span class="hint">教材把字母分散在各单元末尾的书写部分</span></div><div class="toc-grid">%s</div></section>' % "".join(by_unit),
        '<section class="section"><div class="section-head"><h2>书写要点</h2></div><div class="block">%s<p style="margin-top:14px"><a href="script.html">查看完整书写补充 →</a></p></div></section>'
        % "".join('<div class="gram-card"><h3>%s</h3><div class="g-body">%s</div></div>' % (esc(k), rich(v))
                  for k, v in SCRIPT_NOTES[:4]),
    ]
    (OUT / "alphabet.html").write_text(topic_page(
        "阿拉伯字母表", "28 个字母与阴性词尾 ة：名称、标准语／埃及读音对比，以及各单元所学字母索引。",
        [("总导航", REL + "index.html"), ("《埃及口语》", "index.html"), ("阿拉伯字母表", None)],
        blocks, "阿拉伯语字母表中文版，含埃及口语读音与标准语对比、按单元学习顺序。", "专题 · 阿拉伯字母表"),
        encoding="utf-8")


def build_grammar():
    cards = "".join('<div class="gram-card"><h3>%s · %s</h3><div class="g-body">%s</div></div>'
                    % (esc(n), esc(t), rich(d)) for n, t, d in STRUCTURE)
    idx = []
    for u in UNITS:
        if not u.get("grammar"):
            continue
        links = "".join('<li><a href="unit-%02d.html#grammar">%s</a></li>' % (u["id"], esc(g.get("title_zh", "")))
                        for g in u["grammar"])
        idx.append('<div class="info-card"><div class="k">第 %02d 单元 · %s</div><ul class="review-list" style="margin-top:9px;gap:4px">%s</ul></div>'
                   % (u["id"], esc(u["title_zh"]), links))
    blocks = [
        '<section class="section"><div class="section-head"><h2>原书 Structure summary · 19 个语法专题</h2><span class="hint">中文梳理，便于查阅</span></div><div class="block">%s</div></section>' % cards,
        '<section class="section"><div class="section-head"><h2>按单元查阅全部语法点</h2><span class="hint">点击直接跳到对应单元的「语法要点」</span></div><div class="info-grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">%s</div></section>' % "".join(idx),
    ]
    (OUT / "grammar.html").write_text(topic_page(
        "语法结构总表", "原书 Structure summary 的 19 个专题中文梳理，并汇总 15 个单元全部语法点入口。",
        [("总导航", REL + "index.html"), ("《埃及口语》", "index.html"), ("语法结构总表", None)],
        blocks, "埃及阿拉伯语语法结构总表，19 个专题与 15 单元语法点索引。", "专题 · 语法结构总表"),
        encoding="utf-8")


def build_glossary():
    total = sum(len(u.get("vocab", [])) for u in UNITS)
    rows = []
    for u in UNITS:
        for v in u.get("vocab", []):
            rows.append("<tr><td class='ar-cell'>%s</td><td class='zh-cell'>%s %s</td><td class='note-cell'>%s</td><td class='note-cell'><a href='unit-%02d.html#vocab'>第 %02d 单元</a>%s</td></tr>"
                        % (esc(v.get("ar", "")), rich(v.get("zh", "")), say(v.get("ar", "")),
                           rich(v.get("note_zh", "")), u["id"], u["id"], roman(v.get("roman", ""))))
    blocks = ["""<section class="section"><div class="section-head"><h2>全部词条</h2><span class="hint">共 %d 条 · 来自 15 个单元教材原表</span></div>
<div class="block"><div class="filter-bar"><input type="search" placeholder="检索中文、阿拉伯文或原书罗马音……" oninput="filterRows(this,'glossary-table','glossary-count')"><span style="font-size:12.5px;color:var(--ink-3)">显示 <strong id="glossary-count">%d</strong> 条</span><button class="btn btn-sm" data-roman-toggle onclick="toggleRoman()">原书罗马音</button></div>
<div class="tbl-wrap"><table id="glossary-table"><thead><tr><th>阿拉伯文（带元音）</th><th>中文</th><th>用法提示</th><th>出处 / 原书转写</th></tr></thead><tbody>%s</tbody></table></div></div></section>""" % (total, total, "".join(rows))]
    (OUT / "glossary.html").write_text(topic_page(
        "分类词汇总表", "15 个单元全部 %d 条词条，可按中文、阿拉伯文或原书罗马音检索，点击即可朗读。" % total,
        [("总导航", REL + "index.html"), ("《埃及口语》", "index.html"), ("分类词汇总表", None)],
        blocks, "埃及口语教材全部词汇中文对照表，带元音阿拉伯文与检索功能。", "专题 · 分类词汇总表"),
        encoding="utf-8")


def build_script():
    cards = "".join('<div class="gram-card"><h3>%s</h3><div class="g-body">%s</div></div>' % (esc(k), rich(v))
                    for k, v in SCRIPT_NOTES)
    unit_letters = []
    for u in UNITS:
        if u.get("letters"):
            unit_letters.append('<div class="info-card"><div class="k">第 %02d 单元</div><div class="v" dir="rtl" lang="ar" style="font-family:var(--font-ar);font-size:26px;color:var(--teal)">%s</div><div class="d">%s</div></div>'
                                % (u["id"], " ".join(l.get("ar", "") for l in u["letters"]),
                                   esc("、".join(l.get("name_zh", "") for l in u["letters"]))))
    blocks = [
        '<section class="section"><div class="section-head"><h2>书写规则与本站改写说明</h2><span class="hint">依据原书 Arabic script supplement 与各单元书写部分</span></div><div class="block">%s</div></section>' % cards,
        '<section class="section"><div class="section-head"><h2>各单元新学字母一览</h2></div><div class="info-grid">%s</div></section>' % "".join(unit_letters),
        '<section class="section"><div class="section-head"><h2>相关页面</h2></div><div class="block"><div class="resource-grid"><a class="resource-card" href="alphabet.html"><div class="rk">字母</div><h3>完整字母表</h3><p>名称与读音对照。</p></a><a class="resource-card" href="sounds.html"><div class="rk">发音</div><h3>发音与转写规则</h3><p>罗马音与元音符号的对应。</p></a><a class="resource-card" href="index.html"><div class="rk">返回</div><h3>教材首页</h3><p>回到 15 个单元目录。</p></a></div></div></section>',
    ]
    (OUT / "script.html").write_text(topic_page(
        "阿拉伯文字书写补充", "元音符号、长元音、连写规则、太阳字母、ق 的埃及读法与数字书写。",
        [("总导航", REL + "index.html"), ("《埃及口语》", "index.html"), ("书写补充", None)],
        blocks, "阿拉伯文书写规则中文讲解，含元音符号与埃及口语拼写特点。", "专题 · 书写补充"),
        encoding="utf-8")


def main():
    for i, u in enumerate(UNITS, 1):
        build_unit(u, i, OUT)
    build_book_index()
    build_sounds()
    build_alphabet()
    build_grammar()
    build_glossary()
    build_script()
    files = sorted(p.name for p in OUT.glob("*.html"))
    print("已生成 %d 个页面：" % len(files))
    print("  " + "、".join(files))
    for p in sorted(OUT.glob("*.html"), key=lambda x: x.stat().st_size, reverse=True)[:5]:
        print("  %-24s %8.1f KB" % (p.name, p.stat().st_size / 1024))


if __name__ == "__main__":
    main()
