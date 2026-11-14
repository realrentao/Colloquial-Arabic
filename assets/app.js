/* ===== 全站交互：总导航渲染 / 朗读 / 罗马音 / 答案 / 进度 / 检索 ===== */
(function () {
  'use strict';

  /* ---------- 1. 总导航页：由教材注册表渲染卡片 ---------- */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function activeCard(b, i) {
    var stats = (b.stats || []).map(function (s) {
      return '<div class="book-stat"><div class="n">' + esc(s.value) + '</div><div class="l">' + esc(s.label) + '</div></div>';
    }).join('');
    var tags = (b.tags || []).map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('');
    return '<article class="book-card is-active" data-entry="' + esc(b.entry) + '" tabindex="0" role="link" aria-label="进入《' + esc(b.title_zh) + '》">' +
      '<div class="book-no">教材 ' + esc(b.level || ('第 ' + String(i + 1).padStart(2, '0') + ' 册')) + '</div>' +
      '<h2 class="book-title">' + esc(b.title_zh) + '</h2>' +
      '<div class="book-ar" dir="rtl" lang="ar">' + esc(b.title_ar) + '</div>' +
      '<div class="book-original">' + esc(b.title_original) + '</div>' +
      '<p class="book-desc">' + esc(b.summary) + '</p>' +
      '<div class="book-tags">' + tags + '</div>' +
      '<div class="book-stats">' + stats + '</div>' +
      '<div class="book-cta"><span>进入教材 · 展开学习流程</span><span class="go">开始学习 &rarr;</span></div>' +
      '</article>';
  }

  function placeholderCard(i) {
    var no = String(i + 1).padStart(2, '0');
    return '<article class="book-card is-placeholder" aria-label="教材位 ' + no + '，尚未接入">' +
      '<div class="book-no">教材位 ' + no + ' · 预留</div>' +
      '<h2 class="book-title">待接入教材</h2>' +
      '<div class="book-ar" dir="rtl" lang="ar">مَحْجُوزٌ</div>' +
      '<div class="book-original">与已接入教材同层级 · 同入口规则</div>' +
      '<div class="slot-form"><div class="slot-line w1"></div><div class="slot-line w2"></div><div class="slot-line w3"></div></div>' +
      '<p class="book-desc">此位置为后续教材保留。接入新教材时，本卡片自动让位给新教材，版式与入口规则保持不变。</p>' +
      '<div class="book-tags"><span class="tag">预留位</span><span class="tag">尚未接入</span></div>' +
      '<div class="book-stats"><div class="book-stat"><div class="n">—</div><div class="l">单元</div></div><div class="book-stat"><div class="n">—</div><div class="l">词条</div></div></div>' +
      '<div class="book-cta"><span>等待内容接入</span><span class="go">暂不可用</span></div>' +
      '</article>';
  }

  window.renderLibrary = function () {
    var grid = document.getElementById('book-grid');
    if (!grid || !window.LIBRARY) return;
    var lib = window.LIBRARY, books = lib.books || [], total = Math.max(lib.totalSlots || 6, books.length + 3);
    var html = books.map(activeCard).join('');
    for (var i = books.length; i < total; i++) html += placeholderCard(i);
    grid.innerHTML = html;

    Array.prototype.forEach.call(grid.querySelectorAll('.book-card.is-active'), function (card) {
      function go() { window.location.href = card.getAttribute('data-entry'); }
      card.addEventListener('click', go);
      card.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
    });

    var set = function (id, v) { var el = document.getElementById(id); if (el) el.textContent = v; };
    set('stat-total', String(total));
    set('stat-total-2', String(total));
    set('stat-active', String(books.length));
    set('stat-reserved', String(total - books.length));
    var note = document.getElementById('slot-note-text');
    if (note) note.textContent = lib.slotNote;
    var ar = document.getElementById('lib-name-ar');
    if (ar) ar.textContent = lib.name_ar;
  };

  /* ---------- 2. 点击阿拉伯文发音（站内预生成 mp3，不依赖系统语音包） ---------- */
  var audioEl = null, playingEl = null;

  function clearPlaying() {
    if (playingEl) { playingEl.classList.remove('playing'); playingEl = null; }
  }

  function fallbackSpeak(text) {
    if (!text || !('speechSynthesis' in window)) return;
    try {
      window.speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(text);
      u.lang = 'ar-EG'; u.rate = 0.82;
      var vs = window.speechSynthesis.getVoices() || [];
      var v = vs.find(function (x) { return /^ar[-_]?EG/i.test(x.lang); }) ||
              vs.find(function (x) { return /^ar/i.test(x.lang); });
      if (v) u.voice = v;
      window.speechSynthesis.speak(u);
    } catch (e) {}
  }

  window.playArabic = function (el) {
    var src = el.getAttribute('data-audio');
    var text = el.getAttribute('data-say') || (el.textContent || '').trim();
    if (audioEl) { try { audioEl.pause(); } catch (e) {} }
    clearPlaying();
    if (!src) { fallbackSpeak(text); return; }
    if (!audioEl) {
      audioEl = new Audio();
      audioEl.preload = 'none';
      audioEl.addEventListener('ended', clearPlaying);
      audioEl.addEventListener('error', clearPlaying);
    }
    audioEl.src = src;
    playingEl = el;
    el.classList.add('playing');
    var pr = audioEl.play();
    if (pr && pr.catch) pr.catch(function () { clearPlaying(); fallbackSpeak(text); });
  };

  window.speak = function (text) { fallbackSpeak(text); };

  /* ---------- 3. 原书罗马音显示开关（默认隐藏，主体为带元音阿拉伯文） ---------- */
  var ROMAN_KEY = 'ca.showRoman';
  window.toggleRoman = function () {
    var on = !document.body.classList.contains('show-roman');
    document.body.classList.toggle('show-roman', on);
    try { localStorage.setItem(ROMAN_KEY, on ? '1' : '0'); } catch (e) {}
  };

  /* ---------- 4. 练习答案 ---------- */
  window.toggleAnswer = function (btn) {
    var box = btn.nextElementSibling;
    if (!box) return;
    var open = box.classList.toggle('show');
    btn.textContent = open ? '收起参考答案' : '查看参考答案';
  };
  window.toggleAllAnswers = function (on) {
    document.querySelectorAll('.answer').forEach(function (a) { a.classList.toggle('show', on); });
    document.querySelectorAll('.ans-toggle').forEach(function (b) { b.textContent = on ? '收起参考答案' : '查看参考答案'; });
  };

  /* ---------- 5. 词汇检索 ---------- */
  window.filterRows = function (input, tableId, countId) {
    var q = (input.value || '').trim().toLowerCase();
    var rows = document.querySelectorAll('#' + tableId + ' tbody tr');
    var n = 0;
    rows.forEach(function (r) {
      var hit = !q || (r.textContent || '').toLowerCase().indexOf(q) !== -1;
      r.style.display = hit ? '' : 'none';
      if (hit) n++;
    });
    if (countId) { var el = document.getElementById(countId); if (el) el.textContent = String(n); }
  };

  /* ---------- 6. 学习进度（localStorage，仅本机保存） ---------- */
  var PKEY = 'ca.egyptian-arabic.progress';
  function progress() {
    try { return JSON.parse(localStorage.getItem(PKEY) || '[]'); } catch (e) { return []; }
  }
  window.getProgress = progress;
  window.markDone = function (id, btn) {
    var p = progress(), i = p.indexOf(String(id));
    if (i >= 0) p.splice(i, 1); else p.push(String(id));
    try { localStorage.setItem(PKEY, JSON.stringify(p)); } catch (e) {}
    var done = p.indexOf(String(id)) >= 0;
    if (btn) btn.textContent = done ? '✓ 已完成 · 点击取消' : '标记本单元已学完';
    var badge = document.getElementById('done-badge');
    if (badge) badge.textContent = done ? '本单元已标记完成' : '';
    window.renderProgress && window.renderProgress();
  };
  window.renderProgress = function () {
    var p = progress();
    document.querySelectorAll('[data-unit-id]').forEach(function (el) {
      var done = p.indexOf(el.getAttribute('data-unit-id')) >= 0;
      el.textContent = done ? '✓ 已学' : '';
    });
    var n = document.getElementById('progress-count');
    if (n) n.textContent = String(p.length);
    var bar = document.getElementById('progress-bar');
    if (bar) bar.style.width = (p.length / 15 * 100) + '%';
    var btn = document.getElementById('mark-done');
    if (btn && btn.getAttribute('data-unit-id')) {
      btn.textContent = p.indexOf(btn.getAttribute('data-unit-id')) >= 0 ? '✓ 已完成 · 点击取消' : '标记本单元已学完';
    }
    var badge = document.getElementById('done-badge');
    if (badge && badge.getAttribute('data-unit-id')) {
      badge.textContent = p.indexOf(badge.getAttribute('data-unit-id')) >= 0 ? '本单元已标记完成' : '';
    }
  };

  /* ---------- 7. 滚动进度条 ---------- */
  function scrollProgress() {
    var el = document.getElementById('scroll-progress');
    if (!el) return;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    el.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
  }

  /* ---------- 点击阿语原文发音（不再需要独立朗读按钮） ---------- */
  document.addEventListener('click', function (e) {
    if (!e.target.closest) return;
    var el = e.target.closest('.playable[data-say], .playable[data-audio]');
    if (!el || el.tagName === 'A') return;
    window.playArabic(el);
  });

  /* ---------- 初始化 ---------- */
  document.addEventListener('DOMContentLoaded', function () {
    try {
      if (localStorage.getItem(ROMAN_KEY) === '1') {
        document.body.classList.add('show-roman');
      }
    } catch (e) {}
    window.renderLibrary();
    window.renderProgress();
    scrollProgress();
    window.addEventListener('scroll', scrollProgress, { passive: true });
    if ('speechSynthesis' in window) { try { window.speechSynthesis.getVoices(); } catch (e) {} }
  });
})();
