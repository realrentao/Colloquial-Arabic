# -*- coding: utf-8 -*-
"""《黎凡特口语》配音规格：音色配置、说话人性别/音色映射、待配音文本收集。

与 tools/audio_spec.py（埃及册）共用 audio/ 目录与 tools/audio_map.json，
但所有 profile key 一律带 "lev:" 前缀 —— 这样即使两册出现完全相同的
阿拉伯文，md5(文本|音色键) 也不会碰撞，各自保留本册口音的音频。

音色：黎凡特地区可用的 edge-tts 音色共 3 组 6 个（叙利亚／黎巴嫩／约旦）。
- 旁白（词汇、例句、练习答案、字母、讲解里的阿文）→ 叙利亚女声 ar-SY-AmanyNeural。
- 对话台词 → 按说话人性别从 3 个女声／3 个男声中确定性分配，并按人物
  微调 pitch / rate，使同性别不同人物也能听出区别。
"""
import hashlib
import json
import re
import sys
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent
ROOT = BOOK_DIR.parents[1]              # 站点根 Colloquial-Arabic/
DATA = BOOK_DIR / "data"
MAP_PATH = ROOT / "tools" / "audio_map.json"   # 与埃及册共用的总清单
AUDIO_ROOT = ROOT / "audio"                    # 与埃及册共用的音频目录

AR_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]"
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s\u064B-\u065F\u0670\u200C\u200D"
    r"،؛؟«»\-—….,;:!?()\u00A0]*"
)
AR_CHAR = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")

# ---------------------------------------------------------------- 音色
NARRATOR = {
    "voice": "ar-SY-AmanyNeural", "rate": "-10%", "pitch": "+0Hz",
    "label": "叙利亚女声 · 旁白（词汇／例句／讲解）",
}
FEMALE_VOICES = ["ar-SY-AmanyNeural", "ar-LB-LaylaNeural", "ar-JO-SanaNeural"]
MALE_VOICES = ["ar-SY-LaithNeural", "ar-LB-RamiNeural", "ar-JO-TaimNeural"]

# 女性角色（教材人名与情景）；未列出的中性角色按男声处理
FEMALE_NAMES = {
    "莱拉", "萨尔玛", "玛丽亚姆", "拉米斯", "萨米拉", "迪娜", "努尔", "里姆",
    "女士", "小姐", "女士一", "女士二", "女职员", "女店员", "女顾客", "女游客",
    "母亲", "妈妈", "阿姨", "女孩", "姑娘", "妻子", "姐姐", "妹妹", "女主人",
    "莱依拉", "莱拉女士", "萨尔玛女士", "玛丽亚姆女士",
}
MALE_NAMES = {
    "艾哈迈德", "塔米尔", "萨拉赫", "穆斯塔法", "萨米尔", "卡里姆", "哈桑",
    "易卜拉欣", "奥马尔", "阿里", "优素福", "先生", "男士一", "男士二",
    "服务员", "店员", "顾客", "游客", "司机", "父亲", "爸爸", "哥哥", "弟弟",
    "店主", "摊主", "讲师", "学生", "朋友们", "众人", "三人齐声",
}
FEMALE_HINTS = ("女士", "小姐", "太太", "母亲", "妈妈", "阿姨", "女孩", "姑娘",
                "妻子", "姐姐", "妹妹", "女", "莱拉", "萨尔玛", "玛丽亚姆",
                "拉米斯", "萨米拉", "迪娜", "努尔", "里姆", "法蒂玛", "阿伊莎")
ALIAS = {"莱依拉": "莱拉", "塔米尔先生": "塔米尔", "艾哈迈德先生": "艾哈迈德"}

PREFIX_SP = "lev:sp:"
NARRATOR_KEY = "lev:narrator"


def _hz(n):
    return ("+%dHz" % n) if n >= 0 else ("%dHz" % n)


def _pct(n):
    return ("+%d%%" % n) if n >= 0 else ("%d%%" % n)


def normalize(name):
    n = str(name or "").strip()
    return ALIAS.get(n, n)


def is_female(name):
    n = normalize(name)
    if n in FEMALE_NAMES:
        return True
    if n in MALE_NAMES:
        return False
    return any(h in n for h in FEMALE_HINTS)


def speaker_key(name):
    n = normalize(name)
    return PREFIX_SP + n if n else NARRATOR_KEY


def profile(key):
    """确定性生成音色：同一人物永远得到同一组 voice / rate / pitch。"""
    if not key or key == NARRATOR_KEY:
        return NARRATOR
    n = key[len(PREFIX_SP):] if key.startswith(PREFIX_SP) else key
    female = is_female(n)
    pool = FEMALE_VOICES if female else MALE_VOICES
    h = int(hashlib.md5(n.encode("utf-8")).hexdigest()[:12], 16)
    voice = pool[h % len(pool)]
    # 叙利亚／黎巴嫩／约旦 三个音色 + 9 档音高 + 5 档语速 → 人物之间区分明显
    pitch = (-18 if female else -22) + (h // 7) % 9 * 4
    rate = -14 + (h // 13) % 5 * 2
    region = {"ar-SY": "叙利亚", "ar-LB": "黎巴嫩", "ar-JO": "约旦"}.get(voice[:5], "黎凡特")
    return {
        "voice": voice, "rate": _pct(rate), "pitch": _hz(pitch),
        "label": "%s%s · %s（%s，%s）" % (
            region, "女声" if female else "男声", n, _pct(rate), _hz(pitch)),
    }


def map_key(text, key=NARRATOR_KEY):
    return str(text or "").strip() + "|" + key


def akey(text, key=NARRATOR_KEY):
    return hashlib.md5(map_key(text, key).encode("utf-8")).hexdigest()[:16]


def relpath(text, key=NARRATOR_KEY):
    h = akey(text, key)
    return "audio/%s/%s.mp3" % (h[0], h)


# ---------------------------------------------------------------- 文本收集
def load_units():
    return [json.loads((DATA / ("unit-%02d.json" % i)).read_text(encoding="utf-8"))
            for i in range(1, 14)]


SKIP_KEYS = {"ar", "answer_ar", "title_ar", "name_ar", "roman", "title_roman"}


def _walk_strings(obj, fn, key=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_strings(v, fn, k)
    elif isinstance(obj, (list, tuple)):
        # 专题页数据（字母表、发音表、语法专题等）用的是 tuple，必须一并遍历
        for v in obj:
            _walk_strings(v, fn, key)
    elif isinstance(obj, str):
        if key in SKIP_KEYS:
            return
        fn(obj)


def collect_tasks(units=None):
    """返回 {map_key: (text, profile_key)}，覆盖页面上所有可点击朗读的阿文。"""
    units = units if units is not None else load_units()
    tasks = {}

    def add(text, key=NARRATOR_KEY):
        t = str(text or "").strip()
        if not t or not AR_CHAR.search(t) or len(t) > 160:
            return
        tasks[map_key(t, key)] = (t, key)

    def add_fragments(s):
        for m in AR_RE.finditer(str(s or "")):
            core = m.group(0).rstrip()
            if core.strip():
                add(core, NARRATOR_KEY)

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
        _walk_strings(u, add_fragments)

    try:
        from content_extra import (ALPHABET, BOOK_INFO, CONSONANTS, SCRIPT_NOTES,
                                   SOUNDS_NOTES, STRUCTURE, VOWELS)
    except ImportError:
        sys.path.insert(0, str(BOOK_DIR))
        from content_extra import (ALPHABET, BOOK_INFO, CONSONANTS, SCRIPT_NOTES,
                                   SOUNDS_NOTES, STRUCTURE, VOWELS)
    add(BOOK_INFO.get("title_ar", ""))
    _walk_strings([ALPHABET, CONSONANTS, VOWELS, SOUNDS_NOTES, STRUCTURE, SCRIPT_NOTES],
                  add_fragments)
    return tasks


def read_map():
    if MAP_PATH.exists():
        return json.loads(MAP_PATH.read_text(encoding="utf-8"))
    return {}


def merge_map(new_entries):
    """把本册新增音频键并入共享清单，保留埃及册已有键，绝不覆盖整份文件。"""
    m = read_map()
    m.update(new_entries)
    MAP_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=0), encoding="utf-8")
    return len(m)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ts = collect_tasks()
    print("黎凡特待配音条目:", len(ts))
    kinds = {}
    for text, key in ts.values():
        kinds[key] = kinds.get(key, 0) + 1
    print("旁白:", kinds.get(NARRATOR_KEY, 0), "| 角色音色种类:", len(kinds) - 1)
    print("平均字数: %.1f" % (sum(len(t) for t, _ in ts.values()) / max(len(ts), 1)))
    voices = {}
    for k in kinds:
        if k != NARRATOR_KEY:
            v = profile(k)["voice"]
            voices[v] = voices.get(v, 0) + 1
    print("音色分布:", voices)
    print("角色示例:", [(k[7:], profile(k)["voice"], profile(k)["pitch"])
                        for k in list(kinds)[1:8]])
