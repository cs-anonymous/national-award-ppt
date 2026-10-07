# 国奖答辩 PPT

本目录采用 `/Users/a./Documents/systematic-lit-search/ppt` 的 SVG 制作约定，用于制作 2026 年北京航空航天大学计算机学院研究生国家奖学金公开答辩 PPT。

## 目录约定

| 目录 | 用途 |
|---|---|
| `content/` | 内容冻结层：逐页文案、讲稿、图位、来源和证据边界 |
| `assets/` | 图片、论文截图、成果证明截图及 `manifest.md` 资产清单 |
| `svg-src/` | 可编辑 SVG 源稿；允许引用 `assets/` 下的相对路径图片 |
| `svg/` | 自包含 SVG 成品；图片已 Base64 内嵌，可直接导入 SVG→PPT 工具 |
| `svg-preview/` | 1920×1080 PNG 预览，用于逐页视觉检查 |
| `scripts/` | 图片嵌入、预览和 PPTX 打包脚本 |
| `archive/` | 过期页面、旧版本和答辩后归档材料，不参与当前打包 |

## 当前入口

- [制作计划](PLAN-national-award.md)：目标、页序、流程、证据口径和验收清单。
- [逐页内容总览](content/README.md)：12 页页面职责、三大模块归属和完成状态。
- [三个模块写法](content/THREE-MODULES.md)：基本情况、科研成果、其他活动的写作框架和建议内容。
- [资产清单](assets/manifest.md)：图片来源、用途、版权/证明材料和核验状态。
- `svg-src/`、`svg/`、`svg-preview/` 已包含 12 页初稿；后续修改统一编辑 `scripts/generate_slides.py` 后重新生成。
- 当前 PPTX：[national-award-defense-2026.pptx](national-award-defense-2026.pptx)。

## 处理链

```text
材料与证明核验
  -> content/ 逐页文案冻结
  -> assets/manifest.md 登记图片和证据
  -> svg-src/ 设计并生成 1920×1080 源稿
  -> scripts/embed-svg-images.js 生成自包含 svg/
  -> rsvg-convert 生成 svg-preview/
  -> scripts/build-pptx.js 打包满版 SVG PPTX
  -> 逐页视觉检查 + 讲稿计时 + 最终材料一致性核验
```

## 重新生成

```bash
python3 scripts/generate_slides.py
for f in svg-src/*.svg; do
  name=$(basename "$f")
  rsvg-convert -w 1920 -h 1080 -o "svg-preview/${name%.svg}.png" "$f"
done
NODE_PATH=/path/to/node_modules node scripts/build-pptx.js national-award-defense-2026.pptx
```

PPTX 每页默认是一个满版 SVG 图形，因此可以无损缩放，但不会自动拆成独立文本框。需要继续编辑时，先保留 SVG 源稿和原始 PPTX，再在 PowerPoint 中尝试“转换为形状”。
