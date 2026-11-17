# -*- coding: utf-8 -*-
"""《海湾口语》静态站点生成器（第 03 册）。

用法：python tools/gulf/build.py
输入：tools/gulf/data/unit-01.json ... unit-21.json + tools/gulf/content_extra.py
输出：books/gulf-arabic/ 下的教材首页、21 个单元页与 5 个专题页。
共享站点根的 assets/（样式、交互、注册表）与 audio/（配音）；不改动前两册任何页面。
"""
import html
import json
import re
import sys
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BOOK_DIR))
from content_extra import (ALPHABET, BOOK_INFO, CONSONANTS, SCRIPT_NOTES,
                           SOUNDS_NOTES, STRUCTURE, VOWELS)
import audio_spec as AUDIO

ROOT = BOOK_DIR.parents[1]
AUDIO_MAP = AUDIO.read_map()
DATA = BOOK_DIR / "data"
OUT = ROOT / "books" / "gulf-arabic"
OUT.mkdir(parents=True, exist_ok=True)
REL = "../../"
N_UNITS = 21
NARRATOR = AUDIO.NARRATOR_KEY
BOOK_ZH = "海湾口语"

UNITS = [json.loads((DATA / ("unit-%02d.json" % i)).read_text(encoding="utf-8"))
         for i in range(1, N_UNITS + 1)]

AR_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]"
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s\u064B-\u065F\u0670\u200C\u200D"
    r"،؛؟«»\-—….,;:!?()\u00A0]*"
)


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def pa(t, key=NARRATOR):
    """点击阿文发音：命中预生成 mp3 就给出页面相对音频路径。"""
    t = str(t if t is not None else "")
    src = AUDIO_MAP.get(AUDIO.map_key(t, key))
    if src:
        return ' data-audio="%s" data-say="%s" title="点击朗读"' % (esc(REL + src), esc(t))
    return ' data-say="%s"' % esc(t)


def ar(t, cls="", key=NARRATOR):
    return '<span class="ar %s playable" dir="rtl" lang="ar"%s>%s</span>' % (cls, pa(t, key), esc(t))


def rich(t):
    """中文文本里夹杂的阿拉伯文片段自动包成 RTL 且可点击发音。"""
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


def roman(t):
    if not t:
        return ""
    return '<div class="roman">原书罗马音：%s</div>' % esc(t)


def crumb(items):
    parts = []
    for i, (label, href) in enumerate(items):
        if i:
            parts.append('<span class="sep">›</span>')
        if href:
            parts.append('<a href="%s">%s</a>' % (href, esc(label)))
        else:
            parts.append('<span class="cur">%s</span>' % esc(label))
    return '<nav class="crumb" aria-label="面包屑">%s</nav>' % "".join(parts)


def shell(title, crumb_html, body, footer_nav, desc="", tools=True):
    roman_btn = ('<button class="btn btn-sm btn-roman" data-roman-toggle onclick="toggleRoman()">原书罗马音</button>'
                 if tools else "")
    header = """<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{r}index.html"><span class="brand-mark">ع</span> 阿拉伯语口语学习站 <span class="brand-sub">《{book}》</span></a>
    <span class="header-spacer"></span>
    <div class="header-tools">
      <a class="header-back" href="{r}index.html"><span class="lbl-long">← 返回总导航</span><span class="lbl-short">← 总导航</span></a>
      <a class="btn btn-ghost btn-sm btn-to-book" href="index.html">教材首页</a>
      {btn}
    </div>
  </div>
  <div class="progressbar" id="scroll-progress"></div>
</header>""".format(r=REL, book=BOOK_ZH, btn=roman_btn)
    footer = """<footer class="site-footer wrap">
  <div class="fl">
    <div>《{book}》· 本站第 03 册　|　本页内容依据 Routledge《Colloquial Arabic of the Gulf》重编，阿拉伯文已加注完整元音，讲解为中文。</div>
    <div><a href="index.html">教材首页</a>　·　<a href="{r}index.html">返回总导航 ↑</a></div>
  </div>
</footer>""".format(r=REL, book=BOOK_ZH)
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · {book} · 阿拉伯语口语学习站</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{r}assets/style.css">
<link rel="icon" type="image/svg+xml" href="{r}assets/favicon.svg">
</head>
<body data-book-id="gulf-arabic" data-unit-count="21" data-tts-locale="ar-KW">
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
""".format(title=esc(title), book=BOOK_ZH,
           desc=esc(desc or "面向中国学习者的海湾口语阿拉伯语教材页面"),
           r=REL, header=header, crumb=crumb_html, body=body,
           footer_nav=footer_nav, footer=footer)


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
    inner = "".join(
        '<a class="btn %s" href="%s">%s</a>' % ("btn-primary" if p else "", h, esc(l))
        for l, h, p in links
    )
    return '<nav class="footer-nav"><div class="group">%s</div><div class="group"><a class="btn" href="%sindex.html">↑ 返回总导航</a></div></nav>' % (inner, REL)


# ---------------------------------------------------------------- 单元页
def unit_nav_html(idx):
    prev_link = ("unit-%02d.html" % (idx - 1)) if idx > 1 else "index.html"
    next_link = ("unit-%02d.html" % (idx + 1)) if idx < N_UNITS else "grammar.html"
    links = [
        ("← 上一单元" if idx > 1 else "← 教材首页", prev_link, False),
        ("教材首页", "index.html", False),
        ("下一单元 →" if idx < N_UNITS else "语法总表 →", next_link, True),
    ]
    return std_footer(links)


def build_unit(u):
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
  <div class="u-ar playable" dir="rtl" lang="ar"{pa}>{ar}</div>
  <div class="u-sub">{sub}</div>
  <div class="u-roman">原书标题转写：{rom}</div>
  <div style="margin-top:14px;display:flex;gap:9px;flex-wrap:wrap;align-items:center">
    <button class="btn btn-sm" id="mark-done" data-unit-id="{n}" onclick="markDone('{n}',this)">标记本单元已学完</button>
    <span class="badge-done" id="done-badge" data-unit-id="{n}"></span>
  </div>
</section>""".format(n=num, level=esc(u.get("level_zh", "")),
                     review="· 复习单元" if u.get("is_review") else "",
                     title=esc(u["title_zh"]), ar=esc(u["title_ar"]), pa=pa(u["title_ar"]),
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
                a = ln.get("ar", "")
                spk = ln.get("speaker_zh", "")
                lines.append("""<div class="dline">
  <div class="who">%s</div>
  <div class="txt">
    <div class="ar-main playable" dir="rtl" lang="ar"%s>%s</div>
    <div class="zh">%s</div>
    %s
  </div>
</div>""" % (esc(spk), pa(a, AUDIO.speaker_key(spk)), esc(a), rich(ln.get("zh", "")),
             roman(ln.get("roman", ""))))
            ds.append("""<div class="dialog">
  <div class="dialog-head"><h3>%s　<span class="d-ar playable" dir="rtl" lang="ar"%s>%s</span></h3><p>%s</p></div>
  %s
</div>""" % (esc(d.get("title_zh", "")), pa(d.get("title_ar", "")), esc(d.get("title_ar", "")),
             rich(d.get("context_zh", "")), "".join(lines)))
        blocks.append('<section class="block" id="dialogues"><h2><span class="zh-num">02</span> 情景对话</h2>%s</section>' % "".join(ds))

    if u.get("vocab"):
        rows = []
        for v in u["vocab"]:
            note = v.get("note_zh", "")
            a = v.get("ar", "")
            rows.append("<tr><td class='ar-cell playable' dir='rtl' lang='ar'%s>%s</td><td class='zh-cell'>%s</td><td class='note-cell'>%s%s</td></tr>"
                        % (pa(a), esc(a), rich(v.get("zh", "")),
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
                a = e.get("ar", "")
                exs.append('<div class="ex-row"><div class="e-ar playable" dir="rtl" lang="ar"%s>%s</div><div class="e-zh">%s%s</div></div>'
                           % (pa(a), esc(a), rich(e.get("zh", "")), roman(e.get("roman", ""))))
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
                ans = '<div class="answer">%s<br>%s</div>' % (
                    ar(it.get("answer_ar", "")), rich(it.get("answer_zh", "")))
                items.append('<div class="ex-item"><div class="n">%d</div><div><div class="q">%s</div>'
                             '<button class="ans-toggle" onclick="toggleAnswer(this)">查看参考答案</button>%s</div></div>'
                             % (k, rich(it.get("q_zh", "")), ans))
            ex.append('<div class="ex-group"><h3>%s</h3><div class="e-prompt">%s</div>%s</div>'
                      % (esc(e.get("title_zh", "")), rich(e.get("prompt_zh", "")), "".join(items)))
        blocks.append("""<section class="block" id="exercises"><h2><span class="zh-num">05</span> 练习与参考答案 <span class="hint" style="font-size:12px;color:var(--ink-3);font-weight:400">共 %d 小题</span></h2>
  <div class="filter-bar" style="margin-bottom:16px"><button class="btn btn-sm" onclick="toggleAllAnswers(true)">展开全部答案</button><button class="btn btn-sm" onclick="toggleAllAnswers(false)">收起全部答案</button><span style="font-size:12.5px;color:var(--ink-3)">点击阿拉伯文即可发音</span></div>
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
        blocks.append('<section class="block" id="letters"><h2><span class="zh-num">07</span> 本单元所学字母</h2><div class="letter-grid">%s</div><p style="font-size:13px;color:var(--ink-3);margin:14px 0 0"><a href="alphabet.html">查看完整字母表 →</a></p></section>'
                      % "".join(cards))

    if u.get("is_review"):
        rv = u.get("review") or {}
        parts = ['<section class="block" id="review"><h2><span class="zh-num">R</span> 复习与自评</h2>']
        if rv.get("checklist"):
            parts.append('<ul class="review-list">%s</ul>' % "".join("<li>%s</li>" % rich(x) for x in rv["checklist"]))
        if rv.get("tasks"):
            parts.append('<h3 style="font-size:16px;margin:22px 0 10px">复习活动与延展任务</h3><ul class="review-list">%s</ul>'
                         % "".join("<li>%s</li>" % rich(x) for x in rv["tasks"]))
        parts.append('</section>')
        blocks.append("".join(parts))

    blocks.append('<section class="block" id="summary"><h2><span class="zh-num">✓</span> 本单元小结</h2><div class="summary-box">%s</div><div style="margin-top:14px"><button class="btn btn-sm" id="mark-done-2" onclick="markDone(\'%s\',document.getElementById(\'mark-done\'))">标记本单元已学完</button></div></section>'
                  % (rich(u.get("summary_zh", "")), num))

    body = back_strip("第 %02d 单元 · %s" % (num, u["title_zh"])) + hero + mnav + "".join(blocks)
    cr = crumb([("总导航", REL + "index.html"), ("《%s》" % BOOK_ZH, "index.html"),
                ("第 %02d 单元 · %s" % (num, u["title_zh"]), None)])
    page = shell("第 %02d 单元 %s" % (num, u["title_zh"]), cr, body,
                 unit_nav_html(num),
                 desc="海湾口语第 %d 单元：%s。带完整元音标注的阿拉伯语对话、词汇、语法与练习，中文精讲。" % (num, u["title_zh"]))
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

    total_vocab = sum(len(u.get("vocab", [])) for u in UNITS)
    total_lines = sum(len(d.get("lines", [])) for u in UNITS for d in u.get("dialogues", []))
    resources = [
        ("基础", "发音与转写规则", "原书 Pronunciation guide 中文版：本书独有的 9／x／H／g／ch／DH 转写、强调音、元音（含短元音 o）、重音与叠音对照。", "sounds.html"),
        ("基础", "阿拉伯字母表", "原书发音指南的 28 个字母＋圆体 ة：名称、本书转写、标准语与海湾口语读音、连写规则。", "alphabet.html"),
        ("总表", "语法结构总表", "19 个海湾口语语法专题中文梳理，并汇总 21 个单元的全部语法点入口。", "grammar.html"),
        ("总表", "分类词汇总表", "21 个单元全部 %d 条词条，可按中文、阿拉伯文或原书罗马音检索，点击即可朗读。" % total_vocab, "glossary.html"),
        ("书写", "阿拉伯文字书写补充", "元音符号、长元音、短元音 o 与双元音、连写、太阳字母、ق 的海湾读法（q 读 g）、ة 的隐藏 t、hamza 写法。", "script.html"),
    ]
    reshtml = "".join(
        '<a class="resource-card" href="%s"><div class="rk">%s</div><h3>%s</h3><p>%s</p></a>' % (h, esc(k), esc(t), esc(d))
        for k, t, d, h in resources)

    hero = """<section class="hero">
  <h1>《海湾口语》</h1>
  <div class="hero-ar playable" dir="rtl" lang="ar"{pa}>{ar}</div>
  <div class="hero-meta"><span class="hero-chip">21 个单元</span><span class="hero-chip">零起点 → B1</span><span class="hero-chip">带元音阿拉伯文</span><span class="hero-chip">中文精讲</span><span class="hero-chip">海湾六国男女声配音</span></div>
</section>""".format(ar=esc(BOOK_INFO["title_ar"]), pa=pa(BOOK_INFO["title_ar"]))

    body = back_strip("教材首页") + hero

    body += """<section class="section"><div class="section-head"><h2>教材信息</h2><span class="hint">依据原书版权页与前言</span></div>
<div class="info-grid">
  <div class="info-card"><div class="k">原书</div><div class="v">Colloquial Arabic of the Gulf</div><div class="d">The Complete Course for Beginners</div></div>
  <div class="info-card"><div class="k">作者</div><div class="v">克莱夫·霍尔斯</div><div class="d">{authors}</div></div>
  <div class="info-card"><div class="k">版本</div><div class="v">Routledge 第一版（2016）</div><div class="d">Colloquial 系列</div></div>
  <div class="info-card"><div class="k">目标水平</div><div class="v">零起点 → B1</div><div class="d">{level}</div></div>
</div>
<div class="block" style="margin-top:8px"><div class="g-body" style="font-size:14px;line-height:1.9">{intro}</div></div>
</section>""".format(authors=esc(BOOK_INFO["authors"]), level=esc(BOOK_INFO["level"]),
                     intro=esc(BOOK_INFO["intro"]))

    body += """<section class="section"><div class="section-head"><h2>学习流程</h2><span class="hint">从教材首页逐级展开，每页均可返回</span></div>
<div class="block"><div class="path-flow">
<span class="path-node"><a href="{r}index.html">① 总导航</a></span><span class="path-arrow">→</span>
<span class="path-node on">② 教材首页（本页）</span><span class="path-arrow">→</span>
<span class="path-node">③ 选择单元 / 专题</span><span class="path-arrow">→</span>
<span class="path-node">④ 单元内：对话 → 词汇 → 语法 → 练习</span><span class="path-arrow">→</span>
<span class="path-node">⑤ 返回教材首页 / 总导航</span></div>
<p style="font-size:13.5px;color:var(--ink-2);margin:14px 0 0">建议顺序：先读「发音与转写规则」与「阿拉伯字母表」，再按单元编号循序渐进；本书 21 个单元含 19 个正课与 2 个复习单元（第 11、17 单元）。每单元页顶部有模块导航，底部有上一单元／下一单元与返回入口。特别注意本书转写体系与前两册不同：{note}</p></div></section>""".format(
        r=REL, note="9=ع、x=خ、j=ج、g=ق（口语读 g）、ch=ش、DH=ظ；重音写在元音上标，海湾特有短元音 o。")

    body += """<section class="section" id="toc"><div class="section-head"><h2>单元目录</h2><span class="hint">已学 <strong id="progress-count">0</strong> / 21 单元 · 进度仅保存在本机浏览器</span></div>
<div style="height:6px;background:var(--line-2);border-radius:4px;overflow:hidden;margin-bottom:18px"><div id="progress-bar" style="height:100%;width:0;background:linear-gradient(90deg,var(--teal),var(--gold));transition:width .3s"></div></div>
<div class="toc-grid">__TOC__</div></section>""".replace("__TOC__", "".join(toc))

    body += """<section class="section"><div class="section-head"><h2>专题与工具页</h2><span class="hint">与单元同属本册，随时可返回总导航</span></div><div class="resource-grid">%s</div></section>""" % reshtml

    cr = crumb([("总导航", REL + "index.html"), ("《%s》" % BOOK_ZH, None)])
    nav = std_footer([("← 返回总导航", REL + "index.html", False),
                      ("发音与字母", "sounds.html", False),
                      ("从第 01 单元开始 →", "unit-01.html", True)])
    (OUT / "index.html").write_text(shell("教材首页", cr, body, nav,
                                          desc="《海湾口语》教材首页：21 个单元目录、发音与字母、语法总表、词汇总表等完整学习流程入口。"),
                                    encoding="utf-8")


# ---------------------------------------------------------------- 专题页
def topic_page(title, sub, crumb_items, blocks, desc, current):
    hero = """<section class="hero" style="padding:32px 38px">
  <p class="eyebrow">教材 03 · 专题</p>
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
    cards = "".join('<div class="gram-card"><h3>%s</h3><div class="g-body">%s</div></div>'
                    % (esc(k), rich(v)) for k, v in SOUNDS_NOTES)
    blocks = [
        '<section class="section"><div class="section-head"><h2>需要特别留意的辅音</h2><span class="hint">原书 Transliteration key · Table 1，中文改写</span></div><div class="block"><div class="tbl-wrap"><table><thead><tr><th>阿拉伯文</th><th>原书罗马音</th><th>发音要领</th></tr></thead><tbody>%s</tbody></table></div></div></section>' % rows_c,
        '<section class="section"><div class="section-head"><h2>元音、双元音与符号</h2><span class="hint">原书 Table 2–4 · 本站按此对应关系加注元音符号</span></div><div class="block"><div class="tbl-wrap"><table><thead><tr><th>阿拉伯文写法</th><th>原书罗马音</th><th>读法说明</th></tr></thead><tbody>%s</tbody></table></div></div></section>' % rows_v,
        '<section class="section"><div class="section-head"><h2>转写体系、强调音与重音</h2><span class="hint">原书 Introduction 中文梳理</span></div><div class="block">%s</div></section>' % cards,
        '<section class="section"><div class="section-head"><h2>继续学习</h2></div><div class="block"><div class="resource-grid"><a class="resource-card" href="alphabet.html"><div class="rk">下一步</div><h3>阿拉伯字母表</h3><p>字母名称、海湾读音与连写规则。</p></a><a class="resource-card" href="unit-01.html"><div class="rk">开始正课</div><h3>第 01 单元 · 你好，欢迎！</h3><p>问候、介绍与告别。</p></a><a class="resource-card" href="index.html"><div class="rk">返回</div><h3>教材首页</h3><p>查看 21 个单元与全部专题入口。</p></a></div></div></section>',
    ]
    (OUT / "sounds.html").write_text(topic_page(
        "发音与转写规则", "本书独有的转写符号、强调音、元音与重音；罗马音 → 带元音阿拉伯文的完整对照。",
        [("总导航", REL + "index.html"), ("《%s》" % BOOK_ZH, "index.html"), ("发音与转写规则", None)],
        blocks, "海湾阿拉伯语发音规则中文版，含 9／x／H／g／ch／DH 转写与带元音阿拉伯文对照表。", "专题 · 发音与转写规则"),
        encoding="utf-8")


def build_alphabet():
    rows = "".join("<tr><td class='ar-cell playable' dir='rtl' lang='ar' style='font-size:28px'%s>%s</td><td class='zh-cell'>%s<br><span style='font-size:12px;color:var(--ink-3)'>%s</span></td><td class='note-cell'>%s</td><td class='note-cell'>%s</td><td class='note-cell'>%s</td></tr>"
                   % (pa(a[0]), esc(a[0]), ar(a[1]), esc(a[2]), esc(a[3]), esc(a[4]), esc(a[5])) for a in ALPHABET)
    notes = "".join('<div class="gram-card"><h3>%s</h3><div class="g-body">%s</div></div>'
                    % (esc(k), rich(v)) for k, v in SCRIPT_NOTES[:4])
    blocks = [
        '<section class="section"><div class="section-head"><h2>完整字母表</h2><span class="hint">28 个字母＋阴性词尾 ة · 标准语与海湾口语读音对照</span></div><div class="block"><div class="tbl-wrap"><table><thead><tr><th>字母</th><th>名称（阿拉伯文／中文）</th><th>原书转写名</th><th>标准语读音</th><th>海湾口语读音</th></tr></thead><tbody>%s</tbody></table></div><p style="font-size:13px;color:var(--ink-3);margin:14px 0 0">字母顺序依据原书 Transliteration key 的 Table 1。表中「3」是原书用来表示 ع 的数字，不是数词三；大写 H / S / D / T 与 x / DH 分别表示送气音、强调音与特定辅音。本书的 ج 读 j，ق 口语多读 g；短元音 o 是海湾特色。</p></div></section>' % rows,
        '<section class="section"><div class="section-head"><h2>连写与书写要点</h2><span class="hint">原书 Table 1 给出每个字母的四种字形</span></div><div class="block">%s<p style="margin-top:14px"><a href="script.html">查看完整书写补充 →</a></p></div></section>' % notes,
        '<section class="section"><div class="section-head"><h2>相关页面</h2></div><div class="block"><div class="resource-grid"><a class="resource-card" href="sounds.html"><div class="rk">发音</div><h3>发音与转写规则</h3><p>罗马音与元音符号的对应。</p></a><a class="resource-card" href="unit-01.html"><div class="rk">正课</div><h3>第 01 单元</h3><p>从问候与介绍开始。</p></a><a class="resource-card" href="index.html"><div class="rk">返回</div><h3>教材首页</h3><p>回到 21 个单元目录。</p></a></div></div></section>',
    ]
    (OUT / "alphabet.html").write_text(topic_page(
        "阿拉伯字母表", "28 个字母与阴性词尾 ة：名称、标准语／海湾读音对比，以及连写规则。",
        [("总导航", REL + "index.html"), ("《%s》" % BOOK_ZH, "index.html"), ("阿拉伯字母表", None)],
        blocks, "阿拉伯语字母表中文版，含海湾口语读音与标准语对比、连写规则。", "专题 · 阿拉伯字母表"),
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
        '<section class="section"><div class="section-head"><h2>海湾口语 19 个语法专题</h2><span class="hint">依据各单元 Language points 中文梳理</span></div><div class="block">%s</div></section>' % cards,
        '<section class="section"><div class="section-head"><h2>按单元查阅全部语法点</h2><span class="hint">点击直接跳到对应单元的「语法要点」</span></div><div class="info-grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">%s</div></section>' % "".join(idx),
    ]
    (OUT / "grammar.html").write_text(topic_page(
        "语法结构总表", "19 个海湾口语语法专题中文梳理，并汇总 13 个单元全部语法点入口。",
        [("总导航", REL + "index.html"), ("《%s》" % BOOK_ZH, "index.html"), ("语法结构总表", None)],
        blocks, "海湾阿拉伯语语法结构总表，19 个专题与 21 单元语法点索引。", "专题 · 语法结构总表"),
        encoding="utf-8")


def build_glossary():
    total = sum(len(u.get("vocab", [])) for u in UNITS)
    rows = []
    for u in UNITS:
        for v in u.get("vocab", []):
            a = v.get("ar", "")
            rows.append("<tr><td class='ar-cell playable' dir='rtl' lang='ar'%s>%s</td><td class='zh-cell'>%s</td><td class='note-cell'>%s</td><td class='note-cell'><a href='unit-%02d.html#vocab'>第 %02d 单元</a>%s</td></tr>"
                        % (pa(a), esc(a), rich(v.get("zh", "")),
                           rich(v.get("note_zh", "")), u["id"], u["id"], roman(v.get("roman", ""))))
    blocks = ["""<section class="section"><div class="section-head"><h2>全部词条</h2><span class="hint">共 %d 条 · 来自 21 个单元教材原表</span></div>
<div class="block"><div class="filter-bar"><input type="search" placeholder="检索中文、阿拉伯文或原书罗马音……" oninput="filterRows(this,'glossary-table','glossary-count')"><span style="font-size:12.5px;color:var(--ink-3)">显示 <strong id="glossary-count">%d</strong> 条</span><button class="btn btn-sm" data-roman-toggle onclick="toggleRoman()">原书罗马音</button></div>
<div class="tbl-wrap"><table id="glossary-table"><thead><tr><th>阿拉伯文（带元音）</th><th>中文</th><th>用法提示</th><th>出处 / 原书转写</th></tr></thead><tbody>%s</tbody></table></div></div></section>""" % (total, total, "".join(rows))]
    (OUT / "glossary.html").write_text(topic_page(
        "分类词汇总表", "21 个单元全部 %d 条词条，可按中文、阿拉伯文或原书罗马音检索，点击即可朗读。" % total,
        [("总导航", REL + "index.html"), ("《%s》" % BOOK_ZH, "index.html"), ("分类词汇总表", None)],
        blocks, "海湾口语教材全部词汇中文对照表，带元音阿拉伯文与检索功能。", "专题 · 分类词汇总表"),
        encoding="utf-8")


def build_script():
    cards = "".join('<div class="gram-card"><h3>%s</h3><div class="g-body">%s</div></div>'
                    % (esc(k), rich(v)) for k, v in SCRIPT_NOTES)
    blocks = [
        '<section class="section"><div class="section-head"><h2>书写规则与本站改写说明</h2><span class="hint">依据原书 Transliteration key · Table 2–5 与 Introduction</span></div><div class="block">%s</div></section>' % cards,
        '<section class="section"><div class="section-head"><h2>相关页面</h2></div><div class="block"><div class="resource-grid"><a class="resource-card" href="alphabet.html"><div class="rk">字母</div><h3>完整字母表</h3><p>名称与读音对照。</p></a><a class="resource-card" href="sounds.html"><div class="rk">发音</div><h3>发音与转写规则</h3><p>罗马音与元音符号的对应。</p></a><a class="resource-card" href="index.html"><div class="rk">返回</div><h3>教材首页</h3><p>回到 21 个单元目录。</p></a></div></div></section>',
    ]
    (OUT / "script.html").write_text(topic_page(
        "阿拉伯文字书写补充", "元音符号、长元音、短元音 o 与双元音、连写规则、太阳字母，以及 ق 与 ة 的海湾读法。",
        [("总导航", REL + "index.html"), ("《%s》" % BOOK_ZH, "index.html"), ("书写补充", None)],
        blocks, "阿拉伯文书写规则中文讲解，含元音符号与海湾口语拼写特点。", "专题 · 书写补充"),
        encoding="utf-8")


def main():
    for u in UNITS:
        build_unit(u)
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
