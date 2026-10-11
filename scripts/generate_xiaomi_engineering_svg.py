#!/usr/bin/env python3
"""Generate the six-slide Xiaomi engineering-practice chapter as editable SVG."""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "svg-src" / "xiaomi-engineering"

W, H = 1920, 1080

# Match the existing national-award SVG master: white canvas, Beihang blue
# heading, navy body text, pale blue cards, and restrained accent colors.
BG = "#FFFFFF"
PANEL = "#F1F6FB"
PANEL2 = "#E6F1FA"
LINE = "#C8DCEC"
TEXT = "#17263A"
MUTED = "#58708A"
CYAN = "#1675C8"
ORANGE = "#F39B45"
GREEN = "#0E9DB4"
PURPLE = "#0E9DB4"
RED = "#C94B56"
FONT = "PingFang SC, Microsoft YaHei, Arial, sans-serif"


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def txt(x, y, value, size=28, color=TEXT, weight=400, anchor="start", family=FONT, opacity=1.0, boost=True):
    # The chapter uses slightly larger body text than the first draft. Header
    # typography opts out so it remains identical to the national-award master.
    shown = size + (4 if boost and size < 32 else 0)
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{shown}px" font-weight="{weight}" fill="{color}" text-anchor="{anchor}" opacity="{opacity}">{esc(value)}</text>'


def multiline(x, y, lines, size=24, color=TEXT, leading=1.35, weight=400, family=FONT, boost=True):
    shown = size + (4 if boost and size < 32 else 0)
    out = [f'<text x="{x}" y="{y}" font-family="{family}" font-size="{shown}px" font-weight="{weight}" fill="{color}">']
    for i, line in enumerate(lines):
        out.append(f'<tspan x="{x}" dy="{0 if i == 0 else shown * leading}px">{esc(line)}</tspan>')
    out.append("</text>")
    return "".join(out)


def rect(x, y, w, h, fill=PANEL, stroke=LINE, sw=2, rx=18, opacity=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'


def line(x1, y1, x2, y2, color=LINE, sw=2, dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{dash_attr}/>'


def image(path, x, y, w, h, opacity=1, preserve="xMidYMid meet"):
    return f'<image href="assets/{path}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{preserve}" opacity="{opacity}"/>'


def header(kicker, title, subtitle, page):
    # Keep the section/title geometry identical to the national-award master.
    main = kicker.split("·")[0].strip()
    divider = 130 + len(main) * 48 + 30
    return "".join([
        image("beihang-emblem.png", 28, 22, 68, 68),
        txt(130, 88, main, 48, CYAN, 700, boost=False),
        rect(divider, 48, 2, 48, TEXT, "none", 0, 0),
        txt(divider + 30, 86, title, 40, TEXT, 700, boost=False),
        multiline(130, 145, [subtitle], 32, MUTED, 1.32, boost=False),
        txt(1872, 1052, f"{page:02d}", 28, CYAN, 700, "end", boost=False),
    ])


def footer(page, source=""):
    # The national-award master keeps only the right-aligned page number. The
    # lower-left “北航国奖”/event caption is intentionally omitted.
    return ""


def start():
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{BG}"/>'


def end():
    return "</svg>"


def save(name, body):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(start() + body + end(), encoding="utf-8")


def card_block(x, y, w, h, accent, title, lines, label=None, body_size=22):
    out = [rect(x, y, w, h, PANEL, LINE, 2, 18), f'<rect x="{x}" y="{y}" width="10" height="{h}" rx="5" fill="{accent}"/>']
    if label:
        out += [txt(x + 28, y + 38, label, 18, accent, 700), txt(x + 28, y + 82, title, 29, TEXT, 700), multiline(x + 28, y + 126, lines, body_size, MUTED, 1.42)]
    else:
        out += [txt(x + 28, y + 44, title, 29, TEXT, 700), multiline(x + 28, y + 92, lines, body_size, MUTED, 1.42)]
    return "".join(out)


def slide1():
    out = [header("三、工程实践", "实习经历与工作概况", "商汤 AI 应用与模型工具链研发 · TUM 知识图谱与可视化科研合作", 1)]
    # Equal panels: titles at the top, source images in the middle, prose below.
    for x in (48, 976):
        out += [rect(x, 194, 896, 826)]
    out += [txt(80, 246, "商汤实习：AI 应用与基础设施核心开发", 30, CYAN, 700),
            image("shangqi-screenshot.png", 80, 278, 832, 434),
            txt(80, 757, "模型工具链  |  2021.06—2022.08", 27, CYAN, 700),
            multiline(80, 802, ["独立开发 spring.remote，支持训练集群远程登录、", "任务提交与管理；开发系统监控工具，服务模型训练。"], 26, TEXT, 1.40),
            txt(80, 898, "AI 全栈工程  |  2023.02—2023.08", 27, ORANGE, 700),
            multiline(80, 943, ["参与“秒画”产品后端 API 设计与实现；独立开发", "Discord 机器人并上线官方社区，对接 AI 绘画接口。"], 26, TEXT, 1.40)]
    out += [txt(1008, 246, "TUM 科研访学：知识图谱与图可视化合作", 30, GREEN, 700),
            image("tum-logo.png", 1022, 318, 268, 117),
            image("csc-letter.png", 1060, 450, 177, 250),
            image("maribel-acosta.jpg", 1330, 312, 226, 260),
            image("stephen-kobourov.jpg", 1594, 312, 226, 260),
            txt(1008, 757, "国家公派科研访学  |  2025.09—2025.12", 27, GREEN, 700),
            multiline(1008, 802, ["Maribel Acosta：知识图谱与数据管理研究", "Stephen Kobourov：图可视化与图绘制研究"], 26, TEXT, 1.40),
            txt(1008, 898, "研究合作与交流", 27, CYAN, 700),
            multiline(1008, 943, ["围绕 KGVis Survey、RuleDep 开展访问交流与合作；", "获 CSC 资助，积累图谱组织、可视分析与规则推理经验。"], 26, TEXT, 1.40)]
    save("01-experience.svg", "".join(out))


def slide2():
    out = [header("三、工程实践", "材料数据库与知识图谱构建", "主导知识图谱、本体与可视化模块开发；融合文献、结构、性能与实验数据，支撑材料研发任务", 2)]
    out += [rect(48, 194, 866, 826), txt(80, 246, "多源异构数据融合与研发任务", 30, CYAN, 700),
            image("mofkg/fig2-workflow.png", 76, 272, 810, 382),
            image("mofkg/fig1-data-sources.png", 76, 662, 810, 210),
            multiline(80, 903, ["数据来源：文献、KAIST、QMOF、CoRE、CSD、PubChem，", "以及高通量计算与合成实验；统一结构、性能和合成条件。", "围绕合成参数—结构—性能关系，开展逆合成、", "构效关系挖掘、逆向结构设计与合成参数优化。"], 24, TEXT, 1.28)]
    out += [rect(942, 194, 930, 826), txt(974, 246, "材料知识图谱：本体建模与 Neo4j 可视化", 30, ORANGE, 700),
            image("expath-neo4j.png", 970, 274, 628, 440),
            txt(1620, 306, "材料本体", 23, GREEN, 700),
            image("MOFKG-onto.png", 1620, 326, 220, 125),
            txt(1620, 496, "节点与关系统计", 23, CYAN, 700),
            image("mofkg-statistic.png", 1610, 520, 236, 158),
            multiline(974, 750, ["本体：MOF、前驱体、结构单元、合成操作与论文。", "关系：合成、组成、操作条件和文献来源；保留投料量等属性。", "融合：用名称、分子式、结构与标识符对齐多源实体。", "质量与追踪：筛除重复及低质数据，区分标注、抽取与推理来源。", "交互：在 Neo4j 查看关联材料、节点属性、结构及来源分布。", "合成条件 46,701 条 · DOI 非空 46,486 条 · 唯一 DOI 17,715 个"], 24, TEXT, 1.38),
            txt(974, 1005, "Neo4j 原图：eXpath presentation（12页）.pptx，第 1 页", 18, MUTED)]
    save("02-material-kg.svg", "".join(out))


def slide3():
    out = [header("三、工程实践", "材料数字化研发平台设计与实现：ITAS", "架构设计与核心开发：需求分析、模块划分、代码评审与合并；支持材料文献标注、数据生产与智能挖掘", 3)]
    out += [rect(48, 194, 926, 826), txt(80, 246, "真实工作台：论文阅读、段落标注与实体定位", 30, CYAN, 700),
            image("itas-workbench.png", 80, 272, 862, 442),
            image("itas-material-annotation.png", 80, 730, 444, 218),
            image("itas-entity-highlight.png", 548, 734, 392, 51),
            txt(548, 827, "材料文献操作示例", 25, GREEN, 700),
            multiline(548, 871, ["定位合成段落，标注 MOF 化学式、", "金属前驱体、溶剂与反应条件；", "核对实体后提交，审核并导出数据。"], 23, TEXT, 1.42),
            txt(80, 992, "管理员分配任务 → 标注员提交 → 审核与导出 → 科研人员使用", 24, MUTED)]
    out += [rect(1006, 194, 866, 826), txt(1038, 246, "系统模块与 PDF 到结构化数据的处理流程", 30, ORANGE, 700),
            image("itas-pdf-html.png", 1038, 280, 802, 135),
            txt(1038, 467, "平台化协作与数据流", 26, GREEN, 700),
            multiline(1038, 507, ["分层架构：Web 工作台 → 标注/挖掘服务 → 数据与对象存储。", "文本标注：项目管理、任务分配、实体标注、审核与导出。", "智能挖掘：模型管理、段落提取、实体识别与记录管理。", "数据流：PDF → HTML/TXT → 合成段落 → 材料实体", "→ 人工校正与审核 → 导出结构化记录。"], 25, TEXT, 1.34),
            txt(1038, 713, "材料领域预设与数据字典", 26, CYAN, 700),
            image("itas-material-dictionary.png", 1040, 736, 408, 186),
            multiline(1472, 770, ["实体：MOF、金属源、", "有机配体、溶剂、调节剂", "属性：时间、温度、用量", "关系：来源、组成与操作"], 23, TEXT, 1.40),
            multiline(1038, 956, ["预设约束标注范围与输出字段；结果可用于模型训练、", "few-shot 示例整理与后续知识图谱构建。"], 25, MUTED, 1.35)]
    save("03-itas.svg", "".join(out))


def slide4():
    out = [header("三、工程实践", "大模型驱动的结构化知识抽取与迭代", "MaterialBrain：将材料文献转为合成路线数据，通过人机修订、少样本学习与检索增强持续提高抽取质量", 4)]
    out += [rect(48, 194, 826, 740), txt(80, 246, "Figure 1：MaterialBrain 技术流程", 30, CYAN, 700),
            image("materialbrain-fig1.png", 72, 271, 778, 642)]
    out += [rect(902, 194, 970, 740),
            txt(934, 246, "原图解释：从材料文献到可用的合成路线", 30, ORANGE, 700),
            txt(934, 296, "① 数据准备与人机联合整理", 26, GREEN, 700),
            multiline(934, 338, ["从文献定位合成段落，LLM 预标注后由材料专家修订；", "分批、多轮更新标注库，将核验过的样本积累为示例。"], 26, TEXT, 1.35),
            txt(934, 433, "② RAG 选择示例，完成 few-shot 抽取", 26, CYAN, 700),
            multiline(934, 475, ["用 BM25 检索与当前段落相关的 4–6 个示例，结合", "领域定义与提示，让 LLM 提取前驱体、用量及合成条件。"], 26, TEXT, 1.35),
            txt(934, 570, "③ 结构化输出与材料项目的连接", 26, GREEN, 700),
            multiline(934, 612, ["输出合成路线 JSON，供知识入库、性能推断与材料设计使用；", "ITAS 提供标注与校正基础，论文进一步组织示例检索和迭代。"], 26, TEXT, 1.35),
            image("materialbrain-fig3.png", 930, 684, 420, 234),
            txt(1376, 723, "Figure 3：反馈如何进入下一轮", 23, ORANGE, 700),
            multiline(1376, 763, ["冷启动：全文预标注形成初始库。", "主动学习选择待修订的样本。", "批次内：FS-ICL 与专家修订循环。", "批次间：更新示例库，继续抽取。"], 23, TEXT, 1.45)]
    out += [rect(48, 952, 1824, 69, PANEL2, LINE, 1.5, 10),
            txt(76, 982, "论文实验", 23, GREEN, 700),
            txt(230, 982, "三个 MOF 数据集平均 macro-F1：0.94（zero-shot：0.77） · 框架密度推断性能提升 32.9%", 24, TEXT),
            txt(230, 1011, "实验合成 UiO-66 (Zr) 比表面积超过数据集中 99.2% 的同类文献样本；以上为论文验证结果", 23, TEXT),
            txt(48, 1052, "J. Chem. Inf. Model. 2026 · DOI: 10.1021/acs.jcim.5c02299", 18, MUTED)]
    save("04-materialbrain.svg", "".join(out))


def slide5():
    out = [header("三、工程实践", "MaterAgent：Harness 框架设计", "基于 pi-agent 修改，接入材料知识、领域工具与约束校验；核心开发：框架适配、编排与工具接口", 5)]
    # The source architecture is displayed in its original aspect ratio, without
    # an outer frame. The service labels occupy its existing upper-left whitespace.
    out += [image("materagent-stack.png", 48, 208, 1102, 810),
            rect(90, 217, 586, 126, "#FFFFFF", "none", 0, 0),
            txt(108, 251, "服务入口与基础框架", 29, CYAN, 700),
            multiline(108, 291, ["交互：飞书 / 钉钉 / 企业微信 / Web IDE", "API Gateway / FastAPI / REST / WebSocket"], 23, TEXT, 1.38)]
    out += [rect(1178, 194, 694, 826), txt(1210, 246, "规划、工具执行与反馈机制", 30, GREEN, 700),
            txt(1210, 302, "Query Router · 任务进入", 26, CYAN, 700),
            multiline(1210, 344, ["从问题提取任务类型、材料实体、工艺条件", "与目标字段，生成后续执行所需的任务上下文。"], 24, TEXT, 1.35),
            txt(1210, 436, "Plan Agent · 任务规划", 26, ORANGE, 700),
            multiline(1210, 478, ["按任务规则确定检索、取证和预测步骤，", "明确步骤依赖，组织工具输入和中间结果。"], 24, TEXT, 1.35),
            txt(1210, 570, "Tool Executor · 执行与观察", 26, GREEN, 700),
            multiline(1210, 612, ["调用数据库、论文读取和性能预测工具；", "接收结构化结果，汇集材料记录与证据来源。"], 24, TEXT, 1.35),
            txt(1210, 704, "Verify Agent · 校验与终止", 26, CYAN, 700),
            multiline(1210, 746, ["按证据、输出格式、数值和完成条件校验；", "满足条件则完成，否则反馈并调整执行计划。"], 24, TEXT, 1.35),
            line(1210, 815, 1840, 815), txt(1210, 859, "框架状态链路", 25, CYAN, 700),
            multiline(1210, 902, ["RUNNING → TOOL_CALL → OBSERVE", "→ VERIFY → DONE / REPLAN"], 24, TEXT, 1.40),
            txt(1210, 992, "架构图展示整体设计；材料工具与编排持续开发中", 22, MUTED)]
    save("05-materagent.svg", "".join(out))


def slide6():
    out = [header("三、工程实践", "MaterAgent：Paper Browser 与 Database MCP 工具", "核心开发：把材料检索与论文读取封装为结构化工具；从数据库记录追踪到原文证据，再组织回答", 6)]
    out += ["<desc>工具接口依据 material/material-agent 源码；QA 分类与检索策略依据 docs/agent_design.md 第 7 节；评价维度依据 docs/QA_benchmark_V3.2.md。此页展示调用示例与设计策略，不报告 benchmark 实测成绩。</desc>"]
    out += [rect(48, 194, 896, 330), txt(80, 246, "Database MCP：材料记录检索", 30, CYAN, 700),
            txt(80, 292, "material_db_hybrid_search", 26, CYAN, 700, family="Consolas"),
            multiline(80, 338, ["输入：query / retrieval_method / top_k（1–20）。", "检索：hybrid / vector / bm25；dense / sparse 为别名。", "输出：排序结果、材料记录、相关性分数与元数据。", "用于定位配方、工艺与性能数据，保留文献来源，", "将候选材料记录与 DOI 交给论文工具继续核对。"], 26, TEXT, 1.35)]
    out += [rect(976, 194, 896, 330), txt(1008, 246, "Paper Browser：统一论文索引与读取", 30, ORANGE, 700),
            txt(1008, 292, "paper_search / paper_read", 26, ORANGE, 700, family="Consolas"),
            multiline(1008, 338, ["paper_search：按 DOI、标题、章节或正文定位论文。", "paper_read：用 paper_id / section_id 读取原文证据。", "支持 local / HTTP 来源，按章节或分页读取长文。", "返回正文及来源信息；通过索引、日志和读取位置，", "把材料记录关联到可追溯的段落、表格与图注。"], 26, TEXT, 1.35)]
    out += [rect(48, 550, 1824, 245, PANEL2), txt(80, 598, "端到端调用示例：数据库查记录，论文工具核对证据", 30, CYAN, 700),
            txt(80, 642, "任务：烧结工艺的 La/Ce 替代 Nd-Fe-B 永磁体中，Hcj 最高的材料配方是什么？", 28, TEXT, 700)]
    steps = [
        ("1", "任务解析", "工艺 / 替代元素 / Hcj", CYAN),
        ("2", "Database MCP", "检索记录并比较实测 Hcj", ORANGE),
        ("3", "paper_search", "按 DOI 定位来源论文", GREEN),
        ("4", "paper_read", "读取工艺与性能原文", CYAN),
        ("5", "证据与回答", "核对条件、单位与来源", RED),
    ]
    for i, (n, name, desc, color) in enumerate(steps):
        x = 80 + i * 356
        out += [rect(x, 680, 328, 86, PANEL, color, 2, 12),
                txt(x + 16, 715, n, 25, color, 700), txt(x + 54, 715, name, 24, TEXT, 700),
                txt(x + 16, 750, desc, 21, MUTED)]
        if i < 4:
            out += [line(x + 332, 723, x + 347, 723, LINE, 3),
                    f'<polygon points="{x+344},716 {x+354},723 {x+344},730" fill="{LINE}"/>']
    out += [rect(48, 822, 1824, 198),
            txt(80, 868, "面向材料问题的 QA 分类与检索策略", 28, CYAN, 700)]
    categories = [
        ("单条记录查询", "已知配方查 Hcj", "精确查询 → 原文取证", CYAN),
        ("多条件筛选", "限定工艺与性能阈值", "条件筛选 → 去重取证", GREEN),
        ("条件排序与 Top-k", "烧结磁体 Hcj Top3", "数据库排序 → 原文核对", ORANGE),
        ("论文原文取证", "查配方对应表格与段落", "DOI 定位 → 原文读取", CYAN),
        ("材料机理与开放问答", "解释 La/Ce 替代机制", "向量召回 → 原文补证", GREEN),
    ]
    for i, (name, example, strategy, color) in enumerate(categories):
        x = 80 + i * 356
        if i:
            out += [line(x - 14, 890, x - 14, 992)]
        out += [txt(x, 910, name, 26, color, 700),
                txt(x, 949, example, 25, TEXT),
                txt(x, 987, strategy, 23, MUTED)]
    out += [txt(48, 1052, "QA 评估：问题识别、核心结果、来源追溯与材料补充；核对筛选条件、单位、缺失值与 DOI", 19, MUTED)]
    save("06-tools.svg", "".join(out))


if __name__ == "__main__":
    slide1(); slide2(); slide3(); slide4(); slide5(); slide6()
