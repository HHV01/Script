'use strict';
const $ = id => document.getElementById(id);
const stages = ['script','review','voice','scenes','prompts','generate','collect','render','publish'];
const names = ['Biên kịch','Duyệt kịch bản','Phòng thu','Phân cảnh','Mỹ thuật','Google Flow','Kiểm ảnh','Dựng phim','Xuất bản'];
const actions = ['Đang viết câu chuyện lịch sử','Mai đang đọc duyệt, cập nhật tín hiệu YouTube và hướng dẫn thu giọng','Đang tạo giọng đọc và thời gian lời nói','Đang chia cảnh theo lời đọc','Đang thiết kế hình ảnh từng cảnh','Đang tạo ảnh minh họa trên Google Flow','Đang đối chiếu và tải ảnh','Đang ghép ảnh, giọng đọc và phụ đề','Đang chuẩn bị tiêu đề, mô tả và tag'];
const descriptions = ['Chủ đề và phong cách của kênh được chuyển thành một kịch bản có mở đầu, diễn biến và kết thúc.','Chỉ cho thu khi hook, mạch kể, độ cẩn trọng lịch sử và câu đọc đạt yêu cầu. Mai có thể yêu cầu sửa rồi duyệt lại.','Lời kể được đọc thành tiếng và đồng bộ thời gian để hình ảnh bám sát câu chuyện.','Mỗi cảnh nhận một đoạn lời kể cùng thời điểm bắt đầu và kết thúc.','Giữ phong cách hình ảnh nhất quán, ngoại hình nhân vật và bối cảnh đúng câu chuyện.','Browser cần đăng nhập Google và mở đúng project Flow. Nhật ký bên dưới sẽ báo nếu cần thao tác.','Chỉ tải khi ảnh khớp với các cảnh. Ảnh thiếu hoặc trùng sẽ được báo lỗi.','Dựng video theo độ dài lời kể, thêm chuyển động ảnh và phụ đề nhỏ sát đáy.','Chuẩn bị gói đăng YouTube đúng niche lịch sử và gợi ý thumbnail, hook, nhịp kể.'];
let managerState={status:'idle',settings:{},readiness:{}},managerBusy=false,managerPosition={x:-4,z:1.2};
let token='', selected='', state={status:'idle',stages:{},logs:[]}, projectList=[], online=false, pending=false;
$('stage-strip').innerHTML = names.map((n,i)=>`<div class="stage" id="stage-${stages[i]}"><div class="stage-number">${i+1}</div><span>${n}</span></div>`).join('');
stages.forEach((stage,i)=>{const o=document.createElement('option');o.value=stage;o.textContent=`${i+1}. ${names[i]}`;$('start-stage').append(o);});
const statusNames={idle:'Sẵn sàng',running:'Đang làm việc',stopping:'Đang dừng',completed:'Hoàn tất',failed:'Cần xử lý',cancelled:'Đã dừng',interrupted:'Bị gián đoạn'};
function showError(message){$('error').textContent=message;$('error').hidden=!message;}
async function post(path, body){
  const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Studio-Token':token},body:JSON.stringify(body)});
  const result=await response.json();if(!response.ok)throw Error(result.error||'Không thực hiện được yêu cầu.');return result;
}
function render(){
  const matching=selected===state.project;
  const run=matching?state:{status:'idle',stages:{},logs:[]};
  const busy=['running','stopping'].includes(state.status), current=stages.indexOf(run.stage);
  const count=Object.values(run.stages||{}).filter(x=>x==='completed').length;
  $('run').disabled=!selected||busy||pending||!online;
  $('stop').disabled=!busy||pending||!online;
  $('run').textContent=busy?(run.stage==='review'?'● Mai đang đọc duyệt':'● Minh đang làm việc'):'▶ Giao việc cho Minh';
  $('worker-name').textContent=run.stage==='review'?'Mai':'Minh';
  $('worker-role').textContent=run.stage==='review'?'Biên tập viên kịch bản':'Người đại diện sản xuất';
  $('worker-avatar').classList.toggle('editor-avatar',run.stage==='review');
  $('project-select').disabled=busy;
  $('start-stage').disabled=busy;
  $('only-stage').disabled=busy||!$('start-stage').value;
  if(!$('start-stage').value)$('only-stage').checked=false;
  const project=projectList.find(p=>p.name===selected);
  $('project-topic').textContent=project?project.topic:'Bắt đầu bằng một chủ đề lịch sử mà bạn muốn kể.';
  $('agent-state').textContent=statusNames[run.status]||'Sẵn sàng';
  $('agent-state').style.color=['failed','interrupted'].includes(run.status)?'var(--red)':'var(--green)';
  $('progress-label').textContent=`${count} / ${stages.length} công đoạn`;
  $('progress-percent').textContent=`${Math.round(count/stages.length*100)}%`;
  $('progress-fill').style.width=`${count/stages.length*100}%`;
  stages.forEach((key,i)=>{
    const s=run.stages?.[key];const el=$(`stage-${key}`);
    el.className='stage'+(s==='completed'?' done':s==='running'?' active':['failed','cancelled','interrupted'].includes(s)?' failed':'');
    el.querySelector('.stage-number').textContent=s==='completed'?'✓':['failed','cancelled','interrupted'].includes(s)?'!':i+1;
  });
  const active=run.status==='running';
  const action=active&&current>=0?actions[current]:run.status==='completed'?'Đã hoàn tất công việc được giao':['failed','interrupted'].includes(run.status)?'Công việc cần bạn kiểm tra nhật ký':run.status==='cancelled'?'Đã dừng · Có thể tiếp tục từ công đoạn còn lại':run.status==='stopping'?'Đang dừng tiến trình…':'Sẵn sàng cho một câu chuyện mới';
  $('agent-name').textContent=run.stage==='review'?'Mai · Biên tập viên kịch bản':'Minh · Người kể chuyện';
  $('agent-action').textContent=action;
  $('scene-status').textContent=(statusNames[run.status]||'Sẵn sàng').toUpperCase();
  $('current-task').textContent=current>=0?names[current]:'Chưa nhận nhiệm vụ';
  $('task-description').textContent=current>=0?descriptions[current]:'Tôi sẽ đưa câu chuyện của bạn qua 9 công đoạn, từ kịch bản đến gói đăng YouTube.';
  const logs=run.logs||[];const container=$('logs'),atBottom=container.scrollHeight-container.scrollTop-container.clientHeight<45;
  const signature=JSON.stringify(logs);
  if(container.dataset.signature!==signature){
    container.dataset.signature=signature;container.replaceChildren();
    if(!logs.length){const el=document.createElement('div');el.className='empty';el.textContent='⌁ Chưa có hoạt động. Giao cho Minh một câu chuyện để bắt đầu.';container.append(el);}
    logs.forEach(log=>{const row=document.createElement('div');row.className='log';const time=document.createElement('time');time.textContent=new Date(log.time*1000).toLocaleTimeString('vi-VN',{hour12:false});const text=document.createElement('span');text.textContent=log.text;row.append(time,text);container.append(row);});
    if(atBottom)container.scrollTop=container.scrollHeight;
  }
  $('log-count').textContent=logs.length;
  $('run-time').textContent=run.started_at?'Bắt đầu '+new Date(run.started_at*1000).toLocaleTimeString('vi-VN',{hour:'2-digit',minute:'2-digit'}):'Chưa bắt đầu';
  renderReview(project?.review);
  const items=[['script.review.json','Phiếu duyệt của Mai','✓',project?.review?.status&&project.review.status!=='not_reviewed'],['recording_script.md','Bản hướng dẫn thu giọng','≡',project?.review?.status==='approved'],['final.mp4','Video hoàn chỉnh','▷',project?.video],['subtitles.srt','Phụ đề','≡',project?.video],['publish.txt','Tiêu đề · mô tả · tag','↗',project?.metadata],['publish.json','Gói xuất bản đầy đủ','◇',project?.metadata]];
  $('artifacts').replaceChildren();
  items.forEach(([file,label,icon,ready])=>{const el=document.createElement(ready?'a':'div');el.className='artifact'+(ready?'':' disabled');if(ready){el.href=`/artifacts/${encodeURIComponent(selected)}/${file}`;el.download=file;}const symbol=document.createElement('span');symbol.textContent=icon;const info=document.createElement('div');const title=document.createElement('b');title.textContent=label;const filename=document.createElement('small');filename.textContent=file;info.append(title,filename);const arrow=document.createElement('span');arrow.textContent=ready?'↓':'—';el.append(symbol,info,arrow);$('artifacts').append(el);});
  sceneStage=current;
  sceneRunning=active;
  sceneFailed=['failed','interrupted'].includes(run.status);
}
async function refresh(){
  try{
    const response=await fetch('/api/status');if(!response.ok)throw Error('Kết nối lỗi');const data=await response.json();
    token=data.token;state=data.run;online=true;projectList=data.projects;managerState=data.manager||managerState;renderManager();
    const saved=selected||localStorage.getItem('studio-project');
    if(['running','stopping'].includes(state.status)&&state.project)selected=state.project;
    else selected=projectList.some(p=>p.name===saved)?saved:projectList[0]?.name||'';
    $('project-select').replaceChildren();
    if(!projectList.length){const option=document.createElement('option');option.value='';option.textContent='Chưa có dự án';$('project-select').append(option);}
    projectList.forEach(p=>{const option=document.createElement('option');option.value=p.name;option.textContent=p.name;option.disabled=!!p.invalid;$('project-select').append(option);});
    $('project-select').value=selected;
    $('connection').textContent='Đã kết nối · Máy cục bộ';$('connection-dot').className='';render();
  }catch(error){online=false;$('connection').textContent='Mất kết nối · Đang thử lại';$('connection-dot').className='offline';$('run').disabled=true;$('stop').disabled=true;}
}
$('project-select').onchange=()=>{selected=$('project-select').value;localStorage.setItem('studio-project',selected);showError('');render();};
$('start-stage').onchange=render;
$('run').onclick=async()=>{pending=true;render();showError('');try{await post('/api/run',{project:selected,stage:$('start-stage').value||null,only:$('only-stage').checked});await refresh();}catch(e){showError(e.message);}finally{pending=false;render();}};
$('stop').onclick=async()=>{pending=true;render();try{await post('/api/stop',{});await refresh();}catch(e){showError(e.message);}finally{pending=false;render();}};
$('new-project').onclick=()=>$('project-dialog').showModal();$('guide').onclick=()=>$('guide-dialog').showModal();
document.querySelectorAll('.close-dialog').forEach(button=>button.onclick=()=>button.closest('dialog').close());
$('project-form').onsubmit=async event=>{event.preventDefault();const body=Object.fromEntries(new FormData(event.currentTarget));body.minutes=Number(body.minutes);const button=event.currentTarget.querySelector('[type=submit]');button.disabled=true;$('form-error').textContent='';try{const data=await post('/api/projects',body);selected=data.name;localStorage.setItem('studio-project',selected);await refresh();$('project-dialog').close();}catch(e){$('form-error').textContent=e.message;}finally{button.disabled=false;}};
function renderReview(review){
  const r=review||{status:'not_reviewed'};
  const labels={not_reviewed:'Chưa duyệt',pending:'Đang chờ duyệt',blocked:'Chưa đạt · Chặn thu giọng',approved:'Đã duyệt',stale:'Bản duyệt đã cũ'};
  $('review-status').textContent=labels[r.status]||'Cần kiểm tra';
  $('review-summary').textContent=r.summary||'Mai sẽ đọc lại bản nháp, đối chiếu tín hiệu YouTube mới và yêu cầu sửa trước khi chuyển sang phòng thu.';
  $('review-narration').textContent=r.narration_notes||'Bản được duyệt sẽ có kế hoạch chia câu, đoạn và khoảng nghỉ cho phòng thu.';
  $('review-date').textContent=r.researched_at?'Tín hiệu YouTube cập nhật: '+new Date(r.researched_at).toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh'}):'Chưa có tín hiệu YouTube được cập nhật';
  $('review-issues').replaceChildren();(r.reasons||[]).forEach(reason=>{const li=document.createElement('li');li.textContent=reason;$('review-issues').append(li);});
  const dimensions={hook:'Hook',structure:'Mạch kể',historical_care:'Cẩn trọng lịch sử',niche_fit:'Đúng niche',readability:'Dễ đọc',engagement:'Sức cuốn hút'};
  $('review-scores').replaceChildren();Object.entries(dimensions).forEach(([key,label])=>{const item=document.createElement('div');const title=document.createElement('span');title.textContent=label;const score=document.createElement('b');score.textContent=r.scores?.[key]===undefined?'—':r.scores[key]+'/10';item.append(title,score);$('review-scores').append(item);});
}
const formatNumber=value=>value===null||value===undefined?'—':new Intl.NumberFormat('vi-VN',{maximumFractionDigits:1}).format(Number(value));
const formatDate=value=>value?new Date(typeof value==='number'?value*1000:value).toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh'}):'—';
function managerError(message){$('manager-error').textContent=message||'';$('manager-error').hidden=!message;}
function renderManager(){
  const m=managerState,r=m.report,ready=m.readiness||{};
  const working=['researching','planning','reporting'].includes(m.status);
  $('manager-action').textContent=m.action||'Chờ kết nối kênh';
  $('manager-analyze').disabled=working||managerBusy;
  $('manager-analyze').textContent=working?'● An đang nghiên cứu':m.settings?.auto_dispatch?'↗ Phân tích & giao đề tài':'↗ Phân tích & tìm đề tài';
  $('connect-channel').textContent=ready.owner_connected?'Kết nối lại chủ kênh':'Kết nối chủ kênh';
  if(m.error)managerError(m.error);
  if(!$('manager-settings-form').dataset.loaded){
    $('manager-enabled').checked=!!m.settings?.enabled;$('manager-dispatch').checked=!!m.settings?.auto_dispatch;
    $('manager-interval').value=m.settings?.interval_hours||24;$('manager-minutes').value=m.settings?.minutes||8;$('manager-flow').value=m.settings?.flow_url||'';
    $('manager-settings-form').dataset.loaded='true';
  }
  $('manager-next').textContent=m.settings?.enabled?'Lượt tiếp theo: '+formatDate(m.next_run_at)+' · chỉ chạy khi server mở.':'Lịch tự động đang tắt. Bạn có thể phân tích ngay.';
  $('manager-source').textContent=r?(r.channel.title+' · Cập nhật '+formatDate(r.collected_at)+(r.videos_truncated?' · Mẫu 100 video mới nhất':' · '+r.videos.length+' video đã đọc')):'Chưa lấy dữ liệu thật · '+(ready.api_key?'API key đã đặt':'Chưa đặt API key')+(ready.owner_connected?' · OAuth đã lưu':' · Chưa kết nối chủ kênh');
  const stats=r?.channel?.statistics||{},analytics=r?.analytics||{},summary=analytics.summary?.[0]||{};
  $('metric-views').textContent=formatNumber(stats.viewCount);$('metric-subs').textContent=formatNumber(stats.subscriberCount);
  const delta=r?.summary?.delta_since_snapshot?.viewCount;
  $('metric-delta').textContent=delta===null||delta===undefined?'Chưa có mốc so sánh':(delta>=0?'+':'')+formatNumber(delta)+' so với '+formatDate(r.summary.baseline_at);
  $('metric-period').textContent=formatNumber(summary.views);
  $('metric-period-note').textContent=analytics.status==='ok'?analytics.start+' → '+analytics.end:'Cần Analytics chủ kênh; chưa có số liệu';
  $('metric-watch').textContent=summary.averageViewDuration===undefined?'—':formatNumber(summary.averageViewDuration)+' giây';
  $('metric-retention').textContent=summary.averageViewPercentage===undefined?'Cần Analytics chủ kênh':formatNumber(summary.averageViewPercentage)+'% thời lượng video trung bình';
  const gained=summary.subscribersGained,lost=summary.subscribersLost;
  $('manager-owner-summary').textContent=analytics.status==='ok'?'Phút xem: '+formatNumber(summary.estimatedMinutesWatched)+' · Subscriber tăng: '+formatNumber(gained)+' · giảm: '+formatNumber(lost)+' · ròng: '+formatNumber(gained===undefined||lost===undefined?null:Number(gained)-Number(lost)):'Cần kết nối Analytics chủ kênh. '+(analytics.status==='error'?analytics.note:'');
  const trafficNames={YT_SEARCH:'Tìm kiếm YouTube',EXT_URL:'Trang web bên ngoài',RELATED_VIDEO:'Video đề xuất',SUBSCRIBER:'Kênh đăng ký',PLAYLIST:'Danh sách phát',NOTIFICATION:'Thông báo',SHORTS:'Shorts'};
  $('manager-traffic').replaceChildren();(analytics.traffic||[]).forEach(source=>{const li=document.createElement('li');li.textContent=(trafficNames[source.insightTrafficSourceType]||source.insightTrafficSourceType)+': '+formatNumber(source.views)+' lượt xem';$('manager-traffic').append(li);});
  $('manager-downloads').hidden=!r;
  $('brief-count').textContent=(r?.briefs?.length||0)+' đề tài';
  if(!r)return;
  $('manager-assessment').textContent=r.assessment||'Chưa có nhận định.';
  $('manager-actions').replaceChildren();(r.actions||[]).forEach(action=>{const li=document.createElement('li');li.textContent=action;$('manager-actions').append(li);});
  $('manager-caveats').textContent=(analytics.note||'')+' '+(r.summary?.caveats||[]).join(' ');
  const top=r.summary?.top_videos||[],max=Math.max(1,...top.map(v=>v.views||0));
  $('channel-top-videos').replaceChildren();top.slice(0,6).forEach(video=>{const row=document.createElement('div');row.className='video-bar';const line=document.createElement('div'),title=document.createElement('span'),value=document.createElement('span');title.textContent=video.title;title.title=video.title;value.textContent=formatNumber(video.views);line.append(title,value);const track=document.createElement('div');track.className='bar-track';const fill=document.createElement('div');fill.className='bar-fill';fill.style.width=(video.views||0)/max*100+'%';track.append(fill);row.append(line,track);$('channel-top-videos').append(row);});
  const signature=JSON.stringify(r.briefs);
  if($('manager-briefs').dataset.signature!==signature){
    $('manager-briefs').dataset.signature=signature;$('manager-briefs').replaceChildren();
    if(!r.briefs?.length){const p=document.createElement('p');p.className='muted';p.textContent='Chưa có đề tài hợp lệ. Kiểm tra LLM rồi phân tích lại.';$('manager-briefs').append(p);}
    (r.briefs||[]).forEach((brief,i)=>{const card=document.createElement('article');card.className='brief-card';const title=document.createElement('h4');title.textContent=`${i+1}. ${brief.topic}`;const niche=document.createElement('span');niche.className='brief-niche';niche.textContent=brief.niche;const hook=document.createElement('p');hook.textContent='Mở đầu: '+brief.hook;const why=document.createElement('p');why.textContent=brief.rationale;const source=document.createElement('small');source.textContent='Video tham khảo: '+brief.evidence_video_ids.join(', ');const button=document.createElement('button');button.className='outline';const states={queued:'Đang chờ Minh',dispatched:'Đã giao cho Minh',completed:'Đã sản xuất xong',failed:'Sản xuất bị lỗi',cancelled:'Đã dừng',interrupted:'Bị gián đoạn'};button.textContent=states[brief.status]||'Giao đề tài này cho Minh';button.disabled=brief.status!=='proposed';button.onclick=async()=>{button.disabled=true;try{const result=await post('/api/manager/delegate',{brief_id:brief.id});if(result.project)selected=result.project;await refresh();}catch(e){managerError(e.message);button.disabled=false;}};card.append(title,niche,hook,why,source,button);if(brief.project){const project=document.createElement('small');project.textContent='Dự án: '+brief.project;card.append(project);} $('manager-briefs').append(card);});
  }
}
$('manager-analyze').onclick=async()=>{managerBusy=true;managerError('');renderManager();try{await post('/api/manager/analyze',{});$('manager-details').open=true;await refresh();}catch(e){managerError(e.message);}finally{managerBusy=false;renderManager();}};
$('manager-settings-form').onsubmit=async event=>{event.preventDefault();managerError('');const button=event.currentTarget.querySelector('[type=submit]');button.disabled=true;try{await post('/api/manager/settings',{enabled:$('manager-enabled').checked,auto_dispatch:$('manager-dispatch').checked,interval_hours:Number($('manager-interval').value),minutes:Number($('manager-minutes').value),flow_url:$('manager-flow').value.trim()});await refresh();}catch(e){managerError(e.message);}finally{button.disabled=false;}};
$('connect-channel').onclick=async()=>{managerError('');const tab=window.open('','_blank');if(tab)tab.opener=null;try{const result=await post('/api/manager/connect',{});if(tab)tab.location.href=result.url;else managerError('Browser chặn cửa sổ đăng nhập. Cho phép popup rồi kết nối lại.');}catch(e){if(tab)tab.close();managerError(e.message);}};
$('disconnect-channel').onclick=async()=>{try{await post('/api/manager/disconnect',{});await refresh();}catch(e){managerError(e.message);}};

// Small software 3D renderer. All geometry and labels are local; no CDN or external assets.
const canvas=$('world'),ctx=canvas.getContext('2d');let width=0,height=0,angle=-.12,zoom=1,drag=null,sceneStage=-1,sceneRunning=false,sceneFailed=false;
let agent={x:0,z:1.8},lastTime=performance.now();
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const stations=[{x:-5,z:-3.6},{x:4,z:.2},{x:-1.7,z:-3.6},{x:1.7,z:-3.6},{x:5,z:-3.6},{x:-5,z:3.5},{x:-1.7,z:3.5},{x:1.7,z:3.5},{x:5,z:3.5}];
function resize(){const rect=canvas.getBoundingClientRect();width=rect.width;height=rect.height;const dpr=Math.min(devicePixelRatio||1,2);canvas.width=width*dpr;canvas.height=height*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);}
new ResizeObserver(resize).observe(canvas);
function project(x,y,z){const xx=x*Math.cos(angle)-z*Math.sin(angle),zz=x*Math.sin(angle)+z*Math.cos(angle);const scale=Math.min(width/19,height/13)*zoom;return [width/2+xx*scale,height*.48+(zz*.48-y*.95)*scale];}
function polygon(points,color,stroke){ctx.beginPath();points.forEach((p,i)=>{const v=project(...p);i?ctx.lineTo(...v):ctx.moveTo(...v);});ctx.closePath();ctx.fillStyle=color;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=.65;ctx.stroke();}}
function line(a,b,color,width=1){ctx.beginPath();ctx.moveTo(...project(...a));ctx.lineTo(...project(...b));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
function box(x,y,z,w,h,d,colors){const [top,front,side]=colors;polygon([[x,y,z],[x+w,y,z],[x+w,y,z+d],[x,y,z+d]],front);polygon([[x,y,z+d],[x+w,y,z+d],[x+w,y+h,z+d],[x,y+h,z+d]],front);polygon([[x+w,y,z],[x+w,y,z+d],[x+w,y+h,z+d],[x+w,y+h,z]],side);polygon([[x,y+h,z],[x+w,y+h,z],[x+w,y+h,z+d],[x,y+h,z+d]],top);}
function circle(x,y,z,r,color,stroke){const pts=[];for(let i=0;i<40;i++){const a=i/40*Math.PI*2;pts.push([x+Math.cos(a)*r,y,z+Math.sin(a)*r]);}polygon(pts,color,stroke);}
function label(text,x,y,z,color='#9bacb2',size=9){const p=project(x,y,z);ctx.font=`${size}px system-ui`;ctx.textAlign='center';ctx.fillStyle=color;ctx.fillText(text,...p);}
function lamp(x,z){box(x,0,z,.45,.5,.45,['#45525a','#28383d','#203038']);for(let i=0;i<5;i++)box(x+.05+Math.sin(i*2)*.18,.5+i*.13,z+.08+Math.cos(i*2)*.14,.25,.35,.25,['#60756b','#3e5d52','#2d493f']);}
function desk(s,i,t){const active=sceneStage===i,done=state.stages?.[stages[i]]==='completed'&&state.project===selected;const c=active?(sceneFailed?'#b57970':'#d6b574'):done?'#75a88e':'#55707a';
 if(active){circle(s.x,.015,s.z,1.28,'#d6b57408',c);circle(s.x,.02,s.z,1.4,'#00000000',c+'50');}
 const x=s.x-1,z=s.z-.5;
 box(x+.12,0,z+.1,.12,1,.12,['#46545b','#303d45','#24343c']);box(x+1.72,0,z+.1,.12,1,.12,['#46545b','#303d45','#24343c']);box(x+.12,0,z+.85,.12,1,.12,['#46545b','#303d45','#24343c']);box(x+1.72,0,z+.85,.12,1,.12,['#46545b','#303d45','#24343c']);
 box(x,.98,z,2,.12,1.1,['#7a817c','#505b59','#435355']);
 box(s.x-.08,1.1,z+.25,.16,.3,.16,['#444d4f','#323d41','#29363d']);box(s.x-.52,1.28,z+.12,1.04,.65,.12,['#39494f','#26343d','#20313a']);
 polygon([[s.x-.46,1.34,z+.25],[s.x+.46,1.34,z+.25],[s.x+.46,1.87,z+.25],[s.x-.46,1.87,z+.25]],'#122a30',c);
 for(let k=0;k<3;k++)line([s.x-.35,1.75-k*.13,z+.26],[s.x+(.1+Math.sin(i+k)*.15),1.75-k*.13,z+.26],c,1.2);
 box(s.x-.38,1.105,z+.65,.65,.025,.25,['#344750','#24343c','#23353d']);
 box(s.x+.58,1.1,z+.63,.18,.24,.18,['#dbcfad','#a49473','#84755a']);
 box(s.x-.35,0,s.z+.98,.7,.68,.6,['#354a50','#243941','#1d3039']);box(s.x-.35,.65,s.z+1.4,.7,.65,.13,['#415a5d','#304a50','#263d44']);
 label(`${String(i+1).padStart(2,'0')}  ${names[i]}`,s.x,0,s.z+2.05,active?c:'#8b9ea5',Math.max(8,Math.min(width/95,10)));
 if(done)label('✓',s.x+.85,1.9,s.z+.3,'#8ebca3',12);
}
function person(x,z,t,manager=false,editor=false){circle(x,.025,z,.4,'#060e13a0');const moving=Math.abs(agent.x-(stations[sceneStage]?.x||0))>.05;const bob=sceneRunning&&!reduced?Math.sin(t*5)*.025:0;
 box(x-.18,.27+bob,z-.12,.14,.46,.2,['#596568','#273a42','#20313b']);box(x+.05,.27+bob,z-.12,.14,.46,.2,['#596568','#273a42','#20313b']);
 box(x-.25,.65+bob,z-.2,.5,.55,.36,editor?['#c0addb','#886d9d','#68527b']:manager?['#90bcca','#527f91','#3b6273']:['#c4aa74','#977d4c','#796940']);
 box(x-.35,.7+bob,z-.12,.11,.38,.17,['#c4aa74','#b79964','#8a754f']);box(x+.25,.7+bob,z-.12,.11,.38,.17,['#c4aa74','#b79964','#8a754f']);
 box(x-.19,1.21+bob,z-.15,.38,.37,.32,['#d4b997','#c4a784','#a99178']);box(x-.21,1.52+bob,z-.17,.42,.12,.36,['#333b3d','#283235','#202c30']);
 const p=project(x,1.99,z);ctx.font='600 9px system-ui';const text=editor?(sceneStage===1&&sceneRunning?'MAI · ĐỌC DUYỆT':'MAI · BIÊN TẬP'):manager?(['researching','planning'].includes(managerState.status)?'AN · NGHIÊN CỨU':'AN · QUẢN LÝ KÊNH'):(sceneRunning?'MINH · ĐANG LÀM VIỆC':sceneFailed?'MINH · CẦN HỖ TRỢ':'MINH');const measure=ctx.measureText(text).width;ctx.fillStyle='#101b21ee';ctx.strokeStyle=sceneFailed?'#bd8174':'#b59e6e';ctx.lineWidth=.7;ctx.beginPath();ctx.roundRect(p[0]-measure/2-10,p[1]-15,measure+20,24,5);ctx.fill();ctx.stroke();ctx.fillStyle='#e2d3ae';ctx.textAlign='center';ctx.fillText(text,p[0],p[1]);
}
function draw(now){const t=now/1000,dt=Math.min((now-lastTime)/1000,.1);lastTime=now;ctx.clearRect(0,0,width,height);
 // Floor and softly lit perimeter.
 box(-7.5,-.25,-6,15,.25,13,['#1b2b33','#0c1921','#12232b']);
 for(let x=-7;x<=7;x++)line([x,.006,-6],[x,.006,7],'#2b40494f',.5);
 for(let z=-6;z<=7;z++)line([-7.5,.006,z],[7.5,.006,z],'#2b40494f',.5);
 box(-7.5,0,-6,.16,3.1,13,['#3d5059','#293c45','#192b35']);
 box(-7.5,0,-6,15,3.1,.16,['#3d5059','#22353f','#142832']);
 // Architectural windows and a library of histories on the back wall.
 for(let i=0;i<8;i++){
  const x=-6.6+i*1.75;polygon([[x,1.2,-5.82],[x+1.1,1.2,-5.82],[x+1.1,2.7,-5.82],[x,2.7,-5.82]],'#0b1922','#45616c');
  for(let k=0;k<4;k++)for(let j=0;j<4;j++)if((i+k+j)%3!==0)polygon([[x+.12+j*.23,1.3+k*.31,-5.81],[x+.23+j*.23,1.3+k*.31,-5.81],[x+.23+j*.23,1.46+k*.31,-5.81],[x+.12+j*.23,1.46+k*.31,-5.81]],(i+j)%2?'#b29b6350':'#769cad35');
 }
 line([-7.1,3.06,-5.72],[7.1,3.06,-5.72],'#d5bf8577',2);
 lamp(-6.9,-4.6);lamp(6.6,-4.6);lamp(-6.9,5.6);lamp(6.6,5.6);
 // Paths connect workstations, representing the production pipeline.
 for(let i=0;i<stations.length-1;i++){const a=stations[i],b=stations[i+1];line([a.x,.018,1],[b.x,.018,1],'#53655c55',1);line([a.x,.018,a.z+1.7],[a.x,.018,1],'#53655c55',1);}
 circle(0,.025,.5,1.0,'#d6b57409','#c3ab6e44');circle(0,.026,.5,.78,'#00000000','#c3ab6e55');label('◈',0,.03,.65,'#a79568',22);
 const target=sceneStage===1?{x:1,z:.5}:sceneStage>=0?{x:stations[sceneStage].x,z:stations[sceneStage].z+1.6}:{x:0,z:.5};
 if(reduced){agent.x=target.x;agent.z=target.z;}else{const distance=Math.hypot(target.x-agent.x,target.z-agent.z);if(distance>.015){const speed=Math.min(1,dt*3/distance);agent.x+=(target.x-agent.x)*speed;agent.z+=(target.z-agent.z)*speed;}}
 // Painter's order follows depth for a stable 3D camera.
 box(-4.85,0,.15,.12,.9,.12,['#526b75','#334e59','#233d49']);box(-3.25,0,.15,.12,.9,.12,['#526b75','#334e59','#233d49']);
 box(-5,.9,-.2,2,.12,.9,['#67848d','#415f6b','#2e4b58']);box(-4.65,1.02,-.05,1.25,.7,.1,['#4a6875','#142d3b','#264555']);
 for(let j=0;j<4;j++)box(-4.5+j*.26,1.06,.07,.12,.15+j*.1,.03,['#9ac4c4','#5a929d','#487d8b']);
 label('QUẢN LÝ KÊNH',-4,0,2.05,'#92b9c5',9);
 const handing=managerState.action?.startsWith('Đã giao')&&sceneRunning;
 const managerTarget=handing?{x:-1,z:.5}:{x:-4,z:1.2};
 managerPosition.x+=(managerTarget.x-managerPosition.x)*Math.min(1,dt*2);
 managerPosition.z+=(managerTarget.z-managerPosition.z)*Math.min(1,dt*2);
 const objects=stations.map((s,i)=>({depth:s.x*Math.sin(angle)+s.z*Math.cos(angle),draw:()=>desk(s,i,t)}));
 objects.push({depth:4*Math.sin(angle)+1.7*Math.cos(angle),draw:()=>person(4,1.7,t,false,true)});
 objects.push({depth:managerPosition.x*Math.sin(angle)+managerPosition.z*Math.cos(angle),draw:()=>person(managerPosition.x,managerPosition.z,t,true)});
 objects.push({depth:agent.x*Math.sin(angle)+agent.z*Math.cos(angle),draw:()=>person(agent.x,agent.z,t)});
 objects.sort((a,b)=>a.depth-b.depth).forEach(o=>o.draw());
 label('DẤU VẾT VĂN MINH',0,0,6.4,'#526971',9);
 requestAnimationFrame(draw);
}
canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,angle};canvas.setPointerCapture(e.pointerId);});
canvas.addEventListener('pointermove',e=>{if(drag)angle=Math.max(-.8,Math.min(.8,drag.angle+(e.clientX-drag.x)*.004));});
canvas.addEventListener('pointerup',()=>drag=null);canvas.addEventListener('pointercancel',()=>drag=null);
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.65,Math.min(1.5,zoom-e.deltaY*.001));},{passive:false});
$('rotate-left').onclick=()=>angle=Math.max(-.8,angle-.15);$('rotate-right').onclick=()=>angle=Math.min(.8,angle+.15);$('reset-view').onclick=()=>{angle=-.12;zoom=1;};
requestAnimationFrame(draw);
(async function poll(){await refresh();setTimeout(poll,1200);})();
