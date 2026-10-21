import {scriptTarget} from '../production.mjs';
import {ensureScriptLength} from './script-length.mjs';
import {reviewContext,reviewInBatches,locateReviewQuote} from './script-review.mjs';
import {finalizeScriptMetadata} from './script-policy.mjs';
const normalize=s=>String(s).normalize('NFC').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu,' ').replace(/\s+/g,' ').trim();
const count=s=>String(s||'').trim().split(/\s+/).filter(Boolean).length;
const signature=value=>{const text=JSON.stringify(value);let h=2166136261;for(const ch of text)h=Math.imul(h^ch.charCodeAt(0),16777619);return text.length+':'+(h>>>0).toString(16);};
const inputs=(c,p)=>[c.name,c.language,c.angle,c.audience,c.identity,c.openingPlan,c.closingPlan,p.topic,p.outline,p.minutes,p.targetWords,p.researchFacts,p.claims,p.researchSummary,p.researchTimeline,p.researchCast,p.researchSensory,p.packaging?.[p.selectedPackaging||0]?.title,p.openingHook];
export const proofIsCurrent=(c,p)=>p.scriptQuality?.status==='passed'&&p.scriptQuality.basis===signature([inputs(c,p),p.narration]);

export function localScriptProblems(text){
 const issues=[],seen=new Set();
 for(const sentence of String(text).split(/(?<=[.!?…])\s+|\n+/u)){
  const normalized=normalize(sentence),tokens=normalized.split(' ');
  if(tokens.length>=12){if(seen.has(normalized))issues.push('Có câu dài trùng nguyên văn.');seen.add(normalized);}
  if(tokens.some((word,i)=>word&&word===tokens[i+1]&&word===tokens[i+2]))issues.push('Có từ lặp liền nhau ba lần.');
  for(let size=2;size<=5;size++)for(let i=0;i+size*3<=tokens.length;i++){
   const phrase=tokens.slice(i,i+size).join(' ');
   if(phrase===tokens.slice(i+size,i+size*2).join(' ')&&phrase===tokens.slice(i+size*2,i+size*3).join(' '))issues.push('Có cụm từ lặp liền nhau ba lần.');
  }
 }
 return [...new Set(issues)];
}

function editsFor(text,review,ctx,protectedText){
 const applicable=review.issues.filter(x=>x.rewrite&&x.rewrite.trim());
 if(!applicable.length)throw Error('AI chỉ ra lỗi nhưng không đề xuất câu thay; bản nháp được giữ để bạn sửa tay.');
 const candidates=applicable.map(issue=>{
  const at=locateReviewQuote({narration:text},issue);
  if(at<0||text.slice(at,at+issue.quote.length)!==issue.quote)throw Error('Câu cần sửa không còn khớp bản nháp.');
  // User-authored fixed/template segments remain verbatim.
  for(const fixed of protectedText){let start=text.indexOf(fixed);while(start>=0){if(at<start+fixed.length&&at+issue.quote.length>start)throw Error('Chỗ cần sửa thuộc đoạn cố định của kênh; cần bạn chỉnh kế hoạch đó.');start=text.indexOf(fixed,start+fixed.length);}}
  const allowed=new Set((text+' '+JSON.stringify(ctx.facts)).match(/\d+(?:[.,]\d+)*/g)||[]);
  if((issue.rewrite.match(/\d+(?:[.,]\d+)*/g)||[]).some(n=>!allowed.has(n)))throw Error('Gợi ý sửa thêm số liệu mới chưa có trong lời kể hoặc chứng cứ.');
  return {at,end:at+issue.quote.length,text:issue.rewrite};
 });
 // Giữ chỗ sửa ưu tiên cao trước; bỏ chỗ chồng lên để không ghép câu sai.
 const edits=[];
 for(const edit of candidates){if(edits.some(k=>edit.at<k.end&&edit.end>k.at))continue;edits.push(edit);}
 if(!edits.length)throw Error('Các câu sửa chồng nhau; cần duyệt lại bản nháp.');
 edits.sort((a,b)=>a.at-b.at);
 let next=text;for(const edit of edits.toReversed())next=next.slice(0,edit.at)+edit.text+next.slice(edit.end);
 if(next===text)throw Error('Nhận xét chưa có sửa đổi áp dụng được.');
 return next;
}

// Stage generated text separately. Only an all-good full review can publish it.
export async function buildProofedScript(c,p,{write,generate,save,onProgress=()=>{}}){
 scriptTarget(p);
 const basis=signature(inputs(c,p));
 if(p.scriptProofDraft?.basis!==basis)delete p.scriptProofDraft;
 if(!p.scriptProofDraft){
  const candidate=structuredClone(p);
  const saveDraft=async()=>{for(const key of ['scriptDraft','planDraft']){if(candidate[key])p[key]=structuredClone(candidate[key]);else delete p[key];}await save();};
  await write(candidate,saveDraft);
  p.scriptProofDraft={basis,narration:candidate.narration,editorNotes:candidate.editorNotes||[],warnings:candidate.scriptWarnings||[],sections:candidate.scriptSections||[],sfxSegments:[...(candidate.planResult?.opening||[]),...(candidate.planResult?.closing||[])].filter(x=>x.source.sfx).map(x=>({text:x.text||x.source.text,sfx:x.source.sfx})),protectedText:[...(candidate.planResult?.opening||[]),...(candidate.planResult?.closing||[])].filter(x=>['fixed','template'].includes(x.source.kind)).map(x=>x.text||x.source.text).filter(Boolean)};
  await save();
 }
 const draft=p.scriptProofDraft;
 try{
  for(let attempt=0;attempt<3;attempt++){
   onProgress(`Đang duyệt toàn bộ kịch bản · lượt ${attempt+1}/3`);
   await ensureScriptLength(c,p,draft,{generate,save,onProgress});
   const candidate={...p,narration:draft.narration,reviewFull:true,scriptWarnings:[]};
   finalizeScriptMetadata(c,candidate);
   const local=localScriptProblems(draft.narration),ctx=reviewContext(c,candidate);ctx.localChecks.problems=local;
   if(ctx.scope!=='full'||ctx.coveragePercent!==100)throw Error('Cần đọc đủ toàn bài trước khi hoàn tất.');
   // AI duyệt đôi khi trích câu không khớp nguyên văn đoạn văn. Đó là lỗi định
   // dạng của model, không phải bản nháp hỏng: thử lại một lần trước khi bỏ cuộc.
   let review,lastReviewError;
   for(let reviewTry=0;reviewTry<2&&!review;reviewTry++){
    try{draft.reviewBatches||={};review=await reviewInBatches(ctx,{generate,cache:draft.reviewBatches,save,onProgress});}
    catch(e){
     if(!/trích câu|Mức ưu tiên|Gợi ý sửa/.test(e.message))throw e;
     lastReviewError=e;draft.error=e.message;await save();
    }
   }
   if(!review)throw Error('AI duyệt trả câu trích không khớp bản nháp sau 2 lần thử. Bản nháp vẫn được giữ — bấm “Tiếp tục sửa và duyệt bản nháp” để thử lại.');
   const target=scriptTarget(p),lengthOK=!target||Math.abs(count(draft.narration)-target)<=target*.05;
   const clean=review.overall==='ready'&&review.issues.length===0&&review.rubric.every(x=>['good','watch'].includes(x.verdict))&&!local.length&&!(candidate.scriptWarnings||[]).some(x=>/thiếu|tagline|Cần duyệt|còn lặp/.test(x))&&lengthOK;
   draft.review=review;draft.problems=[...local,...(!lengthOK?['Độ dài chưa đạt mục tiêu ±5%.']:[])];await save();
   if(clean){
    if(p.narration)p.previousNarration=p.narration;
    p.narration=draft.narration;p.scriptParts=p.narration.split(/\n\s*\n/).filter(Boolean);p.editorNotes=draft.editorNotes;p.scriptWarnings=[];
    finalizeScriptMetadata(c,p);
    // Recompute word offsets from unchanged fixed text after sentence edits.
    p.scriptSfx=(draft.sfxSegments||[]).map(row=>{const at=p.narration.indexOf(row.text);return at<0?null:{word:count(p.narration.slice(0,at))+count(row.text)-1,text:row.sfx};}).filter(Boolean);
    p.scriptSfxBasis=p.narration.trim().split(/\s+/).join(' ');delete p.planResult;
    p.scriptQuality={status:'passed',basis:signature([inputs(c,p),p.narration]),coveragePercent:100,checkedAt:new Date().toISOString(),review};
    p.approved=(p.approved||[]).filter(x=>x<3);p.rosterReviewed=false;p.rosterConfirmed=false;delete p.scriptProofDraft;delete p.scriptDraft;delete p.planDraft;await save();return p.narration;
   }
   if(attempt===2||!review.issues.length)throw Error('Bản nháp chưa đạt: còn lỗi lặp, độ rõ nghĩa, cấu trúc hoặc độ dài. Chưa xuất thành lời dẫn hoàn chỉnh.');
   const next=editsFor(draft.narration,review,ctx,draft.protectedText||[]);
   if(count(next)>target*1.05)throw Error('Gợi ý sửa vượt mục tiêu số từ; giữ bản nháp để chỉnh tiếp.');
   draft.narration=next;await save();
  }
 }catch(e){draft.error=e.message;await save();throw e;}
}
