import sys,os,json
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
sys.path.insert(0,'src')
from pipeline.common import load_env
load_env();key=os.environ.get('YOUTUBE_API_KEY')
if not key:raise SystemExit('Missing YouTube API key; not printed')
def get(resource,params):
 try:
  with urlopen(Request('https://www.googleapis.com/youtube/v3/'+resource+'?'+urlencode(params),headers={'X-Goog-Api-Key':key}),timeout=25) as r:return json.load(r)
 except HTTPError as e:raise SystemExit('YouTube API HTTP '+str(e.code)) from None
 except (URLError,TimeoutError):raise SystemExit('YouTube API network error') from None
chs=get('channels',{'part':'snippet,statistics,contentDetails','forHandle':'@TunaGamingvn'}).get('items',[])
if not chs:raise SystemExit('Channel handle not found')
c=chs[0];playlist=c['contentDetails']['relatedPlaylists']['uploads'];ids=[];page=None
for _ in range(1):
 args={'part':'contentDetails','playlistId':playlist,'maxResults':50}
 if page:args['pageToken']=page
 batch=get('playlistItems',args);ids.extend(x['contentDetails']['videoId'] for x in batch.get('items',[]));page=batch.get('nextPageToken')
 if not page:break
videos=[]
for i in range(0,len(ids),50):
 for v in get('videos',{'part':'snippet,statistics,contentDetails','id':','.join(ids[i:i+50])}).get('items',[]):
  s=v['snippet'];videos.append({'id':v['id'],'url':'https://www.youtube.com/watch?v='+v['id'],'title':s['title'],'description':s.get('description',''),'published_at':s['publishedAt'],'tags':s.get('tags',[]),'thumbnails':s.get('thumbnails',{}),'statistics':v.get('statistics',{}),'duration':v.get('contentDetails',{}).get('duration')})
r={'retrieved_at':datetime.now(timezone.utc).isoformat(),'channel':c,'videos':videos,'uploads_truncated':bool(page),'scope':'Public API metadata only; no video watching, audio listening, CTR, retention or traffic sources.'}
Path('docs/research/tuna-gaming/api-snapshot.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'channel':c['snippet'],'statistics':c['statistics'],'video_count_fetched':len(videos),'videos':[{'id':v['id'],'title':v['title'],'views':v['statistics'].get('viewCount'),'published':v['published_at'],'duration':v['duration']} for v in sorted(videos,key=lambda x:int(x['statistics'].get('viewCount',0)),reverse=True)]},ensure_ascii=False))
