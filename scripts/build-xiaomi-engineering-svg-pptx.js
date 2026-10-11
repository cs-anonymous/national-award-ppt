#!/usr/bin/env node

// Package the six self-contained SVG pages into a 16:9 PowerPoint.
// The SVGs are the source of truth for layout, typography, and embedded figures.
const fs = require('fs');
const path = require('path');
const PptxGenJS = require('../node_modules/pptxgenjs');
const JSZip = require('../node_modules/jszip');

const ROOT = path.resolve(__dirname, '..');
const SVG_DIR = path.join(ROOT, 'svg', 'xiaomi-engineering');
const PREVIEW_DIR = path.join(ROOT, 'svg-preview', 'xiaomi-engineering');
const notesArg = process.argv.slice(2).find((arg) => arg.startsWith('--notes='));
const notesPath = notesArg ? path.resolve(notesArg.slice('--notes='.length)) : null;
const notes = notesPath
  ? fs.readFileSync(notesPath, 'utf8').split(/^## P[1-6]｜/m).slice(1).map((part) => part.trim())
  : [];
if (notesPath && notes.length !== 6) {
  throw new Error(`Expected six P1–P6 sections in ${notesPath}, found ${notes.length}`);
}
const outputArg = process.argv.slice(2).find((arg) => !arg.startsWith('--'));
const output = path.resolve(
  outputArg || path.join(ROOT, '小米-AI材料算法工程师-工程实践.pptx'),
);

const files = fs.readdirSync(SVG_DIR)
  .filter((name) => /^0[1-6]-.+\.svg$/i.test(name))
  .sort((a, b) => a.localeCompare(b, 'en'));

if (files.length !== 6) {
  throw new Error(`Expected 6 SVG slides in ${SVG_DIR}, found ${files.length}`);
}

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = '孙烨';
pptx.company = '北京航空航天大学';
pptx.subject = '小米 AI 材料算法工程师岗位——工程实践';
pptx.title = '三、工程实践｜面向材料研发的 Agent 工具链';
pptx.lang = 'zh-CN';
pptx.theme = {
  headFontFace: 'Microsoft YaHei',
  bodyFontFace: 'Microsoft YaHei',
  lang: 'zh-CN',
};

for (const [index, name] of files.entries()) {
  const slide = pptx.addSlide();
  slide.background = { color: 'FFFFFF' };
  slide.addImage({
    path: path.join(SVG_DIR, name),
    x: 0,
    y: 0,
    w: 13.333333,
    h: 7.5,
    altText: name,
  });
  if (notes[index]) slide.addNotes(notes[index]);
}

// PptxGenJS uses a placeholder for the SVG's PNG preview in Node. Replace
// it with the verified slide rendering so viewers without SVG support also
// display the complete slide. The embedded SVG stays byte-for-byte intact.
async function exportDeck() {
  const data = await pptx.write({ outputType: 'nodebuffer' });
  const zip = await JSZip.loadAsync(data);
  for (const [index, name] of files.entries()) {
    const pngPart = `ppt/media/image-${index + 1}-1.png`;
    const svgPart = `ppt/media/image-${index + 1}-2.svg`;
    if (!zip.file(pngPart) || !zip.file(svgPart)) {
      throw new Error(`Missing image pair on slide ${index + 1}`);
    }
    const preview = path.join(PREVIEW_DIR, name.replace(/\.svg$/i, '.png'));
    zip.file(pngPart, fs.readFileSync(preview));
  }
  // This PptxGenJS version declares one master per slide even though it
  // writes a single shared master. Remove only these unused declarations.
  const contentTypes = await zip.file('[Content_Types].xml').async('string');
  zip.file('[Content_Types].xml', contentTypes.replace(
    /<Override PartName="(\/ppt\/slideMasters\/slideMaster\d+\.xml)"[^>]*\/>/g,
    (entry, part) => zip.file(part.slice(1)) ? entry : '',
  ));
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
  console.log(output);
}

exportDeck()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
