# -*- coding: utf-8 -*-
"""配音规格：音色配置、说话人性别/音色映射、待配音文本收集、音频键计算。

约定：
- 旁白（词汇、例句、练习答案、字母、专题讲解里的阿文片段）→ 埃及女声 ar-EG-SalmaNeural。
- 对话台词 → 按说话人性别选 ar-EG-ShakirNeural（男）/ ar-EG-SalmaNeural（女），
  并给每个角色固定的 pitch / rate 微调，使同性别的不同人物音色有区分。
- 音频文件名 = md5(文本 + "|" + 音色键)[:16]，按首字符分桶存放。
- audio_map.json 的键 = 文本 + "|" + 音色键，值为站点根相对路径。
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data"
MAP_PATH = ROOT / "tools" / "audio_map.json"
AUDIO_ROOT = ROOT / "audio"

AR_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]"
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s\u064B-\u065F\u0670\u200C\u200D"
    r"،؛؟«»\-—….,;:!?()\u00A0]*"
)
AR_CHAR = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")

# ---------------------------------------------------------------- 音色
FEMALE_VOICE = "ar-EG-SalmaNeural"
MALE_VOICE = "ar-EG-ShakirNeural"

# 角色性别（依据教材人名与情景判断）；未列出的中性角色按男声处理
FEMALE_NAMES = [
    "维达德", "薇达德", "萨米拉", "萨米娅", "莫娜", "女士", "女游客", "迪娜女士",
    "丽塔·斯坦利", "简", "女职员", "女店员", "贾比尔的母亲", "萨米拉的母亲",
    "女士一", "女士二",
]
MALE_NAMES = [
    "贾比尔", "哈桑", "易卜拉欣", "领班", "卡迈勒", "讲师", "萨米拉的父亲",
    "服务员", "店员", "顾客", "游客", "主持人", "男士一", "哈桑与贾比尔",
    "三人齐声", "萨米拉的父亲",
]
ALIAS = {"薇达德": "维达德"}

PROFILES = {
    "narrator": {"voice": FEMALE_VOICE, "rate": "-10%", "pitch": "+0Hz",
                 "label": "埃及女声 · 旁白（词汇／例句／讲解）"},
}


def _hz(n):
    return ("+%dHz" % n) if n >= 0 else ("%dHz" % n)


def _pct(n):
    return ("+%d%%" % n) if n >= 0 else ("%d%%" % n)


def _build_profiles():
    # 每个角色一组固定偏移：同性别之间靠音高、语速错开
    for names, voice, lo in ((FEMALE_NAMES, FEMALE_VOICE, -14),
                             (MALE_NAMES, MALE_VOICE, -20)):
        for i, n in enumerate(dict.fromkeys(names)):
            pitch = lo + (i % 9) * 4
            rate = -12 + (i % 5) * 2
            PROFILES["sp:" + n] = {
                "voice": voice, "rate": _pct(rate), "pitch": _hz(pitch),
                "label": "%s · %s（%s，%s）" % ("女声" if voice == FEMALE_VOICE else "男声",
                                              n, _pct(rate), _hz(pitch)),
            }


_build_profiles()


def speaker_key(name):
    n = ALIAS.get(str(name or "").strip(), str(name or "").strip())
    key = "sp:" + n
    return key if key in PROFILES else "narrator"


def profile(key):
    return PROFILES.get(key, PROFILES["narrator"])


def map_key(text, key="narrator"):
    return str(text or "").strip() + "|" + key


def akey(text, key="narrator"):
    return hashlib.md5(map_key(text, key).encode("utf-8")).hexdigest()[:16]


def relpath(text, key="narrator"):
    h = akey(text, key)
    return "audio/%s/%s.mp3" % (h[0], h)


# ---------------------------------------------------------------- 文本收集
def load_units():
    return [json.loads((DATA / ("unit-%02d.json" % i)).read_text(encoding="utf-8"))
            for i in range(1, 16)]


# 这些字段是显式阿文文本，已按各自音色单独收录；遍历中文讲解时跳过，
# 避免把对话台词再生成一份无用的女声旁白副本。
SKIP_KEYS = {"ar", "answer_ar", "title_ar", "name_ar", "roman", "title_roman"}


def _walk_strings(obj, fn, key=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_strings(v, fn, k)
    elif isinstance(obj, list):
        for v in obj:
            _walk_strings(v, fn, key)
    elif isinstance(obj, str):
        if key in SKIP_KEYS:
            return
        fn(obj)


def collect_tasks(units=None):
    """返回 {map_key: (text, profile_key)}，包含页面上所有可点击朗读的阿文文本。"""
    units = units if units is not None else load_units()
    tasks = {}

    def add(text, key="narrator"):
        t = str(text or "").strip()
        if not t or not AR_CHAR.search(t) or len(t) > 160:
            return
        tasks[map_key(t, key)] = (t, key)

    def add_fragments(s):
        """中文讲解里夹杂的阿文片段，和 build.py 的 rich() 切分规则一致。"""
        for m in AR_RE.finditer(str(s or "")):
            core = m.group(0).rstrip()
            if core.strip():
                add(core, "narrator")

    for u in units:
        add(u.get("title_ar", ""))
        for d in u.get("dialogues", []):
            add(d.get("title_ar", ""))
            for ln in d.get("lines", []):
                add(ln.get("ar", ""), speaker_key(ln.get("speaker_zh", "")))
        for v in u.get("vocab", []):
            add(v.get("ar", ""))
        for g in u.get("grammar", []):
            for e in g.get("examples", []):
                add(e.get("ar", ""))
        for ex in u.get("exercises", []):
            for it in ex.get("items", []):
                add(it.get("answer_ar", ""))
        for l in u.get("letters", []):
            add(l.get("ar", ""))
            add(l.get("name_ar", ""))
        # 所有字符串里的阿文片段（含讲解、释义、题干、提示等）
        _walk_strings(u, add_fragments)

    # 专题页数据
    try:
        from content_extra import (ALPHABET, BOOK_INFO, CONSONANTS, SCRIPT_NOTES,
                                   STRUCTURE, VOWELS)
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from content_extra import (ALPHABET, BOOK_INFO, CONSONANTS, SCRIPT_NOTES,
                                   STRUCTURE, VOWELS)
    add(BOOK_INFO.get("title_ar", ""))
    _walk_strings([ALPHABET, CONSONANTS, VOWELS, STRUCTURE, SCRIPT_NOTES], add_fragments)
    return tasks


def read_map():
    if MAP_PATH.exists():
        return json.loads(MAP_PATH.read_text(encoding="utf-8"))
    return {}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    ts = collect_tasks()
    print("待配音条目:", len(ts))
    kinds = {}
    for text, key in ts.values():
        kinds[key] = kinds.get(key, 0) + 1
    print("旁白:", kinds.get("narrator", 0), "| 角色音色种类:", len(kinds) - 1)
    print("平均字数: %.1f" % (sum(len(t) for t, _ in ts.values()) / max(len(ts), 1)))
    print("角色分布:", ", ".join("%s=%d" % (k[3:], v) for k, v in
                                sorted(kinds.items(), key=lambda x: -x[1])[:12] if k != "narrator"))
