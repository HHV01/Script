import {detectPauses,alignScenes} from './voice-align.mjs';
export const DEFAULT_TEMPLATE='Minh họa nội dung: {loi_ke}\nPhong cách: {phong_cach}\nNhân vật (nếu có): {nhan_vat}\nKhung hình 16:9, bố cục rõ ràng, không chèn chữ.';
export const words=s=>String(s||'').trim().split(/\s+/).filter(Boolean);
export function newProject(id=crypto.randomUUID()){return {id,title:'Video mới',narration:'',promptTemplate:DEFAULT_TEMPLATE,style:'',character:'',voiceSeconds:0,clipSeconds:10,scenes:[]};}
export function parseTime(text){const value=String(text).trim(),parts=value.split(':');if(!value||parts.length>3||parts.some(x=>!/^\d+(?:\.\d+)?$/.test(x))||parts.slice(1).some(x=>Number(x)>=60))throw Error('Nhập giây hoặc mm:ss, h:mm:ss.');const seconds=parts.reduce((n,v)=>n*60+Number(v),0);if(!(seconds>0&&seconds<=14400))throw Error('Thời lượng phải từ 0 đến 4 giờ.');return seconds;}
export function planScenes(p){const tokens=words(p.narration),seconds=Number(p.voiceSeconds)||tokens.length/150*60,clip=Number(p.clipSeconds);if(!tokens.length||!Number.isFinite(seconds)||seconds<=0||!Number.isFinite(clip)||clip<1||clip>30)throw Error('Nhập kịch bản, thời lượng và nhịp cảnh hợp lệ.');const count=Math.min(tokens.length,Math.ceil(seconds/clip));p.scenes=Array.from({length:count},(_,i)=>({index:i+1,narration:tokens.slice(Math.floor(tokens.length*i/count),Math.floor(tokens.length*(i+1)/count)).join(' '),prompt:'',characters:[],start:seconds*i/count,end:seconds*(i+1)/count,duration:seconds/count,timing_source:'words'}));p.voiceSeconds=seconds;p.plannedNarration=p.narration;return p.scenes;}
export function timingStale(p){return Boolean(p.scenes.length&&p.plannedNarration!==p.narration);}
export function fitTiming(p,seconds){if(timingStale(p))throw Error('Lời kể đã đổi. Chia lại cảnh trước khi căn.');if(!p.scenes.length||!Number.isFinite(Number(seconds))||seconds<=0)throw Error('Cần cảnh và thời lượng hợp lệ.');const all=p.scenes.reduce((n,s)=>n+words(s.narration).length,0);let cursor=0;p.scenes.forEach((s,i)=>{s.start=cursor;s.end=i===p.scenes.length-1?Number(seconds):cursor+seconds*words(s.narration).length/all;s.duration=s.end-s.start;s.timing_source='words';cursor=s.end;});p.voiceSeconds=Number(seconds);if(p.scenes.some(s=>s.promptMode==='template'))fillTemplatePrompts(p);}
export function alignAudio(p,samples,sampleRate){if(timingStale(p))throw Error('Lời kể đã đổi, cần chia lại cảnh.');const detection=detectPauses(samples,sampleRate),anchorable=p.scenes.map(s=>/[.?!…:][\s\u0022\u0027”’)}\]]*$/.test(s.narration));let result=alignScenes(p.scenes.map(s=>words(s.narration).length),detection,{anchorable});fitTiming(p,detection.duration);if(result.ends){let cursor=0;p.scenes.forEach((s,i)=>{s.start=cursor;s.end=i===p.scenes.length-1?detection.duration:result.ends[i];s.duration=s.end-cursor;s.timing_source='pauses';cursor=s.end;});}p.alignReport={matched:result.matched,total:anchorable.slice(0,-1).filter(Boolean).length,source:'pauses'};p.alignWarning=p.alignReport.total&&result.matched/p.alignReport.total<.6?'Voice ít ngắt nghỉ hoặc có nhạc nền, mốc cảnh chỉ là ước lượng.':'';if(p.scenes.some(s=>s.promptMode==='template'))fillTemplatePrompts(p);return p.alignReport;}
export function composePrompt(p,s){if(s.promptMode==='template'||s.promptMode==='manual')return String(s.prompt||'');return [p.style.trim(),p.character.trim()?`Nhân vật dùng trong cảnh (nếu có): ${p.character.trim()}`:'',s.prompt.trim()].filter(Boolean).join('\n');}
export function templatePrompt(p,s){
 const template=p.promptTemplate??DEFAULT_TEMPLATE;
 if(!template.trim()||!template.includes('{loi_ke}'))throw Error('Mẫu cần có {loi_ke} để khớp lời kể từng cảnh.');
 const values={loi_ke:s.narration||'',phong_cach:p.style||'',nhan_vat:p.character||'',so_canh:s.index,bat_dau:Number(s.start||0).toFixed(1),ket_thuc:Number(s.end||0).toFixed(1),thoi_luong:Number(Number(s.duration||0).toFixed(2))};
 return template.replace(/\{([\p{L}\w]+)\}/gu,(_,key)=>{if(!Object.hasOwn(values,key))throw Error('Không hỗ trợ biến {'+key+'}.');return String(values[key]);}).trim();
}
export function fillTemplatePrompts(p,{only=null,force=false}={}){
 if(timingStale(p))throw Error('Kịch bản đã đổi. Chia lại cảnh trước.');
 if(!p.scenes.length)throw Error('Chia cảnh trước khi ghép prompt.');
 const pending=p.scenes.filter((s,i)=>(only===null||i===only)&&(force||!s.prompt?.trim()||s.promptMode==='template'));
 const next=pending.map(s=>[s,templatePrompt(p,s)]);
 for(const [s,text] of next){s.prompt=text;s.promptMode='template';}
 return next.length;
}
export function exportCsv(p){const escape=v=>'"'+String(v??'').replaceAll('"','""')+'"';return [['scene','start','end','duration','narration','image_prompt','warnings','prompt_vi','timing_source'],...p.scenes.map(s=>[s.index,s.start,s.end,s.duration,s.narration,composePrompt(p,s),s.duration>Number(p.clipSeconds)+.5?'Vượt nhịp cảnh':'',s.prompt,s.timing_source])].map(row=>row.map(escape).join(',')).join('\r\n');}
