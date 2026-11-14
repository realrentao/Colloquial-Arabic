# 阿拉伯语口语学习站 · Colloquial-Arabic

面向中国阿拉伯语学习者的在线学习站。**总导航页以「一册教材 = 一个入口」为单位组织**，《埃及口语》是目前已接入的**第 01 册**，并非学习站的全部内容；总导航页同时保留了若干同层级的空白教材位，等待后续教材按同一规则接入。

线上入口：<https://realrentao.github.io/Colloquial-Arabic/>（即仓库根目录的 `index.html`）

## 内容改写原则

首册依据 Routledge《Colloquial Arabic of Egypt — The Complete Course for Beginners》（第三版，2014，Jane Wightwick / Mahmoud Gaafar）重编：

- 原书正文以罗马音转写阿拉伯语，本站**全部改写为带完整元音标注（تَشْكِيل）的阿拉伯文**，元音位置对应埃及口语实际读音；原书罗马音保留在 `roman` 字段中，页面上默认收起，可点顶栏「原书罗马音」对照。
- 原书所有英文讲解、词汇释义、练习指令与文化说明，**改写为润色过的简体中文**，并补充中国学习者易错点提示；人名地名使用通行中译。
- 内容规模：15 个单元（含第 08、15 两个复习单元）、32 段情景对话共 261 句、783 条词汇、77 个语法点、90 组练习共 661 道小题、29 个按单元逐步引入的阿拉伯字母。

## 站点结构

```
index.html                       总导航页（学习站首页，由 assets/catalog.js 渲染）
assets/
  catalog.js                     教材注册表：唯一需要维护的教材清单
  style.css / app.js / favicon.svg
audio/<桶>/<hash>.mp3            预生成配音（edge-tts，按哈希分桶）
books/egyptian-arabic/          《埃及口语》—— 已接入的第 01 册
  index.html                     教材首页（单元目录 + 专题入口 + 学习进度）
  unit-01.html … unit-15.html    15 个可直接访问的单元页
  sounds.html                    发音与转写规则
  alphabet.html                  阿拉伯字母表
  grammar.html                   语法结构总表
  glossary.html                  分类词汇总表（可检索）
  script.html                    阿拉伯文字书写补充
tools/
  build.py                       静态页面生成器
  content_extra.py               专题页中文内容
  audio_spec.py                  音色配置、说话人性别映射、配音文本收集
  gen_audio.py                   批量合成配音（断点续传）
  audio_map.json                 文本＋音色 → 音频路径清单（生成脚本产出）
  data/unit-01.json … unit-15.json  各单元结构化数据
```

**学习流程**：总导航 → 教材首页 → 选择单元或专题 → 单元页（学习目标／情景对话／词汇／语法／练习／文化／字母／小结）→ 通过面包屑、页顶「返回总导航」、页底「上一单元／教材首页／下一单元」返回任意层级。

**主要功能**：点击任意阿拉伯文原文即可发音（站内预生成 mp3）、原书罗马音显示开关、练习答案展开／收起、词汇与总表检索、本机保存的学习进度打卡。

## 配音

- 用 edge-tts 预生成 mp3、普通 `<audio>` 播放，不依赖浏览器语音合成或系统阿拉伯语语音包，内嵌浏览器（如 ima 预览）里同样能发声。
- 词汇、语法例句、练习答案、字母、专题讲解中的阿文等旁白统一用**埃及女声** `ar-EG-SalmaNeural`（语速 -10%）。
- 对话台词按说话人性别选**埃及男声** `ar-EG-ShakirNeural` 或埃及女声；每个角色有固定的音高（pitch）与语速（rate）微调，使同性别不同人物也能区分。性别与微调表见 `tools/audio_spec.py`。
- 页面没有独立朗读按钮：阿文原文本身就是播放入口，悬停／播放时有轻量高亮；极少数未收录的超长文本会回退到浏览器语音合成。
- 改动内容后重新生成：`python tools/gen_audio.py`（已存在音频自动跳过）→ `python tools/build.py`。音频清单 `tools/audio_map.json` 由前者维护，页面 `data-audio` 由后者写入。

## 追加新教材（无需改动现有内容）

总导航页不写死任何一本教材：卡片由 `assets/catalog.js` 的 `books` 数组渲染，卡片总数固定为 `totalSlots`，真实教材排在前，其余位置自动渲染为同版式、同字段结构的空白占位卡。

1. 把新教材的页面放到 `books/<id>/`，入口为 `books/<id>/index.html`（可参照《埃及口语》的层级：教材首页 → 单元页 → 模块，并在每页提供返回总导航与返回教材首页的入口）。
2. 在 `assets/catalog.js` 的 `books` 数组末尾追加一条同结构记录：`id`、`status`、`title_zh`、`title_ar`、`title_original`、`authors`、`edition`、`entry`、`summary`、`tags`、`stats`、`level`。
3. 刷新总导航页即可：新教材自动占据最靠前的预留位，剩余占位卡自动顺延，版式与入口规则保持不变；**`index.html`、样式、已接入教材的页面都不需要修改**。

若新教材同样需要把源数据生成静态页，可在 `tools/` 下新增自己的生成器，与本册互不影响。本册页面可用 `python tools/build.py` 从 `tools/data/*.json` 重新生成。

## 版权说明

原书版权归 Routledge（Taylor & Francis Group）及作者所有。本站为面向中国学习者的教学性重编与整理，仅保留学习所需的内容结构；建议配合使用正版教材与配套音频。
