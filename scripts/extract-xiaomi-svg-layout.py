"""Extract ordered SVG primitives and original asset dimensions for editable PPTX."""
from pathlib import Path
from PIL import Image
import json
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
source = root / 'svg-src/xiaomi-engineering'
slides = []
for svg in sorted(source.glob('*.svg')):
    elements = []
    for element in ET.parse(svg).getroot():
        kind = element.tag.split('}')[-1]
        if kind == 'desc':
            continue
        item = dict(element.attrib, kind=kind)
        if kind == 'text':
            lines = []
            y = float(element.get('y', 0))
            if len(element):
                for child in element:
                    y += float(child.get('dy', '0').removesuffix('px'))
                    lines.append({'text': ''.join(child.itertext()),
                                  'x': float(child.get('x', element.get('x', 0))), 'y': y})
            else:
                lines = [{'text': ''.join(element.itertext()),
                          'x': float(element.get('x', 0)), 'y': y}]
            item['lines'] = lines
        elif kind == 'image':
            asset = (svg.parent / element.get('href')).resolve()
            item['asset'] = str(asset)
            with Image.open(asset) as image:
                item['intrinsicWidth'], item['intrinsicHeight'] = image.size
        elif kind not in ('rect', 'line', 'polygon'):
            raise ValueError(f'Unhandled SVG primitive {kind}: {svg}')
        elements.append(item)
    slides.append({'source': str(svg), 'name': svg.stem, 'elements': elements})
Path(sys.argv[1]).write_text(json.dumps(slides, ensure_ascii=False, indent=2))
