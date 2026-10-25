import net from 'node:net';
import {existsSync} from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp,mkdir,rm,readFile} from 'node:fs/promises';
import path from 'node:path';

test('app riêng: tạo, lưu, mở lại dự án; không tự gọi AI và giữ Studio gốc',async(t)=>{
 const socket=net.createServer();await new Promise(r=>socket.listen(0,'127.0.0.1',r));const port=socket.address().port;await new Promise(r=>socket.close(r));const base='http://127.0.0.1:'+port;
 await mkdir('tmp',{recursive:true});const dir=await mkdtemp(path.resolve('tmp/video-app-'));
 const original=await readFile('.studio-data/state.json','utf8').catch(()=>null);
 const child=spawn(process.execPath,['studio/video-server.mjs'],{env:{...process.env,STUDIO_PORT:String(port),STUDIO_DATA_DIR:dir},windowsHide:true,stdio:['ignore','pipe','pipe']});
 let browser;let error='';child.stderr.on('data',b=>error+=b);
 const ready=new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Server chưa sẵn sàng sau 20 giây: '+error)),20000);child.stdout.on('data',b=>{if(String(b).includes('http://localhost:')){clearTimeout(timer);resolve();}});child.once('exit',()=>{clearTimeout(timer);reject(Error(error||'Server đã dừng.'));});});
 try{
  await ready;
  const executablePath=process.env.VIDEO_TEST_BROWSER||'C:/Program Files/Google/Chrome/Application/chrome.exe';
  assert.match(await (await fetch(base)).text(),/video-app.js/);assert.deepEqual((await (await fetch(base+'/api/state')).json()).projects,[]);
  if(process.env.VIDEO_TEST_UI!=='1'){t.diagnostic('HTTP đã kiểm; UI Chrome chạy khi VIDEO_TEST_UI=1, giao diện có thể kiểm thủ công trên app.');return;}
  if(!existsSync(executablePath)){t.diagnostic('Không có Chrome: đã kiểm HTTP, bỏ phần trình duyệt.');return;}
  let chromium;try{({chromium}=await import('playwright-core'));}catch{t.diagnostic('Chưa cài playwright-core: HTTP đã qua, không chạy UI tự động.');return;}
  browser=await chromium.launch({executablePath,headless:true});const page=await browser.newPage();const errors=[],calls=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.url().includes('/api/generate'))calls.push(r.url());});
  await page.goto(base,{waitUntil:'domcontentloaded'});await page.getByRole('button',{name:'Tạo video từ kịch bản',exact:true}).waitFor();
  await page.getByRole('button',{name:'Tạo video từ kịch bản',exact:true}).click();
  const script=page.locator('[data-bind="project.narration"]');await script.waitFor();await script.fill('Một câu chuyện lịch sử. Câu tiếp theo.');await script.blur();
  await page.getByRole('button',{name:'3 · Tạo/nhập hình',exact:true}).click();
  await page.getByRole('button',{name:'4 · Xem trước + xuất',exact:true}).click();await page.getByRole('heading',{name:'Dựng video · ảnh + HTML + Wan + voice thành MP4',exact:true}).waitFor();
  await page.reload();await page.getByRole('button',{name:'1 · Kịch bản + voice',exact:true}).click();await script.waitFor();assert.equal(await script.inputValue(),'Một câu chuyện lịch sử. Câu tiếp theo.');
  await page.getByRole('button',{name:'Dự án',exact:true}).click();await page.getByRole('button',{name:'Chép dự án từ Tích Studio',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('#video-source-list')?.textContent.length>0);
  assert.equal(calls.length,0);assert.deepEqual(errors,[]);
  const stored=JSON.parse(await readFile(path.join(dir,'state.json'),'utf8'));assert.equal(stored.projects.length,1);assert.equal(stored.surveys.length,0);
  assert.equal(await readFile('.studio-data/state.json','utf8').catch(()=>null),original);
 }finally{if(browser)await browser.close();child.kill();if(child.exitCode===null)await once(child,'exit');await rm(dir,{recursive:true,force:true});}
});
