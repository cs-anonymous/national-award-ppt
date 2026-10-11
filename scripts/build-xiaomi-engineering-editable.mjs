// Native text and geometry; individually embedded original complex visual assets.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const root = path.resolve('national-award/ppt');
const taskDir = path.join(root, '.build/xiaomi-engineering-editable');
const runtimeModules = process.env.RUNTIME_NODE_MODULES;
const skillDir = process.env.SKILL_DIR;
if (!runtimeModules || !skillDir) throw new Error('Set RUNTIME_NODE_MODULES and SKILL_DIR');
const requireRuntime = createRequire(path.join(runtimeModules, '__runtime__.cjs'));
const { Presentation, PresentationFile } = await import(pathToFileURL(requireRuntime.resolve('@oai/artifact-tool')));
const skiaPath = path.join(path.dirname(requireRuntime.resolve('@oai/artifact-tool')), '../node_modules/skia-canvas/lib/index.mjs');
const { Canvas, FontLibrary } = await import(pathToFileURL(skiaPath));
const ctx = new Canvas(1920, 1080).getContext('2d');
const font = 'PingFang SC';
// The SVG renderer resolves unavailable Consolas to Arial; retain that visible style.
const codeFont = FontLibrary.families.includes('Consolas') ? 'Consolas' : 'Arial';
if (!FontLibrary.families.includes(font)) throw new Error(`Required source font unavailable: ${font}`);

const data = JSON.parse(await fs.readFile(path.join(taskDir, 'layout.json'), 'utf8'));
const manuscript = await fs.readFile(path.join(root, '小米-AI材料算法工程师-工程实践-演说稿.md'), 'utf8');
const shortPart = manuscript.split('\n---\n')[0];
const notes = [...shortPart.matchAll(/### P\d｜[^\n]+\n\n([\s\S]*?)(?=\n### P\d｜|$)/g)].map(m => m[1].trim());
const sources = [
  'national-award/ppt/svg/12-conference.svg；info/项目与实习经历.md',
  'material/mofs-kg；material/mofs-kg/doc/基于多源异构数据的稀土材料知识图谱.md；Neo4j 图：material/eXpath presentation（12页）.pptx，第 1 页',
  'material/24teama_itas-master/2-课程汇报；ITAS 实际操作界面素材',
  'material/ci5c02299.pdf；Figure 1、Figure 3；DOI 10.1021/acs.jcim.5c02299',
  '原始 MaterAgent 架构图；material/material-agent/docs/agent_design.md；基于 pi-agent 修改',
  'material/material-agent 工具源码；docs/agent_design.md；docs/QA_benchmark_V3.2.md；调用示例及评估维度，不代表 benchmark 实测成绩',
];
const scale = 2 / 3;
const num = (v, fallback = 0) => v === undefined ? fallback : Number.parseFloat(v);
const p = (x, y, w, h) => ({ left: x * scale, top: y * scale, width: w * scale, height: h * scale });
const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const audit = [];

for (const [index, source] of data.entries()) {
  const slide = presentation.slides.add();
  slide.background.fill = '#FFFFFF';
  const record = { page: index + 1, source: source.source, texts: [], shapes: 0, images: [] };
  let sequence = 0;
  for (const el of source.elements) {
    sequence++;
    const name = `${source.name}-${sequence}`;
    if (el.kind === 'rect') {
      // The solid page background is native slide fill.
      if (num(el.width) === 1920 && num(el.height) === 1080) continue;
      slide.shapes.add({ geometry: 'rect', name,
        position: p(num(el.x), num(el.y), num(el.width), num(el.height)),
        fill: el.fill ?? 'none', borderRadius: num(el.rx) * scale,
        line: { fill: el.stroke ?? 'none', width: num(el['stroke-width']) * scale },
      });
      record.shapes++;
    } else if (el.kind === 'line') {
      const x1 = num(el.x1), x2 = num(el.x2), y1 = num(el.y1), y2 = num(el.y2);
      slide.shapes.add({ geometry: 'line', name,
        position: p(Math.min(x1, x2), Math.min(y1, y2), Math.abs(x2 - x1), Math.abs(y2 - y1)),
        fill: 'none', line: { fill: el.stroke, width: num(el['stroke-width'], 1) * scale },
      });
      record.shapes++;
    } else if (el.kind === 'polygon') {
      const points = el.points.trim().split(/\s+/).map(pair => pair.split(',').map(Number));
      const xs = points.map(pt => pt[0]), ys = points.map(pt => pt[1]);
      const x = Math.min(...xs), y = Math.min(...ys), w = Math.max(...xs) - x, h = Math.max(...ys) - y;
      slide.shapes.add({ geometry: 'custom', name, position: p(x, y, w, h), fill: el.fill,
        line: { fill: 'none', width: 0 }, customPaths: [{ width: w, height: h,
          commands: points.map(([px, py], i) => ({ [i ? 'lineTo' : 'moveTo']: { x: px - x, y: py - y } })).concat([{ close: {} }]),
        }],
      });
      record.shapes++;
    } else if (el.kind === 'image') {
      // SVG xMidYMid meet: fit the original aspect ratio and center in its viewport.
      const ratio = Math.min(num(el.width) / el.intrinsicWidth, num(el.height) / el.intrinsicHeight);
      const w = el.intrinsicWidth * ratio, h = el.intrinsicHeight * ratio;
      const x = num(el.x) + (num(el.width) - w) / 2, y = num(el.y) + (num(el.height) - h) / 2;
      slide.images.add({ blob: new Uint8Array(await fs.readFile(el.asset)),
        contentType: /\.jpe?g$/i.test(el.asset) ? 'image/jpeg' : 'image/png',
        alt: `${source.name}: ${path.basename(el.asset)}`, fit: 'contain', position: p(x, y, w, h),
      });
      record.images.push({ asset: el.asset, position: p(x, y, w, h), originalPixels: [el.intrinsicWidth, el.intrinsicHeight] });
    } else if (el.kind === 'text') {
      const size = num(el['font-size'], 30), bold = num(el['font-weight'], 400) >= 600;
      const family = el['font-family'] === 'Consolas' ? codeFont : font;
      ctx.font = `${bold ? 'bold' : 'normal'} ${size}px "${family}"`;
      for (const [lineIndex, sourceLine] of el.lines.entries()) {
        // SVG normal whitespace collapses repeated ASCII spaces.
        const line = { ...sourceLine, text: sourceLine.text.replace(/\s+/g, ' ').trim() };
        const measured = ctx.measureText(line.text);
        const width = measured.width + Math.max(6, size * .12);
        const anchor = el['text-anchor'] ?? 'start';
        let x = line.x;
        if (anchor === 'end') x -= width;
        else if (anchor === 'middle') x -= width / 2;
        // Text frame is zero-inset and uses explicit one-line boxes: no accidental wrapping.
        const ascent = measured.fontBoundingBoxAscent;
        // Measured native export baseline differs from SVG by ~0.06 em.
        const top = line.y - ascent + size * .06;
        const shape = slide.shapes.add({ geometry: 'textbox', name: `${name}-line-${lineIndex + 1}`,
          position: p(x, top, width, (measured.fontBoundingBoxAscent + measured.fontBoundingBoxDescent) * 1.12),
          fill: 'none', line: { fill: 'none', width: 0 },
        });
        shape.text = line.text;
        shape.text.style = { typeface: family, fontSize: size * scale, bold, color: el.fill,
          alignment: anchor === 'end' ? 'right' : anchor === 'middle' ? 'center' : 'left',
          verticalAlignment: 'top', autoFit: 'none', wrap: 'none',
          insets: { left: 0, right: 0, top: 0, bottom: 0 },
        };
        record.texts.push({ text: line.text, baseline: line.y, font: family, fontSize: size * scale, position: shape.position });
      }
    }
  }
  slide.speakerNotes.textFrame.setText(`${notes[index] ?? ''}\n\n材料依据：${sources[index]}\n\n还原说明：标题、正文、图外注释、页码及基础几何为原生可编辑元素；原始照片、Logo、产品界面、Neo4j 与复杂论文/架构图为独立图片，图内小字保留在图片中。`);
  audit.push(record);
}
await fs.writeFile(path.join(taskDir, 'element-audit.json'), JSON.stringify(audit, null, 2));
const candidate = path.join(taskDir, 'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
console.log(JSON.stringify({ candidate, slides: audit.map(a => ({ page: a.page, textBoxes: a.texts.length, nativeShapes: a.shapes, images: a.images.length })) }));
