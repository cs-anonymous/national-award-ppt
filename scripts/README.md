# 脚本入口

逐页 SVG 由 `generate_slides.py` 生成；内容和版式初稿均集中在该脚本中，便于后续删减和调整。

```bash
python3 scripts/generate_slides.py
```

生成后再执行两个不会改变内容的处理步骤：

```bash
node scripts/embed-svg-images.js \
  svg-src/05-expath.svg \
  svg/05-expath.svg

rsvg-convert -w 1920 -h 1080 \
  -o svg-preview/05-expath.png \
  svg/05-expath.svg
```

全部 SVG 就绪后，用临时目录安装 `pptxgenjs` 并打包：

```bash
pptx_temp=$(mktemp -d /tmp/national-award-pptxgen.XXXXXX)
npm install --prefix "$pptx_temp" pptxgenjs --no-audit --no-fund
NODE_PATH="$pptx_temp/node_modules" node scripts/build-pptx.js
```
