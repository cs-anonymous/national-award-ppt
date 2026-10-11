#!/usr/bin/env python3
"""Generate the six-page WKG engineering-practice SVG chapter.

The page grammar intentionally reuses the Xiaomi engineering SVG master:
white canvas, Beihang emblem, blue chapter heading, dark subtitle, pale cards,
and self-contained image references after embedding.
"""
from __future__ import annotations

import sys
from pathlib import Path
import shutil

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import generate_xiaomi_engineering_svg as b

ROOT = SCRIPT_DIR.parent
b.OUT = ROOT / "svg-src" / "ant-wkg"
ASSET_PREFIX = "../xiaomi-engineering/assets/"


def image(path, x, y, w, h, opacity=1, preserve="xMidYMid meet"):
    return (
        f'<image href="{ASSET_PREFIX}{path}" x="{x}" y="{y}" width="{w}" '
        f'height="{h}" preserveAspectRatio="{preserve}" opacity="{opacity}"/>'
    )


# The base module resolves image() through its own module globals. Replace it
# so the shared header and drawing helpers point at the Xiaomi asset library.
b.image = image

PANEL = b.PANEL
PANEL2 = b.PANEL2
LINE = b.LINE
TEXT = b.TEXT
MUTED = b.MUTED
CYAN = b.CYAN
ORANGE = b.ORANGE
GREEN = b.GREEN
PURPLE = b.PURPLE
RED = b.RED


def panel(x, y, w, h, accent, heading, lines, label=None, body_size=24):
    return b.card_block(x, y, w, h, accent, heading, lines, label, body_size)


def slide1():
    out = [
        b.header(
            "三、工程实践",
            "面向知识服务的工程实践总览",
            "从科研文献和多源数据出发，形成知识构建、检索服务、Agent 调用与质量迭代的完整链路",
            1,
        )
    ]
    stages = [
        ("01", "知识发现", ["论文、数据库", "与用户问题"], CYAN),
        ("02", "知识构建", ["标注、抽取", "本体与图谱"], ORANGE),
        ("03", "知识校验", ["来源、规则", "证据与评测"], GREEN),
        ("04", "知识服务", ["检索、RAG、MCP", "与 Agent"], PURPLE),
        ("05", "监控演进", ["日志、反馈", "回归与版本"], RED),
    ]
    for i, (number, heading, body, accent) in enumerate(stages):
        x = 48 + i * 366
        out += [
            b.rect(x, 218, 322, 218, PANEL, LINE, 2, 18),
            b.txt(x + 28, 260, number, 26, accent, 700),
            b.txt(x + 28, 318, heading, 30, TEXT, 700),
            b.multiline(x + 28, 370, body, 23, MUTED, 1.25),
        ]
        if i < len(stages) - 1:
            out += [b.line(x + 328, 326, x + 356, 326, LINE, 4),
                    f'<polygon points="{x+350},316 {x+365},326 {x+350},336" fill="{LINE}"/>']
    out += [
        b.rect(48, 500, 1824, 475, PANEL2, LINE, 2, 18),
        b.txt(82, 552, "已有工程证据", 30, CYAN, 700),
        b.txt(82, 610, "科研文献", 25, ORANGE, 700),
        b.multiline(82, 652, ["ITAS：多领域科研文献标注、审核与数据导出。",
                              "MaterialBrain：人机协同、RAG few-shot",
                              "与结构化抽取、评测和数据回流。"], 23, TEXT, 1.28),
        b.txt(700, 610, "知识图谱", 25, GREEN, 700),
        b.multiline(700, 652, ["国家重点研发计划：多源材料数据、领域本体、",
                                "知识图谱与研发任务；GeneticFlow：在线服务。"], 23, TEXT, 1.28),
        b.txt(1310, 610, "智能服务", 25, PURPLE, 700),
        b.multiline(1310, 652, ["MaterAgent：Agent Harness、",
                                "Database MCP、Paper Browser MCP；",
                                "QA benchmark：查询、筛选、",
                                "取证和机理分析。"], 23, TEXT, 1.23),
        b.line(82, 788, 1835, 788, LINE, 2),
        b.txt(82, 846, "岗位对应", 25, CYAN, 700),
        b.txt(300, 846, "知识发现 → 构建 → 校验 → 服务化 → 监控 → 演进", 29, TEXT, 700),
        b.txt(82, 910, "核心能力", 25, ORANGE, 700),
        b.txt(300, 910, "把知识对象、证据链和工具接口组织成可调用、可验证的运行时能力", 26, TEXT, 700),
    ]
    b.save("01-overview.svg", "".join(out))


def slide2():
    # Keep the approved Xiaomi material-KG page intact; only relocate its
    # shared asset references into the ant-wkg source directory.
    source = ROOT / "svg-src" / "xiaomi-engineering" / "02-material-kg.svg"
    target = b.OUT / "01-knowledge-data.svg"
    content = source.read_text()
    content = content.replace('href="assets/', 'href="../xiaomi-engineering/assets/')
    content = content.replace('>02</text>', '>01</text>')
    target.write_text(content)
    return

    # Legacy generated version retained below for reference.
    out = [
        b.header(
            "三、工程实践",
            "知识数据底座：从多源数据到知识图谱服务",
            "国家重点研发计划课题助理：参与课题申请、年度/中期验收与平台开发；负责知识图谱、本体和可视化模块",
            1,
        ),
        b.rect(48, 194, 866, 826, PANEL, LINE, 2, 18),
        b.txt(80, 246, "多源异构数据融合与研发任务", 30, CYAN, 700),
        image("mofkg/fig2-workflow.png", 76, 272, 810, 382),
        image("mofkg/fig1-data-sources.png", 76, 662, 810, 210),
        b.multiline(80, 903, [
            "文献、计算、实验和公共数据库进入统一的数据底座；",
            "围绕实体、关系、属性和来源构建材料领域知识对象。",
        ], 24, TEXT, 1.28),
        b.rect(942, 194, 930, 826, PANEL, LINE, 2, 18),
        b.txt(974, 246, "知识图谱：本体、质量与研发应用", 30, ORANGE, 700),
        image("expath-neo4j.png", 970, 274, 628, 400),
        b.txt(1620, 306, "领域本体", 23, GREEN, 700),
        image("MOFKG-onto.png", 1620, 326, 220, 125),
        b.txt(1620, 496, "数据统计", 23, CYAN, 700),
        image("mofkg-statistic.png", 1610, 520, 236, 158),
        b.multiline(974, 750, [
            "知识对象：材料、前驱体、结构单元、合成操作与论文。",
            "关系属性：组成、合成、操作条件、性能和文献来源。",
            "质量控制：实体对齐、重复清理、来源区分和字段核验。",
            "服务应用：知识图谱用于合成条件推荐与知识发现。",
            "规模：10^5 级多模态数据库，包含 46,701 条合成条件。",
        ], 24, TEXT, 1.34),
    ]
    b.save("01-knowledge-data.svg", "".join(out))


def slide3():
    out = [
        b.header(
            "三、工程实践",
            "ITAS：面向科研文献的多领域知识构建流程",
            "产品经理、软件开发；把不同学科论文中的段落、实体和关系，转化为可审核、可训练、可复用的结构化知识",
            2,
        ),
        b.rect(48, 194, 892, 826, PANEL, LINE, 2, 18),
        b.txt(80, 246, "科研文献 → 标注数据 → 结构化知识", 30, CYAN, 700),
        image("itas-roadshow-media/image34.png", 78, 278, 286, 430),
        b.txt(398, 304, "一套平台，适配不同学科", 26, ORANGE, 700),
        b.multiline(398, 346, [
            "支持社会科学、生物医学、工程技术等科研文献；",
            "按项目配置实体类别、关系、属性和标注规则。",
            "系统管理员管理项目与模型，标注员负责证据标注，",
            "科研人员通过抽取结果完成检索、分析与知识复用。",
        ], 23, TEXT, 1.32),
        b.txt(398, 516, "知识生产的两个子系统", 25, GREEN, 700),
        b.multiline(398, 556, [
            "文本标注：项目管理、PDF 批量上传、段落定位、",
            "实体标注、审核和带位置证据的数据导出；",
            "智能挖掘：模型管理、段落提取、实体识别、",
            "记录管理、模型训练与应用。",
        ], 23, TEXT, 1.30),
        image("itas-roadshow-media/image45.png", 78, 748, 258, 156),
        image("itas-roadshow-media/image42.png", 350, 748, 258, 156),
        image("itas-roadshow-media/image48.png", 622, 748, 286, 156),
        b.txt(78, 932, "原文定位与实体标注", 20, MUTED, 700),
        b.txt(350, 932, "任务、标注员与导出管理", 20, MUTED, 700),
        b.txt(622, 932, "抽取结果与结构化字段", 20, MUTED, 700),
        b.rect(974, 194, 898, 826, PANEL, LINE, 2, 18),
        b.txt(1006, 246, "从文献阅读到知识生产的闭环", 30, ORANGE, 700),
        image("itas-pdf-html.png", 1006, 280, 810, 132),
        b.txt(1006, 462, "① 配置领域知识模式", 25, GREEN, 700),
        b.multiline(1006, 500, ["按研究项目定义实体类别、属性、关系和标注规则；", "同一套平台可以切换不同科研领域与研究任务。"], 23, TEXT, 1.32),
        b.txt(1006, 594, "② 标注、审核与证据定位", 25, CYAN, 700),
        b.multiline(1006, 632, ["从 PDF 转换后的文本中定位段落和实体，保留原文位置；", "标注员提交后由管理员审核，保证数据一致性与可追溯性。"], 23, TEXT, 1.32),
        b.txt(1006, 726, "③ 模型训练与智能挖掘", 25, ORANGE, 700),
        b.multiline(1006, 764, ["审核通过的标注结果导出为模型训练数据；", "智能挖掘子系统用预设定义和小样本学习，从未标注文献中抽取关键信息。"], 23, TEXT, 1.32),
        b.txt(1006, 884, "④ 反馈回流", 25, GREEN, 700),
        b.multiline(1006, 922, ["抽取结果回到科研人员和标注员复核，", "形成“定义—标注—训练—抽取—修订”的知识构建闭环。"], 23, TEXT, 1.32),
    ]
    b.save("02-itas-knowledge-construction.svg", "".join(out))


def slide4():
    # Keep the detailed MaterialBrain page from the approved Xiaomi chapter.
    source = ROOT / "svg-src" / "xiaomi-engineering" / "04-materialbrain.svg"
    target = b.OUT / "03-materialbrain.svg"
    content = source.read_text()
    content = content.replace('href="assets/', 'href="../xiaomi-engineering/assets/')
    content = content.replace('>04</text>', '>03</text>')
    target.write_text(content)
    return

    # Legacy generated version retained below for reference.
    out = [
        b.header(
            "三、工程实践",
            "MaterialBrain：从科研文献到结构化知识",
            "在 ITAS 产生的标注基础上，结合人机协同、BM25 检索和 few-shot LLM 抽取，持续提高知识生产质量",
            3,
        ),
        b.rect(48, 194, 826, 826, PANEL, LINE, 2, 18),
        b.txt(80, 246, "人机协同的文献抽取流程", 30, CYAN, 700),
        image("materialbrain-fig1.png", 72, 280, 778, 642),
        b.txt(80, 966, "Human-AI curation → Information retrieval → Structured synthesis routes", 21, MUTED),
        b.rect(902, 194, 970, 826, PANEL, LINE, 2, 18),
        b.txt(934, 246, "从冷启动到高质量标注库的迭代", 30, ORANGE, 700),
        b.txt(934, 312, "① 人工定义与联合整理", 25, GREEN, 700),
        b.multiline(934, 350, ["从文献中定位关键段落，LLM 预标注后由领域人员修订；", "把核验过的样本沉淀为可复用的 few-shot 示例。"], 24, TEXT, 1.34),
        b.txt(934, 454, "② 检索增强的结构化抽取", 25, CYAN, 700),
        b.multiline(934, 492, ["用 BM25 为当前段落检索 4–6 个相关示例，", "结合领域定义和提示词，让 LLM 输出统一 JSON 结构。"], 24, TEXT, 1.34),
        b.txt(934, 596, "③ 质量评估与数据回流", 25, GREEN, 700),
        b.multiline(934, 634, ["抽取结果由指标和人工样本共同评估；", "低质量样本回到标注库，更新示例和下一轮抽取策略。"], 24, TEXT, 1.34),
        image("materialbrain-fig3.png", 934, 744, 884, 234),
        b.txt(934, 1000, "图 3：冷启动阶段由 LLM 预标注并经人工整理；主动学习挑选高价值样本，", 21, MUTED, 400),
        b.txt(934, 1028, "再通过 FS-ICL、人工修订和 batch/epoch 迭代持续更新高质量标注数据库。", 21, MUTED, 400),
    ]
    b.save("03-materialbrain.svg", "".join(out))


def slide_ler():
    """Keep the approved Xiaomi LER overview SVG unchanged."""
    source = ROOT / "svg" / "xiaomi-engineering" / "ler-overview.svg"
    target = b.OUT / "04-ler-overview.svg"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def slide5():
    out = [
        b.header(
            "三、工程实践",
            "MaterAgent：面向知识服务的 Agent Harness",
            "架构设计、软件开发；把知识检索、论文证据和领域工具接入可规划、可校验的 Agent 运行时",
            5,
        ),
        image("materagent-stack.png", 48, 208, 1102, 810),
        b.rect(90, 217, 586, 126, "#FFFFFF", "none", 0, 0),
        b.txt(108, 251, "服务入口与基础框架", 29, CYAN, 700),
        b.multiline(108, 291, ["交互：飞书 / 钉钉 / 企业微信 / Web IDE", "API Gateway / FastAPI / REST / WebSocket"], 23, TEXT, 1.38),
        b.rect(1178, 194, 694, 826, PANEL, LINE, 2, 18),
        b.txt(1210, 246, "面向知识服务的运行时边界", 30, GREEN, 700),
        b.txt(1210, 302, "Query Router · 任务进入", 26, CYAN, 700),
        b.multiline(1210, 344, ["从问题中提取意图、实体、条件与目标字段，", "把自然语言问题转成稳定的任务上下文。"], 24, TEXT, 1.35),
        b.txt(1210, 436, "Plan Agent · 工作流规划", 26, ORANGE, 700),
        b.multiline(1210, 478, ["根据任务类型决定数据库检索、论文取证和预测步骤，", "明确依赖关系、工具输入和中间结果。"], 24, TEXT, 1.35),
        b.txt(1210, 570, "Tool Executor · 工具调用", 26, GREEN, 700),
        b.multiline(1210, 612, ["调用 Database MCP、Paper Browser 和领域工具；", "汇集结构化记录、原文段落与来源元数据。"], 24, TEXT, 1.35),
        b.txt(1210, 704, "Verify Agent · 证据校验", 26, CYAN, 700),
        b.multiline(1210, 746, ["按证据完整性、输出格式、数值和完成条件校验；", "证据不足时反馈并重新规划，而不是直接生成答案。"], 24, TEXT, 1.35),
        b.line(1210, 815, 1840, 815),
        b.txt(1210, 859, "状态链路", 25, CYAN, 700),
        b.multiline(1210, 902, ["RUNNING → TOOL_CALL → OBSERVE", "→ VERIFY → DONE / REPLAN"], 24, TEXT, 1.40),
        b.txt(1210, 992, "当前重点：框架适配、工具接口与知识检索链路持续开发", 22, MUTED),
    ]
    b.save("05-materagent.svg", "".join(out))


def slide6():
    out = [
        b.header(
            "三、工程实践",
            "知识服务原子能力：检索、取证与质量评测",
            "Database MCP 与 Paper Browser MCP 将结构化数据、论文原文和证据元数据组织成可调用接口",
            6,
        ),
        b.rect(48, 194, 896, 330, PANEL, LINE, 2, 18),
        b.txt(80, 246, "Database MCP：结构化知识检索", 30, CYAN, 700),
        b.txt(80, 292, "material_db_hybrid_search", 26, CYAN, 700, family="Consolas"),
        b.multiline(80, 338, [
            "输入：query / retrieval_method / top_k（1–20）。",
            "支持：hybrid / vector / bm25；dense / sparse 为别名。",
            "输出：排序记录、相关性分数、字段和来源元数据。",
            "精确筛选、数值比较和 Top-k 排序由数据库完成。",
        ], 25, TEXT, 1.35),
        b.rect(976, 194, 896, 330, PANEL, LINE, 2, 18),
        b.txt(1008, 246, "Paper Browser：论文证据读取", 30, ORANGE, 700),
        b.txt(1008, 292, "paper_search / paper_read", 26, ORANGE, 700, family="Consolas"),
        b.multiline(1008, 338, [
            "按 DOI、标题、章节或正文定位论文。",
            "用 paper_id / section_id 读取段落、表格和图注。",
            "保留来源、读取位置和上下文，形成可复核证据。",
            "将知识记录关联回论文原文，而不是只返回模型生成文本。",
        ], 25, TEXT, 1.35),
        b.rect(48, 550, 1824, 245, PANEL2, LINE, 2, 18),
        b.txt(80, 598, "端到端调用：从问题到带证据的回答", 30, CYAN, 700),
        b.txt(80, 642, "问题：满足限定条件的材料/实体，哪一个结果最好？依据来自哪里？", 27, TEXT, 700),
    ]
    steps = [
        ("1", "意图识别", "实体 / 条件 / 目标", CYAN),
        ("2", "数据库检索", "过滤 / 排序 / 去重", ORANGE),
        ("3", "论文补证", "定位原文段落", GREEN),
        ("4", "证据合并", "记录 / 分数 / 来源", PURPLE),
        ("5", "校验输出", "条件 / 单位 / 引用", RED),
    ]
    for i, (n, name, desc, color) in enumerate(steps):
        x = 80 + i * 356
        out += [
            b.rect(x, 680, 328, 86, PANEL, color, 2, 12),
            b.txt(x + 16, 715, n, 25, color, 700),
            b.txt(x + 54, 715, name, 24, TEXT, 700),
            b.txt(x + 16, 750, desc, 21, MUTED),
        ]
        if i < 4:
            out += [b.line(x + 332, 723, x + 347, 723, LINE, 3),
                    f'<polygon points="{x+344},716 {x+354},723 {x+344},730" fill="{LINE}"/>']
    out += [
        b.rect(48, 822, 1824, 198, PANEL, LINE, 2, 18),
        b.txt(80, 868, "QA benchmark：让知识服务可评测、可回归", 28, GREEN, 700),
        b.txt(80, 914, "10 个任务 · 100 道题", 27, CYAN, 700),
        b.txt(470, 914, "单条查询 · 条件筛选与排序 · 工艺归纳 · 论文取证 · 机理分析", 24, TEXT, 700),
        b.txt(80, 967, "评测对象", 23, ORANGE, 700),
        b.txt(260, 967, "意图识别、核心结果、来源追溯、条件核对和材料补充；结果进入后续迭代。", 23, MUTED),
    ]
    b.save("06-tools-and-evaluation.svg", "".join(out))


if __name__ == "__main__":
    slide_ler()
    slide2()
    slide3()
    slide4()
    slide5()
    slide6()
