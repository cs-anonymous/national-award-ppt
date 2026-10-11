#!/usr/bin/env node

const pptxgen = require('../node_modules/pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = '孙烨';
pptx.subject = '小米 AI 材料算法工程师岗位——工程实践';
pptx.title = '三、工程实践｜面向材料研发的 Agent 工具链';
pptx.company = '北京航空航天大学';
pptx.lang = 'zh-CN';
pptx.theme = {
  headFontFace: 'Microsoft YaHei',
  bodyFontFace: 'Microsoft YaHei',
  lang: 'zh-CN',
};
pptx.defineSlideMaster({
  title: 'MASTER',
  background: { color: '0B1220' },
  objects: [
    { rect: { x: 0, y: 7.22, w: 13.333, h: 0.28, fill: { color: '101B30' }, line: { color: '101B30' } } },
    { text: { text: '北京航空航天大学 · 孙烨 · AI 材料算法工程师', options: { x: 0.55, y: 7.27, w: 6.8, h: 0.1, fontFace: 'Microsoft YaHei', fontSize: 5.5, color: '74849F', margin: 0, breakLine: false } } },
  ],
  slideNumber: { x: 12.4, y: 7.255, color: '74849F', fontFace: 'Arial', fontSize: 6 },
});

const C = {
  bg: '0B1220', panel: '121D31', panel2: '17243B', line: '2B3B58',
  text: 'F3F6FC', muted: 'A8B5CA', cyan: '49D8E8', orange: 'FFB454',
  green: '65D6A3', purple: 'AD9BFF', red: 'FF7B86', white: 'FFFFFF',
};
const W = 13.333, H = 7.5;

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h, fontFace: opts.fontFace || 'Microsoft YaHei',
    fontSize: opts.fontSize || 14, color: opts.color || C.text,
    bold: opts.bold || false, margin: opts.margin === undefined ? 0 : opts.margin,
    breakLine: false, fit: 'shrink', valign: opts.valign || 'mid',
    align: opts.align || 'left', paraSpaceAfterPt: 0,
    charSpacing: opts.charSpacing || 0, italic: opts.italic || false,
  });
}
function rect(slide, x, y, w, h, fill, radius = 0.12, line = fill) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: radius, fill: { color: fill }, line: { color: line, transparency: line === fill ? 100 : 0, width: 1 } });
}
function line(slide, x1, y1, x2, y2, color = C.line, width = 1.4, dash = 'solid') {
  slide.addShape(pptx.ShapeType.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color, width, dashType: dash, beginArrowType: 'none', endArrowType: 'none' } });
}
function dot(slide, x, y, r, color) { slide.addShape(pptx.ShapeType.ellipse, { x, y, w: r, h: r, fill: { color }, line: { color, transparency: 100 } }); }
function title(slide, kicker, headline, sub) {
  addText(slide, kicker, 0.58, 0.28, 1.9, 0.28, { fontSize: 9, color: C.cyan, bold: true, charSpacing: 1.5 });
  addText(slide, headline, 0.58, 0.62, 11.7, 0.48, { fontSize: 25, bold: true });
  if (sub) addText(slide, sub, 0.58, 1.18, 11.8, 0.3, { fontSize: 10.5, color: C.muted });
}
function tag(slide, text, x, y, w, color = C.cyan) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h: 0.3, rectRadius: 0.08, fill: { color, transparency: 86 }, line: { color, width: 0.8 } });
  addText(slide, text, x, y + 0.01, w, 0.24, { fontSize: 8.5, color, bold: true, align: 'center' });
}
function arrow(slide, x1, y, x2, color = C.cyan) {
  slide.addShape(pptx.ShapeType.chevron, { x: x1, y: y - 0.09, w: x2 - x1, h: 0.18, fill: { color }, line: { color, transparency: 100 } });
}
function card(slide, x, y, w, h, accent, heading, body, label) {
  rect(slide, x, y, w, h, C.panel, 0.12, C.line);
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.06, h, fill: { color: accent }, line: { color: accent, transparency: 100 } });
  if (label) tag(slide, label, x + 0.22, y + 0.2, Math.max(0.75, Math.min(w - 0.45, label.length * 0.13 + 0.35)), accent);
  addText(slide, heading, x + 0.22, y + 0.62, w - 0.44, 0.34, { fontSize: 15, bold: true });
  addText(slide, body, x + 0.22, y + 1.04, w - 0.44, h - 1.22, { fontSize: 10.5, color: C.muted, valign: 'top' });
}

// 1. Chapter opener
{
  const s = pptx.addSlide('MASTER');
  title(s, '三、工程实践', '面向材料研发的 Agent 工具链', '把材料数据、论文证据和性能预测组织成可调用、可验证的研发能力');
  const items = [
    ['01', '材料数据底座', '知识图谱 · 本体 · 多模态数据', C.cyan],
    ['02', '研发工具封装', '检索 · 论文证据 · 性能预测', C.orange],
    ['03', 'Agent Harness', '规划 · MCP 工具调用 · 证据组织', C.green],
    ['04', '面向小米落地', '接入仿真、表征与实体实验流程', C.purple],
  ];
  items.forEach((it, i) => {
    const x = 0.72 + i * 3.1;
    rect(s, x, 2.22, 2.55, 2.55, C.panel, 0.14, C.line);
    addText(s, it[0], x + 0.2, 2.43, 0.5, 0.35, { fontSize: 13, color: it[3], bold: true });
    addText(s, it[1], x + 0.2, 3.03, 2.05, 0.4, { fontSize: 15, bold: true });
    addText(s, it[2], x + 0.2, 3.64, 2.05, 0.62, { fontSize: 10, color: C.muted, valign: 'top' });
    dot(s, x + 0.2, 4.47, 0.1, it[3]);
    if (i < items.length - 1) arrow(s, x + 2.65, 3.4, x + 3.02, C.line);
  });
  addText(s, '当前工程实践聚焦材料数据与智能研发工具；多智能体协作、仿真和实验室闭环是下一步接入方向。', 0.8, 5.55, 11.7, 0.36, { fontSize: 13, color: C.text, align: 'center' });
}

// 2. Materials data foundation
{
  const s = pptx.addSlide('MASTER');
  title(s, '三、工程实践 · 01', '材料数据底座：从知识图谱到研发数据服务', '把成分、工艺、性能和论文证据组织成可检索、可计算的材料对象');
  card(s, 0.66, 1.83, 3.05, 3.82, C.cyan, '材料知识图谱', '参与国家重点研发计划课题，主导多源材料知识图谱、本体设计与可视化模块。\n\n将电子态特征、晶体结构、合成策略等多模态数据纳入统一表示。', '项目基础');
  card(s, 3.93, 1.83, 3.05, 3.82, C.orange, '数字化研发平台', '形成 10⁵ 级多模态材料数据库，支撑合成条件推荐与知识发现。\n\n工程重点是数据清洗、实体组织、关系建模和面向研发任务的查询。', '数据服务');
  card(s, 7.20, 1.83, 2.5, 3.82, C.green, '材料 Agent', '在材料智能体项目中，把数据库检索、论文检索和性能预测封装为可调用工具。\n\n查询结果保留来源和证据，便于后续验证。', '工具入口');
  rect(s, 9.98, 1.83, 2.68, 3.82, C.panel2, 0.12, C.line);
  addText(s, '数据对象', 10.22, 2.08, 2.1, 0.3, { fontSize: 14, color: C.orange, bold: true });
  const objs = [['成分', C.cyan], ['工艺', C.orange], ['性能', C.green], ['论文证据', C.purple]];
  objs.forEach((o, i) => {
    const yy = 2.68 + i * 0.55;
    dot(s, 10.23, yy + 0.08, 0.13, o[1]);
    addText(s, o[0], 10.5, yy, 1.6, 0.28, { fontSize: 12, bold: true });
    if (i < objs.length - 1) line(s, 10.3, yy + 0.3, 10.3, yy + 0.52, C.line, 1);
  });
  addText(s, '个人贡献', 10.22, 4.83, 1.2, 0.24, { fontSize: 9, color: C.muted, bold: true });
  addText(s, '知识图谱 · 本体 · 可视化', 10.22, 5.12, 2.1, 0.28, { fontSize: 10.5, color: C.text });
}

// 3. Agent Harness architecture
{
  const s = pptx.addSlide('MASTER');
  title(s, '三、工程实践 · 02', 'Agent Harness：把研发问题拆成可执行工作流', '围绕材料问题的意图识别、工具选择、证据汇总和结果校验组织 Agent 运行支撑');
  const stages = [
    ['用户问题', '配方、工艺、性能或论文证据', C.text],
    ['Intent Plan', '识别任务类型与目标字段', C.cyan],
    ['Workflow', '确定检索、预测和验证步骤', C.orange],
    ['MCP Tools', '调用数据库、论文库和预测器', C.green],
    ['Evidence List', '统一整理来源、结果与置信信息', C.purple],
    ['回答 / 校验', '基于证据生成并检查输出', C.red],
  ];
  const y = 2.1, x0 = 0.54, gap = 0.13, bw = 1.93;
  stages.forEach((st, i) => {
    const x = x0 + i * (bw + gap);
    rect(s, x, y, bw, 1.5, i === 3 ? '18352F' : C.panel, 0.1, st[2]);
    addText(s, st[0], x + 0.12, y + 0.25, bw - 0.24, 0.3, { fontSize: 12, bold: true, color: st[2] });
    addText(s, st[1], x + 0.12, y + 0.72, bw - 0.24, 0.48, { fontSize: 8.5, color: C.muted, valign: 'top' });
    if (i < stages.length - 1) arrow(s, x + bw + 0.02, y + 0.75, x + bw + gap - 0.02, C.line);
  });
  addText(s, '已实现的工具入口', 0.62, 4.15, 2.1, 0.3, { fontSize: 11, color: C.muted, bold: true });
  const tools = [
    ['material_db_hybrid_search', '结构化字段、数值筛选、排序、BM25 / 向量检索', C.cyan],
    ['paper_browser', '论文索引、段落读取、表格与图注证据', C.orange],
    ['property_predictor', '根据成分预测 Hcj、Br、BHmax', C.green],
  ];
  tools.forEach((t, i) => {
    const x = 0.62 + i * 4.15;
    rect(s, x, 4.58, 3.85, 1.2, C.panel, 0.1, C.line);
    addText(s, t[0], x + 0.16, 4.8, 3.5, 0.25, { fontFace: 'Consolas', fontSize: 10.5, color: t[2], bold: true });
    addText(s, t[1], x + 0.16, 5.17, 3.47, 0.42, { fontSize: 9, color: C.muted, valign: 'top' });
  });
  addText(s, '架构边界：LLM 负责理解和规划，数据库 / MCP 工具负责数值过滤与证据获取，避免让模型直接“猜”材料事实。', 0.65, 6.2, 12.0, 0.34, { fontSize: 11, color: C.text });
}

// 4. Engineering implementation details
{
  const s = pptx.addSlide('MASTER');
  title(s, '三、工程实践 · 03', '工程实现：工具调用、证据组织与可追溯性', '把 Agent 能力落到明确的接口、数据结构和测试边界，而不是停留在对话演示');
  const cols = [
    [0.67, C.cyan, '意图规划', 'UserPromptSubmit hook\n→ intent_plan 结构化输出\n→ 主 Agent 选择工具', '已实现'],
    [4.47, C.orange, '论文证据', 'paper_search / paper_read\n支持 local 与 HTTP 来源\n按 paper / section 返回证据', '已实现'],
    [8.27, C.green, '材料预测', '结构化成分输入\n→ predict_property\n输出 Hcj、Br、BHmax', '已实现'],
  ];
  cols.forEach(([x, accent, h, body, label]) => card(s, x, 1.95, 3.45, 2.6, accent, h, body, label));
  rect(s, 0.67, 4.95, 11.05, 1.15, C.panel2, 0.12, C.line);
  addText(s, '一次材料问题的工程链路', 0.92, 5.17, 2.0, 0.25, { fontSize: 10, color: C.muted, bold: true });
  const steps = ['问题解析', '检索 / 预测', '证据合并', '结果校验'];
  steps.forEach((st, i) => {
    const x = 3.02 + i * 2.02;
    rect(s, x, 5.17, 1.5, 0.48, i === 2 ? '24463D' : C.panel, 0.08, i === 2 ? C.green : C.line);
    addText(s, st, x, 5.27, 1.5, 0.22, { fontSize: 10, bold: true, align: 'center', color: i === 2 ? C.green : C.text });
    if (i < steps.length - 1) arrow(s, x + 1.57, 5.41, x + 1.94, C.line);
  });
  addText(s, '代码与测试覆盖 MCP schema、索引更新、分页读取、工具输入校验和典型材料问题。', 0.7, 6.42, 11.2, 0.26, { fontSize: 10.5, color: C.muted });
}

// 5. Xiaomi fit / future plan
{
  const s = pptx.addSlide('MASTER');
  title(s, '三、工程实践 · 04', '面向小米：把 Agent 接入材料研发闭环', '已有的数据与工具基础，下一步对接仿真、表征和实体实验，形成可评估、可迭代的研发系统');
  const steps = [
    ['研发任务拆解', '把材料设计目标转成成分、工艺、性能和约束条件', C.cyan],
    ['多智能体协作', '由规划 Agent 调度数据、论文、预测、DFT / MD / FEM 与实验工具', C.orange],
    ['验证与落地', '保留证据链、实验记录和评测指标，支持产品场景持续迭代', C.green],
  ];
  steps.forEach((st, i) => {
    const x = 0.72 + i * 4.16;
    rect(s, x, 2.05, 3.55, 2.25, C.panel, 0.13, st[2]);
    addText(s, `0${i + 1}`, x + 0.22, 2.3, 0.4, 0.28, { fontSize: 13, color: st[2], bold: true });
    addText(s, st[0], x + 0.22, 2.83, 2.9, 0.35, { fontSize: 16, bold: true });
    addText(s, st[1], x + 0.22, 3.38, 2.95, 0.56, { fontSize: 10.5, color: C.muted, valign: 'top' });
    if (i < steps.length - 1) arrow(s, x + 3.65, 3.16, x + 4.02, C.line);
  });
  rect(s, 0.72, 4.9, 11.95, 1.2, C.panel2, 0.12, C.line);
  addText(s, '我能直接迁移的能力', 0.98, 5.15, 2.15, 0.28, { fontSize: 11, color: C.muted, bold: true });
  addText(s, '知识图谱与本体建模  ·  Agent 规划与工具调用  ·  论文 / 数据证据组织  ·  可视化与系统部署', 3.12, 5.13, 8.9, 0.3, { fontSize: 12.5, color: C.text, bold: true });
  addText(s, '目标：让材料研发 Agent 不只给出答案，还能说明依据、调用工具并留下可复现实验路径。', 0.98, 5.62, 10.8, 0.26, { fontSize: 10.5, color: C.cyan });
}

const out = process.argv[2] || '../小米-AI材料算法工程师-工程实践.pptx';
pptx.writeFile({ fileName: out });
