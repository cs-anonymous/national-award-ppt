#!/usr/bin/env python3
"""Generate the 12 national-award SVG slides.

The source SVGs deliberately use a small, auditable layout vocabulary that follows
the Beihang template: white canvas, navy section bars, blue accents, pale blue cards,
and a restrained footer. Text is kept at 32 px or larger (16 pt at 144 px/in).
"""
from __future__ import annotations

import base64
import html
import mimetypes
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "svg-src"
OUT = ROOT / "svg"
ASSET = ROOT / "assets" / "figures"
W, H = 1920, 1080

NAVY = "#123C73"
BLUE = "#1675C8"
TEAL = "#0E9DB4"
INK = "#17263A"
MUTED = "#58708A"
PALE = "#F1F6FB"
PALE2 = "#E6F1FA"
EDGE = "#C8DCEC"
GREEN = "#E7F6F2"
ORANGE = "#F39B45"
RED = "#C94B56"
WHITE = "#FFFFFF"
FONT = "PingFang SC, Microsoft YaHei, Arial, sans-serif"


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def wrap(text: str, max_chars: int) -> list[str]:
    """Wrap Chinese/English text by display-character count."""
    lines: list[str] = []
    for para in str(text).split("\n"):
        cur = ""
        count = 0
        for ch in para:
            # Latin letters and digits occupy about half a Chinese glyph.
            width = 0.55 if (ch.isascii() and ch not in "，。；：、（）") else 1.0
            if cur and count + width > max_chars:
                lines.append(cur)
                cur, count = "", 0
            cur += ch
            count += width
        lines.append(cur)
    return lines or [""]


def b64(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


IMAGE_CACHE: dict[str, str] = {}


def image_ref(rel: str) -> str:
    path = ASSET / rel
    if rel not in IMAGE_CACHE:
        IMAGE_CACHE[rel] = b64(path)
    return IMAGE_CACHE[rel]


class Slide:
    def __init__(self, number: int, section: str, title: str, takeaway: str | None = None):
        self.number = number
        self.parts: list[str] = []
        self.parts.append(f'<rect width="{W}" height="{H}" fill="{WHITE}"/>')
        if 2 <= number <= 14:
            self.parts.append(f'<image x="28" y="22" width="68" height="68" preserveAspectRatio="xMidYMid meet" href="{image_ref("research/beihang-emblem.png")}"/>')
        # Reference: systematic-lit-search/ppt/svg/02-xie-mge.svg.
        # One horizontal header: blue main heading | dark subtitle.
        main = section.split("·")[0]
        self.text(main, 130, 88, 48, "#0871C9", bold=True)
        divider = 130 + len(main) * 48 + 30
        self.rect(divider, 48, 2, 48, "#263442", stroke="none", r=0)
        self.text(title, divider + 30, 86, 40, INK, bold=True)
        if takeaway:
            self.text(takeaway, 130, 145, 32, MUTED, width=1690, leading=42)
        self.parts.append(f'<text x="62" y="1034" font-family="{FONT}" font-size="32" fill="{MUTED}">北京航空航天大学计算机学院 · 2026 年研究生国家奖学金答辩</text>')
        self.parts.append(f'<text x="1818" y="1034" text-anchor="end" font-family="{FONT}" font-size="32" fill="{BLUE}" font-weight="700">{number:02d}</text>')

        self.header_end = len(self.parts)

    def text(self, text: str, x: float, y: float, size: float = 34, color: str = INK,
             width: float | None = None, bold: bool = False, leading: float | None = None,
             anchor: str = "start") -> float:
        # 32 px corresponds to 16 pt on the 1920 px / 13.333 in canvas.
        size = max(float(size), 32.0)
        leading = leading or size * 1.35
        lines = wrap(text, max(1, int((width or 2000) / (size * 0.95)))) if width else str(text).split("\n")
        weight = "700" if bold else "400"
        for i, line in enumerate(lines):
            yy = y + i * leading
            self.parts.append(
                f'<text x="{x:.1f}" y="{yy:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
                f'font-size="{size:.1f}" fill="{color}" font-weight="{weight}">{esc(line)}</text>'
            )
        return y + len(lines) * leading

    def citation(self, text: str):
        # Citation stays in the fixed header area while body content is reflowed.
        self.parts.insert(self.header_end - 2, f'<text x="56" y="188" font-family="{FONT}" font-size="32" fill="{MUTED}">{esc(text)}</text>')
        # Keep the footer and page number in the fixed header/footer layer after
        # inserting the citation, otherwise the page number would be translated
        # with the body content on cited slides.
        self.header_end += 1

    def rect(self, x: float, y: float, w: float, h: float, fill: str = PALE,
             stroke: str = EDGE, r: float = 16, sw: float = 2):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str = EDGE, sw: float = 4):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"/>')

    def circle(self, cx: float, cy: float, r: float, fill: str, stroke: str = "none", sw: float = 0):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def image(self, rel: str, x: float, y: float, w: float, h: float, opacity: float = 1.0, fit: str = "xMidYMid meet"):
        self.parts.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{fit}" opacity="{opacity}" href="{image_ref(rel)}"/>')

    def interface_figure(self, x, y, w, h):
        # Crop the interface from the paper page, omitting header and caption.
        self.parts.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="80 98 860 425" preserveAspectRatio="none" overflow="hidden"><image width="1020" height="1320" href="{image_ref("research/geneticprism-figure.png")}"/></svg>')

    def pill(self, label: str, x: float, y: float, w: float, fill: str = PALE2, color: str = NAVY):
        self.rect(x, y, w, 52, fill, stroke="none", r=26)
        self.text(label, x + w / 2, y + 36, 30, color, bold=True, anchor="middle")

    def arrow(self, x1: float, y1: float, x2: float, y2: float, color: str = TEAL):
        self.line(x1, y1, x2, y2, color, 5)
        self.parts.append(f'<path d="M{x2-18},{y2-11} L{x2},{y2} L{x2-18},{y2+11}" fill="none" stroke="{color}" stroke-width="5"/>')

    def metric(self, value: str, label: str, x: float, y: float, w: float, color: str = BLUE):
        self.rect(x, y, w, 150, WHITE, stroke=EDGE, r=16)
        self.text(value, x + 24, y + 70, 58, color, bold=True)
        self.text(label, x + 24, y + 118, 32, MUTED, width=w - 48)

    def card(self, title: str, body: str, x: float, y: float, w: float, h: float, fill: str = PALE):
        self.rect(x, y, w, h, fill)
        self.text(title, x + 26, y + 52, 35, NAVY, bold=True, width=w - 52)
        self.text(body, x + 26, y + 102, 32, INK, width=w - 52, leading=45)

    def dot_label(self, n: str, title: str, body: str, x: float, y: float, w: float, color: str = BLUE):
        self.circle(x + 22, y + 26, 22, color)
        self.text(n, x + 22, y + 37, 25, WHITE, bold=True, anchor="middle")
        self.text(title, x + 60, y + 37, 34, NAVY, bold=True, width=w - 60)
        self.text(body, x + 60, y + 85, 31, INK, width=w - 60, leading=43)

    def finish(self, slug: str):
        if 2 <= self.number <= 14:
            # Reclaim the space from the former stacked headings.
            offset = -140 if self.number in (2, 10) else -100
            header, body = self.parts[:self.header_end], self.parts[self.header_end:]
            self.parts = header + [f'<g transform="translate(0,{offset})">'] + body + ['</g>']
            # Page-specific evidence bars are intentionally omitted: the revised
            # deck uses the full lower area for figures, citations, and activities.
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="20in" height="11.25in" viewBox="0 0 {W} {H}">'
               f'<title>{esc(slug)}</title><g>{"".join(self.parts)}</g></svg>')
        (SRC / f"{self.number:02d}-{slug}.svg").write_text(svg, encoding="utf-8")


def cover():
    s = Slide(1, "2026 年研究生国家奖学金答辩", "", None)
    s.parts = [f'<rect width="{W}" height="{H}" fill="{WHITE}"/>', f'<rect x="0" y="0" width="{W}" height="16" fill="{BLUE}"/>']
    s.image("research/beihang-campus.png", 0, 0, 1920, 520, 0.30)
    s.parts.append('<rect x="0" y="0" width="1920" height="520" fill="#FFFFFF" opacity="0.58"/>')
    s.image("research/beihang-logo.png", 64, 54, 620, 66)
    s.text("2026 年计算机学院研究生", 120, 500, 66, NAVY, bold=True)
    s.text("国家奖学金答辩", 120, 590, 82, BLUE, bold=True)
    s.line(120, 645, 930, 645, BLUE, 6)
    s.text("孙烨", 120, 735, 56, INK, bold=True)
    s.text("北京航空航天大学计算机学院 · 软件工程博士研究生", 120, 795, 36, MUTED)
    s.text("导师：时磊教授", 120, 848, 36, MUTED)
    s.text("学号：BY2306093", 120, 900, 36, MUTED)
    s.text("2026 年 9 月", 120, 1000, 34, MUTED)
    s.parts.append('<text x="1818" y="1034" text-anchor="end" font-family="PingFang SC, Microsoft YaHei, Arial" font-size="32" fill="#1675C8" font-weight="700">01</text>')
    s.finish("cover")


def agenda():
    s = Slide(2, "汇报提纲", "基本情况 · 科研成果 · 其他活动", "4 分钟主线：用三项代表性成果说明研究贡献，再以系统工程和国际交流收束。")
    items = [("01", "基本情况", "学习基础、研究主线\n（主讲 1 页）", BLUE), ("02", "科研成果", "eXpath · RuleDep\nGeneticPrism / Flow", TEAL), ("03", "其他活动", "MaterAgent · 国际交流\nINSPIRE 为补充页", ORANGE)]
    for i, (n, title, body, color) in enumerate(items):
        x = 110 + i * 600
        s.rect(x, 370, 500, 360, WHITE, stroke=EDGE, r=24)
        s.circle(x + 92, 470, 48, color)
        s.text(n, x + 92, 487, 34, WHITE, bold=True, anchor="middle")
        s.text(title, x + 60, 580, 44, NAVY, bold=True)
        s.text(body, x + 60, 650, 32, INK, width=380, leading=44)
        if i < 2:
            s.arrow(x + 510, 550, x + 585, 550, color)
    s.rect(110, 815, 1700, 135, PALE, stroke="none", r=16)
    s.text("研究主线", 145, 895, 38, BLUE, bold=True)
    s.text("结构化知识组织 → 规则推理 → 证据解释 → 智能系统", 395, 895, 38, NAVY, bold=True)
    s.finish("agenda")


def profile():
    s = Slide(3, "一、基本情况", "个人信息与学习成绩", None)
    s.image("research/ye-sun.jpg", 90, 250, 270, 360, fit="xMidYMid meet")
    s.text("北京航空航天大学计算机学院", 430, 285, 36, INK)
    s.text("软件工程博士研究生 · 2023 级", 430, 340, 36, INK)
    s.text("出生年月：1999 年 1 月 · 籍贯：湖北宜昌", 430, 395, 32, MUTED)
    s.text("导师：时磊教授", 430, 445, 32, MUTED)
    s.text("研究方向", 430, 520, 36, BLUE, bold=True)
    s.text("知识图谱推理 · 可解释人工智能 · 学术图谱可视化", 430, 570, 32, INK)
    s.metric("3.87 / 4.00", "博士 GPA · 41 学分", 90, 650, 390, BLUE)
    s.metric("3.86 / 4.00", "硕士 GPA · 31 学分", 510, 650, 390, TEAL)
    s.metric("13 / 143", "博士阶段专业排名", 930, 650, 390, ORANGE)
    s.metric("10 年", "2017 至今北航学习", 1350, 650, 390, RED)
    s.rect(90, 835, 1720, 100, PALE, stroke="none", r=16)
    s.text("教育经历", 120, 875, 32, BLUE, bold=True)
    s.text("本科 2017–2021 · 北航计算机学院   ｜   硕士 2021–2023 · 北航软件工程   ｜   博士 2023–至今 · 北航软件工程", 330, 875, 30, INK, width=1450)
    s.text("代表课程", 120, 970, 32, TEAL, bold=True)
    s.text("本科：数学分析 100 · 软件工程 98 · 深度学习 94     研究生：数据挖掘 100 · 算法设计与分析 94 · 数理统计 94 · 计算机图形学 92 · 模式识别 93 · 软件工程综合实验 95", 330, 970, 29, INK, width=1480)
    s.finish("profile")


def study():
    s = Slide(4, "一、基本情况", "荣誉奖项与能力", "科研奖励、竞赛经历、技术栈与英语能力共同支撑科研工作和国际交流。")
    s.rect(80, 285, 690, 600, PALE, stroke=EDGE, r=22)
    s.text("荣誉与奖励", 120, 350, 40, NAVY, bold=True)
    s.text("研究生一等奖学金\n2021 · 2023 · 2025 · 2026", 120, 440, 34, INK, leading=46)
    s.text("ACT 实验室学术贡献奖 · 2026\n人工智能领域十大优秀团队 · 2025", 120, 570, 32, INK, leading=46)
    s.text("冯如杯科技竞赛三等奖 · 2020\n北航数学建模竞赛一等奖 · 2019", 120, 700, 32, INK, leading=46)
    s.image("awards/award-1.png", 820, 300, 370, 450, 0.98)
    s.image("awards/toefl-score.png", 1240, 310, 570, 280, 0.98)
    s.text("TOEFL 105 · GRE 327", 1240, 630, 30, MUTED)
    s.rect(820, 700, 990, 330, GREEN, stroke=EDGE, r=18)
    s.text("技术与语言", 855, 755, 36, TEAL, bold=True)
    s.text("编程：Python / Java / C++\n机器学习：PyTorch / sklearn\n系统：Linux / Docker\n后端：Flask / Django", 855, 805, 32, INK, width=460, leading=42)
    s.text("前端：JavaScript / D3 / Vue\n数据库：MySQL / PostgreSQL\n英语：TOEFL 105 / GRE 327\n认证：CCF CSP 前 8.79%", 1320, 805, 32, INK, width=470, leading=42)
    s.finish("study")


def expath():
    s = Slide(6, "二、科研成果", "eXpath：让链接预测给出路径证据", "面向嵌入式知识图谱链接预测，融合关系路径与本体闭合路径规则，生成更具语义依据的局部解释。")
    s.rect(70, 305, 840, 530, PALE, stroke=EDGE, r=22)
    s.text("从预测到解释", 110, 365, 39, NAVY, bold=True)
    nodes = [("候选链接", 190, 500, BLUE), ("关系路径", 445, 500, TEAL), ("规则证据", 700, 500, ORANGE)]
    for label, x, y, color in nodes:
        s.circle(x, y, 72, color)
        s.text(label, x, y + 12, 30, WHITE, bold=True, anchor="middle")
    s.arrow(262, 500, 370, 500, TEAL); s.arrow(517, 500, 625, 500, ORANGE)
    s.text("双向 BFS ≤ 3 跳", 135, 650, 32, MUTED)
    s.text("Closed Path / Property Transition", 135, 708, 32, MUTED)
    s.text("按规则置信度筛选关键事实", 135, 766, 32, MUTED)
    # Paper figures are cropped directly from the published PDF; use their
    # native aspect ratios so no caption fragments or stretched diagrams remain.
    s.image("research/paperfig/expath-fig1-art.png", 940, 300, 470, 278, fit="xMidYMid meet")
    s.image("research/paperfig/expath-fig3-v2.png", 1430, 300, 390, 420, fit="xMidYMid meet")
    s.metric("≈ 20%", "解释质量提升", 970, 820, 390, BLUE)
    s.metric("−61.4%", "解释耗时下降", 1400, 820, 390, TEAL)
    s.pill("第一作者 · PVLDB / VLDB 2025 · 已录用", 70, 900, 820, PALE2)
    s.citation("Ye Sun et al. eXpath: Explaining Knowledge Graph Link Prediction with Ontological Closed Path Rules. PVLDB, 2025.")
    s.finish("expath")


def ruledep():
    s = Slide(7, "二、科研成果", "RuleDep：建模规则之间的互补与冗余", "当多条规则共同支持一个候选实体时，独立加权会重复计算或忽略协同；RuleDep 用稀疏二阶依赖进行修正。")
    s.rect(70, 310, 610, 470, PALE, stroke=EDGE, r=22)
    s.text("规则聚合的缺口", 105, 375, 39, NAVY, bold=True)
    s.text("规则 A", 150, 510, 34, BLUE, bold=True, anchor="middle")
    s.text("规则 B", 470, 510, 34, ORANGE, bold=True, anchor="middle")
    s.circle(150, 575, 58, BLUE); s.circle(470, 575, 58, ORANGE)
    s.text("证据", 150, 587, 30, WHITE, bold=True, anchor="middle"); s.text("证据", 470, 587, 30, WHITE, bold=True, anchor="middle")
    s.arrow(208, 575, 405, 575, MUTED); s.text("独立假设", 310, 550, 29, MUTED, anchor="middle")
    s.text("互补：联合证据超出相加\n冗余：联合证据存在重叠", 105, 705, 32, INK, width=520, leading=45)
    s.image("research/paperfig/ruledep-fig2-left-art.png", 710, 300, 550, 350, fit="xMidYMid meet")
    s.image("research/paperfig/ruledep-fig1-art.png", 1270, 300, 550, 350, fit="xMidYMid meet")
    s.rect(730, 660, 1080, 180, WHITE, stroke=EDGE, r=18)
    s.text("两阶段训练", 770, 720, 34, NAVY, bold=True)
    s.pill("规则证据", 770, 755, 220, PALE2)
    s.arrow(1000, 781, 1120, 781, TEAL)
    s.pill("稀疏依赖修正", 1140, 755, 280, GREEN, TEAL)
    s.arrow(1430, 781, 1550, 781, ORANGE)
    s.pill("可解释预测", 1570, 755, 200, "#FFF2E5", ORANGE)
    s.metric("+3.7%", "平均 MRR：0.382 → 0.396", 730, 865, 500, BLUE)
    s.metric("21 项", "比较指标最佳或并列最佳", 1260, 865, 550, TEAL)
    s.pill("第一作者 · ICDE 2027 · 已录用", 70, 900, 640, PALE2)
    s.citation("Ye Sun et al. RuleDep: Modeling Complementarity and Redundancy in Rule Aggregation for KGC. ICDE, 2027.")
    s.finish("ruledep")


def geneticprism():
    s = Slide(7, "二、科研成果", "GeneticPrism：多主题研究演化的可视分析", "把主题演化、跨主题引文影响和时间脉络放入一个可探索的多尺度视图。")
    s.interface_figure(70, 310, 980, 510)
    s.rect(1100, 310, 710, 530, PALE, stroke=EDGE, r=22)
    s.text("研究贡献", 1140, 375, 40, NAVY, bold=True)
    s.dot_label("1", "IFHL 布局", "将主题内引用与跨主题影响纳入同一层次图表示，减少拥挤与边交叉。", 1140, 420, 620, BLUE)
    s.dot_label("2", "GeneticPrism 总览", "三维棱柱隐喻承载多主题研究轨迹，支持跨主题探索。", 1140, 570, 620, TEAL)
    s.dot_label("3", "GeneticScroll 局部视图", "展开主题内时间图与跨主题流入／流出，连接全局与局部证据。", 1140, 700, 620, ORANGE)
    s.metric("20 人", "用户研究", 70, 835, 520, TEAL)
    s.pill("第一作者 · IEEE TVCG · CCF-A · 已发表", 620, 860, 620, PALE2)
    s.citation("Ye Sun et al. GeneticPrism: Multifaceted Visualization of Citation-based Scholarly Research Evolution. IEEE TVCG, 2025.")
    s.finish("geneticprism")


def geneticflow():
    s = Slide(8, "二、科研成果·工程转化", "GeneticFlow V2.0：从论文方法到真实系统", "GeneticPrism 的研究方法被实现为持续运行的在线平台，形成从图布局计算到浏览器交互的完整工程链路。")
    s.interface_figure(70, 305, 850, 480)
    s.rect(960, 305, 850, 480, PALE, stroke=EDGE, r=22)
    s.text("系统链路", 1000, 365, 39, NAVY, bold=True)
    chain = [("数据", "主题建模\n引文图", BLUE), ("布局", "Graphviz\nC++\nWASM", TEAL), ("交互", "Flask\n前端交互", ORANGE), ("服务", "在线部署\n运维", RED)]
    for i, (title, body, color) in enumerate(chain):
        x = 1000 + i * 190
        s.rect(x, 455, 160, 240, WHITE, stroke=color, sw=4, r=16)
        s.circle(x + 80, 500, 25, color)
        s.text(str(i + 1), x + 80, 510, 26, WHITE, bold=True, anchor="middle")
        s.text(title, x + 80, 565, 31, NAVY, bold=True, anchor="middle")
        s.text(body, x + 80, 610, 26, INK, width=156, leading=38, anchor="middle")
        if i < 3: s.arrow(x + 165, 545, x + 185, 545, color)
    s.metric("102,129", "累计服务用户", 70, 800, 430, BLUE)
    s.metric("507,827", "累计访问量", 520, 800, 430, TEAL)
    s.metric("V2.0", "独立开发与运维", 970, 800, 430, ORANGE)
    s.text("统计日期：2026-09-15 · 用户数与访问量来自平台累计统计。", 70, 988, 32, MUTED)
    s.finish("geneticflow")


def inspire():
    s = Slide(9, "二、科研成果·补充研究", "INSPIRE：音符级结构化表示与表现力生成", "AAAI 2027 Revision。作为补充研究，展示异质序列表示、生成模型实现与可检验评测能力。")
    s.rect(70, 310, 840, 510, PALE, stroke=EDGE, r=22)
    s.text("Score → Performance", 110, 370, 39, NAVY, bold=True)
    labels = [("符号乐谱", 110, BLUE), ("INR 六槽位", 385, TEAL), ("Transformer", 660, ORANGE)]
    for i, (label, x, color) in enumerate(labels):
        s.rect(x, 495, 220, 100, WHITE, stroke=color, sw=4, r=18)
        s.text(label, x + 110, 557, 30, color, bold=True, anchor="middle")
        if i < 2: s.arrow(x + 225, 545, x + 270, 545, color)
    s.text("音高 · IOI · 音长 · 力度\n音乐信息 · 踏板", 120, 665, 32, MUTED, width=740)
    s.text("每个音符融合为一个 Transformer 时间步，缩短自回归序列。", 120, 755, 31, INK, width=720)
    s.rect(960, 310, 850, 490, PALE, stroke=EDGE, r=22)
    s.text("表示、预测与验证", 1000, 370, 39, NAVY, bold=True)
    s.dot_label("1", "音符级表示", "六类属性融合为一个时间步，自回归序列由 K×N 缩短至 N。", 1000, 400, 760, BLUE)
    s.dot_label("2", "连续分布建模", "分属性输出预测头，保留时序等连续数值结构，并约束预测范围。", 1000, 530, 760, TEAL)
    s.dot_label("3", "多粒度评测", "在 ASAP 数据上评测乐曲级分布与音符级属性，定位改进和局限。", 1000, 660, 760, ORANGE)
    s.metric("13.8%", "乐曲级 Human Relevance 改善", 70, 830, 520, BLUE)
    s.metric("23×", "推理成本：137.3 → 6.0 GPU-min", 620, 830, 650, TEAL)
    s.pill("第一作者 · AAAI 2027", 1300, 835, 510, "#FFF2E5", ORANGE)
    s.text("Revision · 尚未录用", 1330, 940, 32, ORANGE, bold=True)
    
    s.finish("inspire")


def practice():
    s = Slide(10, "三、其他活动", "工程实践：从数据治理到 Agent Harness", "将研究经验迁移到材料研发、数据治理和智能工具链，形成面向真实场景的系统能力。")
    cards = [
        ("材料数据库与数字化研发平台", "国家重点研发计划课题\n主导多源材料知识图谱、本体与可视化模块\n形成 10⁵ 级多模态材料数据库", BLUE),
        ("数据分类分级", "开发 LLM 实体识别工具\n构建 RAG 驱动的分类分级流程\n支持敏感数据自动标注与动态调优", TEAL),
        ("MaterAgent · 工程实践", "新材智脑 / MaterBrain 合作\n材料研发全流程 Agent Harness\nPaper Browser MCP 等工具", ORANGE),
    ]
    project_images = ["research/geneticprism-presentation.png", "international/tum-knowledge-graph-exchange.jpg", "research/geneticflow-video-poster.jpg"]
    for i, (title, body, color) in enumerate(cards):
        x = 75 + i * 610
        s.rect(x, 350, 550, 620, WHITE, stroke=color, sw=5, r=24)
        s.image(project_images[i], x + 24, 368, 502, 105, fit="xMidYMid meet")
        s.rect(x, 495, 550, 82, color, stroke="none", r=0)
        s.text(title, x + 28, 550, 34, WHITE, bold=True, width=494)
        s.text(body, x + 30, 635, 30, INK, width=490, leading=43)
        s.line(x + 30, 885, x + 520, 885, EDGE, 3)
        s.text(["数据基础", "治理流程", "Agent Harness"][i], x + 30, 935, 31, color, bold=True)
    s.rect(75, 990, 1770, 42, GREEN, stroke="none", r=16)
    s.text("共同能力：把复杂科研任务拆解为数据、模型、工具、交互和运维环节，形成可复用的系统工程方法。", 110, 1018, 30, NAVY, bold=True)
    s.finish("practice")


def conference():
    s = Slide(12, "三、其他活动", "国际学术会议：在现场展示研究", "围绕知识图谱推理与学术图谱可视化，参加国际会议并进行公开报告。")
    events = [
        ("VIS 2023", "How “Applied” is Fifteen Years of VAST Conference?\nIEEE VIS 2023 · 第四作者", None, ORANGE),
        ("VLDB 2025 · London", "报告 eXpath\n知识图谱链接预测的结构化解释", "international/vldb-2025-london-presentation.jpg", BLUE),
        ("GD 2025 · Linköping", "报告 GeneticPrism\n学术研究演化与图绘制交流", "international/gd-2025-linkoping-presentation.jpg", TEAL),
    ]
    for i, (title, body, rel, color) in enumerate(events):
        x = 70 + i * 615
        s.rect(x, 325, 555, 520, WHITE, stroke=EDGE, r=20)
        if rel: s.image(rel, x + 20, 350, 515, 275, fit="xMidYMid meet")
        else:
            s.rect(x + 20, 350, 515, 275, PALE2, stroke=color, sw=3, r=12)
            s.text("VIS 2023 图片\n预留位置", x + 278, 500, 36, color, bold=True, anchor="middle")
        s.text(title, x + 28, 685, 37, color, bold=True, width=500)
        s.text(body, x + 28, 745, 32, INK, width=500, leading=46)
        s.pill(["公开报告", "同行交流", "访问与合作"][i], x + 28, 820, 170, PALE2 if i < 2 else "#FFF2E5", color)
    s.rect(70, 895, 1770, 60, PALE, stroke="none", r=14)
    s.text("交流成果：公开展示代表性研究 · 获取国际同行反馈 · 连接可视化与知识图谱研究合作网络", 105, 935, 32, NAVY, bold=True)
    s.finish("conference")


def exchange():
    s = Slide(13, "三、其他活动", "访问交流：连接国际合作研究", "CSC 资助赴慕尼黑工业大学交流访问，围绕知识图谱可视化与规则推理开展持续合作。")
    # Left: four evidence blocks. Right: collaboration text and visit photos.
    s.image("international/tum-logo.png", 80, 300, 390, 165, fit="xMidYMid meet")
    s.image("international/stephen-kobourov.jpg", 525, 305, 145, 190, fit="xMidYMid meet")
    s.image("international/maribel-acosta.jpg", 715, 305, 145, 190, fit="xMidYMid meet")
    s.text("Stephen\nKobourov", 597, 515, 24, NAVY, bold=True, anchor="middle", leading=31)
    s.text("Maribel\nAcosta", 787, 515, 24, TEAL, bold=True, anchor="middle", leading=31)
    s.image("international/csc-funding-fix.png", 70, 570, 425, 410, fit="xMidYMid meet")
    s.image("international/tum-invite.png", 500, 570, 410, 410, fit="xMidYMid meet")
    s.rect(930, 280, 880, 470, PALE, stroke=EDGE, r=20)
    s.text("合作内容", 970, 345, 38, NAVY, bold=True)
    s.text("• 与 Stephen Kobourov 教授开展知识图谱可视化与图绘制研究。\n• 撰写 KGVis Survey 并投 Eurovis STAR paper。\n• 与 Maribel Acosta 教授合作开展基于规则的知识图谱推理研究。\n• 撰写 RuleDep 并被 ICDE 2027 录用。", 970, 420, 32, INK, width=790, leading=49)
    s.rect(930, 770, 880, 185, GREEN, stroke=EDGE, r=18)
    s.image("international/tum-visit.jpg", 955, 790, 390, 145, fit="xMidYMid meet")
    s.image("international/tum-visit-campus.jpg", 1390, 790, 390, 145, fit="xMidYMid meet")
    s.finish("exchange")


def overview():
    s = Slide(5, "二、科研成果", "论文成果总览", "共发表或录用论文 9 篇；第一作者发表 CCF-A 3 篇，另有 1 篇 A 类论文在投。")
    metrics = [("9 篇", "发表或录用论文"), ("3 篇", "一作 CCF-A"), ("2 条", "研究路线"), ("1 篇", "CCF-A 论文在投")]
    for i, (value, label) in enumerate(metrics):
        x = 90 + i * 430
        color = [BLUE, TEAL, ORANGE, RED][i]
        s.rect(x, 260, 390, 190, WHITE, stroke=EDGE, r=16)
        s.text(value, x + 24, 355, 66, color, bold=True)
        s.text(label, x + 24, 415, 32, MUTED, width=335)
    s.rect(70, 485, 650, 420, PALE, stroke=EDGE, r=22)
    s.text("CCF-A 发表难度", 110, 520, 39, TEAL, bold=True)
    s.text("VLDB：数据库领域顶级会议\nTVCG：可视化与计算机图形学顶级期刊\nAAAI：人工智能领域顶级会议\nICDE：数据工程领域顶级会议", 110, 600, 32, INK, width=570, leading=48)
    s.text("四篇代表作围绕知识图谱推理与学术图谱可视化。", 110, 820, 29, MUTED, width=570)
    # Route labels sit above the paper row. Each venue is directly above its
    # first-page screenshot, while the year remains below the image.
    s.text("知识图谱推理", 1028, 465, 32, TEAL, bold=True, anchor="middle")
    s.text("学术图谱可视化", 1430, 465, 32, BLUE, bold=True, anchor="middle")
    s.text("AI 音乐生成", 1705, 465, 32, ORANGE, bold=True, anchor="middle")
    papers = [
        ("research/papers/vldb.png", "PVLDB / VLDB", "2025"),
        ("research/papers/icde.png", "ICDE", "2027"),
        ("research/papers/tvcg.png", "IEEE TVCG", "2025"),
        ("research/papers/aaai.png", "AAAI", "2027 Revision"),
    ]
    for i, (rel, venue, year) in enumerate(papers):
        x = 750 + i * 275
        s.text(venue, x + 130, 505, 32, NAVY, bold=True, anchor="middle")
        s.image(rel, x, 520, 260, 360, fit="xMidYMid meet")
        s.text(year, x + 130, 910, 30, MUTED, bold=True, anchor="middle")
    s.finish("overview")


def lab_work():
    s = Slide(11, "三、其他活动", "实验室工作：把科研组织成长期能力", "围绕国家项目、平台建设、合作申请和实验室基础设施，承担科研组织与工程支撑工作。")
    items = [
        ("国家项目与平台", "国家重点研发课题（XXX）课题助理\n参与课题申请、年度验收、中期验收与平台开发\n协助老师及合作人申请取得国家技术发明一等奖", BLUE),
        ("项目申请与产业合作", "协助完成两个面上项目成功申请\n面向全学科学者的异质学术脉络可视化分析\n促成上奇科技产业-区域可视化合作\n杭州人工智能创新创业大赛特等奖", TEAL),
        ("实验室运行", "辅导学弟开展科研工作\n维护实验室 3 台服务器与云服务器\n持续支撑数据、代码、部署与共享环境", ORANGE),
    ]
    lab_images = [
        "international/shangqi/user-manual-overview-banner.png",
        "international/shangqi/geneticprism-access-banner.png",
        "international/shangqi/geneticprism-api-banner.png",
    ]
    for i, (title, body, color) in enumerate(items):
        x = 70 + i * 615
        s.rect(x, 315, 555, 590, WHITE, stroke=color, sw=5, r=22)
        s.image(lab_images[i], x + 25, 335, 505, 115, fit="xMidYMid meet")
        s.rect(x, 470, 555, 82, color, stroke="none", r=0)
        s.text(title, x + 28, 525, 34, WHITE, bold=True, width=500)
        bullet_body = "\n".join("• " + line for line in body.split("\n"))
        s.text(bullet_body, x + 30, 610, 30, INK, width=490, leading=44)
    s.finish("lab-work")


def genetic():
    s = Slide(8, "二、科研成果", "GeneticPrism：研究贡献", "以 GeneticPrism 与 GeneticScroll 两种视图，把多主题研究演化与局部证据放进同一条探索路径。")
    s.image("research/paperfig/genetic-fig3-ab-tight.png", 70, 290, 850, 500, fit="xMidYMid meet")
    s.image("research/paperfig/genetic-fig4.png", 960, 290, 850, 500, fit="xMidYMid meet")
    s.rect(70, 820, 1740, 230, PALE, stroke="none", r=14)
    s.text("研究贡献", 105, 880, 34, BLUE, bold=True)
    s.text("GeneticPrism：三维棱柱承载多主题全局概览，\n顶视图表达主题间引用影响，侧视图表达单主题研究演化。\nGeneticScroll：以时间轴、流图和层级图展示单主题细节与跨主题影响。\n总体贡献：将全局结构、主题演化和局部证据统一到可交互的学术图谱探索流程中。", 330, 860, 32, INK, width=1430, leading=44)
    s.citation("Ye Sun et al. GeneticPrism: Multifaceted Visualization of Citation-based Scholarly Research Evolution. IEEE TVCG, 2025.")
    s.finish("geneticprism")


def genetic_engineering():
    s = Slide(9, "二、科研成果", "GeneticFlow：工程贡献与真实使用", "将 GeneticPrism 的研究方法转化为持续运行的在线系统，完成布局计算、浏览器交互和服务运维。")
    s.image("research/geneticflow-video-poster.jpg", 70, 300, 1040, 585, fit="xMidYMid meet")
    s.rect(1160, 300, 650, 585, PALE, stroke=EDGE, r=22)
    s.text("系统工程", 1200, 370, 40, NAVY, bold=True)
    s.text("Graphviz C++ / WASM\nFlask 服务与前端交互\n在线部署与持续运维", 1200, 470, 34, INK, leading=58)
    s.metric("102,129", "累计服务用户", 1200, 680, 270, BLUE)
    s.metric("507,827", "累计访问量", 1500, 680, 270, TEAL)
    s.text("在线系统与视频演示", 1200, 840, 29, MUTED, width=390)
    s.rect(70, 915, 1450, 70, GREEN, stroke="none", r=12)
    s.text('ACM Fellow Ion Stoica："This is interesting, especially the visualization"', 100, 960, 30, NAVY, bold=True, width=1380)
    s.image("research/geneticflow-qr.png", 1640, 890, 110, 110, fit="xMidYMid meet")
    s.text("扫码访问 GeneticFlow", 1580, 1015, 30, MUTED)
    s.finish("geneticflow")


def closing():
    s = Slide(14, "汇报结束", "以结构化知识连接研究与系统", None)
    s.parts = [f'<rect width="{W}" height="{H}" fill="{WHITE}"/>', f'<rect x="0" y="0" width="{W}" height="16" fill="{BLUE}"/>']
    s.image("research/beihang-campus.png", 0, 0, 1920, 1080, 0.18)
    s.parts.append('<rect x="0" y="0" width="1920" height="1080" fill="#FFFFFF" opacity="0.74"/>')
    s.image("research/beihang-logo.png", 110, 110, 630, 67)
    s.text("结构化知识组织", 190, 365, 54, NAVY, bold=True)
    s.arrow(640, 350, 780, 350, BLUE)
    s.text("规则推理与证据解释", 820, 365, 54, TEAL, bold=True)
    s.arrow(1325, 350, 1465, 350, ORANGE)
    s.text("可用的智能系统", 1505, 365, 54, ORANGE, bold=True)
    s.text("感谢各位老师指导", 960, 650, 68, NAVY, bold=True, anchor="middle")
    s.text("恳请批评指正", 960, 735, 48, BLUE, anchor="middle")
    s.text("孙烨 · 北京航空航天大学计算机学院", 960, 915, 36, MUTED, anchor="middle")
    s.parts.append('<text x="1818" y="1034" text-anchor="end" font-family="PingFang SC, Microsoft YaHei, Arial" font-size="32" fill="#1675C8" font-weight="700">14</text>')
    s.finish("closing")


def main():
    SRC.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    for p in list(SRC.glob("*.svg")) + list(OUT.glob("*.svg")):
        p.unlink()
    cover(); agenda(); profile(); study(); overview(); expath(); ruledep(); genetic(); genetic_engineering(); practice(); lab_work(); conference(); exchange(); closing()
    # Keep the unpublished INSPIRE material as an off-deck backup page.
    inspire()
    (SRC / "09-inspire.svg").rename(SRC / "back-inspire.svg")
    # Make the packaging directory contain the same self-contained sources.
    for p in SRC.glob("*.svg"):
        (OUT / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"generated {len(list(SRC.glob('*.svg')))} SVG slides")


if __name__ == "__main__":
    main()
