import test from 'node:test';
import assert from 'node:assert/strict';
import {createVideoProject,videoHome,videoWorkshop,videoShell} from './public/video-workspace.mjs';
const esc=s=>String(s??'').replaceAll('<','&lt;');
const btn=(text,action)=>`<button data-action="${action}">${text}</button>`;
test('app video tạo dự án trực tiếp từ kịch bản, không cần khảo sát hay dàn ý',()=>{
 const {channel,project}=createVideoProject(()=> 'id-'+Math.random());
 assert.equal(channel.type,'faceless');assert.equal(project.step,5);assert.equal(project.channelId,channel.id);
 assert.equal(project.narration,'');assert.deepEqual(project.scenes,[]);assert.deepEqual(project.approved,[]);
});
test('trang riêng chỉ có dự án video và thiết lập; không có cổng tìm ngách',()=>{
 const html=videoShell(videoHome({projects:[],channels:[]},{esc,btn}),{esc,btn});
 assert.match(html,/Video Studio/);assert.match(html,/video-new/);assert.doesNotMatch(html,/new-survey|new-channel|auto-pipeline/);
});
test('xưởng video nhận kịch bản và tái sử dụng căn cảnh, prompt, dựng phim',()=>{
 const {channel,project}=createVideoProject(()=> 'id');
 const html=videoWorkshop(channel,project,{esc,field:(label,binding)=>`${label}:${binding}`,btn,phase:1,tabs:()=>'<tabs>',body:()=>'<timing>',roster:()=>'<roster>',bible:()=>'<bible>'});
 assert.match(html,/project.narration/);assert.match(html,/<timing>/);assert.match(html,/<roster>/);assert.match(html,/<bible>/);
 const last=videoWorkshop(channel,project,{esc,btn,phase:4,tabs:()=>'<tabs>',body:()=>'<render>',field:()=>'',roster:()=>'',bible:()=>''});assert.match(last,/<render>/);assert.doesNotMatch(last,/project.narration/);
});
