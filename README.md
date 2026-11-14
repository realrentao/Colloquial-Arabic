# 阿拉伯语口语学习站 · Colloquial-Arabic

面向中国阿拉伯语学习者的在线学习站。**总导航页以「一册教材 = 一个入口」为单位组织**，目前已接入**第 01 册《埃及口语》**与**第 02 册《黎凡特口语》**，任何单册都不是学习站的全部内容；总导航页同时保留了若干同层级的空白教材位，等待后续教材按同一规则接入。

线上入口：<https://realrentao.github.io/Colloquial-Arabic/>（即仓库根目录的 `index.html`）

## 内容改写原则

两册均把原书正文的罗马音转写**改写为带完整元音标注（تَشْكِيل）的阿拉伯文**，元音位置对应各自方言的实际读音；原书罗马音保留在 `roman` 字段中，页面默认收起，可点顶栏「原书罗马音」对照。原书所有英文讲解、词汇释义、练习指令与文化说明一律**改写为润色过的简体中文**，人名地名用通行中译。

- **第 01 册《埃及口语》**：Routledge《Colloquial Arabic of Egypt — The Complete Course for Beginners》（第三版，2014，Jane Wightwick / Mahmoud Gaafar）。15 个单元（含第 08、15 两个复习单元）、32 段情景对话共 261 句、783 条词汇、77 个语法点、90 组练习共 661 道小题、29 个按单元逐步引入的阿拉伯字母。转写体系用 `9`=ع、`g`=ج（埃及读 g）、`H`=ح、`S/D/T/Z`=强调音。
- **第 02 册《黎凡特口语》**：Routledge《Colloquial Arabic — Levantine: The Complete Course for Beginners》（第一版，2016，Mohammad Al-Masri）。13 个正课单元（无单独复习单元），情景对话逐句收录、每单元词汇表与语法要点、练习与参考答案、文化点滴，另配 5 个专题页。**本书转写体系与埃及册不同**：`3`=ع、`x`=خ、`j`=ج（读 j）、`H`=ح、`S/D/T/DH`=强调音、`ʔ`/反引号 = ء；ق 在城市口语多读喉塞音；冠词作 `il-`／`li-`。原书书末附无元音的阿拉伯文词汇表，本站据此校准字形并补全元音。

## 站点结构

```
index.html                       总导航页（学习站首页，由 assets/catalog.js 渲染）
assets/
  catalog.js                     教材注册表：唯一需要维护的教材清单（现有 2 册）
  style.css / app.js / favicon.svg   两册共用；app.js 按页面 data-book-id 区分学习进度
audio/<桶>/<hash>.mp3            两册共用目录，预生成配音（edge-tts，按哈希分桶）
books/egyptian-arabic/          《埃及口语》—— 已接入的第 01 册
  index.html                     教材首页（15 单元目录 + 专题入口 + 学习进度）
  unit-01.html … unit-15.html    15 个单元页
  sounds / alphabet / grammar / glossary / script.html   5 个专题页
books/levantine-arabic/         《黎凡特口语》—— 已接入的第 02 册（与第 01 册同版式）
  index.html                     教材首页（13 单元目录 + 专题入口 + 学习进度）
  unit-01.html … unit-13.html    13 个单元页
  sounds / alphabet / grammar / glossary / script.html   5 个专题页
tools/                            第 01 册工具链（不要改动，页面已定稿）
  build.py / content_extra.py / audio_spec.py / gen_audio.py
  audio_map.json                 两册共享的「文本＋音色 → 音频路径」总清单
  data/unit-01.json … unit-15.json
tools/levantine/                  第 02 册工具链（独立，不改动第 01 册）
  build.py                       第 02 册静态页面生成器
  content_extra.py               第 02 册专题页中文内容
  audio_spec.py                  黎凡特音色配置、说话人性别/音色映射、配音文本收集
  gen_audio.py                   批量合成配音（断点续传，合并写入共享清单）
  data/unit-01.json … unit-13.json
```

**学习流程**：总导航 → 教材首页 → 选择单元或专题 → 单元页（学习目标／情景对话／词汇／语法／练习／文化／小结）→ 通过面包屑、页顶「返回总导航」、页底「上一单元／教材首页／下一单元」返回任意层级。

**主要功能**：点击任意阿拉伯文原文即可发音（站内预生成 mp3）、原书罗马音显示开关、练习答案展开／收起、词汇与总表检索、本机保存的学习进度打卡（两册进度各自独立）。

## 配音

- 用 edge-tts 预生成 mp3、普通 `<audio>` 播放，不依赖浏览器语音合成或系统阿拉伯语语音包，内嵌浏览器（如 ima 预览）里同样能发声；页面没有独立朗读按钮，阿文原文本身就是播放入口。
- **第 01 册（埃及口音）**：旁白用埃及女声 `ar-EG-SalmaNeural`；对话按说话人性别选 `ar-EG-ShakirNeural`（男）／Salma（女），每个角色有固定的 pitch／rate 微调。配置见 `tools/audio_spec.py`。
- **第 02 册（黎凡特口音）**：旁白用叙利亚女声 `ar-SY-AmanyNeural`；对话按说话人性别从叙利亚／黎巴嫩／约旦三组男女声共 6 个音色（`ar-SY-*`、`ar-LB-*`、`ar-JO-*`）中确定性分配，并按人物微调 pitch／rate，同性别不同人物也能听出区别。配置见 `tools/levantine/audio_spec.py`。
- 两册音频键均带各自的 profile 前缀（第 02 册为 `lev:`），即使出现完全相同的阿拉伯文也不会串音；清单 `tools/audio_map.json` 由两册生成脚本合并维护。
- 改动内容后重新生成：
  - 第 01 册：`python tools/gen_audio.py` → `python tools/build.py`
  - 第 02 册：`python tools/levantine/gen_audio.py` → `python tools/levantine/build.py`
  - 已存在的音频自动跳过；`data-audio` 由各自的 build.py 写入。

## 追加新教材（无需改动现有内容）

总导航页不写死任何一本教材：卡片由 `assets/catalog.js` 的 `books` 数组渲染，卡片总数固定为 `totalSlots`，真实教材排在前，其余位置自动渲染为同版式、同字段结构的空白占位卡。

1. 把新教材的页面放到 `books/<id>/`，入口为 `books/<id>/index.html`（可参照已接入两册的层级：教材首页 → 单元页 → 模块，并在每页提供返回总导航与返回教材首页的入口）。
2. 在 `assets/catalog.js` 的 `books` 数组末尾追加一条同结构记录：`id`、`status`、`title_zh`、`title_ar`、`title_original`、`authors`、`edition`、`entry`、`summary`、`tags`、`stats`、`level`。
3. 刷新总导航页即可：新教材自动占据最靠前的预留位，剩余占位卡自动顺延，版式与入口规则保持不变；**样式与已接入教材的页面都不需要修改**。`index.html` 的动态卡片部分也无需改动，仅其静态说明文案（导语段、占位提示、页脚、`<noscript>` 兜底卡）可视情况同步为最新册数。

若新教材同样需要把源数据生成静态页，可在 `tools/` 下新增自己的生成器（参照 `tools/levantine/`），与已接入各册互不影响。页面 `body` 上加 `data-book-id`（另可加 `data-unit-count`、`data-tts-locale`）即可让共用的 `app.js` 为它单独保存学习进度；不加时默认沿用第 01 册行为。

## 版权说明

两册原书版权归 Routledge（Taylor & Francis Group）及各自作者所有。本站为面向中国学习者的教学性重编与整理，仅保留学习所需的内容结构；建议配合使用正版教材与配套音频。
