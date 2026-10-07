#!/usr/bin/env node

// Embed relative PNG/JPG assets into a self-contained SVG without changing the source SVG.
const fs = require('fs');
const path = require('path');

const [inputArg, outputArg] = process.argv.slice(2);
if (!inputArg || !outputArg) {
  console.error('Usage: node embed-svg-images.js <source.svg> <output.svg>');
  process.exit(2);
}

const input = path.resolve(inputArg);
const output = path.resolve(outputArg);
const baseDir = path.dirname(input);
let svg = fs.readFileSync(input, 'utf8').replace(/\s+xlink:href="[^"]+"/g, '');

svg = svg.replace(/href="([^"#][^"]*\.(?:png|jpe?g))"/gi, (match, relativePath) => {
  if (/^data:/i.test(relativePath)) return match;
  const asset = path.resolve(baseDir, relativePath);
  const ext = path.extname(asset).toLowerCase();
  const mime = ext === '.png' ? 'image/png' : 'image/jpeg';
  return `href="data:${mime};base64,${fs.readFileSync(asset).toString('base64')}"`;
});

fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, svg);
