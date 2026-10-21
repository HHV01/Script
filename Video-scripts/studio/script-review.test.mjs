import test from 'node:test';import assert from 'node:assert/strict';
import {reviewContext,runScriptReview,reviewIsCurrent,renderScriptReview,currentScriptParts,validateScriptReview,locateReviewQuote} from './public/script-review.mjs';
const c={language:'vi',angle:'Money mechanics'},p=()=>({topic:'Budget',minutes:1,narration:'Bạn tiêu tiền hôm nay. Bạn đã nghĩ tới ngày mai chưa?\n\nLập ngân sách giúp bạn nhìn rõ thu chi.\n\nBắt đầu bằng ghi lại khoản chi hôm nay.',sources:[{text:'PRIVATE_SOURCE'}],scriptParts:['OUTDATED SCRIPT'],visualStyle:'PRIVATE_STYLE'});
const output=ctx=>({overall:'revise',summary:'Cần làm rõ cơ chế.',strengths:['Mở bằng câu hỏi cụ thể.'],rubric:['hook','flow','clarity','novelty','ending'].map(criterion=>({criterion,verdict:'watch',reason:'Có thể cụ thể hơn.'})),issues:[{priority:'high',paragraph:2,quote:'Lập ngân sách',why:'Thiếu ví dụ.',suggestion:'Thêm một khoản chi cụ thể.',rewrite:'Bạn có thể ghi lại một khoản chi hôm nay.'}]});
test('one review uses current narration only, caches unchanged input, invalidates edits and never rewrites script',async()=>{
 const project=p(),before=project.narration,seen=[];const generate=async(a,ctx)=>{seen.push({a,ctx});return output(ctx);};let saves=0;
 await runScriptReview(c,project,{generate,save:async()=>saves++});assert.equal(seen.length,1);assert.equal(seen[0].a,'scriptReview');assert.doesNotMatch(JSON.stringify(seen[0].ctx),/PRIVATE_SOURCE|PRIVATE_STYLE|OUTDATED/);assert.equal(project.narration,before);assert(reviewIsCurrent(c,project));
 await runScriptReview(c,project,{generate,save:async()=>saves++});assert.equal(seen.length,1);project.narration+=' Câu mới.';assert(!reviewIsCurrent(c,project));await runScriptReview(c,project,{generate,save:async()=>{}});assert.equal(seen.length,2);
});
test('a project niche angle overrides the channel angle in review context',()=>{
 const project=p();project.nicheLock={angle:'Vì sao kim tự tháp được xây?'};
 assert.equal(reviewContext(c,project).angle,'Vì sao kim tự tháp được xây?');
 delete project.nicheLock;assert.equal(reviewContext(c,project).angle,c.angle);
});
test('unlocatable quotations become manual issues instead of failing the batch',async()=>{ const project=p(),ctx=reviewContext(c,project);const bad=output(ctx);bad.issues[0].quote='A quote that does not exist';
 const normalized=validateScriptReview(bad,ctx);assert.equal(normalized.issues[0].quote,'');assert.equal(normalized.issues[0].manual,true);
 bad.issues[0].paragraph=999;const normalized2=validateScriptReview(bad,ctx);assert.equal(normalized2.issues[0].quote,'');assert.equal(normalized2.issues[0].manual,true);
 project.scriptReview={summary:'previous'};let saved=0;await runScriptReview(c,project,{generate:async()=>bad,save:async()=>saved++});assert.equal(saved,1);assert.equal(project.scriptReview.overall,'revise');assert.equal(project.narration,p().narration);
});
test('economy review bounds excerpts and discloses sampling; full mode preserves text',()=>{
 const project=p();project.narration=Array.from({length:30},(_,i)=>('Đoạn '+i+' '+ 'câu chuyện '.repeat(80))).join('\n\n');let ctx=reviewContext(c,project);assert.equal(ctx.scope,'sampled');assert(ctx.coveragePercent<100);assert(ctx.paragraphs.reduce((n,x)=>n+x.text.length,0)<=8000);project.reviewFull=true;ctx=reviewContext(c,project);assert.equal(ctx.scope,'full');assert.equal(ctx.coveragePercent,100);
 assert.deepEqual(currentScriptParts({narration:'Fresh one.\n\nFresh two.',scriptParts:['OLD']}),['Fresh one.','Fresh two.']);
});
test('overview excerpts extend to a complete sentence instead of cutting mid-sentence',()=>{
 const long='Một câu mở đầu rất dài về kim tự tháp, về những khối đá, về hàng nghìn người, về những câu hỏi chưa được giải đáp, và về cách một nền văn minh đã biến niềm tin thành đá trong nhiều thập kỷ. ';
 const rest=Array.from({length:30},(_,i)=>`Đoạn ${i}. `+'Nội dung. '.repeat(60)).join('\n\n');
 const ctx=reviewContext({language:'vi'},{narration:long+'\n\n'+rest});
 assert.equal(ctx.scope,'sampled');
 assert(ctx.paragraphs[0].text.endsWith('.'));
 assert.equal(ctx.paragraphs[0].text,long.trim());
});
test('detail chunks end at sentence boundaries',()=>{
 const ctx=reviewContext({language:'vi'},{narration:'Một câu dài về kim tự tháp. '.repeat(100)});
 assert(ctx.paragraphs.every(x=>/[.!?…]$/.test(x.text)));
});
test('review display shows concrete prioritized fixes and stale/sample limitations with escaped text',async()=>{
 const project=p();await runScriptReview(c,project,{generate:async()=>output(),save:async()=>{}});project.narration+=' Changed';const esc=s=>String(s??'').replaceAll('<','&lt;');const html=renderScriptReview(c,project,{esc,btn:(t,a,x,attrs)=>`<button data-action="${a}" ${attrs}>${t}</button>`});assert.match(html,/cũ|đã đổi/i);assert.match(html,/Sửa trước/);assert.match(html,/Lập ngân sách/);assert.match(html,/không.*bảo đảm|không.*lượt xem/i);
});

test('quote locator selects the exact substring after long paragraph chunk boundaries',()=>{const narration=('word '.repeat(450)+'TARGET phrase').trim(),project={narration},ctx=reviewContext({},project),row=ctx.paragraphs.find(x=>x.text.includes('TARGET'));const at=locateReviewQuote(project,{paragraph:row.index,quote:'TARGET phrase'});assert.equal(narration.slice(at,at+13),'TARGET phrase');});

test('full review is bounded, resumes saved batches and still covers every paragraph',async()=>{
 const {reviewInBatches}=await import('./public/script-review.mjs');
 const ctx={...reviewContext(c,p()),scope:'full',coveragePercent:100,paragraphs:Array.from({length:12},(_,i)=>({index:i+1,text:('đoạn '+i+' ').repeat(180)}))};
 const cache={},seen=[];let fail=true;
 const generate=async(action,input)=>{seen.push(input);assert.ok(input.paragraphs.reduce((n,x)=>n+x.text.length,0)<=7000);if(seen.length===3&&fail)throw Error('offline');return {overall:'ready',summary:'Ổn',strengths:[],issues:[],rubric:Object.keys((await import('./public/script-review.mjs')).REVIEW_CRITERIA).map(criterion=>({criterion,verdict:'good',reason:'Ổn'}))};};
 await assert.rejects(reviewInBatches(ctx,{generate,cache,save:async()=>{}}),/offline/);
 const completed=seen.slice(0,2).map(x=>JSON.stringify(x));fail=false;seen.length=0;
 const result=await reviewInBatches(ctx,{generate,cache,save:async()=>{}});
 assert.equal(result.coveragePercent,100);assert.equal(result.overall,'ready');
 assert.ok(seen.every(x=>!completed.includes(JSON.stringify(x))));
 const all=[...completed.map(JSON.parse),...seen].flatMap(x=>x.paragraphs);
 for(const row of ctx.paragraphs)assert.ok(all.some(x=>x.index===row.index&&x.text===row.text));
});

test('batched review keeps concrete late issues and invalidates cached checks after edits',async()=>{
 const {reviewInBatches,REVIEW_CRITERIA}=await import('./public/script-review.mjs');
 const ctx={...reviewContext(c,p()),scope:'full',coveragePercent:100,paragraphs:Array.from({length:10},(_,i)=>({index:i+1,text:('nội dung '+i+' ').repeat(140)}))};
 const cache={};let calls=0;
 const generate=async(action,input)=>{
  calls++;const result={overall:'ready',summary:'Đã kiểm tra',strengths:[],issues:[],rubric:Object.keys(REVIEW_CRITERIA).map(criterion=>({criterion,verdict:'good',reason:'Ổn'}))};
  if(input.reviewStage==='detail'&&input.paragraphs.some(x=>x.index===10)){
   result.overall='revise';result.rubric.find(x=>x.criterion==='clarity').verdict='fix';
   result.issues=[{priority:'high',paragraph:10,quote:'nội dung 9',why:'Thiếu ý chính.',suggestion:'Làm rõ.',rewrite:'Ý chính cần làm rõ'}];
  }
  return result;
 };
 const first=await reviewInBatches(ctx,{generate,cache});assert.equal(first.overall,'revise');assert.equal(first.issues[0].paragraph,10);assert.equal(first.rubric.find(x=>x.criterion==='clarity').verdict,'fix');
 const done=calls;await reviewInBatches(ctx,{generate,cache});assert.equal(calls,done);
 ctx.paragraphs[0].text+=' mới';await reviewInBatches(ctx,{generate,cache});assert(calls>done);
});

test('long editorial comments normalize safely and unusable quotes/rewrites become manual',()=>{
 const ctx=reviewContext(c,p()),result=output(ctx);result.summary='Giải thích. '.repeat(70);result.rubric[0].reason='Cần sửa. '.repeat(70);result.issues[0].why='Lý do. '.repeat(90);result.issues[0].paragraph='2';
 const normalized=validateScriptReview(result,ctx);assert(normalized.summary.length<=500);assert(normalized.rubric[0].reason.length<=280);assert(normalized.issues[0].why.length<=300);assert.equal(normalized.issues[0].quote,result.issues[0].quote);assert.equal(normalized.issues[0].rewrite,result.issues[0].rewrite);
 const invalid=structuredClone(result);invalid.issues[0].quote='Câu AI tự bịa';const manual=validateScriptReview(invalid,ctx);assert.equal(manual.issues[0].quote,'');assert.equal(manual.issues[0].manual,true);
 invalid.issues[0].quote=result.issues[0].quote;invalid.issues[0].rewrite=Array(141).fill('từ').join(' ');const tooLong=validateScriptReview(invalid,ctx);assert.equal(tooLong.issues[0].rewrite,'');assert.equal(tooLong.issues[0].manual,true);
});

test('review format failure retries once and never retries quota failures',async()=>{
 const {reviewInBatches}=await import('./public/script-review.mjs');const ctx=reviewContext(c,p());let calls=0;
 const result=await reviewInBatches(ctx,{generate:async()=>{if(++calls===1)return {...output(ctx),summary:null};return output(ctx);}});
 assert.equal(calls,2);assert.equal(result.overall,'revise');
 calls=0;await assert.rejects(reviewInBatches(ctx,{generate:async()=>{calls++;throw Object.assign(Error('quota'),{status:429});}}),/quota/);assert.equal(calls,1);
 calls=0;await assert.rejects(reviewInBatches(ctx,{generate:async()=>{calls++;throw Object.assign(Error('Nhận xét sai'),{status:422});}}),/2 lần/);assert.equal(calls,2);
});

test('missing research and missing channel configuration are explicit without promoting an outline to evidence',()=>{
 const project=p();project.outline=[{story:'AI khẳng định mỏ đá 800 km.'}];project.sources=[];
 const ctx=reviewContext({},project);assert.equal(ctx.evidenceStatus.supported,0);assert.equal(ctx.evidenceStatus.status,'missing');assert.equal(ctx.evidenceStatus.sourceCount,0);assert.equal(ctx.evidenceStatus.outlineIsEvidence,false);
 const html=renderScriptReview({},project,{esc:x=>String(x),btn:()=>''});assert.match(html,/chứng cứ.*supported/i);assert.match(html,/chưa.*tên|chưa.*mở.*kết/i);
 project.researchFacts=[{claim:'Chứng cứ được người dùng kiểm.',sourceId:'s1',status:'supported'}];assert.equal(reviewContext({},project).evidenceStatus.supported,1);
});

test('a 229-character verbatim quote is accepted instead of failing the whole review',()=>{
 const narration='Đây là một câu rất dài về kim tự tháp và những người đã xây nó. '.repeat(8).trim();
 const project={narration,minutes:1},ctx=reviewContext({language:'vi'},project),row=ctx.paragraphs[0],quote=row.text.slice(0,229);
 assert.equal(quote.length,229);
 const result={overall:'revise',summary:'Cần gộp ý.',strengths:['Mở đầu rõ.'],rubric:['hook','flow','clarity','novelty','ending'].map(criterion=>({criterion,verdict:'watch',reason:'Có thể gọn hơn.'})),issues:[{priority:'high',paragraph:row.index,quote,why:'Lặp ý.',suggestion:'Gộp lại.',rewrite:'Một câu ngắn thay thế.'}]};
 assert.equal(validateScriptReview(result,ctx).issues[0].quote,quote);
});

test('an issue without a rewrite stays visible for manual editing instead of failing the batch',()=>{
 const ctx=reviewContext(c,p()),result=output(ctx);result.issues[0].rewrite='';
 const normalized=validateScriptReview(result,ctx);
 assert.equal(normalized.issues[0].rewrite,'');assert.equal(normalized.issues[0].manual,true);
});

test('a single issue or strength object is normalized instead of failing the batch',()=>{
 const ctx=reviewContext(c,p()),result=output(ctx);result.issues=result.issues[0];result.strengths=result.strengths[0];
 const normalized=validateScriptReview(result,ctx);
 assert.equal(normalized.issues.length,1);assert.equal(normalized.strengths.length,1);
});

test('a 666-character detail quote is accepted for a long paragraph',()=>{
 const narration='Một câu rất dài về quy trình vận chuyển đá và tổ chức lao động ở Giza. '.repeat(12).trim();
 const ctx=reviewContext({language:'vi'},{narration,minutes:1}),row=ctx.paragraphs[0],quote=row.text.slice(0,666);
 const result={overall:'revise',summary:'Cần gộp.',strengths:['Rõ.'],rubric:['hook','flow','clarity','novelty','ending'].map(criterion=>({criterion,verdict:'watch',reason:'Có thể gọn hơn.'})),issues:[{priority:'high',paragraph:row.index,quote,why:'Lặp ý.',suggestion:'Gộp.',rewrite:'Câu ngắn thay thế.'}]};
 assert.equal(validateScriptReview(result,ctx).issues[0].quote,quote);
});
