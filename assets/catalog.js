/* ============================================================
   教材库注册表 · 全站唯一的教材清单来源
   ------------------------------------------------------------
   总导航页 index.html 只读取本文件，不写死任何一本教材。
   追加新教材时：只需在 books 数组里增加一条同结构的记录，
   并把新教材的页面目录放到 books/<id>/ 下即可。
   index.html、样式、已接入教材的页面都无需改动。
   预留位会自动让位：卡片总数固定为 totalSlots，
   真实教材排在前，剩余位置自动渲染为同版式的空白占位卡。
   ============================================================ */
window.LIBRARY = {
  name: "阿拉伯语口语教材库",
  name_ar: "مَكْتَبَةُ الْعَرَبِيَّةِ الْمُحَكَّاةِ",
  tagline: "面向中国学习者的阿拉伯语口语分级学习站 · 教材以「册」为单位逐册接入",
  totalSlots: 6,
  slotNote: "空白教材位与已接入教材位同级、同版式、同入口规则；新增教材只需在 assets/catalog.js 的 books 数组追加一条记录，占位卡会自动让位，无需改动任何现有页面。",
  books: [
    {
      id: "egyptian-arabic",
      status: "active",
      title_zh: "埃及口语",
      title_ar: "الْعَرَبِيَّةُ الْمِصْرِيَّةُ",
      title_original: "Colloquial Arabic of Egypt · The Complete Course for Beginners",
      authors: "简·怀特威克（Jane Wightwick）／马哈茂德·加法尔（Mahmoud Gaafar）",
      edition: "Routledge 第三版，2014",
      entry: "books/egyptian-arabic/index.html",
      summary: "埃及方言入门到进阶的完整课程。本站将原书全部罗马音转写改写为带完整元音标注的阿拉伯文，英文讲解润色为中文，并按「发音 → 字母 → 15 个单元 → 语法总表 → 词汇表」重整为可逐级展开的学习流程。",
      tags: ["埃及方言", "零起点 → B1", "带元音标注", "中文精讲", "已接入"],
      stats: [
        { label: "正课单元", value: "15" },
        { label: "情景对话", value: "32" },
        { label: "词条", value: "783" },
        { label: "练习题", value: "661" }
      ],
      level: "第 01 册 · 已接入"
    }
  ]
};
