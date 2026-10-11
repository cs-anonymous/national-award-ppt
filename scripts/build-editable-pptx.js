#!/usr/bin/env node

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const PptxGenJS = require('pptxgenjs');

const ROOT = path.resolve(__dirname, '..');
const ANT_WKG = process.argv.includes('--ant-wkg');
const SVG_DIR = ANT_WKG ? path.join(ROOT, 'svg', 'ant-wkg') : path.join(ROOT, 'svg');
const args = process.argv.slice(2);
const slideFlag = args.find((arg) => arg.startsWith('--slide='));
const onlySlide = slideFlag ? Number(slideFlag.split('=')[1]) : null;
const outputArg = args.find((arg) => !arg.startsWith('--'));
const OUT = path.resolve(outputArg || path.join(ROOT, 'national-award-defense-2026-editable.pptx'));
const ORDER = [
  '01-cover.svg', '02-agenda.svg', '03-profile.svg', '04-study.svg',
  '05-overview.svg', '06-expath.svg', '07-ruledep.svg', '08-geneticprism.svg',
  '09-geneticflow.svg', 'back-inspire.svg', '10-practice.svg', '11-lab-work.svg',
  '12-conference.svg', '13-exchange.svg', '14-closing.svg',
];
const ANT_ORDER = [
  '01-knowledge-data.svg', '02-itas-knowledge-construction.svg',
  '03-materialbrain.svg', '04-ler-overview.svg',
  '05-materagent.svg', '06-tools-and-evaluation.svg',
];
const SW = 1920;
const SH = 1080;
const PW = 13.333333;
const PH = 7.5;
const PT_PER_PX = 0.5;

function parseXml(xml) {
  const root = { name: '#root', attrs: {}, children: [] };
  const stack = [root];
  const tokens = xml.match(/<!--[\s\S]*?-->|<\?[\s\S]*?\?>|<[^>]+>|[^<]+/g) || [];
  for (const token of tokens) {
    if (token.startsWith('<?') || token.startsWith('<!--')) continue;
    if (token.startsWith('</')) { stack.pop(); continue; }
    if (token.startsWith('<')) {
      const name = token.match(/^<\s*([\w:-]+)/)?.[1];
      if (!name) continue;
      const attrs = {};
      const rest = token.slice(name.length + 1, token.length - (token.endsWith('/>') ? 2 : 1));
      const re = /([\w:-]+)\s*=\s*(["'])([\s\S]*?)\2/g;
      let m;
      while ((m = re.exec(rest))) attrs[m[1]] = decodeXml(m[3]);
      const node = { name: name.split(':').pop(), qname: name, attrs, children: [] };
      stack[stack.length - 1].children.push(node);
      if (!token.endsWith('/>')) stack.push(node);
    } else {
      stack[stack.length - 1].children.push(decodeXml(token));
    }
  }
  return root.children[0];
}

function decodeXml(s) {
  return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'").replace(/&amp;/g, '&');
}

function escapeXml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function serialize(node) {
  if (typeof node === 'string') return escapeXml(node);
  const attrs = Object.entries(node.attrs).map(([k, v]) => ` ${k}="${escapeXml(v)}"`).join('');
  if (!node.children.length) return `<${node.qname || node.name}${attrs}/>`;
  return `<${node.qname || node.name}${attrs}>${node.children.map(serialize).join('')}</${node.qname || node.name}>`;
}

function number(v, fallback = 0) {
  const n = parseFloat(v);
  return Number.isFinite(n) ? n : fallback;
}

function color(value, fallback = '000000') {
  if (!value || value === 'none') return null;
  const m = value.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
  if (!m) return fallback;
  let hex = m[1];
  if (hex.length === 3) hex = [...hex].map((x) => x + x).join('');
  return hex.toUpperCase();
}

function dataUri(value) {
  if (!value) return null;
  const match = value.match(/^data:([^;,]+)?(;base64)?,([\s\S]*)$/);
  if (!match) return null;
  if (match[2]) return { mime: match[1] || 'application/octet-stream', data: match[3] };
  return { mime: match[1] || 'text/plain', data: Buffer.from(decodeURIComponent(match[3])).toString('base64') };
}

function textContent(node) {
  return node.children.map((c) => typeof c === 'string' ? c : textContent(c)).join('');
}

function collectStyles(root) {
  const styles = {};
  const walk = (node) => {
    if (typeof node === 'string') return;
    if (node.name === 'style') {
      const css = textContent(node);
      for (const rule of css.matchAll(/([^{}]+)\{([^}]*)\}/g)) {
        const declarations = {};
        for (const declaration of rule[2].split(';')) {
          const [key, value] = declaration.split(':').map((v) => v && v.trim());
          if (key && value) declarations[key] = value;
        }
        for (const selector of rule[1].split(',')) styles[selector.trim()] = { ...(styles[selector.trim()] || {}), ...declarations };
      }
    }
    for (const child of node.children || []) walk(child);
  };
  walk(root);
  return styles;
}

function resolveAttrs(node, styles) {
  const resolved = {};
  Object.assign(resolved, styles[node.name] || {});
  for (const cls of (node.attrs.class || '').split(/\s+/).filter(Boolean)) {
    Object.assign(resolved, styles[`.${cls}`] || {});
  }
  if (node.attrs.style) {
    for (const declaration of node.attrs.style.split(';')) {
      const [key, value] = declaration.split(':').map((v) => v && v.trim());
      if (key && value) resolved[key] = value;
    }
  }
  Object.assign(resolved, node.attrs);
  return resolved;
}

function estimatedWidth(text, fontSize) {
  let units = 0;
  for (const char of text) units += /[\x00-\xff]/.test(char) ? 0.56 : 1;
  return Math.max(fontSize * 0.7, units * fontSize * 0.95 * 1.13);
}

function transformXY(node, state) {
  let x = number(node.attrs.x);
  let y = number(node.attrs.y);
  const transform = node.attrs.transform || '';
  for (const m of transform.matchAll(/translate\(\s*([-+\d.e]+)(?:[ ,]+([-+\d.e]+))?\s*\)/g)) {
    x += number(m[1]);
    y += number(m[2]);
  }
  return { x: x + state.dx, y: y + state.dy };
}

function lineOptions(a, b, attrs = {}) {
  return {
    x: a.x * PW / SW, y: a.y * PH / SH,
    w: (b.x - a.x) * PW / SW, h: (b.y - a.y) * PH / SH,
    line: { color: color(attrs.stroke, '000000') || '000000', width: Math.max(0.5, number(attrs['stroke-width'], 2) * PT_PER_PX) },
  };
}

function renderSvgPng(node, x, y, w, h, tempDir, index) {
  const markup = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="${x} ${y} ${w} ${h}">${serialize(node)}</svg>`;
  const inFile = path.join(tempDir, `asset-${index}.svg`);
  const outFile = path.join(tempDir, `asset-${index}.png`);
  fs.writeFileSync(inFile, markup);
  execFileSync('rsvg-convert', ['-w', String(Math.ceil(w * 2)), '-h', String(Math.ceil(h * 2)), '-o', outFile, inFile]);
  return outFile;
}

function addPath(slide, node, state) {
  const d = node.attrs.d || '';
  const tokens = [...d.matchAll(/[MLHVZ]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?/gi)].map((x) => x[0]);
  if (!tokens.length || tokens.some((t) => !/^[MLHVZ]$/i.test(t) && !Number.isFinite(Number(t)))) return false;
  const points = [];
  let command = null;
  let current = { x: 0, y: 0 };
  for (let i = 0; i < tokens.length;) {
    if (/^[MLHVZ]$/i.test(tokens[i])) command = tokens[i++].toUpperCase();
    if (command === 'Z') { command = null; continue; }
    if (!command) return false;
    if (command === 'H') {
      if (i >= tokens.length) return false;
      current = { x: number(tokens[i++]), y: current.y };
    } else if (command === 'V') {
      if (i >= tokens.length) return false;
      current = { x: current.x, y: number(tokens[i++]) };
    } else {
      if (i + 1 >= tokens.length) return false;
      current = { x: number(tokens[i++]), y: number(tokens[i++]) };
    }
    points.push({ x: current.x + state.dx, y: current.y + state.dy });
  }
  for (let i = 1; i < points.length; i++) slide.addShape('line', lineOptions(points[i - 1], points[i], node.attrs));
  return true;
}

function addNode(slide, node, state, tempDir, imageIndex) {
  if (typeof node === 'string') return;
  if (node.name === 'title' || node.name === 'defs') return;
  if (node.name === 'g') {
    const next = { ...state };
    for (const m of (node.attrs.transform || '').matchAll(/translate\(\s*([-+\d.e]+)(?:[ ,]+([-+\d.e]+))?\s*\)/g)) {
      next.dx += number(m[1]); next.dy += number(m[2]);
    }
    for (const child of node.children) addNode(slide, child, next, tempDir, imageIndex);
    return;
  }
  const a = resolveAttrs(node, state.styles || {});
  if (node.name === 'rect') {
    const xy = transformXY(node, state);
    const fill = color(a.fill);
    const stroke = color(a.stroke);
    const opacity = number(a.opacity, 1);
    const line = stroke ? { color: stroke, width: Math.max(0.5, number(a['stroke-width'], 2) * PT_PER_PX) } : { color: fill || 'FFFFFF', transparency: 100, width: 0 };
    slide.addShape('rect', {
      x: xy.x * PW / SW, y: xy.y * PH / SH, w: number(a.width) * PW / SW, h: number(a.height) * PH / SH,
      rectRadius: number(a.rx) * PW / SW,
      fill: fill ? { color: fill, transparency: Math.round((1 - opacity) * 100) } : { color: 'FFFFFF', transparency: 100 },
      line,
    });
    return;
  }
  if (node.name === 'circle') {
    const cx = number(a.cx) + state.dx; const cy = number(a.cy) + state.dy; const r = number(a.r);
    const fill = color(a.fill); const stroke = color(a.stroke);
    slide.addShape('ellipse', {
      x: (cx - r) * PW / SW, y: (cy - r) * PH / SH, w: 2 * r * PW / SW, h: 2 * r * PH / SH,
      fill: fill ? { color: fill } : { color: 'FFFFFF', transparency: 100 },
      line: stroke ? { color: stroke, width: Math.max(0.5, number(a['stroke-width']) * PT_PER_PX) } : { color: fill || 'FFFFFF', transparency: 100, width: 0 },
    });
    return;
  }
  if (node.name === 'line') {
    const p1 = { x: number(a.x1) + state.dx, y: number(a.y1) + state.dy };
    const p2 = { x: number(a.x2) + state.dx, y: number(a.y2) + state.dy };
    slide.addShape('line', lineOptions(p1, p2, a));
    return;
  }
  if (node.name === 'path') {
    if (!addPath(slide, node, state)) {
      const uri = `data:image/svg+xml;base64,${Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SW} ${SH}">${serialize(node)}</svg>`).toString('base64')}`;
      slide.addImage({ data: uri, x: 0, y: 0, w: PW, h: PH });
    }
    return;
  }
  if (node.name === 'text') {
    const xy = transformXY(node, state);
    const fsPx = number(a['font-size'], 32);
    const fsPt = fsPx * PT_PER_PX;
    const anchor = a['text-anchor'] || 'start';
    const tspans = node.children.filter((child) => typeof child !== 'string' && child.name === 'tspan');
    const lines = [];
    let lineY = xy.y;
    if (tspans.length) {
      for (const tspan of tspans) {
        lineY += number(tspan.attrs.dy, 0);
        lines.push({ text: textContent(tspan), x: number(tspan.attrs.x, xy.x), y: lineY });
      }
    } else {
      lines.push({ text: textContent(node), x: xy.x, y: xy.y });
    }
    for (const line of lines) {
      let txt = line.text;
      if (!txt) continue;
      if (line.x > 1700 && /^\d{2}$/.test(txt) && state.pageIndex) txt = String(state.pageIndex).padStart(2, '0');
      if (txt === '在线系统与视频演示') line.y += 180;
      const widthPx = estimatedWidth(txt, fsPx);
      let left = line.x;
      if (anchor === 'middle') left -= widthPx / 2;
      if (anchor === 'end') left -= widthPx;
      const top = line.y - fsPx * 0.84;
      slide.addText(txt, {
        x: left * PW / SW, y: top * PH / SH, w: widthPx * PW / SW, h: fsPx * 1.16 * PH / SH,
        fontFace: (a['font-family'] || 'Microsoft YaHei').split(',')[0].replace(/["']/g, '').trim(), fontSize: fsPt,
        bold: number(a['font-weight']) >= 600 || a['font-weight'] === 'bold',
        color: color(a.fill, '000000') || '000000',
        margin: 0, breakLine: false, valign: 'mid',
        align: anchor === 'middle' ? 'center' : anchor === 'end' ? 'right' : 'left',
        charSpacing: 0,
        fit: 'shrink',
        transparency: Math.round((1 - number(a.opacity, 1)) * 100),
      });
    }
    return;
  }
  if (node.name === 'image') {
    const xy = transformXY(node, state);
    const w = number(a.width); const h = number(a.height);
    const source = a.href || a['xlink:href'];
    const parsed = dataUri(source);
    if (parsed && parsed.mime.startsWith('image/')) {
      slide.addImage({ data: `data:${parsed.mime};base64,${parsed.data}`, x: xy.x * PW / SW, y: xy.y * PH / SH, w: w * PW / SW, h: h * PH / SH, transparency: Math.round((1 - number(a.opacity, 1)) * 100) });
    } else if (source && !source.startsWith('#')) {
      const file = path.resolve(state.svgDir || SVG_DIR, source);
      if (fs.existsSync(file)) slide.addImage({ path: file, x: xy.x * PW / SW, y: xy.y * PH / SH, w: w * PW / SW, h: h * PH / SH, transparency: Math.round((1 - number(a.opacity, 1)) * 100) });
    }
    return;
  }
  if (node.name === 'svg') {
    const xy = transformXY(node, state);
    const w = number(a.width); const h = number(a.height);
    const file = renderSvgPng(node, xy.x, xy.y, w, h, tempDir, imageIndex.value++);
    slide.addImage({ path: file, x: xy.x * PW / SW, y: xy.y * PH / SH, w: w * PW / SW, h: h * PH / SH });
    return;
  }
  for (const child of node.children || []) addNode(slide, child, state, tempDir, imageIndex);
}

async function main() {
  const activeOrder = ANT_WKG ? ANT_ORDER : ORDER;
  for (const name of activeOrder) if (!fs.existsSync(path.join(SVG_DIR, name))) throw new Error(`Missing ${name}`);
  if (onlySlide !== null && (!Number.isInteger(onlySlide) || onlySlide < 1 || onlySlide > activeOrder.length)) throw new Error(`Invalid slide number: ${slideFlag}`);
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.author = '孙烨';
  pptx.company = '北京航空航天大学计算机学院';
  pptx.subject = '2026 年研究生国家奖学金答辩';
  pptx.title = '2026 年计算机学院研究生国家奖学金答辩（可编辑版）';
  pptx.lang = 'zh-CN';
  pptx.theme = { headFontFace: 'Microsoft YaHei', bodyFontFace: 'Microsoft YaHei', lang: 'zh-CN' };
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'national-award-editable-'));
  const imageIndex = { value: 0 };
  const selected = onlySlide === null ? activeOrder : [activeOrder[onlySlide - 1]];
  for (const [index, name] of selected.entries()) {
    const xml = fs.readFileSync(path.join(SVG_DIR, name), 'utf8');
    const root = parseXml(xml);
    const slide = pptx.addSlide();
    slide.background = { color: 'FFFFFF' };
    const pageIndex = onlySlide === null ? index + 1 : onlySlide;
    const styles = collectStyles(root);
    for (const child of root.children) addNode(slide, child, { dx: 0, dy: 0, pageIndex, styles, svgDir: SVG_DIR }, tempDir, imageIndex);
  }
  await pptx.writeFile({ fileName: OUT, compression: true });
  console.log(`${OUT}\nslides=${selected.length}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
