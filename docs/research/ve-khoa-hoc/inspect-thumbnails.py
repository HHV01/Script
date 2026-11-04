import json,io
from pathlib import Path
from urllib.request import urlopen
from PIL import Image,ImageDraw
root=Path('docs/research/ve-khoa-hoc');r=json.loads((root/'api-snapshot.json').read_text(encoding='utf-8'));ids=['vSQXuflK_UQ','mN6-9_wJEf8','-HAXgjegVPk','wIIJQXXn4SE']
board=Image.new('RGB',(960,580),'white');draw=ImageDraw.Draw(board)
for i,vid in enumerate(ids):
 v=next(v for v in r['videos'] if v['id']==vid);url=v['thumbnails'].get('maxres',v['thumbnails']['high'])['url']
 with urlopen(url,timeout=15) as response:im=Image.open(io.BytesIO(response.read())).convert('RGB')
 im.thumbnail((480,270));x=(i%2)*480;y=(i//2)*290;board.paste(im,(x,y));draw.text((x+4,y+272),vid,fill='black')
board.save(root/'thumbnail-observations.jpg');print('4 public thumbnails assembled for visual inspection; no video frames inspected')
