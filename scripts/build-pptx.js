#!/usr/bin/env node

// Package the fourteen self-contained SVG pages into a 16:9 PowerPoint.
const fs = require('fs');
const path = require('path');
const PptxGenJS = require('pptxgenjs');

const ROOT = path.resolve(__dirname, '..');
const SVG_DIR = path.join(ROOT, 'svg');
const outputArg = process.argv.slice(2).find((arg) => !arg.startsWith('--'));
const output = path.resolve(outputArg || path.join(ROOT, 'national-award-defense-2026.pptx'));
const files = fs.readdirSync(SVG_DIR)
  .filter((name) => /^(0[1-9]|1[0-4])-.+\.svg$/i.test(name))
  .sort((a, b) => a.localeCompare(b, 'en'));

if (files.length !== 14) {
  throw new Error(`Expected 14 SVG slides in ${SVG_DIR}, found ${files.length}`);
}

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = '孙烨';
pptx.company = '北京航空航天大学计算机学院';
pptx.subject = '2026 年研究生国家奖学金答辩';
pptx.title = '2026 年计算机学院研究生国家奖学金答辩';
pptx.lang = 'zh-CN';
pptx.theme = { headFontFace: 'Microsoft YaHei', bodyFontFace: 'Microsoft YaHei', lang: 'zh-CN' };

for (const name of files) {
  const slide = pptx.addSlide();
  slide.background = { color: 'FFFFFF' };
  slide.addImage({ path: path.join(SVG_DIR, name), x: 0, y: 0, w: 13.333333, h: 7.5, altText: name });
  if (name === '09-geneticflow.svg') {
    slide.addMedia({ type: 'video', path: '/Users/a./Documents/Obsidian Vault/会议交流签证/GD/GeneticPrismV5head.mp4', x: 0.48, y: 2.08, w: 7.22, h: 4.06, poster: path.join(SVG_DIR, '../assets/figures/research/geneticflow-video-poster.jpg') });
  }
}

pptx.writeFile({ fileName: output, compression: true })
  .then(() => console.log(output))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
