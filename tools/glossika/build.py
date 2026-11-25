# -*- coding: utf-8 -*-
"""Glossika ENARARE F1-F3 静态站点生成器。
每册 1000 句 = 20 单元（每单元 50 句），三栏对照：中文 / 标准阿语 / 埃及阿语。
中文=edge-tts 云希男声；两种阿语=GMS-C 原书真人音。全部 data-audio 点击播放，不依赖浏览器发音。
"""
import json, os, html

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = 'D:/workbuddy工作区/2026-11-14-14-56-52/_work/glossika'
OUT = os.path.join(REPO, 'books')
ZHMAP = json.load(open(os.path.join(REPO, 'tools/glossika/zh_audio_map.json'), encoding='utf-8'))
ARMAP = json.load(open(os.path.join(REPO, 'tools/glossika/ar_audio_map.json'), encoding='utf-8'))

BOOKS = {
  1: {'id':'glossika-f1','title':'Glossika 阿语 · 一级','title_ar':'الْعَرَبِيَّةُ · الْمُسْتَوَى الْأَوَّل',
      'sub':'英语原句 → 中文 / 标准阿语 / 埃及阿语', 'n':1000},
  2: {'id':'glossika-f2','title':'Glossika 阿语 · 二级','title_ar':'الْعَرَبِيَّةُ · الْمُسْتَوَى الثَّانِي',
      'sub':'1000 句进阶句型 · 三语对照', 'n':1000},
  3: {'id':'glossika-f3','title':'Glossika 阿语 · 三级','title_ar':'الْعَرَبِيَّةُ · الْمُسْتَوَى الثَّالِث',
      'sub':'1000 句高阶表达 · 三语对照', 'n':1000},
}

def esc(s): return html.escape(str(s or ''), quote=True)

def aud(key, m):
    rel = m.get(key)
    if not rel: return ''
    return '../../audio/' + rel

def head(title, desc):
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>''' + esc(title) + '''</title>
<meta name="description" content="''' + esc(desc) + '''">
<link rel="stylesheet" href="../../assets/style.css">
<link rel="stylesheet" href="../../assets/glossika.css">
<link rel="icon" type="image/svg+xml" href="../../assets/favicon.svg">
</head>'''

def header(book):
    b = BOOKS[book]
    return '''<body data-book-id="''' + b['id'] + '''" data-unit-count="20">
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="../../index.html"><span class="brand-mark">ع</span> 阿拉伯语口语学习站 <span class="brand-sub">《''' + esc(b['title']) + '''》</span></a>
    <span class="header-spacer"></span>
    <div class="header-tools">
      <a class="header-back" href="../../index.html"><span class="lbl-long">← 返回总导航</span><span class="lbl-short">← 总导航</span></a>
      <a class="btn btn-ghost btn-sm" href="index.html">教材首页</a>
      <button class="btn btn-sm btn-roman" data-roman-toggle onclick="toggleRoman()">原书罗马音</button>
    </div>
  </div>
  <div class="progressbar" id="scroll-progress"></div>
</header>'''

def crumbs(book, cur):
    b = BOOKS[book]
    if cur is None:
        return '''<nav class="crumb" aria-label="面包屑"><a href="../../index.html">总导航</a><span class="sep">›</span><span class="cur">《''' + esc(b['title']) + '''》</span></nav>
<div class="return-strip"><span class="rs-label">当前位置</span><a class="pill" href="../../index.html">① 总导航</a><span>›</span><span class="pill gold">② 教材首页</span>
<span style="margin-left:auto"><a href="../../index.html">← 返回总导航</a></span></div>'''
    return '''<nav class="crumb" aria-label="面包屑"><a href="../../index.html">总导航</a><span class="sep">›</span><a href="index.html">《''' + esc(b['title']) + '''》</a><span class="sep">›</span><span class="cur">第 ''' + str(cur) + ''' 单元</span></nav>
<div class="return-strip"><span class="rs-label">当前位置</span><a class="pill" href="../../index.html">① 总导航</a><span>›</span><a class="pill" href="index.html">② 教材首页</a><span>›</span><span class="pill gold">③ 第 ''' + str(cur) + ''' 单元</span>
<span style="margin-left:auto"><a href="index.html">↑ 返回教材首页</a>　·　<a href="../../index.html">← 返回总导航</a></span></div>'''

def footer():
    return '''<footer class="site-footer"><div class="wrap"><div class="foot-brand">ع　阿拉伯语口语学习站</div>
<div class="foot-links"><a href="../../index.html">总导航</a><a href="index.html">教材首页</a></div></div></footer>
<script src="../../assets/app.js"></script>
</body></html>'''

def build_book(book):
    b = BOOKS[book]
    data = json.load(open(os.path.join(DATA, 'f%d_final.json' % book), encoding='utf-8'))
    outdir = os.path.join(OUT, b['id'])
    os.makedirs(outdir, exist_ok=True)

    cards = []
    for u in range(1, 21):
        lo = (u - 1) * 50 + 1; hi = u * 50
        cards.append('''<a class="g-unit" href="unit-%02d.html"><div class="gu-num">%02d</div>
<div class="gu-body"><div class="gu-title">第 %d 单元 · 句 %d–%d</div>
<div class="gu-sub">50 句 · 中文 / 标准阿语 / 埃及阿语三栏对照</div></div>
<div class="gu-go">开始 →</div></a>''' % (u, u, u, lo, hi))

    idx = (head(b['title'] + ' · 教材首页', 'Glossika ENARARE 三语对照句库，中文、标准阿语、埃及阿语，点击发音。')
        + header(book) + '<main class="wrap">\n' + crumbs(book, None)
        + '''<section class="hero g-hero"><h1>《''' + esc(b['title']) + '''》</h1>
<div class="hero-ar" dir="rtl" lang="ar">''' + b['title_ar'] + '''</div>
<div class="hero-meta"><span class="hero-chip">1000 句</span><span class="hero-chip">中文 / 标准阿语 / 埃及阿语</span><span class="hero-chip">原书元音 + ROM 保留</span><span class="hero-chip">真人配音 + 中文男声</span></div>
</section>
<section class="section"><div class="section-head"><h2>本册说明</h2></div>
<div class="block"><p style="font-size:14.5px;line-height:1.95;color:var(--ink-2);margin:0">
《Glossika ENARARE》原书为英语例句配标准阿拉伯语与埃及阿拉伯语两种写法。本站将英文原句替换为<b>中文译文</b>，保留标准阿语与埃及阿语的原书元音标注及原书 ROM 转写。每句配三段音频：中文为年轻男声合成，标准阿语与埃及阿语均为原书配套真人录音。<b>点击任意一栏文字即可发音</b>；原书罗马音默认隐藏，可用顶栏「原书罗马音」开关显示。
</p></div></section>
<section class="section"><div class="section-head"><h2>单元目录</h2><span class="hint">每单元 50 句 · 共 1000 句</span></div>
<div class="g-unit-grid">''' + ''.join(cards) + '''</div></section>
</main>
''' + footer())
    open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8').write(idx)

    for u in range(1, 21):
        lo = (u - 1) * 50; hi = lo + 50
        rows = []
        miss = {'zh': 0, 'std': 0, 'egy': 0}
        for s in data[lo:hi]:
            sid = s['id']
            zh_a = aud('g%d-%04d-zh' % (book, sid), ZHMAP)
            std_a = aud('g%d-%04d-std' % (book, sid), ARMAP)
            egy_a = aud('g%d-%04d-egy' % (book, sid), ARMAP)
            if not zh_a: miss['zh'] += 1
            if not std_a: miss['std'] += 1
            if not egy_a: miss['egy'] += 1
            zh_cls = 'playable' if zh_a else ''
            std_cls = 'playable' if std_a else ''
            egy_cls = 'playable' if egy_a else ''
            zh_attr = ' data-audio="' + zh_a + '"' if zh_a else ''
            std_attr = ' data-audio="' + std_a + '"' if std_a else ''
            egy_attr = ' data-audio="' + egy_a + '"' if egy_a else ''
            rows.append('''<tr>
<td class="g-num">''' + str(sid) + '''</td>
<td class="g-zh ''' + zh_cls + '''"''' + zh_attr + ''' title="''' + ('点击听中文' if zh_a else '暂无音频') + '''">''' + esc(s['zh']) + '''</td>
<td class="g-ar" dir="rtl" lang="ar"><span class="''' + std_cls + '''"''' + std_attr + ''' title="''' + ('点击听标准阿语' if std_a else '暂无音频') + '''">''' + esc(s['ar']) + '''</span><div class="g-roman">ROM · ''' + esc(s['ar_rom']) + '''</div></td>
<td class="g-ar" dir="rtl" lang="ar"><span class="''' + egy_cls + '''"''' + egy_attr + ''' title="''' + ('点击听埃及阿语' if egy_a else '暂无音频') + '''">''' + esc(s['are']) + '''</span><div class="g-roman">ROM · ''' + esc(s['are_rom']) + '''</div></td>
</tr>''')
        prev_html = '<a class="btn btn-sm" href="unit-%02d.html">← 上一单元</a>' % (u - 1) if u > 1 else '<span></span>'
        next_html = '<a class="btn btn-sm btn-primary" href="unit-%02d.html">下一单元 →</a>' % (u + 1) if u < 20 else '<span></span>'
        note = '' if not any(miss.values()) else '<span class="hint" style="color:#b00">缺音：中文%d / 标准%d / 埃及%d</span>' % (miss['zh'], miss['std'], miss['egy'])
        page = (head('第 %d 单元 · %s' % (u, b['title']), 'Glossika 第 %d 单元，句 %d-%d 三语对照' % (u, lo + 1, hi))
            + header(book) + '<main class="wrap">\n' + crumbs(book, u)
            + '''<section class="section"><div class="section-head"><h2>第 ''' + str(u) + ''' 单元 · 句 ''' + str(lo + 1) + '''–''' + str(hi) + '''</h2>''' + note + '''</div>
<div class="g-tip">点击中文听男声朗读，点击标准阿语 / 埃及阿语听原书真人录音；顶栏可切换显示原书罗马音。</div>
<div class="filter-bar"><input type="search" placeholder="检索本单元中文 / 阿语 / 罗马音……" oninput="filterRows(this,'g-table','g-count')"><span style="font-size:12.5px;color:var(--ink-3)">显示 <strong id="g-count">50</strong> 句</span></div>
<div class="tbl-wrap"><table class="g-table" id="g-table"><thead><tr><th style="width:52px">#</th><th style="width:30%">中文</th><th>标准阿语（原书元音）</th><th>埃及阿语（原书元音）</th></tr></thead>
<tbody>''' + ''.join(rows) + '''</tbody></table></div>
<div class="g-nav">''' + prev_html + '''<a class="btn btn-sm" href="index.html">↑ 返回教材首页</a>''' + next_html + '''</div>
</section>
</main>
''' + footer())
        open(os.path.join(outdir, 'unit-%02d.html' % u), 'w', encoding='utf-8').write(page)
    print('F%d: built 21 pages -> %s' % (book, outdir), flush=True)

if __name__ == '__main__':
    for b in (1, 2, 3): build_book(b)
    print('ALL DONE')
