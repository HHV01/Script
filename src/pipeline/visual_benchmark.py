"""Collect dated public comparison samples, without inventing visual observations."""
import json
import os
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .common import ROOT, load_env
from studio.channel import request_json

QUERIES = {
    'egypt': 'Ai Cập cổ đại kim tự tháp khảo cổ',
    'empires': 'đế chế La Mã lịch sử',
    'lost_cities': 'thành phố cổ mất tích khảo cổ',
    'historical_maps': 'bản đồ lịch sử chiến tranh đế chế',
}


def integer(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def collect(days=90, results=5, min_views=50000, duration='medium', now=None, previous=None):
    load_env()
    key = os.environ.get('YOUTUBE_API_KEY')
    if not key:
        raise ValueError('Cần YOUTUBE_API_KEY trong môi trường hoặc .env để lấy số liệu thật; không nhập key vào chat.')
    if not 1 <= days <= 365 or not 1 <= results <= 10 or min_views < 0 or duration not in ('short','medium','long','any'):
        raise ValueError('Tham số lấy mẫu không hợp lệ.')
    now = now or datetime.now(timezone.utc)
    after = (now-timedelta(days=days)).isoformat().replace('+00:00','Z')
    headers = {'X-Goog-Api-Key': key}
    def get(resource, params):
        return request_json('https://www.googleapis.com/youtube/v3/'+resource,params,headers)
    groups, all_ids = [], []
    for name, query in QUERIES.items():
        response=get('search',{'part':'snippet','q':query,'type':'video','order':'viewCount',
                               'publishedAfter':after,'maxResults':results,'videoDuration':duration,
                               'relevanceLanguage':'vi','regionCode':'VN'})
        ids=[v['id']['videoId'] for v in response.get('items',[]) if v.get('id',{}).get('videoId')]
        groups.append({'niche':name,'query':query,'sampled_ids':ids})
        all_ids.extend(ids)
    ids=list(dict.fromkeys(all_ids))
    videos={}
    baseline={}
    elapsed=None
    context={'days':days,'results':results,'min_views':min_views,'duration':duration,'queries':QUERIES}
    if previous and previous.get('context')==context:
        baseline={v['id']:v for v in previous.get('videos',[])}
        try:
            elapsed=(now-datetime.fromisoformat(previous['collected_at'])).total_seconds()/3600
        except (ValueError,KeyError,TypeError):
            pass
    if ids:
        response=get('videos',{'part':'snippet,statistics,contentDetails','id':','.join(ids)})
        for video in response.get('items',[]):
            sn=video.get('snippet',{});stats=video.get('statistics',{})
            if sn.get('liveBroadcastContent') in ('live','upcoming'):
                continue
            views=integer(stats.get('viewCount'));age=None
            try:
                age=max(1/24,(now-datetime.fromisoformat(sn['publishedAt'].replace('Z','+00:00'))).total_seconds()/86400)
            except (ValueError,KeyError,TypeError):
                pass
            thumbs=sn.get('thumbnails',{})
            thumbnail=next((thumbs[k]['url'] for k in ('maxres','standard','high','medium','default') if thumbs.get(k,{}).get('url')),None)
            before=baseline.get(video['id'],{}).get('views')
            videos[video['id']]={'id':video['id'],'url':'https://www.youtube.com/watch?v='+video['id'],
                                'title':sn.get('title',''),'channel':sn.get('channelTitle',''),
                                'published_at':sn.get('publishedAt'),'views':views,
                                'likes':integer(stats.get('likeCount')),'comments':integer(stats.get('commentCount')),
                                'duration':video.get('contentDetails',{}).get('duration'),
                                'thumbnail_url':thumbnail,
                                'average_views_per_day_since_publish':round(views/age,1) if views is not None and age else None,
                                'view_change':views-before if elapsed and elapsed>0 and views is not None and before is not None else None,
                                'observation_hours':elapsed if elapsed and elapsed>0 and before is not None else None,
                                'visual_observations':None}
    for group in groups:
        sample=[videos[v] for v in group['sampled_ids'] if v in videos]
        qualifying=[v for v in sample if v['views'] is not None and v['views']>=min_views]
        group['qualified_ids']=[v['id'] for v in qualifying]
        group['count']=len(qualifying)
        group['median_views_in_qualified_sample']=statistics.median(v['views'] for v in qualifying) if qualifying else None
    return {'collected_at':now.isoformat(),'context':context,'published_after':after,
            'groups':groups,'videos':list(videos.values()),
            'limitations':['Mẫu kết quả tìm kiếm được chọn theo viewCount, không phải bảng xếp hạng toàn bộ niche.',
                           'Ngôn ngữ vi và vùng VN là điều kiện tìm kiếm, không chứng minh quốc tịch/ngôn ngữ khán giả.',
                           'View tích lũy và view/ngày từ ngày đăng không cho biết CTR hay retention.',
                           'API không cung cấp bố cục ảnh, nhịp cắt, chuyển cảnh hoặc nguyên nhân tăng view. Cần xem thumbnail/video thật.',
                           'visual_observations để null cho tới khi có người/vision model thực sự xem hình.']}


def markdown(report):
    stamp=datetime.fromisoformat(report['collected_at']).astimezone(ZoneInfo('Asia/Ho_Chi_Minh'))
    lines=['# Mẫu đối chiếu hình ảnh video lịch sử','', 'Lấy dữ liệu: '+stamp.strftime('%d/%m/%Y %H:%M (UTC+7)'),
           f"Cửa sổ: {report['context']['days']} ngày; ngưỡng: {report['context']['min_views']:,} lượt xem.",
           '', '| Nhóm tìm kiếm | Số video đạt ngưỡng | View trung vị trong mẫu đạt ngưỡng |', '|---|---:|---:|']
    for group in report['groups']:
        median=group['median_views_in_qualified_sample']
        lines.append(f"| {group['query']} | {group['count']} | {median if median is not None else 'Chưa có'} |")
    lines += ['', '## Video và thumbnail gốc', '']
    for v in report['videos']:
        lines += ['### '+v['title'],v['url'],f"Kênh: {v['channel']} · Ngày đăng: {v['published_at']} · View: {v['views']}",
                  'Thumbnail: '+str(v['thumbnail_url'] or 'Không có'),
                  'Quan sát hình ảnh: chưa thực hiện; API không xác nhận chất lượng hình.', '']
    lines += ['## Khi xem thật, ghi lại', '',
              '- Thumbnail: chủ thể chính, tương phản sáng/tối, vật thể gợi tò mò, độ đọc được trên điện thoại.',
              '- 30–60 giây đầu: thời điểm thay hình, cỡ cảnh, bản đồ/tư liệu/tái dựng; ghi timestamp cụ thể.',
              '- Mỗi hình có làm rõ điều lời kể đang nói không? Bản đồ, sơ đồ và hiện vật xuất hiện ở đoạn nào?',
              '- Phân biệt ảnh tư liệu với AI tái dựng; kiểm tra sai niên đại, trang phục và địa lý.',
              '- Chỉ ghi quan sát từ phần thực sự đã xem. Đối chiếu nhiều video, không sao chép thumbnail của họ.',
              '', '## Giới hạn', '']
    lines += ['- '+item for item in report['limitations']]
    return '\n'.join(lines)+'\n'


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description='Lấy mẫu YouTube cùng niche để đối chiếu hình ảnh')
    parser.add_argument('--days',type=int,default=90)
    parser.add_argument('--results',type=int,default=5)
    parser.add_argument('--min-views',type=int,default=50000)
    parser.add_argument('--duration',choices=['short','medium','long','any'],default='medium')
    args=parser.parse_args(argv)
    directory=ROOT/'.studio/visual-benchmark'
    target=directory/'latest.json'
    previous=None
    if target.exists():
        try:
            previous=json.loads(target.read_text(encoding='utf-8'))
        except (ValueError,OSError):
            pass
    try:
        report=collect(args.days,args.results,args.min_views,args.duration,previous=previous)
    except ValueError as error:
        raise SystemExit(str(error)) from None
    directory.mkdir(parents=True,exist_ok=True)
    temp=target.with_suffix('.tmp')
    temp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(target)
    (directory/'latest.md').write_text(markdown(report),encoding='utf-8')
    print(f"Đã lấy {len(report['videos'])} video đối chiếu. Báo cáo: {directory/'latest.md'}")
