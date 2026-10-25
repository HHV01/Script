// Giao diện app video riêng; dùng lại nghiệp vụ cảnh, voice và render của Studio.
export function createVideoProject(uid) {
  const channel={id:uid(),name:'Dự án video',type:'faceless',language:'vi',characters:[],identity:{},visualStyle:'',promptLanguage:'vi'};
  const project={id:uid(),channelId:channel.id,topic:'Video mới',narration:'',minutes:5,clipSeconds:'10',step:5,approved:[],scenes:[],animations:[],sources:[],outline:[],packaging:[],mainCharacters:[],extraCharacters:[],backgrounds:[],roster:{},rosterConfirmed:true,rosterReviewed:true};
  return {channel,project};
}
export function videoShell(content,{btn}) {
  return `<div class="content"><header class="page-heading"><div><h1>Video Studio</h1><p>Kịch bản → prompt → căn cảnh theo voice/SRT → dựng MP4</p></div><span class="save-state">Đã lưu trên máy</span><nav class="actions">${btn('Dự án','home')}${btn('+ Video mới','video-new','primary')}${btn('Kết nối AI','settings')}</nav></header>${content}</div>`;
}
export function videoHome(state,{esc,btn}) {
  return `<section class="panel"><h2>Dự án video riêng</h2><p>Dán kịch bản đã viết. Dữ liệu app này được lưu riêng với Tích Studio.</p>${state.projects.map(p=>`<article><h3>${esc(p.topic||'Video chưa đặt tên')}</h3><p>${p.scenes?.length||0} cảnh</p>${btn('Mở dự án','video-open','',`data-id="${esc(p.id)}"`)}</article>`).join('')||'<p>Chưa có dự án.</p>'}<div class="actions">${btn('Tạo video từ kịch bản','video-new','primary')}${btn('Chép dự án từ Tích Studio','video-source')}</div><div id="video-source-list"></div></section>`;
}
export function videoWorkshop(c,p,{esc,field,btn,phase,tabs,body,roster,bible}) {
  const input=phase===1?`<section class="panel"><h2>Kịch bản đầu vào</h2>${field('Tên video','project.topic',p.topic)}${field('Toàn bộ lời kể tiếng Việt','project.narration',p.narration,'textarea','Dùng đúng bản đã đưa đi thu voice. Sửa lời kể sau khi chia cảnh cần kiểm tra và căn lại.')}${field('Phong cách hình ảnh dùng chung','channel.visualStyle',c.visualStyle,'textarea')}<label>Nhân vật chủ đạo<select data-bind="channel.type"><option value="faceless" ${c.type==='faceless'?'selected':''}>Không bắt buộc nhân vật chủ đạo</option><option value="character" ${c.type!=='faceless'?'selected':''}>Dùng nhân vật từ bible</option></select></label><details><summary>Nhân vật và bối cảnh</summary>${bible(c)}${roster(c,p)}</details></section>`:'';
  return `<h2>${esc(p.topic||'Video mới')}</h2>${tabs()}${input}${body(c,p)}`;
}
