import sys,os,json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
sys.path.insert(0,'src')
from pipeline.common import load_env
load_env();key=os.environ.get('YOUTUBE_API_KEY');out=[]
for vid in ['vSQXuflK_UQ','XIcp5ZoETQM']:
 try:
  req=Request('https://www.googleapis.com/youtube/v3/commentThreads?'+urlencode({'part':'snippet','videoId':vid,'maxResults':10,'order':'relevance','textFormat':'plainText'}),headers={'X-Goog-Api-Key':key})
  with urlopen(req,timeout=20) as response:r=json.load(response)
  comments=[{'text':x['snippet']['topLevelComment']['snippet']['textDisplay'],'likes':x['snippet']['topLevelComment']['snippet'].get('likeCount',0)} for x in r.get('items',[])]
  out.append({'video_id':vid,'sampling':'10 relevance-ranked top-level comments, not representative','comments':comments})
 except HTTPError as e:out.append({'video_id':vid,'error':'HTTP '+str(e.code)})
 except (URLError,TimeoutError):out.append({'video_id':vid,'error':'network'})
Path('docs/research/ve-khoa-hoc/comment-sample.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
